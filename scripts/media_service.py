"""Canonical media/object-storage boundary.

Untrusted uploads are stored under opaque quarantine keys until confirm-upload
validates size, magic bytes and decodes the image. Permanent media is converted
to WebP and metadata-free bytes before being marked READY.
"""

from __future__ import annotations

import hashlib
import io
import os
import uuid
from datetime import datetime, timezone


class MediaError(ValueError):
    pass


class MediaProviderUnavailable(RuntimeError):
    pass


MAX_UPLOAD_BYTES = 5 * 1024 * 1024
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}


def _s3_client():
    try:
        import boto3
    except ImportError as exc:
        raise MediaProviderUnavailable("boto3 is not installed.") from exc

    endpoint = os.getenv("POL_S3_ENDPOINT_URL")
    access_key = os.getenv("POL_S3_ACCESS_KEY_ID")
    secret_key = os.getenv("POL_S3_SECRET_ACCESS_KEY")
    region = os.getenv("POL_S3_REGION", "us-east-1")

    if not endpoint or not access_key or not secret_key:
        raise MediaProviderUnavailable(
            "S3-compatible storage is not configured; set POL_S3_ENDPOINT_URL, "
            "POL_S3_ACCESS_KEY_ID and POL_S3_SECRET_ACCESS_KEY."
        )

    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region,
    )


def _bucket() -> str:
    return os.getenv("POL_S3_BUCKET", "pol-media")


def _magic_mime(raw: bytes) -> str:
    if raw.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if raw.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
        return "image/webp"
    raise MediaError("Unsupported or invalid image file signature.")


def _target_key(target_type: str, target_id: str, media_id: str) -> str:
    target = target_type.upper()
    if target == "PRODUCT":
        return f"products/{target_id}/canonical/{media_id}.webp"
    if target == "VENDOR":
        day = datetime.now(timezone.utc).date().isoformat()
        return f"vendors/{target_id}/uploads/{day}/{media_id}.webp"
    if target == "DISPUTE":
        return f"disputes/{target_id}/evidence/{media_id}.webp"
    if target == "DELIVERY":
        return f"deliveries/{target_id}/proof/{media_id}.webp"
    if target == "PAYMENT":
        return f"payments/{target_id}/evidence/{media_id}.webp"
    if target == "SUPPORT":
        return f"support/{target_id}/attachments/{media_id}.webp"
    if target == "CANDIDATE":
        return f"vendors/candidates/{target_id}/{media_id}.webp"
    raise MediaError(f"Unsupported media target type: {target_type}")


def _authorize_target(cur, user_id: str, organization_id: str, target_type: str, target_id: str) -> dict:
    target = target_type.upper()

    if target == "PRODUCT":
        cur.execute("SELECT id FROM products WHERE id=%s AND is_active=TRUE", (target_id,))
        if not cur.fetchone():
            raise MediaError("Target product not found.")
        cur.execute(
            """
            SELECT 1
            FROM organization_memberships om
            JOIN organizations o ON o.id=om.organization_id
            WHERE om.user_id=%s AND om.organization_id=%s AND om.status='ACTIVE'
              AND o.status='ACTIVE'
              AND om.role IN ('VENDOR_OWNER','VENDOR_STAFF','OPS_ADMIN','ADMIN_SUPER')
            """,
            (user_id, organization_id),
        )
        if not cur.fetchone():
            raise PermissionError("Not authorized to attach media to this product.")
        return {"provenance": "VENDOR_UPLOADED"}

    table_map = {
        "VENDOR": (
            "SELECT id FROM vendors WHERE id=%s AND organization_id=%s",
            ("VENDOR_OWNER", "VENDOR_STAFF"),
            "VENDOR_UPLOADED",
        ),
        "CANDIDATE": (
            "SELECT v.id FROM product_candidates pc JOIN vendors v ON v.id=pc.vendor_id "
            "WHERE pc.id=%s AND v.organization_id=%s",
            ("VENDOR_OWNER", "VENDOR_STAFF"),
            "VENDOR_UPLOADED",
        ),
        "DISPUTE": (
            "SELECT 1 FROM disputes d "
            "JOIN retailers r ON r.id=d.retailer_id "
            "JOIN vendors v ON v.id=d.vendor_id "
            "WHERE d.id=%s AND (r.organization_id=%s OR v.organization_id=%s)",
            ("RETAILER_OWNER", "RETAILER_STAFF", "VENDOR_OWNER", "VENDOR_STAFF"),
            "POL_OWNED",
        ),
        "DELIVERY": (
            "SELECT 1 FROM deliveries d "
            "JOIN orders o ON o.id=d.order_id "
            "JOIN retailers r ON r.id=o.retailer_id "
            "JOIN vendors v ON v.id=o.vendor_id "
            "WHERE d.id=%s AND (r.organization_id=%s OR v.organization_id=%s)",
            ("RETAILER_OWNER", "RETAILER_STAFF", "VENDOR_OWNER", "VENDOR_STAFF"),
            "POL_OWNED",
        ),
        "PAYMENT": (
            "SELECT 1 FROM payments p "
            "JOIN retailers r ON r.id=p.retailer_id "
            "JOIN vendors v ON v.id=p.vendor_id "
            "WHERE p.id=%s AND (r.organization_id=%s OR v.organization_id=%s)",
            ("RETAILER_OWNER", "RETAILER_STAFF", "VENDOR_OWNER", "VENDOR_STAFF"),
            "POL_OWNED",
        ),
        "SUPPORT": (
            "SELECT 1 FROM support_cases sc WHERE sc.id=%s AND sc.organization_id=%s",
            ("RETAILER_OWNER", "RETAILER_STAFF", "VENDOR_OWNER", "VENDOR_STAFF", "OPS_AGENT", "OPS_ADMIN", "ADMIN_SUPER"),
            "POL_OWNED",
        ),
    }

    if target not in table_map:
        raise MediaError(f"Unsupported media target type: {target_type}")

    sql, roles, provenance = table_map[target]
    params = (target_id, organization_id, organization_id) if target in {"DISPUTE", "DELIVERY", "PAYMENT"} else (target_id, organization_id)
    cur.execute(sql, params)
    if not cur.fetchone():
        raise MediaError("Target not found in the active organization context.")

    placeholders = ",".join(["%s"] * len(roles))
    cur.execute(
        f"""
        SELECT 1
        FROM organization_memberships om
        JOIN organizations o ON o.id=om.organization_id
        WHERE om.user_id=%s AND om.organization_id=%s
          AND om.status='ACTIVE' AND o.status='ACTIVE'
          AND om.role IN ({placeholders})
        """,
        (user_id, organization_id, *roles),
    )
    if not cur.fetchone():
        raise PermissionError("Not authorized for this media target.")
    return {"provenance": provenance}


class MediaService:
    @staticmethod
    def presign(cur, *, user_id: str, organization_id: str, mime_type: str,
                file_size_bytes: int, target_type: str, target_id: str,
                filename: str | None = None) -> dict:
        if mime_type not in ALLOWED_MIME_TYPES:
            raise MediaError("Only JPEG, PNG and WebP uploads are allowed.")
        if file_size_bytes <= 0 or file_size_bytes > MAX_UPLOAD_BYTES:
            raise MediaError("Upload size must be between 1 byte and 5 MB.")

        meta = _authorize_target(cur, user_id, organization_id, target_type, target_id)
        media_id = str(uuid.uuid4())
        object_key = f"quarantine/{organization_id}/{media_id}"

        cur.execute(
            """
            INSERT INTO media_assets (
                id, storage_provider, storage_bucket, storage_key, mime_type,
                file_size_bytes, checksum_sha256, status, provenance, uploaded_by_user_id
            )
            VALUES (%s,'S3_MINIO',%s,%s,%s,%s,'','UPLOADING',%s,%s)
            RETURNING id
            """,
            (media_id, _bucket(), object_key, mime_type, file_size_bytes,
             meta["provenance"], user_id),
        )

        s3 = _s3_client()
        expires = int(os.getenv("POL_MEDIA_PRESIGN_TTL_SECONDS", "300"))
        url = s3.generate_presigned_url(
            ClientMethod="put_object",
            Params={"Bucket": _bucket(), "Key": object_key, "ContentType": mime_type},
            ExpiresIn=expires,
        )
        return {
            "media_id": media_id,
            "upload_url": url,
            "object_key": object_key,
            "expires_in_seconds": expires,
        }

    @staticmethod
    def confirm_upload(cur, *, user_id: str, organization_id: str, media_id: str,
                       target_type: str, target_id: str) -> dict:
        cur.execute(
            """
            SELECT *
            FROM media_assets
            WHERE id=%s AND uploaded_by_user_id=%s AND status='UPLOADING'
            FOR UPDATE
            """,
            (media_id, user_id),
        )
        media = cur.fetchone()
        if not media:
            raise MediaError("Media upload not found or not owned by current user.")

        meta = _authorize_target(cur, user_id, organization_id, target_type, target_id)
        s3 = _s3_client()
        bucket = media["storage_bucket"]

        try:
            obj = s3.get_object(Bucket=bucket, Key=media["storage_key"])
            raw = obj["Body"].read(MAX_UPLOAD_BYTES + 1)
        except Exception as exc:
            raise MediaError("Uploaded object is not available in object storage.") from exc

        if len(raw) > MAX_UPLOAD_BYTES:
            raise MediaError("Uploaded object exceeds the 5 MB limit.")

        actual_mime = _magic_mime(raw)
        if actual_mime not in ALLOWED_MIME_TYPES:
            raise MediaError("Uploaded object failed magic-byte validation.")

        try:
            from PIL import Image
        except ImportError as exc:
            raise MediaProviderUnavailable("Pillow is not installed.") from exc

        try:
            image = Image.open(io.BytesIO(raw))
            image.verify()
            image = Image.open(io.BytesIO(raw))
            if image.mode in ("RGBA", "LA"):
                processed = image.convert("RGBA")
            else:
                processed = image.convert("RGB")
            out = io.BytesIO()
            processed.save(out, format="WEBP", quality=85, method=6)
            final_bytes = out.getvalue()
        except Exception as exc:
            raise MediaError("Uploaded object is not a decodable image.") from exc

        checksum = hashlib.sha256(final_bytes).hexdigest()
        final_key = _target_key(target_type, target_id, media_id)

        s3.put_object(
            Bucket=bucket,
            Key=final_key,
            Body=final_bytes,
            ContentType="image/webp",
            Metadata={"sha256": checksum, "provenance": meta["provenance"]},
        )

        # Remove the untrusted quarantine object after the trusted derivative is stored.
        try:
            s3.delete_object(Bucket=bucket, Key=media["storage_key"])
        except Exception:
            # The trusted final object exists; cleanup can be retried operationally.
            pass

        cur.execute(
            """
            UPDATE media_assets
            SET storage_key=%s,
                storage_bucket=%s,
                mime_type='image/webp',
                file_size_bytes=%s,
                width=%s,
                height=%s,
                checksum_sha256=%s,
                status='READY',
                provenance=%s
            WHERE id=%s
            RETURNING *
            """,
            (
                final_key, bucket, len(final_bytes), processed.width, processed.height,
                checksum, meta["provenance"], media_id,
            ),
        )
        ready = cur.fetchone()

        target = target_type.upper()
        if target == "PRODUCT":
            cur.execute(
                """
                INSERT INTO product_media
                    (id, product_id, media_asset_id, is_primary, display_order)
                VALUES (%s,%s,%s,FALSE,0)
                ON CONFLICT (product_id, media_asset_id) DO NOTHING
                """,
                (str(uuid.uuid4()), target_id, media_id),
            )
        elif target == "CANDIDATE":
            cur.execute(
                "UPDATE product_candidates SET photo_asset_id=%s WHERE id=%s",
                (media_id, target_id),
            )
        elif target == "DISPUTE":
            cur.execute(
                "UPDATE disputes SET evidence_media_id=%s WHERE id=%s",
                (media_id, target_id),
            )
        elif target == "DELIVERY":
            # One POD per delivery is enforced by migration 033.
            cur.execute(
                "SELECT 1 FROM proof_of_delivery WHERE delivery_id=%s",
                (target_id,),
            )
            # Do not create a fake proof record here. Attach when POD is created.
        return {
            "media_id": str(ready["id"]),
            "status": ready["status"],
            "mime_type": ready["mime_type"],
            "file_size_bytes": int(ready["file_size_bytes"]),
            "checksum_sha256": ready["checksum_sha256"],
            "storage_key": ready["storage_key"],
        }

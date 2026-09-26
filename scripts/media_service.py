"""Canonical media/object-storage boundary.

Untrusted uploads are stored under opaque quarantine keys until confirm-upload
validates size, magic bytes and decodes the image. Permanent media is converted
to WebP and metadata-free bytes before being marked READY.
"""

from __future__ import annotations

import hashlib
import io
import math
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


def _validate_bound_upload_target(media: dict, target_type: str, target_id: str) -> None:
    """Reject confirm-upload retargeting after a presign has been authorized."""
    bound_type = str(media.get("upload_target_type") or "").upper()
    bound_id = str(media.get("upload_target_id") or "")
    requested_type = target_type.upper()
    requested_id = str(target_id)

    # Every in-flight upload must have an immutable authorization binding.
    # Historical rows created before migration 048 are therefore fail-closed.
    if str(media.get("status") or "").upper() == "UPLOADING" and (not bound_type or not bound_id):
        raise MediaError("Upload confirmation is missing its authorized target binding.")

    if bound_type != requested_type or bound_id != requested_id:
        raise MediaError("Upload confirmation target does not match the authorized presign target.")



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
        cur.execute(
            """
            SELECT 1
            FROM products
            WHERE id=%s AND is_active=TRUE
            """,
            (target_id,),
        )
        if not cur.fetchone():
            raise MediaError("Target product not found.")

        cur.execute(
            """
            SELECT om.role
            FROM organization_memberships om
            JOIN organizations o ON o.id=om.organization_id
            WHERE om.user_id=%s
              AND om.organization_id=%s
              AND om.status='ACTIVE'
              AND o.status='ACTIVE'
            LIMIT 1
            """,
            (user_id, organization_id),
        )
        membership = cur.fetchone()
        if not membership:
            raise PermissionError("Not authorized to attach media to this product.")

        role = str(membership["role"])
        canonical_ops_roles = {"OPS_AGENT", "OPS_ADMIN", "ADMIN_SUPER", "SUPER_ADMIN"}
        if role in canonical_ops_roles:
            return {"provenance": "POL_OWNED"}

        if role in {"VENDOR_OWNER", "VENDOR_STAFF"}:
            cur.execute(
                """
                SELECT 1
                FROM vendor_products vp
                JOIN vendors v ON v.id=vp.vendor_id
                JOIN organizations o ON o.id=v.organization_id
                WHERE vp.product_id=%s
                  AND v.organization_id=%s
                  AND o.status='ACTIVE'
                  AND v.status='ACTIVE'
                LIMIT 1
                """,
                (target_id, organization_id),
            )
            if cur.fetchone():
                return {"provenance": "VENDOR_UPLOADED"}

        raise PermissionError(
            "Not authorized to attach media to this product from the active organization."
        )

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
                id, storage_provider, storage_bucket, storage_key,
                bucket_name, object_key, mime_type,
                file_size_bytes, checksum_sha256, status, provenance,
                uploaded_by_user_id, upload_target_type, upload_target_id
            )
            VALUES (%s,'S3_MINIO',%s,%s,%s,%s,%s,%s,%s,'UPLOADING',%s,%s,%s,%s)
            RETURNING id
            """,
            (
                media_id, _bucket(), object_key, _bucket(), object_key, mime_type, file_size_bytes,
                None, meta["provenance"], user_id, target_type.upper(), target_id,
            ),
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
    def presign_resumable(cur, *, user_id: str, organization_id: str, mime_type: str,
                          file_size_bytes: int, target_type: str, target_id: str,
                          filename: str | None = None, part_size_bytes: int = 1024 * 1024) -> dict:
        if mime_type not in ALLOWED_MIME_TYPES:
            raise MediaError("Only JPEG, PNG and WebP uploads are allowed.")
        if file_size_bytes <= 0 or file_size_bytes > MAX_UPLOAD_BYTES:
            raise MediaError("Upload size must be between 1 byte and 5 MB.")
        if part_size_bytes < 262144 or part_size_bytes > 5242880:
            raise MediaError("Part size must be between 256 KB and 5 MB.")
        meta = _authorize_target(cur, user_id, organization_id, target_type, target_id)
        media_id = str(uuid.uuid4())
        object_key = f"quarantine/{organization_id}/{media_id}"
        part_count = max(1, math.ceil(file_size_bytes / part_size_bytes))
        if part_count > 10000:
            raise MediaError("Upload requires too many multipart parts.")
        cur.execute(
            """
            INSERT INTO media_assets (
                id, storage_provider, storage_bucket, storage_key, bucket_name, object_key,
                mime_type, file_size_bytes, checksum_sha256, status, provenance,
                uploaded_by_user_id, upload_target_type, upload_target_id
            )
            VALUES (%s,'S3_MINIO',%s,%s,%s,%s,%s,%s,NULL,'UPLOADING',%s,%s,%s,%s)
            RETURNING id
            """,
            (media_id, _bucket(), object_key, _bucket(), object_key, mime_type, file_size_bytes,
             meta["provenance"], user_id, target_type.upper(), target_id),
        )
        s3 = _s3_client()
        created = s3.create_multipart_upload(Bucket=_bucket(), Key=object_key, ContentType=mime_type)
        upload_id = created["UploadId"]
        try:
            cur.execute(
                """INSERT INTO media_upload_sessions
                   (media_asset_id, provider_upload_id, part_size_bytes, part_count)
                   VALUES (%s,%s,%s,%s) RETURNING id""",
                (media_id, upload_id, part_size_bytes, part_count),
            )
            session_id = str(cur.fetchone()["id"])
        except Exception:
            try:
                s3.abort_multipart_upload(Bucket=_bucket(), Key=object_key, UploadId=upload_id)
            finally:
                raise
        expires = int(os.getenv("POL_MEDIA_PRESIGN_TTL_SECONDS", "300"))
        urls = [{
            "part_number": part_number,
            "upload_url": s3.generate_presigned_url(
                ClientMethod="upload_part",
                Params={"Bucket": _bucket(), "Key": object_key, "UploadId": upload_id, "PartNumber": part_number},
                ExpiresIn=expires,
            ),
        } for part_number in range(1, part_count + 1)]
        return {
            "session_id": session_id, "media_id": media_id, "object_key": object_key,
            "part_size_bytes": part_size_bytes, "part_count": part_count,
            "expires_in_seconds": expires, "parts": urls,
        }

    @staticmethod
    def complete_resumable(cur, *, user_id: str, organization_id: str, session_id: str, parts: list[dict]) -> dict:
        cur.execute(
            """
            SELECT s.*, ma.storage_bucket, ma.storage_key, ma.status AS media_status
            FROM media_upload_sessions s
            JOIN media_assets ma ON ma.id = s.media_asset_id
            WHERE s.id=%s AND ma.uploaded_by_user_id=%s
            FOR UPDATE OF s, ma
            """,
            (session_id, user_id),
        )
        session = cur.fetchone()
        if not session:
            raise MediaError("Resumable upload session not found.")
        if session["status"] == "COMPLETED":
            return {"session_id": str(session["id"]), "media_id": str(session["media_asset_id"]), "status": "COMPLETED"}
        if session["status"] != "OPEN" or session["media_status"] != "UPLOADING":
            raise MediaError("Resumable upload session is not open.")
        by_number = {}
        for part in parts:
            number = int(part["part_number"])
            if number in by_number:
                raise MediaError("Multipart parts must not repeat a part number.")
            by_number[number] = str(part["etag"])
        if sorted(by_number) != list(range(1, int(session["part_count"]) + 1)):
            raise MediaError("Every expected multipart part must be supplied exactly once.")
        s3 = _s3_client()
        s3.complete_multipart_upload(
            Bucket=session["storage_bucket"], Key=session["storage_key"],
            UploadId=session["provider_upload_id"],
            MultipartUpload={"Parts": [{"ETag": etag, "PartNumber": number} for number, etag in sorted(by_number.items())]},
        )
        cur.execute(
            "UPDATE media_upload_sessions SET status='COMPLETED', completed_at=now() WHERE id=%s RETURNING id",
            (session_id,),
        )
        return {"session_id": str(session_id), "media_id": str(session["media_asset_id"]), "status": "COMPLETED", "needs_processing": True}

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

        _validate_bound_upload_target(media, target_type, target_id)
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
            image.info.clear()  # Explicit EXIF/metadata stripping before trusted persistence.
            if image.mode in ("RGBA", "LA"):
                processed = image.convert("RGBA")
            else:
                processed = image.convert("RGB")
            out = io.BytesIO()
            processed.save(out, format="WEBP", quality=85, method=6, exif=b"")
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

        thumbnail = processed.copy()
        try:
            from PIL import ImageOps
            thumbnail = ImageOps.fit(thumbnail, (150, 150), method=Image.Resampling.LANCZOS)
        except Exception as exc:
            raise MediaError("Failed to generate thumbnail.") from exc
        thumb_out = io.BytesIO()
        thumbnail.save(thumb_out, format="WEBP", quality=82, method=6, exif=b"")
        thumbnail_bytes = thumb_out.getvalue()
        thumbnail_checksum = hashlib.sha256(thumbnail_bytes).hexdigest()
        thumbnail_key = final_key.rsplit(".", 1)[0] + "-thumb.webp"
        s3.put_object(
            Bucket=bucket,
            Key=thumbnail_key,
            Body=thumbnail_bytes,
            ContentType="image/webp",
            Metadata={"sha256": thumbnail_checksum, "variant": "THUMBNAIL", "source_media_id": media_id},
        )
        cur.execute(
            """
            INSERT INTO media_variants (
                source_media_asset_id, variant_type, storage_bucket, storage_key,
                mime_type, file_size_bytes, width, height, checksum_sha256
            )
            VALUES (%s,'THUMBNAIL',%s,%s,'image/webp',%s,%s,%s,%s)
            ON CONFLICT (source_media_asset_id, variant_type) DO UPDATE SET
                storage_bucket=EXCLUDED.storage_bucket,
                storage_key=EXCLUDED.storage_key,
                file_size_bytes=EXCLUDED.file_size_bytes,
                width=EXCLUDED.width,
                height=EXCLUDED.height,
                checksum_sha256=EXCLUDED.checksum_sha256
            """,
            (media_id, bucket, thumbnail_key, len(thumbnail_bytes),
             thumbnail.width, thumbnail.height, thumbnail_checksum),
        )
        cur.execute(
            "UPDATE media_upload_sessions SET status='COMPLETED', completed_at=COALESCE(completed_at, now()) "
            "WHERE media_asset_id=%s AND status='OPEN'",
            (media_id,),
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
                object_key=%s,
                bucket_name=%s,
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
                final_key, bucket, final_key, bucket, len(final_bytes), processed.width, processed.height,
                checksum, meta["provenance"], media_id,
            ),
        )
        ready = cur.fetchone()

        target = target_type.upper()
        if target == "PRODUCT":
            cur.execute(
                """
                INSERT INTO product_media
                    (id, product_id, media_asset_id, media_type, source_provenance,
                     approval_status, approved_by_user_id, approved_at, is_primary, display_order)
                VALUES (
                    %s,%s,%s,'PRIMARY_IMAGE',%s,
                    CASE WHEN %s = 'POL_OWNED' THEN 'APPROVED' ELSE 'PENDING' END,
                    CASE WHEN %s = 'POL_OWNED' THEN %s ELSE NULL END,
                    CASE WHEN %s = 'POL_OWNED' THEN now() ELSE NULL END,
                    FALSE,0
                )
                ON CONFLICT (product_id, media_asset_id) DO UPDATE SET
                    media_type=EXCLUDED.media_type,
                    source_provenance=EXCLUDED.source_provenance
                """,
                (
                    str(uuid.uuid4()), target_id, media_id, meta["provenance"],
                    meta["provenance"], meta["provenance"], user_id,
                    meta["provenance"],
                ),
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
            "thumbnail": {"storage_key": thumbnail_key, "checksum_sha256": thumbnail_checksum},
        }

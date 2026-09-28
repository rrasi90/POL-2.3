from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from scripts.api.dependencies import get_application_boundary, require_roles
from scripts.api.errors import success_payload
from scripts.api.schemas import (
    MediaConfirmUploadRequest,
    MediaPresignRequest,
    MediaResumableCompleteRequest,
    MediaResumableInitRequest,
)

router = APIRouter(prefix="/media", tags=["media"])


@router.post("/presigned-url", status_code=200)
def media_presigned_url(
    payload: MediaPresignRequest,
    boundary=Depends(get_application_boundary),
    _auth: dict = Depends(
        require_roles(
            "RETAILER_OWNER", "RETAILER_STAFF",
            "VENDOR_OWNER", "VENDOR_STAFF",
            "OPS_AGENT", "OPS_ADMIN", "ADMIN_SUPER",
        )
    ),
):
    return success_payload(
        boundary.media_presign(
            mime_type=payload.mime_type,
            file_size_bytes=payload.file_size_bytes,
            target_type=payload.target_type,
            target_id=payload.target_id,
            filename=payload.filename,
        )
    )


@router.post("/resumable/init", status_code=200)
def media_resumable_init(
    payload: MediaResumableInitRequest,
    boundary=Depends(get_application_boundary),
    _auth: dict = Depends(
        require_roles(
            "RETAILER_OWNER", "RETAILER_STAFF", "VENDOR_OWNER", "VENDOR_STAFF",
            "OPS_AGENT", "OPS_ADMIN", "ADMIN_SUPER",
        )
    ),
):
    return success_payload(
        boundary.media_presign_resumable(
            mime_type=payload.mime_type, file_size_bytes=payload.file_size_bytes,
            target_type=payload.target_type, target_id=payload.target_id, filename=payload.filename,
        )
    )


@router.post("/resumable/complete", status_code=200)
def media_resumable_complete(
    payload: MediaResumableCompleteRequest,
    boundary=Depends(get_application_boundary),
    _auth: dict = Depends(
        require_roles(
            "RETAILER_OWNER", "RETAILER_STAFF", "VENDOR_OWNER", "VENDOR_STAFF",
            "OPS_AGENT", "OPS_ADMIN", "ADMIN_SUPER",
        )
    ),
):
    return success_payload(
        boundary.media_complete_resumable(
            session_id=payload.session_id,
            parts=[item.model_dump() for item in payload.parts],
        )
    )


@router.post("/confirm-upload", status_code=200)
def media_confirm_upload(
    payload: MediaConfirmUploadRequest,
    boundary=Depends(get_application_boundary),
    _auth: dict = Depends(
        require_roles(
            "RETAILER_OWNER", "RETAILER_STAFF",
            "VENDOR_OWNER", "VENDOR_STAFF",
            "OPS_AGENT", "OPS_ADMIN", "ADMIN_SUPER",
        )
    ),
):
    return success_payload(
        boundary.media_confirm_upload(
            media_id=payload.media_id,
            target_type=payload.target_type,
            target_id=payload.target_id,
        )
    )

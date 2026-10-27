"""Operational management HTTP routes backed by POLApplicationBoundary."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from scripts.api.dependencies import get_application_boundary
from scripts.api.errors import success_payload
from scripts.api.schemas import (
    AdminOrganizationStatusRequest,
    AdminUserStatusRequest,
    VendorStaffInviteRequest,
    VendorStaffUpdateRequest,
    AdminSlaOverrideRequest,
    AdminProductCandidateReviewRequest,
    DelegatedPermissionGrantRequest,
    DelegatedPermissionRevokeRequest,
)

vendor_router = APIRouter(prefix="/vendors", tags=["vendor-management"])
admin_router = APIRouter(prefix="/admin", tags=["admin-management"])
ops_router = APIRouter(prefix="/ops", tags=["ops-management"])


@vendor_router.get("/customers")
def vendor_customers(
    query: str | None = Query(default=None, max_length=120),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.vendor_customers_list(query=query, offset=offset, limit=limit)
    )


@vendor_router.get("/staff")
def vendor_staff(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    boundary=Depends(get_application_boundary),
):
    return success_payload(boundary.vendor_staff_list(offset=offset, limit=limit))


@vendor_router.post("/staff/invite", status_code=201)
def vendor_staff_invite(
    payload: VendorStaffInviteRequest,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.vendor_staff_invite(
            phone_number=payload.phone_number,
            full_name=payload.full_name,
        )
    )


@vendor_router.get("/staff/{membership_id}/permissions")
def vendor_staff_permissions(
    membership_id: UUID,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.delegated_permissions_list(membership_id=str(membership_id))
    )


@vendor_router.post("/staff/{membership_id}/permissions")
def vendor_staff_permission_grant(
    membership_id: UUID,
    payload: DelegatedPermissionGrantRequest,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.delegated_permission_grant(
            membership_id=str(membership_id),
            permission_key=payload.permission_key,
            reason=payload.reason,
            client=payload.client,
        )
    )


@vendor_router.post("/staff/{membership_id}/permissions/{permission_key}/revoke")
def vendor_staff_permission_revoke(
    membership_id: UUID,
    permission_key: str,
    payload: DelegatedPermissionRevokeRequest,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.delegated_permission_revoke(
            membership_id=str(membership_id),
            permission_key=permission_key,
            reason=payload.reason,
            client=payload.client,
        )
    )


@vendor_router.patch("/staff/{membership_id}")
def vendor_staff_update(
    membership_id: UUID,
    payload: VendorStaffUpdateRequest,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.vendor_staff_update(
            membership_id=str(membership_id),
            role=payload.role,
            status=payload.status,
        )
    )


@admin_router.get("/users")
def admin_users(
    query: str | None = Query(default=None, max_length=120),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.admin_users_list(query=query, offset=offset, limit=limit)
    )


@admin_router.patch("/users/{user_id}/status")
def admin_user_status(
    user_id: UUID,
    payload: AdminUserStatusRequest,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.admin_user_update(
            user_id=str(user_id),
            is_active=payload.is_active,
        )
    )


@admin_router.post("/sla-overrides")
def admin_sla_override(
    payload: AdminSlaOverrideRequest,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.admin_sla_override(
            order_id=str(payload.order_id),
            extension_minutes=payload.extension_minutes,
            reason=payload.reason,
        )
    )


@admin_router.get("/product-candidates")
def admin_product_candidates(
    status: str | None = Query(default="PENDING_REVIEW"),
    query: str | None = Query(default=None, max_length=160),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.admin_product_candidates_list(
            status=status,
            query=query,
            offset=offset,
            limit=limit,
        )
    )


@admin_router.patch("/product-candidates/{candidate_id}")
def admin_product_candidate_review(
    candidate_id: UUID,
    payload: AdminProductCandidateReviewRequest,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.admin_product_candidate_review(
            candidate_id=str(candidate_id),
            action=payload.action,
            reason=payload.reason,
            brand_id=str(payload.brand_id) if payload.brand_id else None,
            category_id=str(payload.category_id) if payload.category_id else None,
            subcategory_id=str(payload.subcategory_id) if payload.subcategory_id else None,
            canonical_name_fa=payload.canonical_name_fa,
            target_product_id=str(payload.target_product_id) if payload.target_product_id else None,
        )
    )


@admin_router.get("/organizations")
def admin_organizations(
    query: str | None = Query(default=None, max_length=120),
    org_type: str | None = Query(default=None, max_length=32),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.admin_organizations_list(
            query=query, org_type=org_type, offset=offset, limit=limit
        )
    )


@admin_router.patch("/organizations/{organization_id}/status")
def admin_organization_status(
    organization_id: UUID,
    payload: AdminOrganizationStatusRequest,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.admin_organization_update(
            organization_id=str(organization_id),
            status=payload.status,
        )
    )


@ops_router.get("/permissions/audit")
def permission_audit(
    membership_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.delegated_permission_audit(
            membership_id=str(membership_id) if membership_id else None,
            limit=limit,
        )
    )


@ops_router.get("/permissions")
def permission_catalog(boundary=Depends(get_application_boundary)):
    return success_payload(boundary.permission_catalog())


@ops_router.get("/returns")
def global_returns(
    status: str | None = Query(default=None, max_length=32),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.global_returns_list(status=status, offset=offset, limit=limit)
    )

"""Authenticated support case HTTP routes — create, list, get, message, transition."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from scripts.api.dependencies import get_application_boundary
from scripts.api.errors import success_payload
from scripts.api.schemas import (
    SupportCaseCreateRequest,
    SupportCaseMessageRequest,
    SupportCaseTransitionRequest,
)


router = APIRouter(prefix="/support/cases", tags=["support"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_support_case(
    payload: SupportCaseCreateRequest,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.support_create(
            organization_id=boundary.context.organization_id,
            case_type=payload.case_type,
            subject=payload.subject,
            related_order_id=payload.related_order_id,
            priority=payload.priority,
        )
    )


@router.get("")
def list_support_cases(
    boundary=Depends(get_application_boundary),
):
    return success_payload(boundary.support_list())


@router.get("/{case_id}")
def get_support_case(
    case_id: UUID,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.support_get(case_id=str(case_id))
    )


@router.post("/{case_id}/messages", status_code=status.HTTP_201_CREATED)
def add_support_message(
    case_id: UUID,
    payload: SupportCaseMessageRequest,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.support_message(
            case_id=str(case_id),
            message_text=payload.message_text,
        )
    )


@router.patch("/{case_id}")
def transition_support_case(
    case_id: UUID,
    payload: SupportCaseTransitionRequest,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.support_transition(
            case_id=str(case_id),
            target_status=payload.target_status,
            resolution_code=payload.resolution_code,
            resolution_note=payload.resolution_note,
        )
    )

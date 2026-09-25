"""Canonical dispute application adapter.

The concrete persistence implementation remains in the domain service while
HTTP/application boundaries depend on this adapter, making the canonical
dependency explicit and keeping legacy imports out of transport boundaries.
"""

from scripts.domain_services import DisputeService


class CanonicalDisputeService:
    open_dispute = staticmethod(DisputeService.open_dispute)
    resolve_dispute = staticmethod(DisputeService.resolve_dispute)

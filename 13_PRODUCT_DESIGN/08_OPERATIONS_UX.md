# Phase 4 — POL Operations UX

## Product goal
Give POL operators one controlled workbench for exceptions, queues and customer/vendor support without exposing raw database mechanics.

## Primary queues
- Orders requiring intervention
- Fulfillment exceptions
- Support cases
- RMA / disputes
- Payment reconciliation
- Reliability/risk events
- Notification delivery failures
- Vendor daily-confirmation exceptions
- Pilot activation / referral signals

## Information hierarchy
1. What needs action now?
2. Why is it blocked?
3. What context is needed to decide?
4. What action is allowed?
5. What audit trail will be recorded?

## Detail view
Every operational object should combine:
- current state;
- timeline/audit;
- related customer/vendor/order;
- evidence;
- next allowed actions;
- ownership/assignment.

## Tables
Tables are for high-density review. Use responsive cards for mobile. Keyboard interaction, visible focus and accessible controls are component requirements, consistent with Carbon's current data-table accessibility approach. citeturn990483search6

## Risk / exception UX
Never hide why an action is blocked. Distinguish:
- user-correctable input problem;
- business-rule rejection;
- system/service failure;
- permission/tenant restriction.

The error language should tell operators what happened and what the recovery path is rather than merely exposing technical exceptions. citeturn990483search1

## Permission model
Ops UI is persona-adaptive but authorization must be resolved by authenticated membership context and canonical RBAC. UI hiding is not a security control.

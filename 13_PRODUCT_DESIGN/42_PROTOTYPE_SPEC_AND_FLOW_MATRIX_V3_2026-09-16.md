# POL Prototype Specification v3

## Prototype philosophy
Prototype the user's task, not the page collection. Every critical path must include normal, changed-state and failure recovery branches.

## Retailer critical flows
### RP-01 Purchase
Home → Search → Results → Product → Quantity → Basket → Revalidate → Allocation → Final review → Submit → Order group.
Branches:
- price changed
- stale inventory
- vendor unavailable
- MOQ failure
- partial allocation
- session expiry before submit

### RP-02 Reorder
Order history → Previous basket → Change detection → Basket → Allocation → Submit.

### RP-03 RMA
Order → Issue type → Item/qty → Evidence → Review → Submit → Tracking.
Branches: evidence failure, unsupported file, clarification requested.

### RP-04 Support
Help → Category → Context auto-attached → Message → Attachment → Submit → Case state.

## Vendor critical flows
### VP-01 Accept order
Queue → Detail → Accept / Partial / Reject → Reason if required → Confirmation → Updated state.

### VP-02 Inventory
Dashboard → Confirmation → Edit → Submit → Receipt; stale/unknown values remain visible.

### VP-03 Reconciliation
Reconciliation → Transaction → Evidence → Submit → Pending/Rejected/Reconciled.

## Ops critical flows
### OP-01 Queue work
Queue → Detail → Evidence → Allowed action → Confirmation → Audit timeline.

### OP-02 RMA decision
Claim → Evidence → Vendor response → Review → Clarification or decision → Adjustment/refund status.

### OP-03 Reliability
Incident → Severity/reason → Linked objects → Remediation → Closed with audit.

## Field critical flows
### FP-01 Activation
Today → Retailer → Business context → Consent → Membership → First assisted action → Receipt.

### FP-02 Assisted order
Retailer context → Search → Basket → Allocation → Submit.

### FP-03 Weak network
Task → Action → Network degraded → Local pending indicator → Retry/sync → Success or conflict recovery.

## Corporate flows
- Home → Pilot proof → Contact CTA.
- Home → Vendor → How POL works → Contact.

## Prototype acceptance
A flow passes only if:
- user can identify current state;
- next action is obvious;
- constraints appear before commitment;
- failure branches do not lose context or data;
- back/cancel behavior is defined;
- deep links land on the correct object;
- every terminal state communicates outcome and next step.

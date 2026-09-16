# POL — Prototype Flows & Failure Branches v2

Status: CANONICAL PROTOTYPE QA SPEC

## 1. Prototype philosophy
Prototype the user's decision journey, not every backend endpoint. Every critical happy path must have at least one realistic failure/recovery branch.

## 2. Retailer core loop
`Home → Search → Results → Product → Quantity → Basket → Allocation Review → Checkout → Confirmation → Order`

Required branches:
- no result
- unavailable product
- stale inventory
- MOQ not met
- price changed during revalidation
- vendor unavailable
- session expired
- checkout submission failure

## 3. Retailer reorder
`Orders → Order detail → Repeat purchase → Review changes → Basket → Checkout`
Branch:
- historical product unavailable
- pack changed
- price changed

## 4. Retailer dispute
`Order → Issue → Items/quantity → Evidence → Submit → Tracking`
Branches:
- unsupported evidence type
- upload failure
- missing required information
- vendor response pending
- clarification requested
- decision

## 5. Vendor acceptance
`Dashboard → Orders → Detail → Accept / Partial / Reject → Reason → Submit → Receipt`
Branches:
- inventory insufficient
- stale inventory
- duplicate submit
- session expiry

## 6. Vendor daily inventory
`Dashboard → Inventory confirmation → Review → Edit → Confirm → Receipt`
Branches:
- conflict
- stale snapshot
- invalid quantity
- save retry

## 7. Ops workbench
`Queue → Object → Evidence → Action → Audit`
Branches:
- permission denied
- evidence unavailable
- stale object
- concurrent change
- action rejected by canonical rule

## 8. Field activation
`Today → Retailer → Context → Consent → Profile/Persona → Assisted action → Receipt`
Branches:
- weak network
- duplicate retailer match
- no active organization
- incomplete mandatory context

## 9. Failure design rules
1. Preserve recoverable input.
2. State the problem in user language.
3. Explain the next action.
4. Keep the affected object visible.
5. Avoid generic “something went wrong”.
6. Do not expose internal stack traces or policy codes.
7. Maintain focus after error.
8. Never imply success before server confirmation.
9. Avoid destructive resets after temporary failure.
10. When the service is at fault, do not blame the user.

These rules align with GOV.UK guidance on clear, specific error messages, recovery instructions and preserving entered values. citeturn218293search0turn218293search1

## 10. Prototype acceptance
A flow passes only if:
- user understands current state;
- next action is obvious;
- no critical constraint is hidden;
- error branch is recoverable where possible;
- state transitions match domain contracts;
- RTL and mixed-direction content remain readable;
- mobile and desktop behavior are explicit.

# POL Design Tokens & Component Inventory

## Token layers
### Global
- color
- typography
- spacing
- radius
- elevation
- motion
- breakpoint

### Semantic
- surface / content / border
- brand / interactive
- success / warning / danger / info
- status: pending / active / blocked / completed / cancelled

### Product
- retailer density
- vendor data density
- ops data density
- field touch density

## Component inventory v1
Foundation:
- Button
- IconButton
- TextInput
- NumberInput
- SearchField
- Select
- Checkbox / Radio
- Switch

Commerce:
- ProductCard
- ProductRow
- QuantityStepper
- PriceBlock
- PackBlock
- MOQNotice
- AvailabilityBadge
- BasketLine
- VendorAllocationCard
- CheckoutSummary
- OrderCard
- OrderTimeline

Operations:
- StatusBadge
- FilterBar
- DataTable
- QueueCard
- AssignmentBlock
- EvidencePanel
- AuditTimeline

Navigation:
- TopBar
- SideNav
- BottomNav
- Tabs
- Breadcrumb
- TenantSwitcher

System:
- EmptyState
- LoadingState
- Skeleton
- ErrorState
- RetryAction
- Toast
- Banner
- Modal
- BottomSheet
- Drawer
- Confirmation

Identity:
- Avatar
- ProfileCard
- MembershipContext
- PersonaHeader

## Component acceptance
Each component must have:
- RTL and LTR behavior;
- keyboard/focus behavior;
- touch target validation;
- loading/disabled/error states where applicable;
- content-length stress cases;
- mobile and desktop behavior;
- contract/state examples;
- accessibility annotation.

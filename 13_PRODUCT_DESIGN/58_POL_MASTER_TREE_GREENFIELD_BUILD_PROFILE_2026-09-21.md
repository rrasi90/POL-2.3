# POL — Master Tree Greenfield Build Profile

**Document ID:** `POL-DESIGN-GREENFIELD-001`  
**Version:** `1.0.0`  
**Date:** 2026-09-21  
**Status:** ACTIVE / CANONICAL BUILD PROFILE / BLANK PENPOT FILE  
**Repository:** `rrasi90/POL-2.3`  
**Branch:** `product-architecture-evolution-2026-09-20`  
**Master Tree:** `50_POL_MASTER_PENPOT_UI_UX_TREE_SPEC_2026-09-21.md` v4.1.0  
**Visual Authority:** `56_POL_PRECISION_COMMERCE_VISUAL_DESIGN_SYSTEM_2026-09-21.md`

---

# 0. Purpose

This profile defines how the POL Master Tree must be executed when the target Penpot file is **completely new and empty**.

This is not a migration plan.

This is not a redesign of an existing Penpot file.

This is not a frame-by-frame repair exercise.

It is a **GREENFIELD / FROM-ZERO / EMPTY-FILE BUILD**.

The target operating equation is:

`Repository Truth → Master Tree → Build Profile → Foundations → Components → Patterns → Golden Screens → Product Screens → Flows → QA`

Penpot becomes authoritative only after the corresponding artifact has been created and verified.

---

# 1. Target state

## 1.1 Initial Penpot state

At WAVE-00 the target Penpot file is expected to contain:

- one empty file;
- no trusted existing pages;
- no trusted components;
- no trusted design tokens;
- no trusted styles;
- no trusted reusable patterns;
- no trusted prototypes;
- no trusted screens.

The agent MUST verify the actual initial state before mutation.

A successful file-open/tool response is not enough.

## 1.2 Historical Penpot is evidence only

The previously inspected Penpot export is **historical reference material**.

It may be used for:

- identifying previous design intent;
- discovering old naming;
- locating historical contradictions;
- comparing visual direction;
- validating what the repository previously claimed.

It MUST NOT be used as the construction baseline for the new blank file.

No old frame is automatically copied.

No old component is automatically copied.

No old token is automatically imported.

No old page structure is automatically preserved.

The new file is built from current canonical repository truth.

## 1.3 Greenfield source precedence

For construction:

1. current product/architecture decisions;
2. current domain/data/API/security authorities;
3. current Master Tree;
4. current executable schema;
5. current Precision Commerce visual system;
6. current design contracts/pattern rules;
7. historical design artifacts as evidence only.

Historical Penpot must never outrank current canonical sources.

---

# 2. GREENFIELD build objective

The objective is NOT:

> reproduce the old Penpot file.

The objective is:

> construct the smallest complete, structurally correct, visually coherent and agent-verifiable Penpot system that realizes the current POL product architecture from zero.

The new file must therefore optimize for:

- canonical foundations;
- reusable components;
- explicit variants;
- Light/Night theme parity;
- responsive behavior;
- RTL/bidi correctness;
- accessibility;
- low-bandwidth behavior;
- explicit states;
- exact traceability;
- golden references;
- agent-safe construction.

---

# 3. File architecture to create

The blank file MUST converge to the following page architecture.

### P00 — Foundations
Purpose:
- brand;
- visual DNA;
- primitive tokens;
- semantic tokens;
- typography;
- spacing;
- radius;
- borders;
- elevation;
- iconography;
- grid/layout;
- RTL/Bidi specimens;
- Light;
- Night.

### P01 — Components
Purpose:
- canonical reusable components;
- variants;
- state variants;
- accessibility states;
- theme variants;
- responsive component behavior.

### P02 — Shared UX
Purpose:
- navigation;
- search;
- filters;
- contextual feedback;
- notifications;
- identity/context switcher;
- revalidation;
- evidence/POD;
- universal feedback;
- shared loading/empty/error/recovery.

### P03 — States & Patterns
Purpose:
- canonical UI state library;
- state transitions shown visually;
- reusable operational patterns;
- tables/queues;
- financial rows;
- permission matrix;
- scanner;
- handoff;
- candidate review;
- provenance;
- partial acceptance;
- session/security.

### P04 — Retailer
Purpose:
- Retailer / POL Market experience.

### P05 — Vendor
Purpose:
- Vendor / POL Vendor experience.

### P06 — Operations
Purpose:
- operator/admin workflows.

### P07 — Field Activator
Purpose:
- Field operations.

### P08 — Corporate
Purpose:
- corporate/institutional surface.

### P09 — Prototypes & Flows
Purpose:
- end-to-end walking skeletons;
- critical failure branches;
- theme parity;
- responsive demonstrations.

### P10 — Design QA
Purpose:
- accessibility;
- RTL;
- content stress;
- responsive;
- theme;
- component coverage;
- traceability;
- visual baseline.

### P99 — Agent QA & Golden Evals
Purpose:
- golden components;
- golden screens;
- capability probes;
- structure probes;
- persistence probes;
- visual checkpoints;
- evaluator outputs;
- circuit-breaker evidence.

This page architecture is a **construction target**, not merely documentation.

---

# 4. Build order

The build order is strict.

## WAVE-00 — Preflight / Empty File

Do not design product screens.

Verify:

- file is accessible;
- file is actually empty or classified;
- initial revision is recorded;
- page count is recorded;
- meaningful object count is recorded;
- no trusted tokens/components are assumed;
- Agent capabilities are probed.

Persist:

- RUN_ID;
- WAVE_ID = WAVE-00;
- repository HEAD;
- Master Tree version;
- schema version;
- build profile version;
- Penpot file identity;
- initial Penpot revision.

---

# 5. WAVE-01 — Foundations

Build only the design system foundation.

Order:

1. primitive color tokens;
2. semantic Light tokens;
3. semantic Night tokens;
4. typography tokens;
5. spacing tokens;
6. dimension/radius tokens;
7. border tokens;
8. elevation tokens;
9. motion tokens;
10. density definitions;
11. grid/layout conventions;
12. iconography;
13. RTL/Bidi specimen;
14. content-stress specimen.

No full product screen should be constructed before the foundation checkpoint passes.

Penpot's token system supports token sets, themes and reusable token bindings; POL should use that native mechanism rather than encoding Light/Night through duplicated raw values. citeturn491925search0

---

# 6. WAVE-02 — Golden Components

Build the minimum reusable component kernel.

Priority:

1. Button
2. Icon Button
3. Input
4. Search
5. Select / Filter
6. Chip
7. Badge / Status
8. Card
9. List Row
10. Table Row
11. Tabs / Segmented Control
12. Navigation
13. Modal
14. Bottom Sheet
15. Toast / Alert
16. Skeleton
17. Empty State
18. Error State
19. Confirmation
20. Timeline
21. Financial Activity Row
22. Permission Matrix
23. Permission Editor
24. Scanner Surface
25. Delivery Handoff
26. Provenance Badge
27. Candidate Product
28. Partial Acceptance
29. Session Card
30. Media Picker

Where related component states exist, use Penpot variants rather than duplicating independent components. Penpot's variant model is explicitly designed to group states, sizes and styles into a single customizable component with preserved overrides. citeturn491925search2turn491925search1

---

# 7. WAVE-03 — Shared Patterns

Construct patterns only from Golden Components.

Required patterns include:

- authenticated shell;
- tenant/membership context;
- list + filter;
- search results;
- product comparison;
- order queue;
- financial history;
- exception queue;
- audit log;
- permission editor;
- candidate approval;
- media provenance review;
- handoff verification;
- partial acceptance review;
- notification/inbox;
- empty/error/recovery;
- loading/skeleton;
- offline/read-only network states where canonical runtime supports them.

A screen-specific visual invention must be treated as an exception requiring explicit classification.

---

# 8. WAVE-04 — Golden Screens

Before constructing every product screen, build a small golden set proving the system works.

Required Golden Screens:

1. Retailer Home
2. Product Search
3. Product Detail
4. Vendor Storefront
5. Basket
6. Checkout
7. OrderGroup Detail
8. Vendor Order Queue
9. Operations Exceptions
10. Financial Activity
11. Permission Editor
12. Scanner
13. Delivery Handoff
14. Corporate Landing

Each Golden Screen MUST exist in:

- Light;
- Night;
- mobile where applicable;
- desktop where applicable;
- critical states;
- RTL content;
- long-content stress where relevant.

Golden screens are reference implementations, not disposable mockups.

---

# 9. WAVE-05 — Product surfaces

Build product surfaces only from approved components and patterns.

Construction order:

### Retailer
Auth → Home → Search → Vendor Search → Vendor Storefront → Product Detail → Basket → Allocation → Checkout → OrderGroup → Partial Acceptance → Financial Activity → Delivery → Handoff → Returns/Disputes → History → Account/Support

### Vendor
Inventory/Price → Order Queue → Partial Acceptance → Loading/Dispatch → Discrepancy → Catalog → Storefront Management → Staff/Permissions → Scanner → Financial Activity → Documents/Invoices → Referral → Customers → Reconciliation

### Operations
Exceptions → Arbitration → Reconciliation → Pilot Analytics → Support → Risk → Notifications → Admin → Permission Audit → Financial Investigation → Candidate Review → Media Provenance → Handoff Exceptions

### Field
Route/Task → Assisted Order → Merchant Consent → Follow-up/Proof → Network/Operational recovery

### Corporate
Institutional Landing → operational model → architecture/trust → about/contact/legal surfaces

---

# 10. Theme construction rule

Do NOT:

1. build Light;
2. duplicate it;
3. change colors until it looks dark.

Instead:

1. define semantic tokens;
2. define Light token set;
3. define Night token set;
4. connect component variants to semantic tokens;
5. verify both themes;
6. build screens with active theme context.

Penpot supports multi-dimensional themes and theme groups, including mode/platform combinations, which fits POL's Light/Night + Web/Android design architecture. citeturn491925search0

---

# 11. Responsive construction rule

Do not create mobile and desktop as unrelated redesigns.

Use:

**same information architecture + same component contracts + responsive composition.**

Desktop may add:

- persistent navigation;
- wider tables;
- side context;
- parallel columns;
- keyboard efficiency.

Mobile may add:

- bottom navigation;
- stacked layout;
- bottom sheets;
- larger touch targets;
- simplified simultaneous information.

The semantic node remains the same.

---

# 12. RTL construction rule

The blank file must establish RTL before product screens.

Foundations must include stress specimens for:

- Persian paragraphs;
- mixed Persian/Latin names;
- URLs;
- phone numbers;
- prices;
- SKUs;
- barcodes;
- order IDs;
- timestamps;
- mixed-direction table cells.

Do not solve RTL after screens are built.

---

# 13. Component construction rule

The main component becomes the source of truth.

Instances are used on screens.

Do not draw visual copies of a Button/Card/Input separately on every page.

Penpot's component architecture is specifically built around a main component and linked copies/instances, allowing controlled reuse and propagation. citeturn491925search1

---

# 14. State construction rule

For every critical component/screen, construct only states supported by the canonical product/runtime truth.

Typical state families:

- default;
- hover where applicable;
- focus;
- pressed;
- selected;
- loading;
- success;
- empty;
- error;
- permission denied;
- unavailable;
- stale;
- expired;
- concurrent change;
- already completed.

Do not add invented states such as persisted offline writes unless the runtime contract supports them.

---

# 15. Penpot object naming

Every canonical object must have a stable semantic name.

Recommended structure:

`[Domain]/[NodeType]/[CanonicalID]/[Variant]`

Examples:

- `Retailer/SCR/RT-02/Home/Light`
- `Retailer/SCR/RT-02/Home/Night`
- `Shared/CMP/Button/Primary/Default`
- `Vendor/PATTERN/VD-02/OrderQueue`
- `Ops/CMP/PermissionEditor`

Names must not depend on temporary generation wording.

---

# 16. Build checkpoints

Every wave has an explicit checkpoint.

## Checkpoint A — Foundation

Pass only when:

- tokens persist;
- Light exists;
- Night exists;
- typography persists;
- spacing persists;
- RTL specimen exists;
- no arbitrary raw design values are introduced in canonical components.

## Checkpoint B — Components

Pass only when:

- canonical components persist;
- required variants exist;
- token bindings are real;
- component states are inspectable;
- Light/Night parity exists.

## Checkpoint C — Patterns

Pass only when:

- patterns use real components;
- no duplicated semantic component exists;
- critical states are represented.

## Checkpoint D — Golden Screens

Pass only when:

- screens use canonical components;
- Light/Night exist;
- responsive behavior is represented;
- RTL stress passes;
- structural persistence is proven.

## Checkpoint E — Product Surfaces

Pass only when:

- capability-to-screen traceability is intact;
- actions map to state/permission;
- API/domain contracts are mapped;
- screen artifact bindings exist.

## Checkpoint F — Final QA

Pass only when:

- visual;
- structural;
- semantic;
- accessibility;
- RTL;
- responsive;
- network;
- prototype;
- traceability

evidence exists for applicable dimensions.

---

# 17. Agent mutation rules for the blank file

The agent must prefer:

**Create → Verify → Reuse**

rather than:

**Draw → Duplicate → Repair**

For every mutation:

1. resolve target canonical node;
2. resolve current build wave;
3. resolve applicable closure profile;
4. resolve required tokens;
5. resolve component/pattern dependencies;
6. inspect current Penpot state;
7. mutate one logical unit;
8. fresh-read persistence;
9. export/inspect at meaningful checkpoints;
10. record evidence;
11. update artifact binding;
12. update maturity.

---

# 18. Parallelism rule

Parallel agent execution is allowed only across independent regions.

Safe examples:

- Foundations token documentation vs research evidence preparation;
- Retailer screen specification vs Operations screen specification;
- visual QA preparation vs API traceability preparation.

Unsafe examples:

- two agents simultaneously mutating the same component family;
- two agents editing the same page;
- two agents changing global tokens;
- simultaneous mutation of prototypes and their underlying screen structure.

Global tokens, canonical components and shared patterns are serialized.

---

# 19. What NOT to build from the old Penpot

The new file must NOT automatically reproduce:

- old component variants;
- old OTP box count;
- old 30-minute SLA copy;
- historical Driver App;
- unsupported rich offline flows;
- stale wallet-like UI;
- obsolete role aliases;
- arbitrary page-level visual inconsistencies;
- historical duplicated components;
- generic Text/Rectangle artifacts.

The repository's current canonical truth decides what is rebuilt.

---

# 20. Greenfield artifact policy

At first build, artifact binding status may legitimately be:

`PLANNED`

then:

`CREATED`

then:

`PERSISTED`

then:

`STRUCTURALLY_VERIFIED`

then:

`VISUALLY_VERIFIED`

Do not skip directly from PLANNED to VERIFIED.

---

# 21. Blank-file Definition of Done

The blank-file build is complete only when:

### Architecture
The page architecture exists and is correctly ordered.

### Foundations
Tokens/themes/type/spacing/RTL are persisted.

### Components
Required reusable components and variants exist.

### Patterns
Shared patterns are built from components.

### Golden Screens
Reference screens prove the design language.

### Product surfaces
All MVP design surfaces are represented.

### Theme
Every applicable visual node has Light + Night.

### Responsive
Mobile/Web behavior is explicitly represented.

### RTL
Persian and mixed-direction stress has evidence.

### Accessibility
Applicable accessibility evidence exists.

### Prototype
Critical walking skeletons and failure branches exist.

### Traceability
Every canonical screen maps back to capability/domain/API/permission.

### Artifact integrity
Every canonical Penpot artifact has a stable binding.

### QA
No PASS claim exists without current evidence.

### Release
A Design Release Snapshot is created.

---

# 22. Greenfield anti-patterns

The following are hard anti-patterns:

### AP-01 — Screen-first build
Building all screens before establishing the design system.

### AP-02 — Light-first then fake Night
Duplicating Light and recoloring manually.

### AP-03 — Screenshot design
Creating visually convincing static frames that do not use reusable components.

### AP-04 — Component explosion
Creating a new component for every state instead of controlled variants.

### AP-05 — Legacy copying
Copying historical Penpot structures merely because they already exist.

### AP-06 — Page-local tokens
Inventing local colors/spacing that bypass the global token system.

### AP-07 — Unbounded agent prompt
Giving the agent the entire repository with no bounded source packet.

### AP-08 — Tool-success closure
Treating a successful mutation response as persistence proof.

### AP-09 — Architecture by screenshot
Letting an old screenshot define current product semantics.

### AP-10 — Hidden exceptions
Introducing screen-specific behavior without registering an exception.

---

# 23. Recommended execution sequence

The ideal sequence is:

```
WAVE-00
Empty File Preflight
        ↓
WAVE-01
Foundations + Light/Night + RTL
        ↓
WAVE-02
Golden Components + Variants
        ↓
WAVE-03
Shared Patterns + State Library
        ↓
WAVE-04
Golden Screens
        ↓
WAVE-05
Retailer
        ↓
WAVE-06
Vendor
        ↓
WAVE-07
Operations
        ↓
WAVE-08
Field Activator + Corporate
        ↓
WAVE-09
End-to-End Prototypes
        ↓
WAVE-10
Design QA + Evidence + Release Snapshot
```

No product screen wave should silently create missing global foundations.

When a global dependency is discovered to be missing, return to the dependency wave, fix it centrally, re-verify affected nodes, then continue.

---

# 24. Blank-file success criterion

The new Penpot file should emerge as:

**one coherent design system that happens to contain many product surfaces**

not:

**many product screens that happen to share some colors.**

That distinction is the primary optimization for a completely empty file.

---

# 25. Research basis for greenfield construction

Penpot's current documentation defines tokens, token sets and themes as reusable design-system infrastructure and describes components/variants as the reusable source-of-truth mechanism for UI construction. citeturn491925search0turn491925search1turn491925search2

Penpot's AI Kit architecture also separates instructions, skills, workflows, MCP, policies and evals, reinforcing the need for a staged execution model rather than a single giant prompt. citeturn491925search5

Therefore this profile deliberately puts:

**Foundations → Components → Patterns → Golden Screens → Product Screens → Prototype → QA**

ahead of broad screen generation.

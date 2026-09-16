# POL Research → Principle Matrix v1

## Purpose
This file is the mandatory bridge from external design research to POL decisions. No visual decision should bypass this layer when a relevant principle exists.

## 1. Core heuristics
| Research principle | POL interpretation | Design consequence | QA question |
|---|---|---|---|
| Visibility of system status | Retailer/vendor must know what the system is doing | persistent order, sync, allocation and submission states | Can the user tell what happened and what happens next? |
| Match to real world | Persian B2B vocabulary and wholesale mental models | use مغازه، بنکدار، سفارش، بسته، حداقل خرید; avoid internal domain jargon | Would a real operator understand without training? |
| User control/freedom | reversible edits before commitment | edit basket, allocation review, cancel where permitted | Can a mistaken action be recovered? |
| Consistency and standards | same semantic meaning everywhere | shared status, buttons, forms and navigation | Does the same label mean one thing everywhere? |
| Error prevention | prevent invalid commercial actions before submission | MOQ/pack/availability checks at decision time | Is the failure prevented or explained before commitment? |
| Recognition over recall | show product, pack, price, MOQ and state together | compact product rows and visible context | Must user remember something from another screen? |
| Flexibility | routine users need fast paths | reorder, saved lists, keyboard shortcuts in ops | Is the common path fast without making novice path opaque? |
| Minimalist design | reduce irrelevant information, not necessary information | one primary job per screen | Does every visible element help the next decision? |
| Error recovery | errors must be actionable | preserve entered values; inline recovery | Does the user know exactly how to recover? |
| Help/context | assistance at point of need | contextual hints, support and deep links | Is help available without abandoning the task? |

## 2. Accessibility principles
- WCAG 2.2 AA is the baseline, not an optional polish layer.
- Focus must remain visible and sufficiently contrasting.
- Status cannot rely on color alone; combine color with label/icon/pattern.
- Keyboard order follows visual/task order.
- Touch targets should normally exceed the minimum where the target demographic benefits.
- Persian text must survive long labels, larger text settings and mixed-direction strings.

## 3. Form and error principles
- Validate primarily at meaningful task boundaries; do not create noisy inline validation while the user is still typing unless research justifies it.
- Preserve entered values after validation errors.
- Show a page-level summary plus local field errors for forms with multiple validation failures.
- Error copy states: what happened + what to do.
- Never expose internal error codes as the primary user message.

## 4. Operational-table principles
- Sortable headers expose sorting through keyboard as well as pointer interaction.
- Interactive cell controls remain in normal keyboard order.
- State and exception information stays visible in dense rows.
- Tables become task-oriented lists on narrow mobile widths rather than shrunken desktop tables.

## 5. POL-specific decision rules
1. Product recognition outranks decorative imagery.
2. Commercial constraints appear before commitment.
3. Allocation is explained, not algorithmically over-exposed.
4. Direct settlement must never visually resemble a POL wallet.
5. Ops is a queue system first and a dashboard second.
6. Field is task-first and resilient to weak networks.
7. Corporate pages prove value without unsupported guarantees.

## Sources
- Nielsen Norman Group, 10 Usability Heuristics: https://www.nngroup.com/articles/ten-usability-heuristics/
- W3C WCAG 2.2: https://www.w3.org/TR/WCAG22/
- GOV.UK Design System, Error message and Validation patterns
- IBM Carbon Design System, Data table accessibility

# POL Design System Compatibility — CP8

**Question:** can Cartona-derived patterns integrate into POL's existing design system without breaking its coherence?

## POL's actual design system (verified this run)

| Layer | Location | Content |
|---|---|---|
| Canonical tokens | `mvp/packages/tokens/src/index.ts` (authority: doc 56 POL-DESIGN-VISUAL-001 v2.0.0) + `.pol-design/tokens/tokens.json` | semantic colors (`bg.canvas`, `surface.default`, `brand.primary`, `semantic.success/warning/danger`, `focus.ring`), typeScale, font **Vazirmatn** |
| Mobile runtime theme | `mvp/apps/mobile/src/theme.ts` (read in full) | light/night `Palette` (brand `#2563EB` light / `#60A5FA` night), `spacing {xs:4…xxl:32}`, card radius 16, button min-height 48 |
| Mobile primitives | `mvp/apps/mobile/src/components/ui.tsx` (read in full) | `Screen, Title, Card, Btn, Input, StatusChip, ErrorBox, Empty, IconBadge` — RTL-native (`direction: "rtl"` at screen root), text alignment right, LTR escapes for OTP/numeric |
| Web library | `mvp/packages/ui/src/` (Button, Field, QtyStepper, Skeleton, EmptyState, ErrorState…) | richer set; mobile does not import it today |
| Governance | `.pol-design/` (DESIGN.md, visual-rules, component contracts, VISUAL_QA) + `visual-qa/MASTER_MOBILE_VISUAL_INVENTORY.md` (60 items) | existing QA process to absorb new changes |

## Compatibility verdict per Cartona-derived pattern family

| Pattern family | Compatible with POL DS? | Integration path |
|---|---|---|
| Empty/error states with illustrations | **Yes — high** | extend existing `Empty`/`ErrorBox` primitives with optional slots; tokens unchanged |
| Image error placeholder | **Yes — high** | new primitive in `ui.tsx` using `Palette.danger/dangerBg` |
| Reorder affordance | **Yes** | existing `Btn` + existing pipeline |
| Category illustration tiles | **Yes** | presentation swap inside existing tile component |
| Supplier signal chips | **Yes** | reuse `StatusChip` (already tone-parameterized) |
| Home section hierarchy | **Yes** | existing Card/Title composition |
| Dark mode | **Yes — required** | any new component must use `useThemedStyles` (both palettes), never hardcoded hex; Cartona asset-derived colors (`#455a73` etc.) must NOT be adopted as POL tokens |
| RTL/Persian | **Yes — already native** | POL's RTL approach is sound; Cartona's Arabic strings are not transferable |

## Rules for a future implementation phase

1. New colors come only from POL token authority — Cartona's palette informs *pattern shape*, never hex values (mission §41).
2. Typography stays Vazirmatn; do not adopt SomarSans/Cairo/Rubik.
3. All new components get light+night styles via `useThemedStyles` and appear in `visual-qa/MASTER_MOBILE_VISUAL_INVENTORY.md` (60-item matrix) with light/night entries.
4. Illustrations/icons are POL-original; Cartona assets (license `cartona-proprietary-unknown`) are never copied.
5. Anything classified `INTERACTION_PRESENTATION` in the mapping CSV must ship with the regression guards named in `pol-ux-recommendations.md`.

## Conclusion

POL's design system is mature enough to absorb every VISUAL_ONLY recommendation without structural change: the primitive set is small but extensible, tokens are semantic, RTL is native, and a visual-QA governance process exists. The main integration risk is not visual but the INTERACTION_PRESENTATION items (reorder, search entry), which carry explicit regression guards and product gates.

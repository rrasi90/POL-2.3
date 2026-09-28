# POL Landing Page Design Specification — 2026-09-28

**Surface:** Corporate/Public `/`  
**Design mode:** Editorial Commerce / Precision Commerce  
**Status:** Active implementation on `deploy/vps-self-hosted-20260928`

## Intent

The landing page must explain POL in the first viewport, distinguish POL as the master brand from POL Market and POL Vendor, and move visitors toward a role-appropriate entry point without exposing internal implementation jargon.

## Information hierarchy

1. Brand + pilot context
2. Plain-language value proposition
3. Primary entry CTA
4. Visual explanation of the connected B2B order flow
5. Proof rail: basket / order flow / traceability
6. Four-step narrative: discovery → basket → order → transparency
7. Three role perspectives: retailer / vendor / operations
8. Operational differentiation
9. Ahvaz pilot CTA
10. Corporate footer

## Visual language

- Base: the repository Precision Commerce Light/Night semantic tokens.
- Tone: premium B2B commerce, not consumer marketplace and not developer dashboard.
- Surfaces: restrained borders, medium corner radii, controlled elevation.
- Accent: existing POL blue/indigo brand tokens only.
- Typography: Vazirmatn with large Persian display hierarchy and short line lengths on mobile.
- Real brand assets:
  - Corporate: `logo/pol company logo.png`
  - Retailer: `logo/لوگو پل برای مغازه داران.png`
  - Vendor: `logo/لوگو پل برای بنکدار.png`

## Motion system

Motion is explanatory rather than ornamental:
- hero flow lines pulse slowly to suggest the movement of an order;
- central POL mark breathes subtly;
- nodes/cards float with small amplitude;
- content enters with short upward reveals;
- all non-essential motion is disabled under `prefers-reduced-motion`.

## Mobile rules

- Navigation collapses to brand + primary CTA + an accessible compact menu.
- Hero becomes single-column before the visual storytelling panel.
- Display heading uses fluid sizing and controlled line length.
- All CTA controls remain full-width and touch friendly.
- Hero visualization reduces density without removing the conceptual order-flow relationship.
- Role cards stack vertically and retain their dedicated product logo.

## Asset delivery

The canonical repository logos are served same-origin from `/brand/{asset}` by `mvp/apps/web/src/app/brand/[asset]/route.ts`. The web image is packaged into the VPS runtime image by `deploy/Dockerfile.web`.

## Explicit non-goals

- No domain/API/database changes.
- No external image-host dependency for the canonical logo assets.
- No synthetic business metrics presented as proof.
- No internal gap IDs, migration IDs, or unnecessary engineering terminology in the primary marketing narrative.

## Verification gate

Fresh `npm run typecheck`, `npm run lint`, `npm run build`, route smoke, and desktop/mobile visual capture are required before promoting the new landing surface to a `VERIFIED` visual state.

## 2026-09-29 usability refinement

This implementation pass makes the public landing explicitly Persian-first. In-page navigation uses native anchor targets for deterministic browser behavior; route transitions remain Next.js `Link` navigations. The public brand asset route is included in the middleware allowlist. Typography uses the existing canonical Vazirmatn stack but reduces aggressive negative tracking on Persian headlines and increases readable line-height/body sizing.

The page intentionally uses plain user-facing terms such as «فروشگاه»، «بنکدار»، «سبد خرید» و «پیگیری» instead of exposing internal orchestration vocabulary in the marketing surface.

# Tech Stack Recommendation

## Frontend
- **Next.js (React)** — SSR/SSG helps SEO for free-tool pages (Manglik checker, free kundali) which is a real organic traffic channel for this category.
- Tailwind CSS — fast to build a clean, mobile-first UI; pair with `frontend-design` best practices for a polished, non-templated look rather than default Tailwind aesthetics.
- `i18next` or Next.js built-in i18n routing for Marathi/English toggle.

## Backend
- **Python + FastAPI** recommended over Node, specifically because the astrology engine needs `pyswisseph` (the most mature, widely-used Swiss Ephemeris binding is Python-first). Keeping engine + API in the same language avoids a cross-language service hop for the most latency-sensitive part of the product.
- Alternative: Node.js backend + a small Python microservice just for the engine (`/engine/*` endpoints from API design doc), if the team is more Node-native. Either is fine — the key architectural point (isolated, stateless engine service) matters more than the language.

## Astrology Core
- `pyswisseph` (Python binding for Swiss Ephemeris) — planetary positions, ayanamsa, houses.
- Swiss Ephemeris data files (`.se1`) — download and bundle the relevant ephemeris files (covers a wide date range; confirm coverage includes the decades your users' parents/grandparents were born in).
- `timezonefinder` + `pytz`/`zoneinfo` — resolve IANA timezone from lat/long, then correct historical offset for the exact date.
- Custom modules (build in-house, not a library): Koota comparison, Dasha calculation, Mangal Dosha rules, verdict templating — these encode the classical rule tables from the engine spec.

## Database & Storage
- PostgreSQL (Supabase or Neon are good managed options if avoiding self-hosting) — `jsonb` fields suit the chart data structure well.
- Redis — session state, rate limiting, payment-lock during checkout.
- S3-compatible storage (Cloudflare R2 recommended for cost — no egress fees) — PDFs, chart images, uploaded biodata photos.

## PDF/Image Generation
- Server-side HTML → PDF via **Playwright** (headless Chromium) rendering a styled HTML template — gives the most design control for both the astrology report and biodata templates, and lets you reuse the same React/HTML components for on-screen preview and PDF export.
- Chart rendering (North/South Indian kundali diagrams): render as SVG programmatically (a fixed-geometry template you place planet glyphs into) — precise and crisp compared to image-based approaches.

## Payment
- Razorpay SDK (server-side order creation + webhook verification) — see `07-PAYMENT-INTEGRATION.md`.

## Hosting
- Frontend: Vercel (native Next.js support, generous free tier to start).
- Backend: Railway, Render, or Fly.io — need a persistent server (not pure serverless) since Swiss Ephemeris data files + native bindings don't suit cold-start serverless well.
- Consider co-locating backend in a region close to India (Mumbai/Singapore) for latency.

## Observability (add once past prototype stage)
- Basic error tracking (Sentry) — especially important for the engine service, since a silent calculation bug is worse than a crash.
- Structured logging on payment webhook events (see payment doc).

## Testing
- Unit tests for every koota calculation function individually (pure functions, easy to test).
- The reference-tool validation test suite from the engine spec (`03-ASTROLOGY-ENGINE-SPEC.md §4`) should be wired into CI as a regression gate — no merge to main should be able to silently change engine output without a human reviewing the diff.

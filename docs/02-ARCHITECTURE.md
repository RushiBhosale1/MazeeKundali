# System Architecture

## High-Level Diagram (described)

```
[Browser - React/Next.js]
        |
        | HTTPS
        v
[API Gateway / Backend - Node.js or Python]
   |            |                |
   v            v                v
[Astrology   [Payment       [PDF/Image
 Engine       Gateway         Generation
 Service]     Webhook]        Service]
   |
   v
[Swiss Ephemeris (native lib via bindings)]
   |
   v
[Geocoding + Historical Timezone Service]

[PostgreSQL] <- stores kundali data, orders, biodata drafts
[Object Storage (S3-compatible)] <- generated PDFs, chart images, photos
[Redis] <- session cache, rate limiting, payment-lock during checkout
```

## Why a separate "Astrology Engine Service"
Isolate the calculation logic (ephemeris → chart → koota tables → verdict) behind a clean internal API
(`POST /engine/kundali`, `POST /engine/match`) so that:
- It can be unit-tested independently against reference test vectors (critical for accuracy — see engine spec).
- It can be rewritten/optimized later without touching payment or UI code.
- It can be reused by both the Kundali feature and the Matching feature (matching calls kundali generation twice internally, then runs koota comparison).

## Recommended Stack (details in `08-TECH-STACK.md`)
- Frontend: Next.js (React) — SSR helps SEO for the free-tool traffic-driver pages
- Backend: Node.js (NestJS or Express) or Python (FastAPI) — Python is a good fit if using `pyswisseph`
- Astrology core: Swiss Ephemeris via `pyswisseph` (Python) or a Node wrapper
- Database: PostgreSQL
- File storage: S3-compatible (AWS S3, Cloudflare R2, or Backblaze B2 — R2/B2 cheaper for a bootstrapped India-focused app)
- Payment: Razorpay (best India-first UX, UPI support) — see `07-PAYMENT-INTEGRATION.md`
- PDF generation: server-side headless rendering (Puppeteer/Playwright on an HTML template, or WeasyPrint if Python)
- Hosting: Vercel (frontend) + Railway/Render/Fly.io or a small VPS (backend, since ephemeris calc needs a persistent server, not pure serverless due to native lib cold-start cost)

## Request Flow — Kundali Generation
1. User submits DOB/time/place on frontend.
2. Frontend calls Geocoding service (internal, cached) to resolve place → lat/long + IANA timezone.
3. Backend resolves **historical UTC offset** for that place/date (see engine spec — critical for pre-1947 India).
4. Backend calls Astrology Engine Service with (UTC datetime, lat, long, ayanamsa=Lahiri).
5. Engine returns: planetary positions, Rashi, Nakshatra, Lagna, houses, dasha.
6. Backend stores result in DB (draft, unpaid), returns **free-tier subset** to frontend.
7. If user pays → webhook confirms → backend flags record as paid → full data + PDF unlocked.

## Request Flow — Matching
1. User selects/enters two kundalis (generate on the fly if not already stored).
2. Backend runs both through Astrology Engine Service if not cached.
3. Backend runs Koota Comparison module (pure function, no ephemeris needed — just Rashi/Nakshatra lookup tables) — see engine spec §Ashtakoot Algorithm.
4. Free-tier: total score + Manglik yes/no. Paid: full breakdown + verdict text + PDF.

## Security Notes
- Birth data + generated charts are sensitive personal data (linked to real names, DOB, family matching intent) — treat as PII, encrypt at rest, restrict access, define a data retention/deletion policy and state it in a privacy policy.
- Payment must gate access server-side (check `paid=true` in DB on every fetch of premium fields), never trust a frontend "unlocked" flag alone.
- Rate-limit the free tier per IP/session to prevent scraping the engine as a free API.

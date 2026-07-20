# API Design

## Conventions
- REST, JSON, versioned under `/api/v1/`.
- All premium fields gated server-side by checking `paid=true` on the related record — never trust client state.
- Rate limit public endpoints (geocode, free kundali generation) per IP to prevent scraping/abuse.

## Geocoding
`GET /api/v1/geocode?query=Kolhapur`
→ returns list of candidate places with lat/long + IANA timezone, cached in `geocode_cache`.

## Kundali
`POST /api/v1/kundalis`
Body: `{ name, gender, dob, time_of_birth, time_accuracy, place_query }`
→ resolves place, calls internal Astrology Engine, stores `birth_profile` + `kundali` (paid=false), returns **free-tier fields only**.

`GET /api/v1/kundalis/:id`
→ returns free-tier fields always; premium fields (`planet_positions` full detail, `dasha_timeline`, `written_analysis`, `navamsa chart`) only if `paid=true`, else returns a `locked: true` flag per field group so frontend can render blur/lock UI.

`POST /api/v1/kundalis/:id/pdf`
→ (post-payment only) triggers PDF generation job, returns `pdf_url` when ready (poll or webhook-to-frontend via SSE/websocket for "generating..." state).

## Matching
`POST /api/v1/matches`
Body: `{ bride_kundali_id | bride_birth_details, groom_kundali_id | groom_birth_details }`
→ generates missing kundalis if raw details given, runs Koota Comparison module, stores `match` (paid=false), returns free-tier fields (total score, manglik yes/no).

`GET /api/v1/matches/:id`
→ same locked/unlocked field pattern as kundali.

`POST /api/v1/matches/:id/pdf`
→ post-payment PDF generation.

## Biodata
`POST /api/v1/biodatas` → create draft
`PATCH /api/v1/biodatas/:id` → update fields (multi-step form saves incrementally)
`POST /api/v1/biodatas/:id/link-kundali` → `{ kundali_id }`, auto-fills `horoscope_info` (only allowed if that kundali is paid, or expose only the free-tier horoscope fields if not)
`POST /api/v1/biodatas/:id/render` → generates PDF/image using chosen template

## Orders / Payment
`POST /api/v1/orders` → `{ product_type, related_id }` → creates Razorpay order, returns `gateway_order_id` + checkout config for frontend
`POST /api/v1/webhooks/razorpay` → **server-to-server only**, verifies signature, marks `orders.status=paid`, flips `paid=true` on the related kundali/match/biodata record. This webhook is the *only* source of truth for unlocking content — frontend-side "payment success" callbacks are for UX only, never used to unlock data.

## Internal-only (not public) — Astrology Engine Service
`POST /engine/kundali` → `{ utc_datetime, latitude, longitude, ayanamsa, house_system, rahu_mode }` → returns full planetary/chart data (pure calculation, no DB access, easily unit-testable in isolation)
`POST /engine/match` → `{ kundali_a, kundali_b }` → returns koota breakdown + verdict (pure function, no ephemeris call needed since it just compares already-computed Rashi/Nakshatra data)

Keeping the engine as internal-only, stateless, pure-function endpoints is what makes the validation/regression-testing strategy in the engine spec practical — you can run hundreds of test vectors against it directly with no DB or payment dependency in the loop.

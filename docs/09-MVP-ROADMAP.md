# MVP Roadmap

## Phase 0 — Foundations (before any UI)
- Set up Swiss Ephemeris + `pyswisseph`, build the core engine pipeline (Steps 1–6 in engine spec).
- Build the 10–15 reference test-vector suite (birth data + expected output from DrikPanchang/AstroSage) and get the engine passing it. **Do not proceed to Phase 1 until this passes** — it's the foundation everything else sits on.
- Set up Razorpay sandbox/test account, confirm no category-approval blockers for astrology use case.

## Phase 1 — Kundali Generator (free tier only)
- Input form → geocoding → engine call → store → display free-tier result.
- Basic D1 chart rendering (pick one style first, e.g. North Indian, add South Indian toggle later).
- No payment yet — validate that the free result alone is accurate and delightful before adding monetization complexity.

## Phase 2 — Kundali Generator (paid tier + payment)
- Full planet table, Navamsa chart, Manglik detail, Dasha, written analysis (templated).
- Razorpay integration end-to-end (order → checkout → webhook → unlock).
- PDF generation + WhatsApp share.

## Phase 3 — Patrika Matching
- Koota comparison module (pure function, reuses Phase 1's kundali engine output) + its own test-vector validation.
- Free tier (total score + manglik) → paid tier (full breakdown + verdict) → payment integration (reuse Phase 2's payment plumbing).
- PDF + WhatsApp share for matching report.

## Phase 4 — Biodata Builder
- Multi-step form, template gallery, PDF/image export.
- Auto-fill horoscope section from a linked kundali (the key retention loop).

## Phase 5 — Polish & Growth Features
- Standalone free Manglik checker (SEO/traffic driver).
- Bundle pricing (Kundali + Matching).
- Marathi/English full dual-language pass across all screens and PDFs.
- Admin/reconciliation view for payment support.
- Error tracking, structured logging.

## Explicit Non-Goals for MVP (see `01-FEATURES-SCOPE.md` for full list)
- User accounts/login — use resumable session links instead.
- AI-generated free-text predictions — all output must trace to the deterministic engine.
- Astrologer consultation booking, Muhurta tool, DashaKoota — defer until core product validates.

## Suggested Build Order Rationale
Engine accuracy is validated **before** any UI work, because every downstream feature (free kundali, paid kundali, matching, biodata auto-fill) depends on it, and retrofitting accuracy fixes after users have seen wrong charts is a trust problem you don't want to create. Payment is deferred until Phase 2 so Phase 1 can validate the free product's quality in isolation.

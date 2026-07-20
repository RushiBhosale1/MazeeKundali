# 🪔 मराठी कुंडली व बायोडाटा प्लॅटफॉर्म — Phase-Wise Implementation Plan

> **Thinking lens**: Expert product builder, Marathi-family-first UX, zero tolerance for engine inaccuracy, free-to-paid funnel with maximum conversion momentum.

---

## Product Summary

A web platform for Marathi marriage-seeking families to:
1. Generate an accurate Vedic kundali (जन्मकुंडली / पत्रिका)
2. Match two kundalis via Ashtakoot Guna Milan (पत्रिका जुळणी)
3. Auto-generate a shareable Marathi biodata (बायोडाटा)

**Pricing**: Kundali ₹100 | Patrika Matching ₹50 | Bundle ₹130 | Biodata bundled or free standalone

---

## Key Design Principles (Non-Negotiable)

| Principle | What it means in practice |
|---|---|
| **अचूकता (Accuracy first)** | Engine validated against DrikPanchang/AstroSage before any UI work starts |
| **सोपेपण (Simplicity)** | ≤5 fields to get a free result; Marathi default, English toggle |
| **मोबाईल-फर्स्ट** | Large tap targets, single-column, WhatsApp-native outputs |
| **मोफत → पेड फनेल** | Free preview shows real value, paywall feels like "unlock more" not "buy from scratch" |
| **विश्वास (Trust)** | Templated verdicts traceable to classical rules, never free-text AI; dosha cancellations always explained |

---

## Edge Cases Accounted For (UX-level)

| Edge Case | Handling |
|---|---|
| वेळ माहित नाही (Birth time unknown) | Toggle "वेळ अंदाजे आहे / अचूक वेळ माहित नाही" → show disclaimer on Lagna-dependent results |
| छोटे गाव (Small village not found in geocoding) | Allow manual lat/long entry or "जवळचे शहर" fallback with explanatory note |
| Pre-1947 birth dates (grandparents) | IANA tz database resolves historical offset correctly — never hardcode +5:30 |
| Payment fails mid-flow | Keep unpaid draft resumable via a unique link — user doesn't re-enter data |
| Payment webhook delayed | Frontend shows "processing…" state; polls for unlock; doesn't trust client-side callback |
| Duplicate webhook events | Idempotency via payment_id check before any unlock action |
| Planet near sign/nakshatra boundary | Swiss Ephemeris precision handles this; regression test suite covers boundary cases |
| Rahu calculation mode mismatch | Default True Node (exposed as a setting); validated against reference tools |
| User entered wrong DOB | Free regeneration offer (trust-builder, avoids refund requests) |
| WhatsApp share on low-end Android | Image export over PDF for share; compressed image for low bandwidth |
| No UPI app installed | Razorpay checkout shows all options (card, netbanking, wallet) not just UPI |
| Nadi/Bhakoot Dosha cancellation | Always show which cancellation rule applied + why — never silently adjust score |
| Same Rashi/Nakshatra pair (Nadi exception) | Implement the same-Rashi+same-Nakshatra-pada Nadi Dosha exception explicitly |
| User goes back/forward (browser nav) | Multi-step form state preserved; don't lose data on back button |
| Screen reader / accessibility | Semantic HTML, ARIA labels in both Marathi and English |

---

## Architecture Decision Summary

| Layer | Choice | Reason |
|---|---|---|
| Frontend | Next.js + Tailwind CSS | SSR for SEO, i18n routing for mr/en toggle |
| Backend | Python + FastAPI | Best fit for `pyswisseph`; engine + API same language = no cross-language hop |
| Astrology Core | `pyswisseph` + Swiss Ephemeris `.se1` files | Gold standard for Vedic calculation |
| Geocoding | `timezonefinder` + `geopy` + IANA `zoneinfo` | Historical timezone handling |
| Database | PostgreSQL (Supabase or Neon) | JSONB for chart data; managed = no infra overhead |
| Cache | Redis | Session state, rate limiting, payment-lock |
| Storage | Cloudflare R2 | Zero egress fees; PDFs, chart images, photos |
| Payment | Razorpay | UPI-first India checkout; webhook-only unlock |
| PDF | Playwright (headless Chromium) | Same HTML template used for on-screen preview + PDF |
| Chart Rendering | SVG (programmatic) | Crisp, scalable, North/South Indian toggle |
| Frontend Hosting | Vercel | Native Next.js, CDN edge |
| Backend Hosting | Railway / Render / Fly.io (Mumbai/Singapore region) | Persistent server for ephemeris + native libs |

---

---

# 🏗️ PHASE 0 — Foundation & Engine Accuracy Gate
**Duration estimate: 2–3 weeks**
**Hard gate: Nothing proceeds until engine passes validation suite.**

## Goals
- Working astrology engine that matches reference tools
- Dev environment fully set up
- Razorpay KYC started (long lead time)
- No UI work yet

## 0.1 — Project Infrastructure Setup

### Repositories & Monorepo Structure
```
/
├── backend/           # Python + FastAPI
│   ├── engine/        # Pure astrology calculation module
│   ├── api/           # REST endpoints
│   ├── db/            # DB models, migrations
│   └── tests/         # Unit + engine validation tests
├── frontend/          # Next.js
│   ├── components/
│   ├── pages/
│   └── public/
├── docker-compose.yml # Local dev: PostgreSQL + Redis
└── docs/              # Existing documentation
```

### Dev Environment
- [ ] Python 3.11+ virtual environment
- [ ] Install `pyswisseph`, `timezonefinder`, `pytz`, `zoneinfo`, `geopy`, FastAPI, SQLAlchemy, Alembic, psycopg2, redis-py
- [ ] Download Swiss Ephemeris `.se1` data files (cover ~1800–2100 CE range)
- [ ] PostgreSQL + Redis via Docker Compose locally
- [ ] Linting: `ruff`, `mypy`; Testing: `pytest`
- [ ] Next.js project bootstrapped (`npx create-next-app@latest`)

## 0.2 — Astrology Engine Core (Python module: `engine/`)

### Pipeline implementation (strictly follow engine spec `03-ASTROLOGY-ENGINE-SPEC.md`):

#### Step 1: Geocoding + Historical Timezone Resolution
```python
# engine/geocoding.py
def resolve_place(query: str) -> PlaceResult:
    # Try geocode_cache first (PostgreSQL lookup)
    # Fall back to geopy/Nominatim
    # Return: lat, long, tz_iana

def resolve_utc_birth_moment(local_time, tz_iana, dob) -> datetime:
    # Use zoneinfo.ZoneInfo(tz_iana) — handles pre-1947 offsets automatically
    # NEVER hardcode +5:30
```

#### Step 2: Planetary Positions (Tropical)
```python
# engine/ephemeris.py
# Use pyswisseph: swe.calc_ut() for each planet
# Planets: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn
# Rahu: swe.MEAN_NODE (default True Node = swe.TRUE_NODE — expose as setting)
# Ketu: Rahu longitude + 180°
# Ascendant: swe.houses() with house system WHOLE_SIGN ('W')
```

#### Step 3: Sidereal Conversion (Lahiri Ayanamsa)
```python
# swe.set_sid_mode(swe.SIDM_LAHIRI)
# sidereal_long = tropical_long - ayanamsa_value_for_date
```

#### Step 4: Rashi, Nakshatra, Pada, Lagna
```python
# Rashi = int(sidereal_long / 30)   # 0-11 = Aries to Pisces
# Nakshatra = int(sidereal_long / (360/27))   # 0-26
# Pada = int((sidereal_long % (360/27)) / (360/108)) + 1   # 1-4
```

#### Step 5: House Placement — Whole Sign System
```python
# Each house = one sign starting from Lagna sign
# Planet house = (planet_rashi - lagna_rashi) % 12 + 1
```

#### Step 6: Vimshottari Dasha
```python
# Sequence: Ketu(7) → Venus(20) → Sun(6) → Moon(10) → Mars(7)
#           → Rahu(18) → Jupiter(16) → Saturn(19) → Mercury(17)
# Starting from Moon nakshatra position
# Compute: current_mahadasha, current_antardasha, start/end dates
```

### Derived Fields
```python
# engine/derived.py
GANA_MAP = { "Ashwini": "Deva", "Bharani": "Manushya", ... }  # 27 nakshatras
NADI_MAP = { "Ashwini": "Aadi", "Bharani": "Madhya", ... }
VARNA_MAP = { "Cancer": "Brahmin", "Aries": "Kshatriya", ... }
```

## 0.3 — Ashtakoot Guna Milan Engine (engine/matching.py)

Pure lookup/comparison functions — no ephemeris needed:

| Koot | Points | Implementation note |
|---|---|---|
| वर्ण (Varna) | 1 | Rashi → Varna hierarchy table |
| वश्य (Vashya) | 2 | Rashi → group + affinity matrix; validate half-sign splits for Sagittarius/Capricorn |
| तारा (Tara) | 3 | Nakshatra counting formula, mod 9 → mod 3 → inauspicious/auspicious lookup |
| योनी (Yoni) | 4 | 27-nakshatra → 14-animal table; animal friendship matrix |
| ग्रह मैत्री (Graha Maitri) | 5 | Moon sign lord → classical friendship table |
| गण (Gana) | 6 | Nakshatra → Deva/Manushya/Rakshasa |
| भकूट (Bhakoot) | 7 | Rashi distance check: 2/12, 6/8, 5/9 = dosha (0 pts) |
| नाडी (Nadi) | 8 | Nakshatra → Aadi/Madhya/Antya; same = Nadi Dosha |

**Dosha Cancellation rules**: Implement as explicit, cited rule functions. Show which rule applied.

**Mangal Dosha**: Mars in houses 1,2,4,7,8,12 from Lagna (and from Moon, from Venus as variants). Cancellation rules as explicit functions.

**Verdict Logic**: Templated sentences in Marathi + English per score band, with active dosha callouts.

## 0.4 — Validation Test Suite (HARD GATE 🚨)

Build test file: `tests/test_engine_validation.py`

### Test Vector Requirements
- 10–15 birth datasets including:
  - [ ] Pre-1947 birth date (to test historical timezone handling)
  - [ ] Birth near sign boundary (Moon near 29°59' of a sign)
  - [ ] Birth near nakshatra boundary
  - [ ] Both Rahu modes (True vs Mean Node)
  - [ ] Birth place: small Maharashtra town (test geocoding)
  - [ ] Birth time "unknown" path
- Expected outputs verified against DrikPanchang AND AstroSage for each test case
- Diff: Rashi, Nakshatra, Pada, Lagna, all planet positions, dasha, all 8 koota scores
- Any mismatch must be root-caused before Phase 1

```python
@pytest.mark.parametrize("test_vector", REFERENCE_TEST_VECTORS)
def test_engine_matches_reference(test_vector):
    result = engine.compute_kundali(test_vector.input)
    assert result.rashi == test_vector.expected.rashi
    assert result.nakshatra == test_vector.expected.nakshatra
    # ... all fields
```

**DO NOT proceed to Phase 1 until `pytest tests/test_engine_validation.py` passes for all test vectors.**

## 0.5 — Razorpay Account Setup (parallel with engine work)
- [ ] Sign up for Razorpay business account
- [ ] Submit KYC documents (business registration or sole proprietorship)
- [ ] Contact Razorpay support: confirm astrology/kundali services are approved under their MCC
- [ ] Have fallback gateway in mind: PayU or Cashfree
- [ ] Set up Razorpay test/sandbox environment

---

---

# 🌟 PHASE 1 — Kundali Generator (Free Tier)
**Duration estimate: 2–3 weeks**
**Goal: User enters birth details, sees accurate free kundali. No payment yet.**

## 1.1 — Database Setup

```sql
-- Migrations via Alembic
CREATE TABLE geocode_cache (...);
CREATE TABLE birth_profiles (...);
CREATE TABLE kundalis (...);
-- Index: kundalis.paid, birth_profiles.place_text
```

## 1.2 — Backend API (FastAPI)

### Endpoints to build:
```
GET  /api/v1/geocode?query=Kolhapur       → place candidates list
POST /api/v1/kundalis                     → create + compute (returns free-tier only)
GET  /api/v1/kundalis/:id                → fetch (locked fields flagged if not paid)
POST /engine/kundali                      → internal, pure calc (no DB)
```

### Rate limiting (Phase 1 already):
- `/api/v1/geocode`: 30 req/min per IP
- `/api/v1/kundalis` POST: 5 req/10min per IP (prevents free API scraping)

### Free-tier response shape:
```json
{
  "id": "uuid",
  "rashi": "वृश्चिक (Scorpio)",
  "nakshatra": "अनुराधा (Anuradha)",
  "pada": 2,
  "lagna": "सिंह (Leo)",
  "gana": "देव (Deva)",
  "nadi": "आदी (Aadi)",
  "varna": "ब्राह्मण (Brahmin)",
  "chart_d1_svg": "...",
  "locked": {
    "planet_positions": true,
    "navamsa_chart": true,
    "mangal_dosha": true,
    "dasha": true,
    "written_analysis": true
  }
}
```

## 1.3 — Frontend (Next.js)

### Pages:
- `/` — Landing page
- `/kundali/new` — Input form
- `/kundali/[id]` — Result page (free + paid states)

### Landing Page (/)
**Marathi-first design decisions:**
- Headline: **"तुमची अचूक जन्मपत्रिका मोफत पाहा"**
- Sub: "फक्त ५ माहिती द्या — रास, नक्षत्र, लग्न आणि बरेच काही तात्काळ मिळवा"
- Big CTA: **"कुंडली बनवा →"** (saffron/marigold color, bold)
- Secondary CTAs: "पत्रिका जुळणी" | "बायोडाटा"
- Trust badges: "अचूक गणना" · "२ मिनिटांत" · "मोफत"
- Marathi/English toggle (top-right, persistent via cookie/localStorage)

### Input Form (/kundali/new)
**UX decisions for Marathi families:**
```
नाव (Name): _____________          [text, required]
लिंग (Gender): ○ मुलगा  ○ मुलगी    [radio]
जन्म तारीख (DOB): [DD] / [MM] / [YYYY]   [date picker, native mobile]
जन्म वेळ (Time): [HH] : [MM] [AM/PM]    [time picker]
  └── ☐ वेळ अंदाजे आहे  ☐ वेळ माहित नाही   [toggle]
जन्म ठिकाण (Place): [autocomplete search]
  └── गाव सापडले नाही? → lat/long manual entry link
```

**Validation & UX rules:**
- Date of birth: cannot be future; max 130 years back
- Time: if "unknown" selected → disable time picker → show disclaimer preview
- Place autocomplete: debounced 300ms, show district/state for disambiguation (e.g., "Kolhapur, Maharashtra" vs "Kolhapur, Karnataka")
- "Submit" button disabled until Name + DOB + Place filled; Time optional
- Marathi error messages: "नाव आवश्यक आहे", "जन्म ठिकाण निवडा"

### Loading State
- Animated kundali-drawing visual (SVG animation of chart being drawn, ~3 sec)
- Text: "तुमची कुंडली बनवत आहोत..." → "ग्रहांची स्थिती तपासत आहोत..." → "तयार!"
- **This is not a blank spinner — it builds perceived value**

### Free Result Screen (/kundali/[id])
```
┌─────────────────────────────────┐
│  [Name]'s जन्मकुंडली           │
│  [Share] [WhatsApp]             │
├──────────────┬──────────────────┤
│  D1 Chart    │  Result Cards    │
│  (SVG)       │  रास: वृश्चिक   │
│  North/South │  नक्षत्र: अनुरा │
│  toggle      │  लग्न: सिंह     │
│              │  गण: देव        │
│              │  नाडी: आदी      │
│              │  वर्ण: ब्राह्मण │
├──────────────┴──────────────────┤
│  [BLURRED PREVIEW SECTION]      │
│  🔒 ग्रह तक्ता | नवमांश | दशा  │
│  🔒 मंगळ दोष | लिखित विश्लेषण  │
│                                  │
│  ┌──────────────────────────┐   │
│  │ संपूर्ण अहवाल मिळवा     │   │
│  │  ₹100 · UPI · Instant   │   │
│  │  ✓ ग्रह तक्ता           │   │
│  │  ✓ नवमांश चार्ट         │   │
│  │  ✓ मंगळ दोष विश्लेषण    │   │
│  │  ✓ दशा                  │   │
│  │  ✓ PDF + WhatsApp share  │   │
│  │  [संपूर्ण अहवाल पाहा →] │   │
│  └──────────────────────────┘   │
└─────────────────────────────────┘
```

### Chart Rendering
- SVG-based North Indian kundali diagram (diamond layout, fixed house positions)
- Planet glyphs placed programmatically into correct house cells
- South Indian chart toggle (square grid, fixed sign positions) — Phase 1 stretch, Phase 2 confirmed
- Render SVG on backend, serve as string; can also render client-side with React SVG components

## 1.4 — i18n Setup
- All strings in `public/locales/mr/common.json` and `public/locales/en/common.json`
- Marathi default; English toggle persists across sessions (localStorage)
- Technical terms always show both: "नाडी (Nadi)", "रास (Rashi)"
- Use Noto Sans Devanagari + Inter fonts

## 1.5 — Phase 1 Acceptance Criteria (QA)
- [ ] A Marathi-speaking user with no astrology knowledge can generate their kundali in <2 minutes on mobile
- [ ] Free result matches DrikPanchang for at least 5 spot-checked birth datasets
- [ ] Birth time "unknown" flow shows correct disclaimer
- [ ] Small village geocoding failure handled gracefully
- [ ] Pre-1947 birth date handled correctly (grandparent's chart)
- [ ] Rate limiting works (6th request in 10min rejected with friendly Marathi message)

---

---

# 💳 PHASE 2 — Kundali Generator (Paid Tier + Payment)
**Duration estimate: 2–3 weeks**
**Goal: Full paid unlock, PDF, WhatsApp share, end-to-end payment flow.**

## 2.1 — Paid-Tier Engine Output

### New engine output fields (Phase 2 unlocks):
```json
{
  "planet_positions": [
    { "planet": "चंद्र (Moon)", "sign": "वृश्चिक", "degree": 15.3,
      "house": 4, "nakshatra": "अनुराधा", "pada": 2, "retrograde": false }
    ...
  ],
  "navamsa_chart": { "d9_svg": "..." },
  "mangal_dosha": {
    "status": true,
    "reference_point": "Lagna",
    "mars_house": 7,
    "cancellation_applied": false,
    "rule_notes": "कोणताही नियम लागू नाही",
    "explanation_mr": "मंगळ ७व्या घरात आहे, त्यामुळे मंगळ दोष आहे."
  },
  "dasha_current": {
    "mahadasha": "शनि", "antardasha": "गुरु",
    "start_date": "2023-04-01", "end_date": "2025-08-15"
  },
  "written_analysis": {
    "rashi_analysis_mr": "...",
    "lagna_analysis_mr": "...",
    "mangal_detail_mr": "..."
  }
}
```

### Written analysis templates
- Templated, data-driven paragraphs (not free-text AI generation)
- Template variables: `{rashi_name}`, `{nakshatra_name}`, `{lagna_name}`, `{gana}`, `{dasha_lord}`, etc.
- Maintained as Marathi Jinja2 templates on the backend

## 2.2 — Orders & Payment API

```
POST /api/v1/orders                   → create Razorpay order
POST /api/v1/webhooks/razorpay        → server-to-server webhook (ONLY source of truth)
GET  /api/v1/orders/:id/status        → frontend polls this for unlock confirmation
```

### Payment flow (critical details):
1. User clicks "संपूर्ण अहवाल पाहा" → POST /api/v1/orders → backend creates Razorpay order server-side
2. Frontend opens Razorpay Checkout (UPI first in UI)
3. Razorpay payment success → frontend calls `GET /orders/:id/status` to poll
4. Razorpay webhook (server-to-server) → backend verifies HMAC signature → marks order paid → flips `kundali.paid = true`
5. Poll returns `{ paid: true }` → frontend refreshes full data
6. **Idempotency**: if webhook fires twice, check payment_id already processed before acting

### Payment UX copy:
- Pre-payment: "हा अहवाल मार्गदर्शनासाठी आहे. वैयक्तिक सल्ल्यासाठी तज्ञ ज्योतिषांचा सल्ला घ्या."
- Post-payment: "धन्यवाद! तुमचा संपूर्ण अहवाल तयार आहे. 🙏"
- Failure: "पेमेंट झाले नाही. तुमचा अहवाल जपला आहे — [इथे पुन्हा प्रयत्न करा]" (resumable link)

### Resumable draft links
- On kundali creation → generate unique token → store in DB
- Email/SMS this link after payment failure (if user provided contact)
- Link: `/kundali/resume/[token]` → restores input state, user retries payment

## 2.3 — PDF Generation (Playwright)

### PDF template components:
- **Cover page**: Name, DOB, place, kundali header in Marathi
- **D1 Chart** (North Indian SVG embedded)
- **Planet placement table**: sign, house, degree, retrograde, nakshatra
- **D9 Navamsa chart** (SVG embedded)
- **Mangal Dosha section**: status + explanation + cancellation note
- **Dasha section**: current Mahadasha/Antardasha + brief description
- **Written analysis**: templated paragraphs
- **Footer**: disclaimer + "हे अहवाल [ProductName] द्वारे बनवले गेले"

### PDF generation flow:
1. `POST /api/v1/kundalis/:id/pdf` (post-payment)
2. Backend renders HTML template with Playwright → PDF bytes
3. Upload PDF to Cloudflare R2 → store `pdf_url` in DB
4. Return `pdf_url` to frontend
5. **WhatsApp share**: generate a summary image (1200x630 px) + short text → share link

## 2.4 — Unlocked Result Screen

```
┌─────────────────────────────────────┐
│  🎉 [Name]'s संपूर्ण कुंडली       │
│  [PDF डाउनलोड] [WhatsApp वर पाठवा] │
├─────────────────────────────────────┤
│  D1 + D9 Charts (toggle)            │
│  North/South Indian style toggle    │
├─────────────────────────────────────┤
│  ग्रह तक्ता (Planet Table)          │
│  [table: planet, sign, house, deg…] │
├─────────────────────────────────────┤
│  मंगळ दोष: ✅ आहे / ❌ नाही        │
│  [explanation + cancellation rule]  │
├─────────────────────────────────────┤
│  सध्याची दशा                        │
│  महादशा: शनि (2023–2042)            │
│  अंतर्दशा: गुरु (2025 Aug)          │
├─────────────────────────────────────┤
│  विश्लेषण                            │
│  [templated analysis paragraphs]    │
├─────────────────────────────────────┤
│  ╔══════════════════════════════╗   │
│  ║ 📋 बायोडाटा बनवा            ║   │
│  ║ तुमची माहिती आधीच भरलेली!   ║   │
│  ║ [बायोडाटा सुरू करा →]       ║   │
│  ╚══════════════════════════════╝   │
└─────────────────────────────────────┘
```

## 2.5 — Phase 2 Acceptance Criteria
- [ ] Payment completes and unlocks content within same session (no manual intervention)
- [ ] Webhook-based unlock works even if browser tab is closed and reopened
- [ ] PDF downloads correctly on mobile and desktop
- [ ] WhatsApp share generates readable image + text
- [ ] Resumable draft link works after payment failure
- [ ] Mangal Dosha cancellation rules display transparently
- [ ] Webhook idempotency tested (duplicate webhook does not double-process)

---

---

# ⚖️ PHASE 3 — पत्रिका जुळणी (Patrika Matching)
**Duration estimate: 2–3 weeks**
**Goal: Ashtakoot Guna Milan with full Marathi verdict, reusing Phase 1–2 infrastructure.**

## 3.1 — Matching Engine API

```
POST /api/v1/matches     → { bride_kundali_id | bride_birth_details,
                              groom_kundali_id | groom_birth_details }
GET  /api/v1/matches/:id → locked/unlocked field pattern
POST /api/v1/matches/:id/pdf → post-payment PDF
```

### Internal engine:
```
POST /engine/match → { kundali_a, kundali_b } → koota_breakdown + verdict
```

## 3.2 — Input Screen UX

```
┌──────────────────┬──────────────────┐
│   मुलगी (Bride) │   मुलगा (Groom) │
│                  │                  │
│ नाव: ________   │ नाव: ________   │
│ जन्म तारीख:___  │ जन्म तारीख:___  │
│ जन्म वेळ: ___   │ जन्म वेळ: ___   │
│ जन्म ठिकाण: __  │ जन्म ठिकाण: __  │
│                  │                  │
│ [आधीची कुंडली   │ [आधीची कुंडली   │
│  वापरा ↗]       │  वापरा ↗]       │
└──────────────────┴──────────────────┘
           [जुळणी तपासा →]
```

- Mobile: stacked vertically, Bride first then Groom
- "आधीची कुंडली वापरा": enter the kundali token/link to pre-fill

## 3.3 — Free Result Screen

```
┌─────────────────────────────────┐
│         पत्रिका जुळणी           │
│    [Bride Name] ↔ [Groom Name]  │
│                                  │
│         २४ / ३६ गुण             │
│    [big score display]           │
│                                  │
│  मंगळ दोष:                       │
│  मुलगी: नाही ✅                  │
│  मुलगा: आहे ⚠️                   │
│                                  │
│  [LOCKED] 8-कूट तपशील           │
│  [LOCKED] दोष विश्लेषण           │
│  [LOCKED] संपूर्ण निकाल          │
│                                  │
│  [संपूर्ण जुळणी अहवाल — ₹50]   │
└─────────────────────────────────┘
```

## 3.4 — Paid Result Screen

```
┌─────────────────────────────────────┐
│  📋 संपूर्ण जुळणी निकाल            │
│  [PDF] [WhatsApp]                   │
├─────────────────────────────────────┤
│  VERDICT (bold, top):               │
│  "साधारण जुळणी — गुण ठीक आहेत     │
│   पण नाडी दोष तपासा"              │
├─────────────────────────────────────┤
│  ८-कूट तक्ता                        │
│  ┌────────────┬───┬───┬──────────┐  │
│  │ वर्ण      │ 1 │ 1 │ ████████│  │
│  │ वश्य      │ 2 │ 1 │ ████    │  │
│  │ तारा      │ 3 │ 3 │ ████████│  │
│  │ योनी      │ 4 │ 2 │ ████    │  │
│  │ ग्रह मैत्री│ 5 │ 4 │ ████████│  │
│  │ गण        │ 6 │ 6 │ ████████│  │
│  │ भकूट      │ 7 │ 0 │         │  │
│  │ नाडी      │ 8 │ 0 │         │  │
│  └────────────┴───┴───┴──────────┘  │
│  एकूण: २४/३६                        │
├─────────────────────────────────────┤
│  दोष विश्लेषण                        │
│  ⚠️ नाडी दोष: आहे                   │
│     (दोन्हींची नाडी आदी आहे)         │
│     रद्द: नाही (कोणताही नियम नाही) │
│  ✅ भकूट दोष: नाही                  │
│  ✅ मंगळ दोष: मुलगी — नाही          │
│              मुलगा — आहे (पण…)     │
└─────────────────────────────────────┘
```

- Visual bar per koota (not just numbers) — easier to scan on mobile
- Dosha cancellation note always visible even if no cancellation applied
- Verdict sentence always at the top (what Marathi families ask first)

## 3.5 — Verdict Templates (Marathi)

```
Score 33–36: "उत्तम जुळणी — हे जोडपे एकमेकांसाठी अतिशय अनुकूल आहे."
Score 25–32: "चांगली जुळणी — [active_doshas_string] असल्यास तज्ञांचा सल्ला घ्या."
Score 18–24: "साधारण जुळणी — गुण ठीक आहेत पण [active_doshas_string] तपासा."
Score  0–17: "अल्प जुळणी — या जोडप्यासाठी तज्ञ ज्योतिषांचे मार्गदर्शन घ्या."
```

Dosha callouts woven into the template string, not appended after.

## 3.6 — Phase 3 Acceptance Criteria
- [ ] All 8 koota scores match reference tool for 5+ test matching pairs
- [ ] Nadi Dosha + Bhakoot Dosha cancellation rules display transparently
- [ ] Verdict sentence in Marathi matches expected band for each test pair
- [ ] Pre-filling from existing kundali token works (bride or groom side)
- [ ] Bundle pricing option displayed (Kundali + Matching at ₹130)

---

---

# 📋 PHASE 4 — बायोडाटा बिल्डर (Biodata Builder)
**Duration estimate: 2 weeks**
**Goal: Multi-step Marathi biodata with horoscope auto-fill from kundali.**

## 4.1 — Multi-Step Form

### Steps (progress bar shown):
```
Step 1: वैयक्तिक माहिती (Personal Info)
  - पूर्ण नाव, जन्म तारीख, उंची, रक्तगट
  - फोटो अपलोड (R2 storage, 5MB limit, JPEG/PNG)
  - मूळ जिल्हा

Step 2: कुटुंब माहिती (Family Info)
  - वडिलांचे नाव, व्यवसाय
  - आईचे नाव, माहेरचे आडनाव
  - भाऊ/बहीण
  - कुलदैवत (optional text)
  - गोत्र (optional text)

Step 3: शिक्षण व करिअर (Education & Career)
  - शिक्षण, महाविद्यालय, वर्ष
  - व्यवसाय / नोकरी, संस्था
  - वार्षिक उत्पन्न (optional)

Step 4: कुंडली माहिती (Horoscope)
  - [Auto-fill from linked kundali: रास, नक्षत्र, गण, नाडी, मंगळ दोष]
  - Manual override if no kundali linked
  - "कुंडलीशी जोडा" button → enter kundali token to auto-fill

Step 5: अपेक्षा (Expectations / Preferences)
  - Free text (Marathi)
  - Community-specific fields (optional): आमराई, प्रांत
```

**UX decisions:**
- Each step saves to DB incrementally (PATCH /api/v1/biodatas/:id)
- Back/forward navigation preserves state
- Progress bar shows "Step 2 of 5"
- "नंतर पूर्ण करा" (Save for later) → generates resumable link

## 4.2 — Template Gallery

- 3 visual templates at launch:
  1. **पारंपरिक (Traditional)** — saffron/gold tones, decorative border
  2. **आधुनिक (Modern)** — clean, minimalist, professional
  3. **धार्मिक (Religious)** — temple motif, auspicious patterns
- Live preview updates as user fills fields (react-to-PDF or iframe preview)
- Template picker: visual cards with thumbnail; single click to switch

## 4.3 — Auto-Fill Logic

```
POST /api/v1/biodatas/:id/link-kundali
  { kundali_id: "uuid" }
  → if kundali.paid == true: auto-fill full horoscope_info
  → if kundali.paid == false: auto-fill only free-tier fields (Rashi, Nakshatra, Gana, Nadi)
  → return updated horoscope_info
```

This is the key retention loop: kundali → upsell → biodata.

## 4.4 — Export
- PDF (A4 + letter size)
- Image (WhatsApp-friendly 1080x1920px)
- WhatsApp share button: image + "हे माझे बायोडाटा पाहा: [link]"

## 4.5 — Phase 4 Acceptance Criteria
- [ ] All 5 steps complete on mobile without data loss on back navigation
- [ ] Horoscope auto-fill from linked kundali works correctly
- [ ] All 3 templates render correctly in PDF
- [ ] Photo upload works (5MB limit enforced, compressed to R2)
- [ ] WhatsApp share button generates correct image

---

---

# ✨ PHASE 5 — Polish, Growth & Operations
**Duration estimate: 2–3 weeks**
**Goal: SEO traffic drivers, admin tools, observability, full dual-language pass.**

## 5.1 — Free Traffic Drivers (SEO)

### Standalone Manglik Checker (free, no payment)
- URL: `/manglik-checker`
- Minimal input: Name, DOB, Time, Place
- Output: Manglik yes/no + which house, which cancellation rules checked
- Designed to rank for "मंगळ दोष तपासा", "am I manglik", etc.
- CTA at bottom: "संपूर्ण कुंडली बनवा →" (funnels into paid kundali)

### SEO pages (SSG via Next.js):
- `/` — main landing page
- `/kundali-calculator` — for English search terms
- `/janmkundali` — Marathi search term page
- `/patrika-julanee` — matching search page
- Metadata, OpenGraph tags, structured data (JSON-LD) on each page

## 5.2 — Bundle Pricing

```
┌──────────────────────────────────┐
│  💎 कुंडली + जुळणी बंडल        │
│  ₹130 (वेगळ्याने ₹150)          │
│  बचत: ₹20                        │
│  [बंडल घ्या →]                  │
└──────────────────────────────────┘
```

- `product_type: bundle` in orders table
- Backend unlocks both kundali + one match record on payment

## 5.3 — Full Marathi Language Pass

- Audit every screen, error message, PDF, email for Marathi completeness
- Marathi numerals option (१२३ vs 123) — toggle in settings
- Ensure Devanagari font renders correctly on all PDF templates

## 5.4 — Admin/Reconciliation View

A simple authenticated internal page (not public):
```
/admin/orders?search=[order_id|payment_id|name]
→ Shows: order status, paid_at, which record unlocked, Razorpay payment_id
→ "Force unlock" button for manual resolution of edge cases
→ Webhook event log viewer (last 90 days)
```

Auth: HTTP Basic Auth or a simple secret token header (not a full auth system for MVP admin).

## 5.5 — Observability

- **Sentry** on frontend + backend (especially engine service — silent calculation bugs are worse than crashes)
- **Structured logging** on all webhook events (raw payload + processing result)
- **Uptime monitoring**: UptimeRobot or Better Uptime for `/health` endpoint
- **Basic metrics**: requests/day, conversion rate (free → paid), payment success rate

## 5.6 — Error Handling Pass

| Scenario | UX Response |
|---|---|
| Engine calculation error | "तांत्रिक समस्या आली. आपोआप पुन्हा प्रयत्न करत आहोत..." + retry + Sentry alert |
| Geocoding service down | Fallback to cached results + "जवळचे शहर वापरा" prompt |
| PDF generation timeout | "PDF बनवत आहोत — थोड्या वेळाने डाउनलोड करा" + async job + email link |
| Payment gateway down | "पेमेंट सध्या उपलब्ध नाही. थोड्या वेळाने पुन्हा प्रयत्न करा." + alternative (bank transfer info if needed) |
| R2 storage unavailable | Log error, retry with exponential backoff, alert admin |

## 5.7 — Privacy & Legal

- Privacy Policy page (Marathi + English): data retention, what's stored, deletion request email
- "हे अहवाल मार्गदर्शनासाठी आहे" disclaimer on every result page and PDF
- Cookie consent banner (minimal — session cookies only for MVP)
- GDPR/IT Act compliance: data deletion on request within 30 days

---

---

# 🗄️ CROSS-CUTTING CONCERNS (apply across all phases)

## Security
- All premium fields gated **server-side** via `paid=true` DB check — never trust frontend state
- Razorpay secret key never exposed to frontend
- HTTPS everywhere; HSTS headers
- SQL injection: use SQLAlchemy ORM with parameterized queries only
- Rate limiting: via Redis + a library like `slowapi` (FastAPI)
- Birth data = PII: encrypt at rest in PostgreSQL (column-level encryption for name/DOB if needed)
- Define a data retention policy: auto-delete unpaid kundalis after 30 days

## Performance
- Geocode cache in PostgreSQL (same towns queried repeatedly)
- Kundali computation cached in DB (don't recompute if same birth profile already exists)
- SVG chart served as string (not an image file → no extra S3 request for free tier)
- PDF generated async → return poll URL immediately
- Next.js ISR for SEO landing pages

## Mobile-First UX Rules
- All buttons ≥ 44px touch target
- No horizontal scroll
- Autocomplete uses native mobile keyboard type (numeric for dates, search for place)
- WhatsApp share works natively on Android + iOS
- PDF download: test on Chrome Android, Safari iOS

## Marathi UX Copy Standards
- Always show both: "नाडी (Nadi)", "रास (Rashi)" — not one or the other
- Error messages in Marathi first: "वेळ अंदाजे असल्याने Lagna अचूक नसू शकते"
- CTA buttons: action-oriented Marathi verbs: "कुंडली बनवा", "जुळणी तपासा", "डाउनलोड करा"
- Scores shown in Marathi numerals when Marathi mode: "२४ / ३६ गुण"
- Use respectful second person ("आपण" / "तुम्ही") — avoid informal "तू"

---

---

# 📊 Success Metrics & Launch Gates

| Gate | Criteria |
|---|---|
| **Phase 0 Gate** | Engine validation test suite passes 100% for all 10–15 test vectors vs DrikPanchang + AstroSage |
| **Phase 1 Gate** | Marathi user generates kundali in <2 minutes on mobile; free result accurate |
| **Phase 2 Gate** | Payment → unlock → PDF in same session; no manual intervention |
| **Phase 3 Gate** | Koota scores match reference for 5+ matching test pairs; Marathi verdict correct |
| **Phase 4 Gate** | Full biodata cycle works; auto-fill from kundali works |
| **Phase 5 Gate** | Manglik checker ranks; admin can resolve payment queries in <2 min |

---

# 📅 Rough Timeline Summary

| Phase | Focus | Est. Duration |
|---|---|---|
| Phase 0 | Engine accuracy + validation | 2–3 weeks |
| Phase 1 | Free kundali (input → result) | 2–3 weeks |
| Phase 2 | Paid kundali + payment + PDF | 2–3 weeks |
| Phase 3 | Patrika matching | 2–3 weeks |
| Phase 4 | Biodata builder | 2 weeks |
| Phase 5 | Polish, SEO, admin, observability | 2–3 weeks |
| **Total** | **MVP to launch** | **~13–17 weeks** |

> Note: Phase 0 and Razorpay KYC run in parallel. Razorpay KYC can take 1–2 weeks; start it on Day 1.

---

## Open Questions (Require Decision Before Building)

> [!IMPORTANT]
> **Q1: Biodata pricing** — Is standalone biodata free (loss-leader to drive kundali upsell) or small fee (₹29–49)?
> Current plan: free if kundali already paid, small fee standalone. Confirm.

> [!IMPORTANT]
> **Q2: User accounts** — MVP is session/token-based (no login). Should we collect phone number or email upfront for PDF resend? Recommend: optional email at payment step only.

> [!IMPORTANT]
> **Q3: South Indian chart** — Phase 1 (basic, one style) or Phase 2 toggle? Maharashtra users are mixed. Recommend: North Indian in Phase 1, toggle in Phase 2.

> [!WARNING]
> **Q4: Razorpay category approval** — This is a blocker. If Razorpay rejects the astrology MCC, fallback to PayU or Cashfree. Must be resolved before Phase 2.

> [!CAUTION]
> **Q5: Data deletion policy** — How long do we retain unpaid kundali drafts? Recommend: 30 days for unpaid, 2 years for paid (PDF re-download support).

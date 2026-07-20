# User Flow & UX Design

## Design Principles
- Mobile-first, single column, large tap targets.
- Marathi as default language with an English toggle top-right; technical astrology terms show both scripts together (e.g. "नाडी (Nadi)").
- Minimum fields to get a free result; ask for more only after the user has seen value.
- WhatsApp share button on every result screen — this is how these documents actually circulate.
- Every paid unlock should feel like "unlocking more of something I already have," not "buy again from scratch."

## Flow A — Kundali Generation

1. **Landing page** — headline in Marathi ("तुमची अचूक कुंडली मोफत पाहा"), single CTA: "कुंडली बनवा."
2. **Input screen** (one screen, minimal fields):
   - Name
   - Gender
   - Date of birth (date picker)
   - Time of birth (time picker + toggle "वेळ अंदाजे आहे / अचूक वेळ माहित नाही")
   - Place of birth (autocomplete search, resolves lat/long silently)
3. **Loading state** (2–4 sec) — show a nice animated chart-drawing visual, not a blank spinner; builds perceived value.
4. **Free result screen**:
   - Basic chart image (D1)
   - Rashi, Nakshatra, Lagna, Gan, Nadi, Varna — shown as simple labeled cards
   - Blurred/locked preview of: planet table, Navamsa chart, Manglik detail, Dasha, written analysis
   - CTA: "संपूर्ण अहवाल मिळवा — ₹100" with a short bullet list of what's unlocked
5. **Payment sheet** (Razorpay checkout — UPI first, since that's the default expectation)
6. **Unlocked result screen**:
   - Full chart set, planet table, dasha, Manglik detail, written analysis
   - "PDF डाउनलोड करा" and "WhatsApp वर पाठवा" buttons prominent at top
   - Soft upsell card: "आता याच माहितीने बायोडाटा बनवा" → leads into Biodata flow with horoscope fields pre-filled

## Flow B — Patrika Matching

1. **Entry points**: from homepage directly, OR "आता जुळणी तपासा" CTA after generating one kundali (pre-fills one side).
2. **Input screen**: two side-by-side (stacked on mobile) mini-forms — Bride details, Groom details. Option: "आधीच कुंडली बनवली आहे? निवडा" to pick a saved one instead of re-entering.
3. **Loading state** — similar animated feedback.
4. **Free result screen**:
   - Total score big and central: "२४ / ३६ गुण"
   - Manglik status of both (yes/no badges)
   - Locked preview: 8-koota breakdown, dosha details, verdict sentence
   - CTA: "संपूर्ण जुळणी अहवाल — ₹50"
5. **Payment sheet**
6. **Unlocked result screen**:
   - 8-koota table with points per koota (visual bar per koota, not just numbers — easier to scan)
   - Dosha section: Nadi/Bhakoot/Mangal with plain-language explanation + cancellation note if applicable
   - Verdict sentence at the top in bold, e.g. "साधारण जुळणी — गुण ठीक आहेत पण नाडी दोष तपासा"
   - PDF + WhatsApp share buttons

## Flow C — Biodata Builder

1. Entry: from homepage, or upsell after kundali generation (pre-filled horoscope section).
2. **Step form** (multi-step, progress bar, not one giant form):
   - Step 1: Personal info + photo upload
   - Step 2: Family info
   - Step 3: Education & career
   - Step 4: Horoscope (auto-filled if linked kundali exists, editable)
   - Step 5: Expectations (Apeksha)
3. **Template picker** — visual gallery, 3+ templates at launch, live preview updates as user fills fields (delightful, reduces drop-off).
4. **Download/Share** — PDF + image formats, WhatsApp share.

## Cross-Feature Retention Loop
Kundali → (upsell) → Biodata (horoscope auto-filled) → (upsell) → Matching against a prospective match's kundali → shared results drive new user acquisition via WhatsApp forwards.

## Error/Edge Case UX
- Unknown/approximate birth time: show a visible disclaimer on the result ("वेळ अंदाजे असल्याने Lagna अचूक नसू शकते") since Lagna-dependent results (houses, Manglik-from-Lagna) are sensitive to time accuracy.
- Failed geocoding (small village not found): allow manual lat/long entry or "nearest known town" fallback, with a note.
- Payment failure: keep the generated (unpaid) draft accessible via a resumable link so the user doesn't have to re-enter data.

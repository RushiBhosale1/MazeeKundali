# Features & Scope

## 1. Kundali Generator (₹100)

### Free tier (lead magnet)
- Input: Name, DOB, time of birth, place of birth (city search → lat/long + historical timezone).
- Output shown free:
  - Rashi (Moon sign), Nakshatra + Pada, Lagna (Ascendant)
  - Gana, Nadi, Varna (single-line, no explanation)
  - Basic North/South Indian chart (D1) image, no planet-by-planet writeup

### Paid tier (₹100 unlocks)
- Full D1 (Rashi) chart + D9 (Navamsa) chart, toggle North/South Indian style
- Planet-by-planet placement table (sign, house, degree, retrograde flag, nakshatra)
- Mangal Dosha (Manglik) status with explanation and cancellation-rule check
- Vimshottari Dasha timeline (current Mahadasha/Antardasha minimum; full timeline as stretch)
- Written "detailed analysis" section (templated, data-driven paragraphs — not free-text AI generation for the core facts; see engine spec on why)
- Downloadable PDF (Marathi + English toggle)
- "Share on WhatsApp" export (image + short text summary)

## 2. Patrika Matching (₹50)

### Free tier
- Input two people's birth details (or select from previously generated kundalis)
- Output shown free: total Guna score out of 36, Manglik status of both (yes/no only)

### Paid tier (₹50 unlocks)
- Full 8-koota breakdown table (Varna, Vashya, Tara, Yoni, Graha Maitri, Gana, Bhakoot, Nadi) with points earned/max per koota
- Dosha flags: Nadi Dosha, Bhakoot Dosha, Mangal Dosha — with cancellation-rule notes if applicable
- Plain-language Marathi verdict sentence (templated based on score band + which doshas are active — see engine spec §Verdict Logic)
- Downloadable PDF matching report
- "Share on WhatsApp" export

## 3. Biodata Builder (bundled or standalone)
- Standard Marathi biodata fields: personal, family, education/career, horoscope, expectations, photo upload
- **Auto-fill horoscope section** (Rashi, Nakshatra, Gan, Nadi, Manglik) from a kundali the user already generated — this is the key retention/upsell link between features 1 and 3
- Multiple templates (at least 3 at launch), PDF + image export
- Community-specific fields optional (e.g., Kul-Daivat, Gotra) — text fields, not validated data

## Explicitly Out of Scope for MVP (revisit later)
- Personalized AI-written predictions/horoscope readings beyond templated, data-driven text — free-text LLM astrology predictions are a credibility and liability risk; keep all "predictions" traceable to a specific classical rule.
- Live astrologer chat/consultation booking
- Muhurta (auspicious date/time) selection tool
- DashaKoota (10-point South Indian matching) — Ashtakoot only for MVP
- Multi-language beyond Marathi/English
- User accounts with saved family trees — single-session generation is enough for MVP; add accounts only if retention data justifies it

## Nice-to-Have Add-ons (from expert review, prioritize after MVP validates)
- Standalone free Manglik checker (traffic driver, funnels into paid kundali)
- Bundle pricing: Kundali + Matching together at a discount vs. ₹150 separately
- Regenerate-for-free if birth details were wrong (trust/refund alternative)

# Astrology Calculation Engine Spec

**Read this fully before writing any calculation code. Accuracy here is the entire product's credibility.**

## 1. Core Calculation Pipeline

### Step 1 — Resolve exact birth moment in UTC
Input: DOB, time of birth (as told by family — often approximate), place of birth.
- Geocode place → latitude, longitude.
- Resolve the **historical UTC offset** for that place/date — do NOT hardcode IST = +5:30 always.
  - India used regional local mean time and different offsets before 1 Sep 1947.
  - India briefly used +5:30 and a wartime +6:30 (IST forward) during 1941–1945 in some references — verify against an authoritative historical tz database (IANA `tz` database via a library like `pytz`/`zoneinfo` handles this correctly if you use the place's real IANA zone, e.g. `Asia/Kolkata`, rather than a hardcoded offset).
  - **Rule: always resolve offset via IANA tz database for the exact date, never hardcode +5:30.**
- Convert local birth time → UTC datetime. This UTC datetime + lat/long is the only input the ephemeris needs.

### Step 2 — Planetary positions (tropical)
- Use **Swiss Ephemeris** (`pyswisseph` in Python, or equivalent bindings) to compute tropical longitude of: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu (Mean or True Node — pick **True Node** as default, it's what most Indian software defaults to today; expose as a setting), Ketu (always 180° from Rahu).
- Also compute Ascendant (Lagna) using the birth's exact time + lat/long (this requires house-system calculation, not just planet positions).

### Step 3 — Convert to sidereal (Vedic) positions
- Subtract the **Ayanamsa** value for that date from each tropical longitude to get sidereal longitude.
- **Default ayanamsa: Lahiri (Chitrapaksha)** — this is India's government-standard ayanamsa and what the vast majority of Indian users/astrologers expect. Swiss Ephemeris has this built in (`SE_SIDM_LAHIRI`).
- Do not silently use a different ayanamsa (e.g., Raman, KP) without the user choosing it — mismatched ayanamsa is the #1 cause of "this doesn't match what my astrologer said."

### Step 4 — Derive Rashi, Nakshatra, Pada, Lagna
- **Rashi (Moon sign)**: sidereal Moon longitude ÷ 30° → 12 signs (Aries=0 through Pisces=11).
- **Nakshatra**: sidereal Moon longitude ÷ 13°20' (13.333...°) → 27 nakshatras.
- **Pada (quarter)**: remainder within the nakshatra ÷ 3°20' → 1 of 4 padas.
- **Lagna (Ascendant sign)**: from Step 2's ascendant calculation, sidereal-corrected same as above.
- Do the same sign/nakshatra derivation for every planet, to place them in the chart.

### Step 5 — House placement & chart rendering
- Default house system: **Whole Sign** (most common in traditional Vedic practice) — each house = one full sign starting from Lagna sign. Avoid Placidus/other Western house systems unless a user explicitly wants a Western-style breakdown.
- Render as North Indian (diamond, fixed house positions) or South Indian (square grid, fixed sign positions) style — make this a UI toggle, not a fixed choice, since Maharashtra households vary in what they're used to.

### Step 6 — Vimshottari Dasha
- Standard 120-year cycle, sequence: Ketu(7) → Venus(20) → Sun(6) → Moon(10) → Mars(7) → Rahu(18) → Jupiter(16) → Saturn(19) → Mercury(17) years.
- Starting dasha and elapsed portion is derived from Moon's exact nakshatra position at birth (proportion through the nakshatra = proportion elapsed of the first dasha lord's period).
- Compute current Mahadasha/Antardasha as of "today" for MVP; full multi-level timeline (Pratyantardasha etc.) is a stretch goal.

---

## 2. Ashtakoot Guna Milan Algorithm (Matching)

Once both people's Rashi + Nakshatra + Rashi-lord + Lagna are known (from the pipeline above), matching is a **pure lookup/comparison function** — no further ephemeris calls needed. Max 36 points across 8 koots.

### 2.1 Varna (1 point) — spiritual/mental compatibility
Each Rashi maps to a Varna:
- Brahmin: Cancer, Scorpio, Pisces
- Kshatriya: Aries, Leo, Sagittarius
- Vaishya: Taurus, Virgo, Capricorn
- Shudra: Gemini, Libra, Aquarius
Hierarchy: Brahmin > Kshatriya > Vaishya > Shudra.
**Score: 1 if groom's Varna ≥ bride's Varna, else 0.**

### 2.2 Vashya (2 points) — mutual attraction/dominance
Rashis grouped into 5 categories (Chatushpada/quadruped, Manava/human, Jalachara/water, Vanachara/wild, Keeta/insect — note Vrishchika/Scorpio is its own Keeta group). Some rashis (Sagittarius, Capricorn) are traditionally split by degree (first half vs second half belongs to different groups) — **this half-sign split needs to be validated against a reference tool during QA (§4), do not assume a single source's table is authoritative without cross-checking.**
**Score: 2 if same group / natural affinity, 1 if one-way affinity, 0 if none.**

### 2.3 Tara (3 points) — health/wellbeing, based on birth-star counting
- Count nakshatras from bride's nakshatra to groom's, and groom's to bride's (each count mod 9, then mod 3 to get the "Tara" category: 1,3,5,7 = inauspicious; 2,4,6,8,9(0) = auspicious — exact classification table must be implemented precisely, this is formulaic not subjective).
**Score: 3 if both directions auspicious, 1.5 if one direction auspicious, 0 if neither.**

### 2.4 Yoni (4 points) — physical/sexual compatibility
Each of the 27 nakshatras maps to one of 14 animal symbols (with male/female variants), e.g. Ashwini→Horse, Bharani→Elephant, Krittika→Sheep, Rohini→Serpent, etc. (full 27-row table required — implement from a verified classical source, cross-check against reference tool per §4).
**Score: 4 if same animal, 3 if friendly animals, 2 if neutral, 1 if unfriendly, 0 if enemy pair (per the classical Yoni-friendship matrix).**

### 2.5 Graha Maitri (5 points) — mental/intellectual compatibility
Based on the planetary lord of each person's Moon-Rashi, using the classical 7-planet (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn) natural friendship table (friend/neutral/enemy matrix).
**Score: 5 if mutual friends, 4 if one friend, 3 if both neutral, 1–2 for mixed neutral/enemy, 0 if mutual enemies** (exact graded scale must follow the classical table — implement as a lookup, not an approximation).

### 2.6 Gana (6 points) — temperament
Each nakshatra is Deva, Manushya, or Rakshasa gana:
- **Deva**: Ashwini, Mrigashira, Punarvasu, Pushya, Hasta, Swati, Anuradha, Shravana, Revati
- **Manushya**: Bharani, Rohini, Ardra, Purva Phalguni, Uttara Phalguni, Purva Ashadha, Uttara Ashadha, Purva Bhadrapada, Uttara Bhadrapada
- **Rakshasa**: Krittika, Ashlesha, Magha, Chitra, Vishakha, Jyeshtha, Mula, Dhanishta, Shatabhisha
**Score: 6 if same gana, graded lower for Manushya-Deva vs Manushya-Rakshasa vs Deva-Rakshasa pairs (Deva-Rakshasa is the worst combination), 0 for the most incompatible pairing.**

### 2.7 Bhakoot (7 points) — emotional/financial/family harmony
Based on the Rashi distance (in signs) between bride and groom's Moon signs.
- Certain distances are dosha-triggering: **2/12 (2nd-12th), 6/8 (6th-8th), 5/9 (5th-9th)** relationships between the two Moon signs are classically flagged as Bhakoot Dosha.
**Score: 7 if no dosha distance, 0 if dosha distance present** (Bhakoot is binary in most implementations — either full points or zero, unlike the graded koots above).

### 2.8 Nadi (8 points) — health/genetic compatibility (highest weight)
Each nakshatra is Aadi (Vata), Madhya (Pitta), or Antya (Kapha):
- **Aadi**: Ashwini, Ardra, Punarvasu, Uttara Phalguni, Hasta, Jyeshtha, Mula, Shatabhisha, Purva Bhadrapada
- **Madhya**: Bharani, Mrigashira, Pushya, Purva Phalguni, Chitra, Anuradha, Purva Ashadha, Dhanishta, Uttara Bhadrapada
- **Antya**: Krittika, Rohini, Ashlesha, Magha, Swati, Vishakha, Uttara Ashadha, Shravana, Revati
**Score: 8 if different Nadi, 0 if same Nadi (Nadi Dosha — single biggest point loss in the system).**

### 2.9 Dosha Cancellation Rules
Classical texts allow certain doshas to be cancelled under specific conditions (e.g., Nadi Dosha cancelled if bride/groom's Rashi-lords are the same and in mutual friendship, or if Nadi Dosha occurs but Rashi/Nakshatra are identical (same Rashi+Nakshatra pada exception), etc.). **Implement cancellation rules as an explicit, cited rule-set — do not silently cancel doshas without showing the user which rule applied and why.** Show cancellation status transparently in the report ("Nadi Dosha present, but cancelled per [rule]") rather than just adjusting the score invisibly.

### 2.10 Mangal Dosha (Manglik) — computed separately, not part of the 36
- Check if Mars falls in house 1, 2, 4, 7, 8, or 12 from the Lagna (some traditions also check from Moon and from Venus — expose which reference point is used).
- Apply standard cancellation checks (e.g., Mars in own sign or exaltation, aspects from Jupiter, both partners Manglik cancelling each other, etc.) — again, show the rule applied, don't just output yes/no with no reasoning.

### 2.11 Verdict Logic (plain-language summary)
Build a templated (not free-generated) verdict based on:
- Total score band: 0–17 (below threshold), 18–24 (average), 25–32 (good), 33–36 (excellent) — but the template must reference which koots are behind the number, not just the number, per the earlier research: a 24/36 with Nadi+Bhakoot intact is materially different from 24/36 without them.
- Explicit call-out if Nadi Dosha, Bhakoot Dosha, or Mangal Dosha (uncancelled) are present, since these are what Marathi families ask about first regardless of total score.
- Output in Marathi with an English mirror line.

---

## 3. What NOT to Do
- Do not use free-text LLM generation for the core astrological facts (planet positions, koota scores, dosha status) — these must come from the deterministic engine. LLM/AI text generation, if used at all, should only be for phrasing the *already-computed* verdict into natural sentences, never for computing or inventing the underlying numbers.
- Do not hardcode a single ayanamsa or house system without a way to verify/override it.
- Do not assume +5:30 for all Indian birth times — historical/regional offset errors silently shift the whole chart.
- Do not show a total Guna score without offering the breakdown — this is explicitly called out as what separates credible tools from cheap ones.

## 4. Mandatory Validation Strategy Before Launch
Because getting a single lookup table wrong (e.g., Yoni or Vashya edge cases) silently produces wrong results with no error thrown, you must validate the engine, not just trust the implementation:
1. Pick 10–15 real or synthetic birth datasets spanning different decades, regions (including at least one pre-1947 birth date to test historical timezone handling), and edge cases (planets near sign boundaries, Nakshatra boundaries, both Rahu calculation modes).
2. Run each through your engine and through 2 independent reference tools (e.g., DrikPanchang and AstroSage) for the same inputs.
3. Diff every output field: Rashi, Nakshatra, Pada, Lagna, all planet positions, dasha, and (for matching) every individual koota score.
4. Any mismatch must be root-caused (ayanamsa difference, house system difference, Rahu calculation mode, rounding at a boundary) before launch — do not launch with unexplained discrepancies.
5. Turn these test cases into an automated regression test suite so future changes to the engine can't silently break accuracy.

Treat this validation step as a hard release gate, not optional QA — this is what makes the product trustworthy to actual astrologers and families, versus being "just another web tool."

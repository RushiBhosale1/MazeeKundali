"""
engine/templates.py
Templated Marathi written analysis paragraphs.

These are data-driven, deterministic templates — NOT free-text LLM generation.
Every sentence is traceable to a specific classical rule or placement.
The template variables are filled from computed kundali data.

This keeps the product credible: users can verify claims against their chart data.
"""
from __future__ import annotations
from engine.models import KundaliResult, Rashi, Nakshatra, Gana, Nadi, Planet
from api.schemas import WrittenAnalysis


# ---------------------------------------------------------------------------
# Rashi analysis templates (Marathi)
# ---------------------------------------------------------------------------
RASHI_ANALYSIS_MR: dict[Rashi, str] = {
    Rashi.ARIES: (
        "मेष राशीचे जातक उत्साही, धाडसी आणि नेतृत्वगुण असलेले असतात. "
        "मंगळ हा या राशीचा स्वामी असल्याने यांच्यात कृतिशीलता आणि स्वाभिमान प्रबळ असतो."
    ),
    Rashi.TAURUS: (
        "वृषभ राशीचे जातक स्थिर, व्यावहारिक आणि कलाप्रिय असतात. "
        "शुक्र स्वामी असल्याने सौंदर्यदृष्टी आणि भौतिक सुखाची आवड असते."
    ),
    Rashi.GEMINI: (
        "मिथुन राशीचे जातक बुद्धिमान, संवादप्रिय आणि बहुमुखी प्रतिभेचे असतात. "
        "बुध स्वामी असल्याने शिक्षण, व्यापार आणि संचारात प्रावीण्य असते."
    ),
    Rashi.CANCER: (
        "कर्क राशीचे जातक भावनाशील, कुटुंबवत्सल आणि स्मरणशक्ती तीव्र असतात. "
        "चंद्र स्वामी असल्याने मातृप्रेम आणि घराशी जिव्हाळा विशेष असतो."
    ),
    Rashi.LEO: (
        "सिंह राशीचे जातक आत्मविश्वासी, उदार आणि नेतृत्वप्रिय असतात. "
        "सूर्य स्वामी असल्याने यांच्यात प्रभावशाली व्यक्तिमत्त्व आणि स्वाभिमान दिसतो."
    ),
    Rashi.VIRGO: (
        "कन्या राशीचे जातक विश्लेषणात्मक, सेवाभावी आणि सुव्यवस्थित असतात. "
        "बुध स्वामी असल्याने तपशीलांकडे लक्ष आणि कौशल्यपूर्ण कार्यपद्धती असते."
    ),
    Rashi.LIBRA: (
        "तुळ राशीचे जातक न्यायप्रिय, सौंदर्यप्रेमी आणि सहकार्यशील असतात. "
        "शुक्र स्वामी असल्याने कलागुण, परस्पर संबंध आणि समतोल जीवन महत्त्वाचे असते."
    ),
    Rashi.SCORPIO: (
        "वृश्चिक राशीचे जातक तीव्र इच्छाशक्ती, संशोधनवृत्ती आणि अंतर्ज्ञान असलेले असतात. "
        "मंगळ स्वामी असल्याने यांच्यात जिद्द आणि गहन भावनिक खोली असते."
    ),
    Rashi.SAGITTARIUS: (
        "धनु राशीचे जातक तत्त्वज्ञानी, साहसी आणि उच्च आदर्श बाळगणारे असतात. "
        "गुरु स्वामी असल्याने ज्ञान, धर्म आणि प्रवास यांची आवड असते."
    ),
    Rashi.CAPRICORN: (
        "मकर राशीचे जातक महत्त्वाकांक्षी, शिस्तप्रिय आणि व्यावहारिक असतात. "
        "शनि स्वामी असल्याने कठोर परिश्रम आणि दीर्घकालीन यशाकडे कल असतो."
    ),
    Rashi.AQUARIUS: (
        "कुंभ राशीचे जातक मौलिक विचारसरणी, मानवतावादी आणि स्वतंत्र मनाचे असतात. "
        "शनि स्वामी असल्याने समाजसेवा आणि नवकल्पना यांची आवड असते."
    ),
    Rashi.PISCES: (
        "मीन राशीचे जातक कल्पनाशील, सहानुभूतीशील आणि अध्यात्मप्रवण असतात. "
        "गुरु स्वामी असल्याने भावना आणि आध्यात्मिक बुद्धी प्रबळ असते."
    ),
}

# ---------------------------------------------------------------------------
# Nakshatra analysis (brief — focused on character)
# ---------------------------------------------------------------------------
NAKSHATRA_ANALYSIS_MR: dict[Nakshatra, str] = {
    Nakshatra.ASHWINI: "अश्विनी नक्षत्र जातक वेगवान, उपचारशक्ती असणारे आणि नवोन्मेषी असतात.",
    Nakshatra.BHARANI: "भरणी नक्षत्र जातक कर्मठ, जबाबदार आणि निर्णायक असतात.",
    Nakshatra.KRITTIKA: "कृत्तिका नक्षत्र जातक तीक्ष्ण बुद्धी, स्पष्टवक्ते आणि महत्त्वाकांक्षी असतात.",
    Nakshatra.ROHINI: "रोहिणी नक्षत्र जातक सुंदर, कलाप्रिय आणि भोगप्रवण असतात.",
    Nakshatra.MRIGASHIRA: "मृगशीर्ष नक्षत्र जातक जिज्ञासू, प्रवासप्रिय आणि संवेदनशील असतात.",
    Nakshatra.ARDRA: "आर्द्रा नक्षत्र जातक बुद्धिमान, तीव्र भावना असणारे आणि संशोधनप्रवण असतात.",
    Nakshatra.PUNARVASU: "पुनर्वसू नक्षत्र जातक उदार, आशावादी आणि पुनर्जन्म/नवीन सुरुवात करणारे असतात.",
    Nakshatra.PUSHYA: "पुष्य नक्षत्र जातक पोषण करणारे, धार्मिक आणि समाजप्रिय असतात.",
    Nakshatra.ASHLESHA: "आश्लेषा नक्षत्र जातक चाणाक्ष, रहस्यमय आणि तीव्र इच्छाशक्ती असणारे असतात.",
    Nakshatra.MAGHA: "मघा नक्षत्र जातक परंपरानिष्ठ, गर्वशील आणि नेतृत्वगुण असणारे असतात.",
    Nakshatra.PURVA_PHALGUNI: "पूर्वा फाल्गुनी नक्षत्र जातक सुखप्रिय, कलाकार आणि आनंददायी असतात.",
    Nakshatra.UTTARA_PHALGUNI: "उत्तरा फाल्गुनी नक्षत्र जातक सेवाभावी, विश्वासू आणि व्यावसायिक असतात.",
    Nakshatra.HASTA: "हस्त नक्षत्र जातक कुशल, चतुर आणि हस्तकलेत प्रवीण असतात.",
    Nakshatra.CHITRA: "चित्रा नक्षत्र जातक कलाकुसरीचे, आकर्षक व्यक्तिमत्त्व आणि सर्जनशील असतात.",
    Nakshatra.SWATI: "स्वाती नक्षत्र जातक स्वतंत्र विचार, व्यापारी बुद्धी आणि लवचिक असतात.",
    Nakshatra.VISHAKHA: "विशाखा नक्षत्र जातक ध्येयनिष्ठ, तीव्र इच्छाशक्ती आणि स्पर्धाशील असतात.",
    Nakshatra.ANURADHA: "अनुराधा नक्षत्र जातक मैत्रीप्रिय, भक्तिभावी आणि यशस्वी असतात.",
    Nakshatra.JYESHTHA: "ज्येष्ठा नक्षत्र जातक वडिलोपार्जित गुण, नेतृत्व आणि अभिमानी असतात.",
    Nakshatra.MULA: "मूळ नक्षत्र जातक मूलतत्त्वांचा शोध घेणारे, तीव्र आणि परिवर्तनशील असतात.",
    Nakshatra.PURVA_ASHADHA: "पूर्वाषाढा नक्षत्र जातक उत्साही, आशावादी आणि विजयी वृत्तीचे असतात.",
    Nakshatra.UTTARA_ASHADHA: "उत्तराषाढा नक्षत्र जातक धर्मनिष्ठ, विजयी आणि दीर्घायुषी असतात.",
    Nakshatra.SHRAVANA: "श्रवण नक्षत्र जातक श्रवणशक्ती उत्तम, शिकण्याची आवड आणि पारंपरिक असतात.",
    Nakshatra.DHANISHTA: "धनिष्ठा नक्षत्र जातक संगीतप्रिय, समृद्ध आणि सामाजिक असतात.",
    Nakshatra.SHATABHISHA: "शततारका नक्षत्र जातक रहस्यमय, उपचारक आणि स्वतंत्र असतात.",
    Nakshatra.PURVA_BHADRAPADA: "पूर्वा भाद्रपदा नक्षत्र जातक उत्साही, द्वैतवृत्ती आणि परिवर्तनशील असतात.",
    Nakshatra.UTTARA_BHADRAPADA: "उत्तरा भाद्रपदा नक्षत्र जातक ज्ञानी, शांत आणि आध्यात्मिक असतात.",
    Nakshatra.REVATI: "रेवती नक्षत्र जातक दयाळू, कलाकार आणि पोषण करणारे असतात.",
}

# ---------------------------------------------------------------------------
# Gana analysis
# ---------------------------------------------------------------------------
GANA_ANALYSIS_MR: dict[Gana, str] = {
    Gana.DEVA: (
        "देव गणाचे जातक सात्विक, धार्मिक आणि सहकार्यशील स्वभावाचे असतात. "
        "यांच्या जीवनात सत्य, सेवा आणि आध्यात्मिक मूल्ये महत्त्वाची भूमिका बजावतात."
    ),
    Gana.MANUSHYA: (
        "मनुष्य गणाचे जातक व्यावहारिक, संतुलित आणि सामाजिक असतात. "
        "यांच्यात भौतिक आणि आध्यात्मिक यांचे समतोल चांगले असते."
    ),
    Gana.RAKSHASA: (
        "राक्षस गणाचे जातक तीव्र इच्छाशक्ती, स्वयंनिर्भर आणि जिद्दी असतात. "
        "यांच्यात नेतृत्वगुण आणि स्वतःचे मार्ग आखण्याची प्रवृत्ती असते."
    ),
}

# ---------------------------------------------------------------------------
# Nadi analysis
# ---------------------------------------------------------------------------
NADI_ANALYSIS_MR: dict[Nadi, str] = {
    Nadi.AADI: (
        "आदी (वात) नाडीचे जातक गतिशील, सर्जनशील आणि वेगवान विचारसरणीचे असतात. "
        "विवाहासाठी मध्य किंवा अंत्य नाडीचा जोडीदार अनुकूल असतो."
    ),
    Nadi.MADHYA: (
        "मध्य (पित्त) नाडीचे जातक संघटित, तीव्र बुद्धिमत्ता आणि नेतृत्वगुण असणारे असतात. "
        "विवाहासाठी आदी किंवा अंत्य नाडीचा जोडीदार अनुकूल असतो."
    ),
    Nadi.ANTYA: (
        "अंत्य (कफ) नाडीचे जातक स्थिर, धैर्यशील आणि सहनशील असतात. "
        "विवाहासाठी आदी किंवा मध्य नाडीचा जोडीदार अनुकूल असतो."
    ),
}

# ---------------------------------------------------------------------------
# Yoga detection — Classical Vedic yoga combinations
# ---------------------------------------------------------------------------
RASHI_LORDS: dict[Rashi, Planet] = {
    Rashi.ARIES: Planet.MARS,
    Rashi.TAURUS: Planet.VENUS,
    Rashi.GEMINI: Planet.MERCURY,
    Rashi.CANCER: Planet.MOON,
    Rashi.LEO: Planet.SUN,
    Rashi.VIRGO: Planet.MERCURY,
    Rashi.LIBRA: Planet.VENUS,
    Rashi.SCORPIO: Planet.MARS,
    Rashi.SAGITTARIUS: Planet.JUPITER,
    Rashi.CAPRICORN: Planet.SATURN,
    Rashi.AQUARIUS: Planet.SATURN,
    Rashi.PISCES: Planet.JUPITER,
}


def _detect_yogas(result: KundaliResult) -> list[str]:
    """
    Detect classical yoga combinations from the kundali.
    Returns a list of Marathi descriptions for detected yogas.
    """
    if not result.planet_positions:
        return []

    yogas = []

    # Build maps
    planet_rashi: dict[str, Rashi] = {}
    planet_house: dict[str, int] = {}
    planet_retro: dict[str, bool] = {}
    planet_exalted: dict[str, bool] = {}

    for pp in result.planet_positions:
        planet_rashi[pp.planet.value] = pp.rashi
        planet_house[pp.planet.value] = pp.house
        planet_retro[pp.planet.value] = pp.retrograde
        planet_exalted[pp.planet.value] = pp.is_exalted

    # ── 1. Gajakesari Yoga ───────────────────────────────────────────────────
    # Moon and Jupiter in kendra (1,4,7,10) from each other
    moon_h = planet_house.get("Moon", 0)
    jup_h = planet_house.get("Jupiter", 0)
    if moon_h and jup_h:
        diff = abs(moon_h - jup_h)
        if diff in (0, 3, 6, 9):
            yogas.append(
                "🌟 गजकेसरी योग: चंद्र आणि गुरु परस्पर केंद्रात आहेत. "
                "हा उत्तम राजयोग असून बुद्धिमत्ता, यश आणि प्रतिष्ठा मिळण्याचे संकेत देतो."
            )

    # ── 2. Budha-Aditya Yoga (Nipuna Yoga) ──────────────────────────────────
    # Sun and Mercury in same house (conjunction)
    sun_h = planet_house.get("Sun", 0)
    mer_h = planet_house.get("Mercury", 0)
    if sun_h and mer_h and sun_h == mer_h:
        yogas.append(
            "🌟 बुधादित्य योग (निपुण योग): सूर्य आणि बुध एकत्र आहेत. "
            "तीव्र बुद्धिमत्ता, संवादकौशल्य आणि व्यावसायिक यशाचे लक्षण."
        )

    # ── 3. Chandra-Mangal Yoga ───────────────────────────────────────────────
    # Moon and Mars in same house
    mars_h = planet_house.get("Mars", 0)
    if moon_h and mars_h and moon_h == mars_h:
        yogas.append(
            "🌟 चंद्र-मंगळ योग: चंद्र आणि मंगळ एकत्र. "
            "धन संचय, उद्योगशीलता आणि धाडसी स्वभावाचे संकेत."
        )

    # ── 4. Hamsa Yoga (Panch Mahapurush) ────────────────────────────────────
    # Jupiter in its own sign or exaltation in kendra (1,4,7,10)
    jup_rashi = planet_rashi.get("Jupiter")
    if jup_rashi in (Rashi.SAGITTARIUS, Rashi.PISCES, Rashi.CANCER) and jup_h in (1, 4, 7, 10):
        yogas.append(
            "🌟 हंस योग (पंचमहापुरुष): गुरु केंद्रात स्वगृही/उच्चस्थ आहे. "
            "ज्ञान, धार्मिकता, उच्च सामाजिक प्रतिष्ठा आणि दीर्घायुषाचे लक्षण."
        )

    # ── 5. Ruchaka Yoga (Panch Mahapurush) ──────────────────────────────────
    # Mars in Aries, Scorpio or Capricorn in kendra
    mars_rashi = planet_rashi.get("Mars")
    if mars_rashi in (Rashi.ARIES, Rashi.SCORPIO, Rashi.CAPRICORN) and mars_h in (1, 4, 7, 10):
        yogas.append(
            "🌟 रुचक योग (पंचमहापुरुष): मंगळ केंद्रात बलवान. "
            "शौर्य, नेतृत्व, शारीरिक बळ आणि यशाचे लक्षण."
        )

    # ── 6. Malavya Yoga (Panch Mahapurush) ──────────────────────────────────
    # Venus in Taurus, Libra or Pisces in kendra
    ven_rashi = planet_rashi.get("Venus")
    ven_h = planet_house.get("Venus", 0)
    if ven_rashi in (Rashi.TAURUS, Rashi.LIBRA, Rashi.PISCES) and ven_h in (1, 4, 7, 10):
        yogas.append(
            "🌟 मालव्य योग (पंचमहापुरुष): शुक्र केंद्रात बलवान. "
            "सौंदर्य, वैवाहिक सुख, कलाप्रेम आणि भौतिक समृद्धीचे संकेत."
        )

    # ── 7. Sasha Yoga (Panch Mahapurush) ────────────────────────────────────
    # Saturn in Capricorn, Aquarius or Libra in kendra
    sat_rashi = planet_rashi.get("Saturn")
    sat_h = planet_house.get("Saturn", 0)
    if sat_rashi in (Rashi.CAPRICORN, Rashi.AQUARIUS, Rashi.LIBRA) and sat_h in (1, 4, 7, 10):
        yogas.append(
            "🌟 शश योग (पंचमहापुरुष): शनि केंद्रात बलवान. "
            "दीर्घ परिश्रम, नेतृत्व, व्यवस्थापनकौशल्य आणि दीर्घायुषाचे लक्षण."
        )

    # ── 8. Bhadra Yoga (Panch Mahapurush) ───────────────────────────────────
    # Mercury in Gemini or Virgo in kendra
    mer_rashi = planet_rashi.get("Mercury")
    if mer_rashi in (Rashi.GEMINI, Rashi.VIRGO) and mer_h in (1, 4, 7, 10):
        yogas.append(
            "🌟 भद्र योग (पंचमहापुरुष): बुध केंद्रात स्वगृही. "
            "वाणी, बुद्धी, लेखन, व्यापार आणि तांत्रिक क्षेत्रात यशाचे लक्षण."
        )

    # ── 9. Dharma-Karma Adhipati Yoga ────────────────────────────────────────
    # Lord of 9th and 10th in mutual kendra or conjunction
    if result.lagna:
        lagna_rashi_list = list(Rashi)
        lagna_idx = lagna_rashi_list.index(result.lagna)
        ninth_rashi = lagna_rashi_list[(lagna_idx + 8) % 12]
        tenth_rashi = lagna_rashi_list[(lagna_idx + 9) % 12]
        lord9 = RASHI_LORDS.get(ninth_rashi)
        lord10 = RASHI_LORDS.get(tenth_rashi)
        if lord9 and lord10 and lord9 != lord10:
            h9_lord = planet_house.get(lord9.value, 0)
            h10_lord = planet_house.get(lord10.value, 0)
            if h9_lord and h10_lord and h9_lord == h10_lord:
                yogas.append(
                    "🌟 धर्म-कर्माधिपती योग: ९व्या आणि १०व्या घराचे स्वामी एकत्र. "
                    "करिअर, यश आणि सामाजिक प्रतिष्ठेत उत्कर्षाचे लक्षण."
                )

    # ── 10. Viparita Raja Yoga ────────────────────────────────────────────────
    # Lords of Dusthanas (6,8,12) in dusthanas — can give sudden rise
    if result.lagna:
        lagna_rashi_list = list(Rashi)
        lagna_idx = lagna_rashi_list.index(result.lagna)
        d6 = lagna_rashi_list[(lagna_idx + 5) % 12]
        d8 = lagna_rashi_list[(lagna_idx + 7) % 12]
        d12 = lagna_rashi_list[(lagna_idx + 11) % 12]
        lord6 = RASHI_LORDS.get(d6)
        lord8 = RASHI_LORDS.get(d8)
        lord12 = RASHI_LORDS.get(d12)
        dusthana_lords = {p for p in (lord6, lord8, lord12) if p}
        for l in dusthana_lords:
            lh = planet_house.get(l.value, 0)
            if lh in (6, 8, 12):
                yogas.append(
                    "🌟 विपरीत राजयोग: अशुभ भावांचे स्वामी अशुभ भावातच. "
                    "जीवनात अनपेक्षित उत्थान, संकटातून यश मिळण्याचे संकेत."
                )
                break

    return yogas


# ---------------------------------------------------------------------------
# Conclusion / निष्कर्ष — detailed life-area paragraph
# ---------------------------------------------------------------------------
def _generate_conclusion(result: KundaliResult) -> str:
    """
    Generate a detailed conclusion paragraph covering key life areas:
    personality, career, wealth, marriage/relationship, health.
    Based on Lagna, Rashi, Nakshatra, planet placements and Dasha.
    """
    parts = []

    # ── Personality ──────────────────────────────────────────────────────────
    if result.lagna and result.rashi:
        parts.append(
            f"या कुंडलीचे जातक {result.lagna.name_mr} लग्न आणि {result.rashi.name_mr} राशीचे आहेत. "
            f"यामुळे बुद्धिमत्ता, निर्णयक्षमता आणि व्यक्तिमत्त्वात विशेष आकर्षण दिसते."
        )
    elif result.rashi:
        parts.append(
            f"जातक {result.rashi.name_mr} राशीचे असल्याने स्वभावात {RASHI_ANALYSIS_MR.get(result.rashi, '')}".strip()
        )

    # ── Career / Profession ──────────────────────────────────────────────────
    career_text = ""
    if result.planet_positions:
        for pp in result.planet_positions:
            if pp.planet.value == "Jupiter" and pp.house in (1, 4, 7, 10):
                career_text = "गुरु केंद्रात असल्याने व्यावसायिक क्षेत्रात सन्मान आणि पदोन्नती मिळण्याचे योग आहेत."
                break
            if pp.planet.value == "Mercury" and pp.house in (1, 4, 7, 10):
                career_text = "बुध केंद्रात असल्याने तांत्रिक, लेखन किंवा संवाद क्षेत्रात यश संभव."
                break
            if pp.planet.value == "Sun" and pp.is_exalted:
                career_text = "सूर्य उच्चस्थ असल्याने सरकारी क्षेत्र, नेतृत्व किंवा प्रशासनात यशाचे संकेत."
                break
            if pp.planet.value == "Saturn" and pp.house in (3, 6, 10, 11):
                career_text = "शनि कर्मभावाशी संबंधित असल्याने परिश्रमाने यश, तंत्रज्ञान किंवा सेवा क्षेत्र अनुकूल."
                break
    if career_text:
        parts.append(f"📊 व्यवसाय: {career_text}")

    # ── Wealth ───────────────────────────────────────────────────────────────
    wealth_text = ""
    if result.planet_positions:
        for pp in result.planet_positions:
            if pp.planet.value == "Venus" and pp.house in (2, 11):
                wealth_text = "शुक्र धन/लाभ भावात असल्याने आर्थिक समृद्धी आणि भौतिक सुखाचे योग."
                break
            if pp.planet.value == "Jupiter" and pp.house in (2, 11):
                wealth_text = "गुरु धन/लाभ भावात असल्याने आर्थिक स्थिरता आणि वारसाहक्कातून लाभ संभव."
                break
            if pp.planet.value == "Moon" and pp.house in (2, 4, 11):
                wealth_text = "चंद्र धन/सुख भावात असल्याने कुटुंबाकडून संपत्ती आणि भावनिक समृद्धी."
                break
    if wealth_text:
        parts.append(f"💰 आर्थिक: {wealth_text}")

    # ── Marriage / Relationships ─────────────────────────────────────────────
    marriage_text = ""
    if result.planet_positions:
        for pp in result.planet_positions:
            if pp.planet.value == "Venus" and pp.house in (1, 4, 7):
                marriage_text = "शुक्र शुभ स्थानात असल्याने वैवाहिक जीवन सुखकर आणि जोडीदाराशी प्रेमपूर्ण संबंध."
                break
            if pp.planet.value == "Jupiter" and pp.house == 7:
                marriage_text = "गुरु सप्तम भावात असल्याने सुयोग्य, सुसंस्कृत जोडीदार लाभण्याचे संकेत."
                break
    if not marriage_text and result.mangal_dosha:
        if result.mangal_dosha.is_manglik:
            marriage_text = "मंगळ दोष असल्याने विवाहासाठी मंगळिक जोडीदार अनुकूल. योग्य परिहारांनी दोष कमी करता येतो."
        elif result.mangal_dosha.cancellation_applied:
            marriage_text = "मंगळ दोष परिहार लागू असल्याने वैवाहिक जीवनावर विशेष प्रतिकूल परिणाम नाही."
    if marriage_text:
        parts.append(f"💍 विवाह/संबंध: {marriage_text}")

    # ── Health ───────────────────────────────────────────────────────────────
    health_text = ""
    if result.planet_positions:
        for pp in result.planet_positions:
            if pp.planet.value == "Saturn" and pp.house == 6:
                health_text = "शनि षष्ठ भावात असल्याने आजारावर मात करण्याची क्षमता, परंतु वात-संबंधित विकारांकडे लक्ष द्यावे."
                break
            if pp.planet.value == "Mars" and pp.house in (6, 8, 12):
                health_text = "मंगळ अशुभ भावात असल्याने दुखापत किंवा शस्त्रक्रियेची शक्यता, नियमित व्यायाम लाभदायक."
                break
            if pp.planet.value == "Moon" and pp.house in (6, 8, 12):
                health_text = "चंद्र अशुभ भावात असल्याने मानसिक ताण, निद्रानाश याबाबत जागरूकता आवश्यक."
                break
    if not health_text:
        health_text = "एकूण ग्रहस्थितीनुसार आरोग्य समाधानकारक. नियमित दिनचर्या आणि संतुलित आहाराने आरोग्य उत्तम राहील."
    parts.append(f"🏥 आरोग्य: {health_text}")

    # ── Dasha forecast ───────────────────────────────────────────────────────
    if result.dasha:
        d = result.dasha
        parts.append(
            f"⏳ दशा: सध्या {d.mahadasha_lord.name_mr} महादशेत {d.antardasha_lord.name_mr} अंतर्दशा चालू आहे "
            f"({d.antardasha_start.strftime('%Y')}–{d.antardasha_end.strftime('%Y')}). "
            f"या काळात {d.mahadasha_lord.name_mr} संबंधित क्षेत्रात विशेष प्रगतीची संधी आहे."
        )

    return "\n\n".join(parts) if parts else ""


# ---------------------------------------------------------------------------
# Main: generate_written_analysis
# ---------------------------------------------------------------------------
def generate_written_analysis(result: KundaliResult) -> WrittenAnalysis:
    """
    Generate the written analysis for a kundali using templated paragraphs.
    All text is deterministic and traceable to the engine's computed data.
    """
    rashi_text = RASHI_ANALYSIS_MR.get(result.rashi, "") if result.rashi else ""
    nak_text = NAKSHATRA_ANALYSIS_MR.get(result.nakshatra, "") if result.nakshatra else ""
    gana_text = GANA_ANALYSIS_MR.get(result.gana, "") if result.gana else ""
    nadi_text = NADI_ANALYSIS_MR.get(result.nadi, "") if result.nadi else ""

    # Lagna analysis
    lagna_text = ""
    if result.lagna and result.lagna_reliable:
        lagna_rashi_text = RASHI_ANALYSIS_MR.get(result.lagna, "")
        lagna_text = (
            f"{result.lagna.name_mr} लग्न: {lagna_rashi_text}"
        )
    elif not result.lagna_reliable:
        lagna_text = "जन्मवेळ अंदाजे असल्याने लग्नावर आधारित विश्लेषण उपलब्ध नाही."

    # Dasha analysis
    dasha_text = ""
    if result.dasha:
        d = result.dasha
        dasha_text = (
            f"सध्या {d.mahadasha_lord.name_mr} महादशा ({d.mahadasha_start.year}–{d.mahadasha_end.year}) "
            f"आणि {d.antardasha_lord.name_mr} अंतर्दशा ({d.antardasha_start.strftime('%b %Y')}–"
            f"{d.antardasha_end.strftime('%b %Y')}) चालू आहे."
        )

    # Yoga detection
    yogas = _detect_yogas(result)
    yogas_text = "\n".join(yogas) if yogas else "या कुंडलीत कोणतेही विशेष पंचमहापुरुष योग/राजयोग आढळले नाहीत."

    # Conclusion / निष्कर्ष
    conclusion_text = _generate_conclusion(result)

    return WrittenAnalysis(
        rashi_analysis_mr=rashi_text,
        nakshatra_analysis_mr=nak_text,
        lagna_analysis_mr=lagna_text,
        gana_analysis_mr=gana_text,
        nadi_analysis_mr=nadi_text,
        dasha_analysis_mr=dasha_text,
        yogas_detected_mr=yogas_text,
        conclusion_mr=conclusion_text,
    )

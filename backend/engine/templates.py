"""
engine/templates.py
Templated Marathi written analysis paragraphs.

These are data-driven, deterministic templates — NOT free-text LLM generation.
Every sentence is traceable to a specific classical rule or placement.
The template variables are filled from computed kundali data.

This keeps the product credible: users can verify claims against their chart data.
"""
from __future__ import annotations
from engine.models import KundaliResult, Rashi, Nakshatra, Gana, Nadi
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

    return WrittenAnalysis(
        rashi_analysis_mr=rashi_text,
        nakshatra_analysis_mr=nak_text,
        lagna_analysis_mr=lagna_text,
        gana_analysis_mr=gana_text,
        nadi_analysis_mr=nadi_text,
        dasha_analysis_mr=dasha_text,
    )

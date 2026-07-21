from engine.models import Varna, Rashi, Nakshatra, Nadi, Gana, Planet

def get_varna_interpretation(b_varna: Varna, g_varna: Varna, score: float) -> tuple[str, str]:
    mr = f"मुलाचा वर्ण {b_varna.name_mr} असून मुलीचा वर्ण {g_varna.name_mr} आहे. "
    en = f"The boy belongs to {b_varna.value} varna while the girl comes under {g_varna.value} varna. "
    
    if score == 1:
        mr += "वर्ण जुळणी उत्तम आहे. मुलगा कष्टाळू आणि महत्त्वाकांक्षी असेल आणि मुलगी त्याला त्याच्या ध्येयापर्यंत पोहोचण्यासाठी प्रेरणा देईल. या जोडप्यात एकमेकांना समजून घेण्याची चांगली क्षमता असेल."
        en += "This is a favorable and good combination. The boy will be ambitious and hard-working, and the girl will prove to be an inspiration in his achievements. This combination indicates a long-lasting relationship full of enjoyment and romance."
    else:
        mr += "वर्ण जुळणी कमी गुण दर्शवते. वैचारिक पातळीवर किंवा कार्यक्षेत्रात काही मतभेद असू शकतात, परंतु एकमेकांच्या विचारांचा आदर केल्यास नाते सुधारेल."
        en += "This combination is considered less favorable in terms of varana. There might be some differences in their professional or intellectual approaches. Mutual respect and understanding will be required."
    return mr, en

def get_vashya_interpretation(score: float) -> tuple[str, str]:
    if score == 2:
        mr = "वश्य जुळणी उत्तम आहे. दोघेही एकमेकांशी अत्यंत सुसंगत राहतील. त्यांच्यात चांगले आकर्षण आणि एकमेकांना समजून घेण्याची नैसर्गिक प्रवृत्ती असेल. हे एक परिपूर्ण आणि आनंदी नाते दर्शवते."
        en = "The vashya compatibility is excellent. The natives will stimulate each other's self-expression and respond positively to each other's subconscious mind. They encourage mutual responsibility, making them loyal and attractive to each other."
    elif score == 1:
        mr = "वश्य जुळणी मध्यम आहे. नात्यात बऱ्यापैकी सुसंवाद राहील, पण काही वेळा एकमेकांच्या गरजा समजून घेण्यासाठी प्रयत्न करावे लागतील."
        en = "The vashya compatibility is average. They will have a fair amount of mutual attraction, but may need to work occasionally on understanding each other's emotional needs."
    elif score == 0.5:
        mr = "वश्य जुळणी साधारण आहे. एकमेकांवर वर्चस्व गाजवण्याचा प्रयत्न होऊ शकतो. नात्यात समजूतदारपणा आवश्यक आहे."
        en = "The vashya compatibility is below average. There might be a tendency to dominate each other. Compromise is essential."
    else:
        mr = "वश्य जुळणी शून्य आहे. स्वभाव भिन्न असल्याने एकमेकांशी जुळवून घेणे कठीण जाऊ शकते."
        en = "The vashya compatibility is poor. Their inherent natures are quite different, which may lead to friction if not handled maturely."
    return mr, en

def get_tara_interpretation(score: float) -> tuple[str, str]:
    if score == 3:
        mr = "तारा जुळणी अत्यंत शुभ आहे. दोघांचेही नशीब एकमेकांना पूरक ठरेल. त्यांच्यात परस्पर प्रेम आणि आदर राहील."
        en = "The tara compatibility is highly auspicious. Their destinies will complement each other well, bringing mutual love, respect, and good fortune."
    elif score == 1.5:
        mr = "तारा जुळणी मध्यम आहे. हे नाते बऱ्यापैकी सुसंगत असेल. योग्य शिस्त आणि नैतिक मार्गदर्शनाने परस्पर आदर टिकून राहील. कठीण प्रसंगात संयमाने वागण्याचा सल्ला दिला जातो."
        en = "As far as tara compatibility is concerned, this is a fairly compatible match. There will be mutual love and respect combined with reasonable discipline. In adverse situations, one may panic while the other handles it calmly."
    else:
        mr = "तारा जुळणी कमकुवत आहे. नशिबाची साथ कमी मिळू शकते. एकमेकांना पाठिंबा देणे अत्यंत गरजेचे आहे."
        en = "The tara compatibility is weak. They may face some luck-related challenges. Mutual support and tolerance are highly recommended to provide a solid base for the relationship."
    return mr, en

def get_yoni_interpretation(score: float) -> tuple[str, str]:
    if score == 4:
        mr = "दोघांचीही योनी समान आहे. हे उत्तम शारीरिक आणि मानसिक संतुलन दर्शवते. हे एक अतिशय सुसंगत आणि आनंदी नाते असेल."
        en = "Both belong to the same yoni. This makes for excellent physical and mental bonding. They will understand each other perfectly and share a highly compatible match."
    elif score == 3:
        mr = "दोघांची योनी एकमेकांशी मैत्रीपूर्ण आहे. ते एकमेकांना चांगल्या प्रकारे समजून घेतील आणि शारीरिक आणि मानसिक स्तरावर उत्कृष्ट नाते तयार होईल."
        en = "Their yonis are highly friendly. They will work most constructively together, making an excellent bonding. Both are loving, emotional, and attractive to each other. Physically, a good compatible match."
    elif score == 2:
        mr = "योनी जुळणी मध्यम (तटस्थ) आहे. शारीरिक आणि मानसिक सुसंवाद साधारण असेल. एकमेकांच्या गरजा समजून घेण्यासाठी जाणीवपूर्वक प्रयत्न करावे लागतील."
        en = "Their yonis are neutral to each other. Physical and mental compatibility is average. They will need to make conscious efforts to understand each other's intimate and emotional needs."
    elif score == 1:
        mr = "योनी जुळणी कमकुवत आहे. स्वभाव आणि मानसिकतेमध्ये भिन्नता असू शकते."
        en = "Their yonis are mildly inimical. There may be differences in their inherent temperaments and physical needs."
    else:
        mr = "योनी जुळणी पूर्णपणे प्रतिकूल आहे. शारीरिक आणि मानसिक सुसंवादाचा अभाव असू शकतो."
        en = "Their yonis are strictly inimical. This indicates a potential lack of physical compatibility and significant differences in mentalities."
    return mr, en

def get_maitri_interpretation(score: float) -> tuple[str, str]:
    if score >= 4:
        mr = "ग्रह मैत्री उत्तम आहे. दोघांची विचारसरणी आणि स्वभाव एकमेकांशी मिळताजुळता राहील. ते एकमेकांना चांगला पाठिंबा देतील आणि त्यांचे नाते मैत्रीपूर्ण असेल."
        en = "Graha Maitri is excellent. The thought process and nature of both boy and girl will be quite similar and harmonious. They will act as great friends and support each other."
    elif score == 3:
        mr = "ग्रह मैत्री मध्यम आहे. बहुतांश वेळा विचार जुळतील, पण काही विशिष्ट बाबतीत मतभेद होऊ शकतात."
        en = "Graha Maitri is average. Their mentalities align well on most things, though they might have differences of opinion occasionally."
    elif score >= 1:
        mr = "ग्रह मैत्री साधारण आहे. दोघांच्या स्वभावात तफावत असू शकते. नाते टिकवण्यासाठी तडजोड करावी लागेल."
        en = "Graha Maitri is below average. There are noticeable differences in their psychological makeup. It might be difficult for them to completely understand each other without effort."
    else:
        mr = "ग्रह मैत्री शून्य आहे. दोघांचीही विचारसरणी पूर्णपणे वेगळी असल्यामुळे वैचारिक संघर्ष होण्याची दाट शक्यता आहे."
        en = "Graha Maitri is poor. Their thought processes are strongly opposite, which may lead to one-upmanship and frequent misunderstandings."
    return mr, en

def get_gana_interpretation(b_gana: Gana, g_gana: Gana, score: float) -> tuple[str, str]:
    mr = f"मुलाचा गण {b_gana.name_mr} असून मुलीचा गण {g_gana.name_mr} आहे. "
    en = f"The boy belongs to {b_gana.value} gan and the girl belongs to {g_gana.value} gan. "
    
    if score >= 5:
        mr += "गण जुळणी उत्तम आहे. ते एकमेकांना समजून घेतील आणि एकमेकांच्या यशात योगदान देतील. स्वभाव एकमेकांना पूरक असेल."
        en += "This is generally a good match. They will understand each other and contribute to each other's success. Their temperaments are well-aligned."
    elif score > 0:
        mr += "गण जुळणी मध्यम आहे. दोघांच्या स्वभावात काही फरक असतील, परंतु समजुतीने प्रश्न सुटतील."
        en += "This is an average match. Their temperaments have some differences, but with patience, they can handle each other well."
    else:
        mr += "गण जुळणी अत्यंत कमकुवत आहे. स्वभावातील मोठ्या तफावतीमुळे खटके उडू शकतात. एकमेकांच्या भावनांचा आदर करणे आवश्यक आहे."
        en += "This is a poor match in terms of temperament. Significant differences in their natural behavior may lead to clashes. Mutual tolerance is highly required."
    return mr, en

def get_bhakoot_interpretation(score: float) -> tuple[str, str]:
    if score == 7:
        mr = "भकूट जुळणी उत्तम आहे. ही जोडी सुख, समृद्धी आणि मजबूत नाते दर्शवते. दोघांचेही विचार व्यावहारिक असतील आणि ते एकमेकांच्या ध्येयप्राप्तीसाठी मदत करतील."
        en = "This is a good combination as far as sign compatibility is concerned. It indicates happiness, prosperity, and a strong relationship. Both will be practical, resourceful, and help in achieving each other's goals."
    else:
        mr = "भकूट दोष आहे. या जुळणीमुळे आरोग्य, आर्थिक स्थिती किंवा परस्पर सुसंवादावर परिणाम होऊ शकतो. तज्ञांचा सल्ला घ्यावा."
        en = "There is a Bhakoot Dosha. This combination may pose challenges related to health, financial stability, or emotional distance. Caution and further astrological consultation are advised."
    return mr, en

def get_nadi_interpretation(b_nadi: Nadi, g_nadi: Nadi, score: float) -> tuple[str, str]:
    if score == 8:
        mr = "नाडी जुळणी उत्तम आहे. मुलाची आणि मुलीची नाडी वेगळी असल्यामुळे त्यांच्या प्रकृती आणि आरोग्यासाठी हे अत्यंत अनुकूल आहे. यातून निरोगी आणि दीर्घायुषी संततीची शक्यता वाढते."
        en = "Nadi compatibility is excellent since they belong to different Nadis. This is highly favorable for the couple's health and ensures strong genetics and a healthy progeny."
    else:
        mr = f"दोघांचीही नाडी समान ({b_nadi.name_mr}) आहे. यामुळे नाडी दोष निर्माण होतो. आरोग्याच्या आणि संततीच्या दृष्टीने ही जुळणी अशुभ मानली जाते आणि शक्यतो टाळण्याचा सल्ला दिला जातो."
        en = f"The boy and the girl both belong to the same Nadi ({b_nadi.value}). This combination creates Nadi Dosha, which is not considered good for the longevity of the marriage or the health of progeny. This match is not preferable and should generally be avoided."
    return mr, en

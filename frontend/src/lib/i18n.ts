/**
 * lib/i18n.ts
 * All user-facing strings in Marathi (mr) and English (en).
 * Marathi is the default. English toggle uses 'en'.
 * Technical terms always show both: "नाडी (Nadi)"
 */

export type Lang = 'mr' | 'en';

export const strings = {
  // Navbar
  appName:    { mr: 'माझी कुंडली', en: 'Mazi Kundali' },
  tagline:    { mr: 'अचूक · विश्वासार्ह · मराठमोळे', en: 'Accurate · Trusted · Marathi' },

  // Landing hero
  heroTitle:  { mr: 'तुमची अचूक जन्मपत्रिका मोफत पाहा', en: 'View Your Accurate Kundali Free' },
  heroSub:    { mr: 'फक्त ५ माहिती द्या — रास, नक्षत्र, लग्न आणि बरेच काही तात्काळ मिळवा', en: 'Enter 5 details — get Rashi, Nakshatra, Lagna & more instantly' },
  ctaKundali: { mr: 'कुंडली बनवा →', en: 'Generate Kundali →' },
  ctaMatch:   { mr: 'पत्रिका जुळणी', en: 'Match Kundalis' },
  ctaBiodata: { mr: 'बायोडाटा', en: 'Biodata' },

  // Trust badges
  badge1:     { mr: 'अचूक गणना', en: 'Accurate Calc' },
  badge2:     { mr: '२ मिनिटांत', en: 'In 2 Minutes' },
  badge3:     { mr: 'मोफत पूर्वावलोकन', en: 'Free Preview' },

  // Input form
  formTitle:  { mr: 'जन्म माहिती भरा', en: 'Enter Birth Details' },
  name:       { mr: 'नाव', en: 'Name' },
  namePh:     { mr: 'पूर्ण नाव लिहा', en: 'Enter full name' },
  gender:     { mr: 'लिंग', en: 'Gender' },
  male:       { mr: 'मुलगा', en: 'Male' },
  female:     { mr: 'मुलगी', en: 'Female' },
  dob:        { mr: 'जन्म तारीख', en: 'Date of Birth' },
  time:       { mr: 'जन्म वेळ', en: 'Birth Time' },
  timeExact:  { mr: 'अचूक वेळ', en: 'Exact time' },
  timeApprox: { mr: 'वेळ अंदाजे आहे', en: 'Approximate time' },
  timeUnknown:{ mr: 'वेळ माहित नाही', en: 'Time unknown' },
  place:      { mr: 'जन्म ठिकाण', en: 'Birth Place' },
  placePh:    { mr: 'शहर किंवा गाव शोधा...', en: 'Search city or village...' },
  placeNoResult: { mr: 'ठिकाण सापडले नाही. lat/lng स्वतः टाका.', en: 'Place not found. Enter lat/lng manually.' },
  submit:     { mr: 'कुंडली बनवा', en: 'Generate Kundali' },
  submitting: { mr: 'बनवत आहोत...', en: 'Generating...' },

  // Errors
  errName:    { mr: 'नाव आवश्यक आहे', en: 'Name is required' },
  errDob:     { mr: 'जन्म तारीख आवश्यक आहे', en: 'Date of birth is required' },
  errPlace:   { mr: 'जन्म ठिकाण निवडा', en: 'Please select a birth place' },
  errGeneral: { mr: 'तांत्रिक समस्या आली. पुन्हा प्रयत्न करा.', en: 'A technical error occurred. Please try again.' },

  // Loading
  loadStep1:  { mr: 'तुमची कुंडली बनवत आहोत...', en: 'Building your kundali...' },
  loadStep2:  { mr: 'ग्रहांची स्थिती तपासत आहोत...', en: 'Computing planetary positions...' },
  loadStep3:  { mr: 'नक्षत्र आणि दशा काढत आहोत...', en: 'Calculating nakshatra & dasha...' },
  loadStep4:  { mr: 'तयार!', en: 'Ready!' },

  // Free result
  resultTitle:    { mr: 'जन्मकुंडली', en: 'Birth Kundali' },
  rashi:          { mr: 'रास (Rashi)', en: 'Rashi (Moon Sign)' },
  nakshatra:      { mr: 'नक्षत्र (Nakshatra)', en: 'Nakshatra' },
  pada:           { mr: 'पाद (Pada)', en: 'Pada' },
  lagna:          { mr: 'लग्न (Lagna)', en: 'Ascendant' },
  gana:           { mr: 'गण (Gana)', en: 'Gana' },
  nadi:           { mr: 'नाडी (Nadi)', en: 'Nadi' },
  varna:          { mr: 'वर्ण (Varna)', en: 'Varna' },
  lagnaUnreliable:{ mr: 'वेळ अंदाजे असल्याने लग्न अचूक नसू शकते', en: 'Lagna may not be accurate — approximate birth time' },

  // Paywall
  unlockTitle:    { mr: 'संपूर्ण अहवाल मिळवा', en: 'Get Full Report' },
  unlockFeature1: { mr: '✓ सर्व ९ ग्रहांचे तपशील', en: '✓ All 9 planet positions' },
  unlockFeature2: { mr: '✓ नवमांश (D9) चार्ट', en: '✓ Navamsa (D9) chart' },
  unlockFeature3: { mr: '✓ मंगळ दोष विश्लेषण', en: '✓ Mangal Dosha analysis' },
  unlockFeature4: { mr: '✓ महादशा / अंतर्दशा', en: '✓ Mahadasha / Antardasha' },
  unlockFeature5: { mr: '✓ लिखित विश्लेषण', en: '✓ Written analysis' },
  unlockFeature6: { mr: '✓ PDF + WhatsApp शेअर', en: '✓ PDF + WhatsApp share' },
  unlockCTA:      { mr: 'संपूर्ण अहवाल पाहा', en: 'View Full Report' },
  disclaimer:     { mr: 'हा अहवाल मार्गदर्शनासाठी आहे. वैयक्तिक सल्ल्यासाठी तज्ञ ज्योतिषांचा सल्ला घ्या.', en: 'This report is for guidance only. Consult an expert astrologer for personal advice.' },

  // Paid result
  downloadPDF:    { mr: 'PDF डाउनलोड करा', en: 'Download PDF' },
  shareWhatsApp:  { mr: 'WhatsApp वर पाठवा', en: 'Share on WhatsApp' },
  biodataUpsell:  { mr: 'आता याच माहितीने बायोडाटा बनवा', en: 'Create Biodata with this info' },
  biodataUpsellSub:{ mr: 'तुमची कुंडली माहिती आधीच भरलेली असेल!', en: 'Horoscope section will be pre-filled!' },
  matchUpsell:    { mr: 'जुळणी तपासा', en: 'Check Compatibility' },

  // Planet table headers
  planet:         { mr: 'ग्रह', en: 'Planet' },
  sign:           { mr: 'राशी', en: 'Sign' },
  house:          { mr: 'घर', en: 'House' },
  degree:         { mr: 'अंश', en: 'Degree' },
  nakshIn:        { mr: 'नक्षत्र', en: 'Nakshatra' },
  retro:          { mr: 'वक्री', en: 'Retro' },

  // Mangal dosha
  mangalDosha:    { mr: 'मंगळ दोष', en: 'Mangal Dosha' },
  manglikYes:     { mr: 'मंगळ दोष आहे ⚠️', en: 'Manglik ⚠️' },
  manglikNo:      { mr: 'मंगळ दोष नाही ✅', en: 'Not Manglik ✅' },
  manglikCancelled:{ mr: 'मंगळ दोष रद्द ✅', en: 'Dosha Cancelled ✅' },

  // Dasha
  currentDasha:   { mr: 'सध्याची दशा', en: 'Current Dasha' },
  mahadasha:      { mr: 'महादशा', en: 'Mahadasha' },
  antardasha:     { mr: 'अंतर्दशा', en: 'Antardasha' },

  // Nav links
  navKundali:     { mr: 'कुंडली', en: 'Kundali' },
  navMatch:       { mr: 'जुळणी', en: 'Matching' },
  navBiodata:     { mr: 'बायोडाटा', en: 'Biodata' },
  navManglik:     { mr: 'मंगळ तपासा', en: 'Manglik Check' },
} as const;

export function t(key: keyof typeof strings, lang: Lang): string {
  return strings[key][lang];
}

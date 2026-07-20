'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

type Lang = 'mr' | 'en';
type Section = 'personal' | 'family' | 'education' | 'horoscope' | 'photo';

const SECTIONS = [
  { id: 'personal' as Section, icon: '👤', mr: 'वैयक्तिक', en: 'Personal' },
  { id: 'family'   as Section, icon: '🏠', mr: 'कौटुंबिक', en: 'Family' },
  { id: 'education'as Section, icon: '🎓', mr: 'शिक्षण', en: 'Education' },
  { id: 'horoscope'as Section, icon: '🪐', mr: 'पत्रिका', en: 'Horoscope' },
  { id: 'photo'    as Section, icon: '📸', mr: 'फोटो/थीम', en: 'Photo/Theme' },
];

interface FieldProps {
  id: string;
  labelMr: string;
  labelEn: string;
  field: string;
  ph?: string;
  type?: string;
  lang: Lang;
  form: Record<string, string>;
  set: (field: string, value: string) => void;
  required?: boolean;
}

function Field({ id, labelMr, labelEn, field, ph, type = 'text', lang, form, set, required = false }: FieldProps) {
  return (
    <div style={{ marginBottom: 16 }}>
      <label className="input-label">
        {lang === 'mr' ? labelMr : labelEn} {required && <span className="required" style={{ fontSize: '0.75rem', marginLeft: 4, fontWeight: 'normal' }}>{lang === 'mr' ? '(आवश्यक)' : '(Required)'}</span>}
      </label>
      <input
        id={id}
        className="input-field"
        type={type}
        placeholder={ph || ''}
        value={form[field] || ''}
        onChange={e => {
          let val = e.target.value;
          if (type === 'tel') val = val.replace(/\D/g, ''); // Remove non-digits
          set(field, val);
        }}
        maxLength={type === 'tel' ? 10 : undefined}
      />
      {type === 'time' && (
        <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '4px', textAlign: 'right' }}>
          {lang === 'mr' ? '(उदा. दुपारी २:०० = 14:00)' : '(e.g. 2:00 PM = 14:00)'}
        </div>
      )}
    </div>
  );
}

export default function BiodataPage() {
  const router = useRouter();
  const [lang, setLang] = useState<Lang>('mr');
  const [activeSection, setActiveSection] = useState<Section>('personal');
  
  // To handle progressive saving
  const [biodataId, setBiodataId] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [kundaliIdToLink, setKundaliIdToLink] = useState('');

  const mr = (m: string, e: string) => lang === 'mr' ? m : e;

    const [form, setForm] = useState({
      // Personal
      full_name: '', dob: '', birth_time: '', birth_place: '', native_place: '', height: '', blood_group: '', complexion: '', caste: '', diet: '', spectacles: '',
      // Family
      father_name: '', father_occupation: '', mother_name: '', mother_occupation: '', brothers: '', sisters: '', mama_surname: '', mama_gotra: '', relatives_surnames: '', address: '', contact_number: '',
    // Education
    education: '', college: '', occupation: '', employer: '', annual_income: '',
    // Horoscope
    rashi_mr: '', nakshatra_mr: '', pada: '', gana_mr: '', nadi_mr: '', varna_mr: '', devak: '', gotra: '', kuldaivat: '', mangal_dosha: '',
    // Expectations
    expectations: '',
    // Theme & Photo
    photo_url: '', template_id: 'traditional',
  });

  const set = (field: string, value: string) => setForm(f => ({ ...f, [field]: value }));

  // Initialize draft biodata on load
  useEffect(() => {
    async function initBiodata() {
      if (biodataId) return;
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/biodatas`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ template_id: form.template_id })
        });
        if (res.ok) {
          const data = await res.json();
          setBiodataId(data.id);
        }
      } catch (err) {
        console.error('Failed to init biodata', err);
      }
    }
    initBiodata();
  }, [biodataId]);

  // Progressive auto-save when switching sections
  const saveSection = async () => {
    if (!biodataId) return;
    setIsSaving(true);
    try {
      const payload = {
        personal_info: { full_name: form.full_name, dob: form.dob, birth_time: form.birth_time, birth_place: form.birth_place, native_place: form.native_place, height: form.height, blood_group: form.blood_group, complexion: form.complexion, caste: form.caste, diet: form.diet, spectacles: form.spectacles },
        family_info: { father_name: form.father_name, father_occupation: form.father_occupation, mother_name: form.mother_name, mother_occupation: form.mother_occupation, brothers: form.brothers, sisters: form.sisters, mama_surname: form.mama_surname, mama_gotra: form.mama_gotra, relatives_surnames: form.relatives_surnames, address: form.address, contact_number: form.contact_number },
        education_info: { education: form.education, college: form.college, occupation: form.occupation, employer: form.employer, annual_income: form.annual_income },
        horoscope_info: { rashi_mr: form.rashi_mr, nakshatra_mr: form.nakshatra_mr, pada: form.pada, gana_mr: form.gana_mr, nadi_mr: form.nadi_mr, varna_mr: form.varna_mr, devak: form.devak, gotra: form.gotra, kuldaivat: form.kuldaivat, mangal_dosha: form.mangal_dosha },
        expectations: form.expectations,
        template_id: form.template_id,
        photo_url: form.photo_url
      };
      
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/biodatas/${biodataId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    } finally {
      setIsSaving(false);
    }
  };

  const linkKundali = async () => {
    if (!biodataId || !kundaliIdToLink) return;
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/biodatas/${biodataId}/link-kundali`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ kundali_id: kundaliIdToLink })
      });
      if (res.ok) {
        const data = await res.json();
        const horo = data.horoscope_info || {};
        setForm(f => ({
          ...f,
          rashi_mr: horo.rashi_mr || '',
          nakshatra_mr: horo.nakshatra_mr || '',
          pada: horo.pada || '',
          gana_mr: horo.gana_mr || '',
          nadi_mr: horo.nadi_mr || '',
          varna_mr: horo.varna_mr || '',
          mangal_dosha: horo.mangal_dosha === true ? 'आहे' : horo.mangal_dosha === false ? 'नाही' : '',
        }));
        alert(data.note_mr);
      } else {
        const err = await res.json();
        alert(err.detail || 'Failed to link');
      }
    } catch (e) {
      alert('Error linking kundali');
    }
  };

  const reqFields: { key: keyof typeof form; section: Section; name: string }[] = [
    { key: 'full_name', section: 'personal', name: 'पूर्ण नाव' },
    { key: 'dob', section: 'personal', name: 'जन्म तारीख' },
    { key: 'birth_time', section: 'personal', name: 'जन्म वेळ' },
    { key: 'birth_place', section: 'personal', name: 'जन्म ठिकाण' },
    { key: 'height', section: 'personal', name: 'उंची' },
    { key: 'caste', section: 'personal', name: 'जात / पोटजात' },
    { key: 'father_name', section: 'family', name: 'वडिलांचे नाव' },
    { key: 'mother_name', section: 'family', name: 'आईचे नाव' },
    { key: 'contact_number', section: 'family', name: 'संपर्क क्रमांक' },
    { key: 'education', section: 'education', name: 'शिक्षण' },
    { key: 'occupation', section: 'education', name: 'व्यवसाय / नोकरी' },
  ];

  const validateSection = (section: Section): boolean => {
    const fields = reqFields.filter(f => f.section === section);
    for (const f of fields) {
      if (!form[f.key]?.trim()) {
        alert(mr(`कृपया ${f.name} भरा. (Please fill ${f.name}.)`, `Please fill ${f.name}.`));
        return false;
      }
    }
    if (section === 'family' && form.contact_number && form.contact_number.length !== 10) {
      alert(mr('कृपया १० अंकी वैध संपर्क क्रमांक प्रविष्ट करा.', 'Please enter a valid 10-digit contact number.'));
      return false;
    }
    return true;
  };

  const handleNextSection = async (next: Section) => {
    const currentIndex = SECTIONS.findIndex(s => s.id === activeSection);
    const nextIndex = SECTIONS.findIndex(s => s.id === next);
    
    // Validate if moving forward
    if (nextIndex > currentIndex) {
      if (!validateSection(activeSection)) return;
    }
    
    await saveSection();
    setActiveSection(next);
  };

  const submitPreview = async () => {
    // Check all sections just in case they bypassed anything
    for (const s of SECTIONS) {
      if (!validateSection(s.id)) {
        setActiveSection(s.id);
        return;
      }
    }

    await saveSection();
    if (biodataId) {
      router.push(`/biodata/${biodataId}`);
    }
  };

  const renderField = (id: string, labelMr: string, labelEn: string, field: keyof typeof form, ph?: string, type = 'text', required = false) => (
    <Field id={id} labelMr={labelMr} labelEn={labelEn} field={field} ph={ph} type={type} lang={lang} form={form as any} set={set} required={required} />
  );

  return (
    <div style={{ minHeight: '100dvh', paddingBottom: 120 }}>
      <nav className="navbar">
        <div style={{ maxWidth: 680, margin: '0 auto', padding: '0 16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: 56 }}>
          <button onClick={() => router.push('/')} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', fontFamily: 'var(--font-devanagari)' }}>
            ‹ {mr('मागे', 'Back')}
          </button>
          <span style={{ fontFamily: 'var(--font-devanagari)', fontWeight: 700, color: 'var(--saffron-400)', fontSize: '1rem' }}>
            📄 {mr('मराठी बायोडाटा', 'Marathi Biodata')}
          </span>
          <div className="lang-toggle">
            <button className={`lang-btn${lang === 'mr' ? ' active' : ''}`} onClick={() => setLang('mr')}>मराठी</button>
            <button className={`lang-btn${lang === 'en' ? ' active' : ''}`} onClick={() => setLang('en')}>EN</button>
          </div>
        </div>
      </nav>

      <div className="page-container" style={{ paddingTop: 16 }}>
        {/* Section tabs */}
        <div style={{ display: 'flex', gap: 6, overflowX: 'auto', paddingBottom: 4, marginBottom: 20, scrollbarWidth: 'none' }}>
          {SECTIONS.map(s => (
            <button key={s.id} onClick={() => handleNextSection(s.id)} style={{
              flexShrink: 0,
              padding: '8px 14px',
              borderRadius: 999,
              border: `1.5px solid ${activeSection === s.id ? 'var(--saffron-500)' : 'rgba(255,255,255,0.1)'}`,
              background: activeSection === s.id ? 'rgba(240,124,0,0.15)' : 'transparent',
              color: activeSection === s.id ? 'var(--saffron-400)' : 'var(--text-secondary)',
              fontFamily: 'var(--font-devanagari)',
              fontSize: '0.82rem',
              fontWeight: activeSection === s.id ? 600 : 400,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 5,
              minHeight: 38,
              transition: 'all 0.2s',
            }}>
              {s.icon} {lang === 'mr' ? s.mr : s.en}
            </button>
          ))}
        </div>

        {/* ── Personal ─────────────────────────────────── */}
        {activeSection === 'personal' && (
          <div className="animate-fade-up">
            {renderField("bio-name", "पूर्ण नाव", "Full Name", "full_name", mr('आडनाव प्रथम', 'Surname first'), 'text', true)}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                {renderField("bio-dob", "जन्म तारीख", "Date of Birth", "dob", undefined, "date", true)}
                {renderField("bio-btime", "जन्म वेळ", "Birth Time", "birth_time", undefined, "time", true)}
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                {renderField("bio-bplace", "जन्म ठिकाण", "Place of Birth", "birth_place", mr('उदा: सातारा', 'e.g. Satara'), 'text', true)}
                {renderField("bio-nplace", "मूळ गाव", "Native Place", "native_place", mr('उदा: जाखुरी, पुणे', 'e.g. Pune'))}
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              {renderField("bio-height", "उंची", "Height", "height", "उदा: ५ फूट ६ इंच", 'text', true)}
              {renderField("bio-blood", "रक्त गट", "Blood Group", "blood_group", "A+")}
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                {renderField("bio-complexion", "त्वचा / वर्ण", "Complexion", "complexion", mr('उदा: गोरा, गव्हाळ', 'Fair, Wheatish'))}
                {renderField("bio-caste", "जात / पोटजात", "Caste / Sub-Caste", "caste", mr('९६ कुळी मराठा', '96 Kuli Maratha'), 'text', true)}
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                {renderField("bio-diet", "आहार", "Diet", "diet", mr('शाकाहारी / मांसाहारी', 'Veg / Non-Veg'))}
                {renderField("bio-specs", "चष्मा", "Spectacles", "spectacles", mr('आहे / नाही', 'Yes / No'))}
            </div>
          </div>
        )}

        {/* ── Family ───────────────────────────────────── */}
        {activeSection === 'family' && (
          <div className="animate-fade-up">
            {renderField("bio-father", "वडिलांचे नाव", "Father's Name", "father_name", undefined, 'text', true)}
            {renderField("bio-father-occ", "वडिलांचा व्यवसाय", "Father's Occupation", "father_occupation")}
            {renderField("bio-mother", "आईचे नाव", "Mother's Name", "mother_name", undefined, 'text', true)}
            {renderField("bio-mother-occ", "आईचा व्यवसाय/माहेर", "Mother's Occupation/Maiden", "mother_occupation")}
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                {renderField("bio-bros", "भाऊ", "Brothers", "brothers", mr('उदा: १ विवाहित', '1 Married'))}
                {renderField("bio-sis", "बहीण", "Sisters", "sisters", mr('उदा: १ अविवाहित', '1 Unmarried'))}
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                {renderField("bio-mama", "मामांचे नाव / आडनाव", "Maternal Uncles (Mama)", "mama_surname", mr('उदा: दाभाडे', 'Dabhade'))}
                {renderField("bio-mama-gotra", "मामांचे गोत्र / देवक", "Mama's Gotra/Devak", "mama_gotra", mr('माहित असल्यास', 'If known'))}
            </div>
            {renderField("bio-relatives", "नातेसंबंध / नातेवाईक", "Relatives' Surnames", "relatives_surnames", mr('उदा: देशमुख, मोरे', 'Deshmukh, More'))}
            {renderField("bio-address", "कायमचा पत्ता", "Permanent Address", "address")}
            {renderField("bio-contact", "संपर्क क्रमांक (फोन)", "Contact Number", "contact_number", mr('१० अंकी मोबाईल नंबर', '10 digit mobile number'), "tel", true)}
          </div>
        )}

        {/* ── Education ────────────────────────────────── */}
        {activeSection === 'education' && (
          <div className="animate-fade-up">
            {renderField("bio-edu", "शिक्षण", "Education", "education", mr('उदा: B.E. Computer', 'e.g. B.E. Computer'), 'text', true)}
            {renderField("bio-college", "महाविद्यालय", "College / University", "college")}
            {renderField("bio-occ", "व्यवसाय / नोकरी", "Occupation", "occupation", undefined, 'text', true)}
            {renderField("bio-emp", "कंपनी / नियोक्ता", "Employer / Company", "employer")}
            {renderField("bio-income", "वार्षिक उत्पन्न", "Annual Income", "annual_income", mr('उदा: ५-७ लाख', 'e.g. 5-7 LPA'))}
          </div>
        )}

        {/* ── Horoscope ────────────────────────────────── */}
        {activeSection === 'horoscope' && (
          <div className="animate-fade-up">

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              {renderField("bio-rashi", "रास", "Rashi", "rashi_mr")}
              {renderField("bio-nakshatra", "नक्षत्र व चरण", "Nakshatra & Pada", "nakshatra_mr")}
              {renderField("bio-gana", "गण", "Gana", "gana_mr")}
              {renderField("bio-nadi", "नाडी", "Nadi", "nadi_mr")}
              {renderField("bio-varna", "वर्ण", "Varna", "varna_mr")}
              {renderField("bio-devak", "देवक", "Devak", "devak")}
              {renderField("bio-gotra", "गोत्र", "Gotra", "gotra")}
              {renderField("bio-kul", "कुलदैवत", "Kuldaivat", "kuldaivat")}
            </div>
            
            {renderField("bio-mangal", "मंगळ दोष", "Mangal Dosha", "mangal_dosha", mr('आहे / नाही', 'Yes / No'))}
            {renderField("bio-expectations", "अपेक्षा", "Expectations", "expectations")}
          </div>
        )}

        {/* ── Photo & Theme ────────────────────────────────────── */}
        {activeSection === 'photo' && (
          <div className="animate-fade-up">
            
            <div style={{ marginBottom: 24 }}>
                <label className="input-label" style={{ fontSize: '1rem', color: 'var(--saffron-400)' }}>{mr('फोटो अपलोड करा', 'Upload Photo')}</label>
                
                <div style={{
                  border: `2px dashed ${form.photo_url ? 'var(--saffron-500)' : 'rgba(240,124,0,0.3)'}`,
                  borderRadius: 'var(--radius-lg)',
                  padding: '24px 16px',
                  textAlign: 'center',
                  background: 'rgba(255,255,255,0.02)',
                  position: 'relative'
                }}>
                  {form.photo_url ? (
                    <div>
                        <img src={process.env.NEXT_PUBLIC_API_URL + form.photo_url} alt="Uploaded" style={{ width: 120, height: 120, objectFit: 'cover', borderRadius: 8, marginBottom: 12, border: '2px solid var(--saffron-400)' }} />
                        <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>फोटो अपलोड झाला आहे (Uploaded)</div>
                    </div>
                  ) : (
                    <>
                        <div style={{ fontSize: '2.5rem', marginBottom: 12 }}>📸</div>
                        <div style={{ fontFamily: 'var(--font-devanagari)', fontWeight: 600, color: 'var(--text-primary)', marginBottom: 6 }}>
                            {mr('फोटो निवडण्यासाठी क्लिक करा', 'Click to choose a photo')}
                        </div>
                        <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                            {mr('JPG, PNG — जास्तीत जास्त 5 MB', 'JPG, PNG — max 5 MB')}
                        </div>
                    </>
                  )}
                  
                  <input type="file" accept="image/*" onChange={async (e) => {
                      const file = e.target.files?.[0];
                      if (!file) return;
                      const formData = new FormData();
                      formData.append("file", file);
                      
                      try {
                          const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/upload`, {
                              method: "POST",
                              body: formData
                          });
                          if (res.ok) {
                              const data = await res.json();
                              set('photo_url', data.url);
                          } else {
                              alert("फोटो अपलोड अयशस्वी (Upload failed)");
                          }
                      } catch (err) {
                          alert("Error uploading file");
                      }
                  }} style={{ opacity: 0, position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, width: '100%', height: '100%', cursor: 'pointer' }} />
                </div>
            </div>

            <div style={{ marginBottom: 32 }}>
                <label className="input-label" style={{ fontSize: '1rem', color: 'var(--saffron-400)' }}>{mr('बायोडाटा थीम निवडा', 'Select Biodata Theme')}</label>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                    {[
                        {id: 'royal_gold', mr: 'रॉयल सुवर्ण'},
                        {id: 'marathi_classic', mr: 'मराठी अभिमान'},
                        {id: 'traditional', mr: 'पारंपरिक सोनेरी'},
                        {id: 'shahi', mr: 'शाही भगवा'},
                        {id: 'ruby', mr: 'लग्न लाल'},
                        {id: 'modern', mr: 'आधुनिक निळा'},
                        {id: 'peacock', mr: 'मोरपिसी हिरवा'},
                        {id: 'floral', mr: 'नक्षीदार सोपे'},
                    ].map(theme => (
                        <div key={theme.id} onClick={() => set('template_id', theme.id)} style={{
                            border: `2px solid ${form.template_id === theme.id ? 'var(--saffron-500)' : 'rgba(255,255,255,0.1)'}`,
                            borderRadius: 'var(--radius-md)',
                            overflow: 'hidden',
                            cursor: 'pointer',
                            background: form.template_id === theme.id ? 'rgba(240,124,0,0.12)' : 'transparent',
                            transition: 'all 0.2s',
                        }}>
                            <img src={`/themes/${theme.id}.jpg`} alt={theme.mr} style={{ width: '100%', height: 'auto', display: 'block', borderBottom: '1px solid rgba(255,255,255,0.1)' }} />
                            <div style={{ padding: '8px', textAlign: 'center', fontFamily: 'var(--font-devanagari)', fontSize: '0.85rem', color: form.template_id === theme.id ? 'var(--saffron-400)' : 'var(--text-secondary)' }}>
                                {theme.mr}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
            
          </div>
        )}

        {/* ─── Sticky bottom bar ───────────────────────── */}
        <div style={{
          position: 'fixed', bottom: 0, left: 0, right: 0,
          background: 'rgba(13,27,42,0.95)',
          backdropFilter: 'blur(12px)',
          borderTop: '1px solid var(--border-subtle)',
          padding: '12px 16px',
          display: 'flex',
          gap: 10,
          zIndex: 99,
        }}>
          <div style={{ maxWidth: 680, margin: '0 auto', width: '100%', display: 'flex', gap: 10 }}>
            {activeSection !== 'photo' ? (
              <button 
                className="btn-primary" 
                style={{ flex: 1 }} 
                onClick={() => {
                  const idx = SECTIONS.findIndex(s => s.id === activeSection);
                  if (idx < SECTIONS.length - 1) handleNextSection(SECTIONS[idx + 1].id);
                }}
              >
                {mr('पुढील माहिती →', 'Next Step →')}
              </button>
            ) : (
              <button className="btn-primary" style={{ flex: 1, opacity: isSaving ? 0.7 : 1 }} onClick={submitPreview} disabled={isSaving || !biodataId}>
                {isSaving ? 'सेव्ह करत आहे...' : mr('बायोडाटा तयार करा →', 'Generate Biodata →')}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

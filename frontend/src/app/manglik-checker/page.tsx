'use client';
import { useState, useRef, useCallback, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { geocodePlace, type PlaceCandidate } from '@/lib/api';

type Lang = 'mr' | 'en';

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

interface MangalResult {
  is_manglik: boolean;
  reference_point: string;
  mars_house: number | null;
  cancellation_applied: boolean;
  cancellation_rule: string | null;
  explanation_mr: string;
  explanation_en: string;
}

const MARS_HOUSES_MR: Record<number, string> = {
  1: 'पहिल्या', 2: 'दुसऱ्या', 4: 'चौथ्या',
  7: 'सातव्या', 8: 'आठव्या', 12: 'बाराव्या',
};

export default function ManglikCheckerPage() {
  const router = useRouter();
  const [lang, setLang] = useState<Lang>('mr');
  const mr = (m: string, e: string) => lang === 'mr' ? m : e;

  const [form, setForm] = useState({
    name: '',
    gender: 'male' as 'male' | 'female',
    dob: '',
    time_of_birth: '',
    time_accuracy: 'exact' as 'exact' | 'approximate' | 'unknown',
    place_query: '',
    selected_place: null as PlaceCandidate | null,
  });

  const [suggestions, setSuggestions] = useState<PlaceCandidate[]>([]);
  const [searching, setSearching] = useState(false);
  const [showDrop, setShowDrop] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<MangalResult | null>(null);
  const [error, setError] = useState('');
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const wrapRef = useRef<HTMLDivElement>(null);

  const handlePlace = useCallback((val: string) => {
    setForm(f => ({ ...f, place_query: val, selected_place: null }));
    if (timerRef.current) clearTimeout(timerRef.current);
    if (val.trim().length < 2) { setSuggestions([]); setShowDrop(false); return; }
    timerRef.current = setTimeout(async () => {
      setSearching(true);
      try { const res = await geocodePlace(val); setSuggestions(res); setShowDrop(res.length > 0); }
      catch { setSuggestions([]); }
      finally { setSearching(false); }
    }, 150);
  }, []);

  useEffect(() => {
    const h = (e: MouseEvent) => {
      if (wrapRef.current && !wrapRef.current.contains(e.target as Node)) setShowDrop(false);
    };
    document.addEventListener('mousedown', h);
    return () => document.removeEventListener('mousedown', h);
  }, []);

  const handleSubmit = async () => {
    setError('');
    if (!form.name.trim()) { setError(mr('नाव आवश्यक आहे', 'Name is required')); return; }
    if (!form.dob)          { setError(mr('जन्म तारीख आवश्यक आहे', 'Date of birth required')); return; }
    if (!form.selected_place) { setError(mr('जन्म ठिकाण निवडा', 'Select birth place')); return; }
    if (form.time_accuracy !== 'unknown' && !form.time_of_birth) {
      setError(mr('मंगळ दोष अचूक काढण्यासाठी जन्म वेळ आवश्यक आहे', 'Birth time needed for accurate Mangal Dosha')); return;
    }

    setLoading(true);
    setResult(null);
    try {
      // Use the engine endpoint for a full kundali compute, then extract mangal dosha
      const resp = await fetch(`${API_URL}/api/v1/engine/kundali`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: form.name.trim(),
          gender: form.gender,
          dob: form.dob,
          time_of_birth: form.time_accuracy === 'unknown' ? null : (form.time_of_birth || null),
          time_accuracy: form.time_accuracy,
          place_query: form.place_query,
          latitude: form.selected_place.latitude,
          longitude: form.selected_place.longitude,
          tz_iana: form.selected_place.tz_iana,
          rahu_mode: 'true_node',
        }),
      });
      if (!resp.ok) throw new Error(await resp.text());
      const data = await resp.json();
      if (data.mangal_dosha) {
        setResult(data.mangal_dosha);
      } else {
        setError(mr('मंगळ दोष काढता आला नाही. कृपया जन्म वेळ द्या.', 'Could not compute Mangal Dosha. Please provide birth time.'));
      }
    } catch (e) {
      setError(mr('तांत्रिक समस्या आली. पुन्हा प्रयत्न करा.', 'Technical error. Please try again.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100dvh', paddingBottom: 60 }}>
      {/* Navbar */}
      <nav className="navbar">
        <div style={{ maxWidth: 680, margin: '0 auto', padding: '0 16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: 56 }}>
          <button onClick={() => router.push('/')} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', fontFamily: 'var(--font-devanagari)' }}>
            ‹ {mr('मुख्य', 'Home')}
          </button>
          <span style={{ fontFamily: 'var(--font-devanagari)', fontWeight: 700, color: 'var(--saffron-400)' }}>
            🔴 {mr('मंगळ दोष तपासा', 'Mangal Dosha Checker')}
          </span>
          <div className="lang-toggle">
            <button className={`lang-btn${lang === 'mr' ? ' active' : ''}`} onClick={() => setLang('mr')}>मराठी</button>
            <button className={`lang-btn${lang === 'en' ? ' active' : ''}`} onClick={() => setLang('en')}>EN</button>
          </div>
        </div>
      </nav>

      <div className="page-container" style={{ paddingTop: 24 }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: 28 }}>
          <h1 style={{ fontFamily: 'var(--font-devanagari)', fontSize: 'clamp(1.3rem,4vw,1.8rem)', fontWeight: 800, color: 'var(--text-primary)', marginBottom: 8 }}>
            {mr('मोफत मंगळ दोष तपासा', 'Free Mangal Dosha Check')}
          </h1>
          <p style={{ fontFamily: 'var(--font-devanagari)', color: 'var(--text-secondary)', fontSize: '0.9rem', maxWidth: 480, margin: '0 auto' }}>
            {mr(
              'जन्म माहिती द्या आणि लगेच जाणून घ्या — मंगळ दोष आहे का, कोणत्या घरात आहे, आणि रद्दीकरण नियम लागतात का.',
              'Enter birth details and instantly find out — is Mangal Dosha present, which house, and if any cancellation rules apply.'
            )}
          </p>
          <div style={{ display: 'flex', gap: 8, justifyContent: 'center', marginTop: 12, flexWrap: 'wrap' }}>
            <span className="chip chip-green">{mr('✓ मोफत', '✓ Free')}</span>
            <span className="chip chip-saffron">{mr('⚡ तात्काळ', '⚡ Instant')}</span>
            <span className="chip chip-gold">{mr('🔍 रद्दीकरण तपासतो', '🔍 Checks Cancellations')}</span>
          </div>
        </div>

        {/* Form */}
        <div className="card animate-fade-up" style={{ padding: 20, marginBottom: 16 }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 14 }}>
            <div>
              <label className="input-label">{mr('नाव', 'Name')} <span className="required" style={{ fontSize: '0.75rem', marginLeft: 4, fontWeight: 'normal' }}>{mr('(आवश्यक)', '(Required)')}</span></label>
              <input className="input-field" type="text" placeholder={mr('पूर्ण नाव', 'Full name')}
                value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} />
            </div>
            <div>
              <label className="input-label">{mr('लिंग', 'Gender')}</label>
              <div style={{ display: 'flex', gap: 6 }}>
                {(['male', 'female'] as const).map(g => (
                  <button key={g} onClick={() => setForm(f => ({ ...f, gender: g }))} style={{
                    flex: 1, padding: '10px 4px',
                    border: `1.5px solid ${form.gender === g ? 'var(--saffron-500)' : 'rgba(255,255,255,0.1)'}`,
                    borderRadius: 'var(--radius-md)',
                    background: form.gender === g ? 'rgba(240,124,0,0.12)' : 'transparent',
                    color: form.gender === g ? 'var(--saffron-400)' : 'var(--text-secondary)',
                    fontFamily: 'var(--font-devanagari)', fontSize: '0.82rem', cursor: 'pointer', minHeight: 44,
                  }}>
                    {g === 'male' ? mr('♂ मुलगा', '♂ Male') : mr('♀ मुलगी', '♀ Female')}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div style={{ marginBottom: 14 }}>
            <label className="input-label">{mr('जन्म तारीख', 'Date of Birth')} <span className="required" style={{ fontSize: '0.75rem', marginLeft: 4, fontWeight: 'normal' }}>{mr('(आवश्यक)', '(Required)')}</span></label>
            <input className="input-field" type="date" max={new Date().toISOString().split('T')[0]} min="1900-01-01"
              value={form.dob} onChange={e => setForm(f => ({ ...f, dob: e.target.value }))} style={{ colorScheme: 'dark' }} />
          </div>

          <div style={{ marginBottom: 14 }}>
            <label className="input-label">{mr('जन्म वेळ', 'Birth Time')}</label>
            <div style={{ display: 'flex', gap: 6, marginBottom: 8 }}>
              {([['exact', mr('अचूक', 'Exact')], ['approximate', mr('अंदाजे', 'Approx')], ['unknown', mr('माहित नाही', 'Unknown')]] as [string, string][]).map(([v, l]) => (
                <button key={v} onClick={() => setForm(f => ({ ...f, time_accuracy: v as typeof form.time_accuracy }))} style={{
                  flex: 1, padding: '8px 4px',
                  border: `1.5px solid ${form.time_accuracy === v ? 'var(--saffron-500)' : 'rgba(255,255,255,0.1)'}`,
                  borderRadius: 'var(--radius-md)',
                  background: form.time_accuracy === v ? 'rgba(240,124,0,0.12)' : 'transparent',
                  color: form.time_accuracy === v ? 'var(--saffron-400)' : 'var(--text-secondary)',
                  fontFamily: 'var(--font-devanagari)', fontSize: '0.75rem', cursor: 'pointer', minHeight: 40,
                }}>{l}</button>
              ))}
            </div>
            {form.time_accuracy !== 'unknown' && (
              <input className="input-field" type="time" value={form.time_of_birth}
                onChange={e => setForm(f => ({ ...f, time_of_birth: e.target.value }))} style={{ colorScheme: 'dark' }} />
            )}
            {form.time_accuracy === 'unknown' && (
              <div style={{ padding: '8px 12px', background: 'rgba(245,158,11,0.08)', borderRadius: 8, fontFamily: 'var(--font-devanagari)', fontSize: '0.78rem', color: 'var(--warning)', marginTop: 4 }}>
                ⚠️ {mr('वेळाशिवाय लग्नापासून मंगळ दोष काढता येणार नाही. रासीपासून तपासला जाईल.', 'Without time, Lagna-based check not possible. Rashi-based check will be done.')}
              </div>
            )}
          </div>

          <div style={{ position: 'relative' }} ref={wrapRef}>
            <label className="input-label">{mr('जन्म ठिकाण', 'Birth Place')} <span className="required" style={{ fontSize: '0.75rem', marginLeft: 4, fontWeight: 'normal' }}>{mr('(आवश्यक)', '(Required)')}</span></label>
            <div style={{ position: 'relative' }}>
              <input className="input-field" type="text" placeholder={mr('शहर किंवा गाव...', 'City or village...')}
                value={form.place_query} autoComplete="off"
                onChange={e => handlePlace(e.target.value)}
                onFocus={() => suggestions.length > 0 && setShowDrop(true)} />
              {searching && <span style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', fontSize: '0.75rem', color: 'var(--text-muted)' }}>...</span>}
              {form.selected_place && <span style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--success)' }}>✓</span>}
            </div>
            {showDrop && suggestions.length > 0 && (
              <div className="autocomplete-dropdown">
                {suggestions.map((p, i) => (
                  <div key={i} className="autocomplete-item"
                    onMouseDown={e => { e.preventDefault(); setForm(f => ({ ...f, place_query: p.display_name, selected_place: p })); setShowDrop(false); }}>
                    <div style={{ fontWeight: 500, color: 'var(--text-primary)', fontSize: '0.88rem' }}>{p.display_name.split(',')[0]}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{p.display_name.split(',').slice(1).join(',').trim()}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {error && (
          <div style={{ padding: '12px 16px', background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: 'var(--radius-md)', marginBottom: 14, fontFamily: 'var(--font-devanagari)', fontSize: '0.88rem', color: '#f87171' }}>
            ⚠️ {error}
          </div>
        )}

        <button className="btn-primary" style={{ width: '100%', marginBottom: 20 }}
          onClick={handleSubmit} disabled={loading}>
          {loading ? mr('तपासत आहोत...', 'Checking...') : mr('🔴 मंगळ दोष तपासा', '🔴 Check Mangal Dosha')}
        </button>

        {/* Result */}
        {result && (
          <div className={`card animate-fade-up`} style={{ padding: '20px', marginBottom: 20, borderColor: result.is_manglik && !result.cancellation_applied ? 'rgba(239,68,68,0.4)' : 'rgba(34,197,94,0.4)', background: result.is_manglik && !result.cancellation_applied ? 'rgba(239,68,68,0.04)' : 'rgba(34,197,94,0.04)' }}>
            <div style={{ textAlign: 'center', marginBottom: 16 }}>
              <div style={{ fontSize: '2.5rem', marginBottom: 8 }}>
                {result.is_manglik && !result.cancellation_applied ? '⚠️' : '✅'}
              </div>
              <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '1.3rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: 4 }}>
                {result.is_manglik && !result.cancellation_applied
                  ? mr('मंगळ दोष आहे', 'Mangal Dosha Present')
                  : result.cancellation_applied
                    ? mr('मंगळ दोष रद्द', 'Mangal Dosha Cancelled')
                    : mr('मंगळ दोष नाही', 'No Mangal Dosha')}
              </div>
              {result.mars_house && (
                <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
                  {mr(
                    `मंगळ ${MARS_HOUSES_MR[result.mars_house] ?? result.mars_house + 'व्या'} घरात आहे`,
                    `Mars is in house ${result.mars_house}`
                  )}
                </div>
              )}
            </div>

            <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: 12 }}>
              {lang === 'mr' ? result.explanation_mr : result.explanation_en}
            </div>

            {result.cancellation_applied && result.cancellation_rule && (
              <div style={{ padding: '10px 14px', background: 'rgba(34,197,94,0.08)', border: '1px solid rgba(34,197,94,0.2)', borderRadius: 10, fontFamily: 'var(--font-devanagari)', fontSize: '0.82rem', color: '#4ade80' }}>
                📌 {mr('रद्दीकरण नियम:', 'Cancellation rule:')} {result.cancellation_rule}
              </div>
            )}

            <div className="divider" style={{ margin: '16px 0' }} />

            {/* Reference point */}
            <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.75rem', color: 'var(--text-muted)', textAlign: 'center', marginBottom: 12 }}>
              {mr(`तपासणी: ${result.reference_point} पासून`, `Checked from: ${result.reference_point}`)}
            </div>

            {/* CTA to full kundali */}
            <div style={{ padding: '14px 16px', background: 'rgba(240,124,0,0.08)', border: '1px solid rgba(240,124,0,0.2)', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
              <div style={{ fontFamily: 'var(--font-devanagari)', fontWeight: 600, color: 'var(--saffron-400)', marginBottom: 6 }}>
                {mr('संपूर्ण कुंडली पाहायची आहे?', 'Want your full kundali?')}
              </div>
              <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.82rem', color: 'var(--text-secondary)', marginBottom: 12 }}>
                {mr('ग्रह स्थिती, दशा, लग्न, नवमांश — सगळे एकत्र', 'Planet positions, Dasha, Lagna, Navamsa — all together')}
              </div>
              <button className="btn-primary" style={{ minWidth: 200 }}
                onClick={() => router.push('/kundali/new')}>
                🪐 {mr('कुंडली बनवा', 'Generate Full Kundali')}
              </button>
            </div>
          </div>
        )}

        {/* SEO content block */}
        <div style={{ marginTop: 32 }}>
          <div className="divider-gold" />
          <h2 style={{ fontFamily: 'var(--font-devanagari)', fontSize: '1rem', fontWeight: 700, color: 'var(--text-secondary)', marginBottom: 12 }}>
            {mr('मंगळ दोष म्हणजे काय?', 'What is Mangal Dosha?')}
          </h2>
          <p style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.7, marginBottom: 10 }}>
            {mr(
              'मंगळ दोष (मांगलिक दोष) तेव्हा होतो जेव्हा जन्म कुंडलीत मंगळ ग्रह पहिल्या, दुसऱ्या, चौथ्या, सातव्या, आठव्या किंवा बाराव्या घरात असतो. विवाह संस्थेत याचा प्रभाव विशेष मानला जातो.',
              'Mangal Dosha (Manglik Dosha) occurs when Mars is placed in the 1st, 2nd, 4th, 7th, 8th, or 12th house of the birth chart. It is considered significant in the context of marriage compatibility.'
            )}
          </p>
          <p style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.7 }}>
            {mr(
              'महत्त्वाचे: अनेक प्रकरणांमध्ये मंगळ दोष रद्द होऊ शकतो — उदाहरणार्थ, दोन्ही जोडीदार मांगलिक असल्यास, किंवा मंगळ उच्चीचा असल्यास. आमचा कॅल्क्युलेटर हे सर्व नियम तपासतो.',
              'Important: In many cases, Mangal Dosha can be cancelled — for example, if both partners are Manglik, or if Mars is exalted. Our calculator checks all these rules.'
            )}
          </p>
        </div>

        <p className="disclaimer" style={{ marginTop: 20 }}>
          {mr('हे परिणाम मार्गदर्शनासाठी आहेत. वैयक्तिक सल्ल्यासाठी तज्ञ ज्योतिषांचा सल्ला घ्या.', 'Results are for guidance only. Consult an expert astrologer for personal decisions.')}
        </p>
      </div>
    </div>
  );
}

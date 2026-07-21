'use client';
import { useState, useRef, useCallback, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { geocodePlace, createKundali, type PlaceCandidate } from '@/lib/api';

type Lang = 'mr' | 'en';
type TimeAccuracy = 'exact' | 'approximate' | 'unknown';
type Step = 1 | 2 | 3;

interface FormData {
  name: string;
  gender: 'male' | 'female' | '';
  dob: string;
  time_of_birth: string;
  time_accuracy: TimeAccuracy;
  place_query: string;
  selected_place: PlaceCandidate | null;
}

const LOAD_STEPS_MR = [
  'जन्म माहिती तपासत आहोत...',
  'ग्रहांची स्थिती मोजत आहोत...',
  'नक्षत्र आणि दशा काढत आहोत...',
  'तुमची कुंडली तयार!',
];

export default function NewKundaliPage() {
  const router = useRouter();
  const [lang, setLang] = useState<Lang>('mr');
  const [step, setStep] = useState<Step>(1);
  const [loading, setLoading] = useState(false);
  const [loadStep, setLoadStep] = useState(0);
  const [error, setError] = useState('');

  const [form, setForm] = useState<FormData>({
    name: '',
    gender: '',
    dob: '',
    time_of_birth: '',
    time_accuracy: 'exact',
    place_query: '',
    selected_place: null,
  });

  const [placeSuggestions, setPlaceSuggestions] = useState<PlaceCandidate[]>([]);
  const [placeSearching, setPlaceSearching] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<Partial<Record<keyof FormData, string>>>({});
  const searchTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);
  const placeInputRef = useRef<HTMLInputElement>(null);

  // Language toggle
  const mr = (marathi: string, english: string) => lang === 'mr' ? marathi : english;

  // Place autocomplete with debounce
  const handlePlaceInput = useCallback((value: string) => {
    setForm(f => ({ ...f, place_query: value, selected_place: null }));
    if (searchTimeout.current) clearTimeout(searchTimeout.current);
    if (value.trim().length < 2) { setPlaceSuggestions([]); setShowDropdown(false); return; }
    searchTimeout.current = setTimeout(async () => {
      setPlaceSearching(true);
      try {
        const results = await geocodePlace(value);
        setPlaceSuggestions(results);
        setShowDropdown(results.length > 0);
      } catch {
        setPlaceSuggestions([]);
      } finally {
        setPlaceSearching(false);
      }
    }, 150);
  }, []);

  const selectPlace = (place: PlaceCandidate) => {
    setForm(f => ({ ...f, place_query: place.display_name, selected_place: place }));
    setShowDropdown(false);
    setFieldErrors(e => ({ ...e, place_query: undefined }));
  };

  // Field updater
  const set = (field: keyof FormData, value: string) => {
    setForm(f => ({ ...f, [field]: value }));
    setFieldErrors(e => ({ ...e, [field]: undefined }));
    setError('');
  };

  // Validate current step
  const validateStep = (s: Step): boolean => {
    const errs: Partial<Record<keyof FormData, string>> = {};
    if (s === 1) {
      const name = form.name.trim();
      if (!name) errs.name = mr('नाव आवश्यक आहे', 'Name is required');
      else if (name.length < 2) errs.name = mr('नाव किमान २ अक्षरांचे असावे', 'Name must be at least 2 characters');
      else if (/[0-9!@#$%^&*()_+=\[\]{};':"\\|,.<>\/?]+/.test(name)) errs.name = mr('नावात फक्त अक्षरे असावीत', 'Name can only contain letters');

      if (!form.gender)      errs.gender = mr('लिंग निवडा', 'Please select gender');
    }
    if (s === 2) {
      if (!form.dob) {
        errs.dob = mr('जन्म तारीख आवश्यक आहे', 'Date of birth is required');
      } else {
        const selectedDate = new Date(form.dob);
        const today = new Date();
        if (selectedDate > today) {
          errs.dob = mr('भविष्यातील तारीख निवडू शकत नाही', 'Future date is not allowed');
        }
      }
      
      if (form.time_accuracy !== 'unknown' && !form.time_of_birth) {
        errs.time_of_birth = mr('जन्म वेळ आवश्यक आहे', 'Birth time is required');
      }
    }
    if (s === 3) {
      if (!form.selected_place) errs.place_query = mr('जन्म ठिकाण निवडा', 'Please select a birth place');
    }
    setFieldErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const nextStep = () => {
    if (!validateStep(step)) return;
    setStep(s => Math.min(3, s + 1) as Step);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const prevStep = () => {
    setStep(s => Math.max(1, s - 1) as Step);
    setError('');
  };

  const handleSubmit = async () => {
    if (!validateStep(3)) return;
    if (!form.selected_place) return;

    setLoading(true);
    setLoadStep(0);

    // Animate load steps
    const intervals = [600, 1200, 1800];
    intervals.forEach((delay, i) => {
      setTimeout(() => setLoadStep(i + 1), delay);
    });

    try {
      const result = await createKundali({
        name: form.name.trim(),
        gender: form.gender as 'male' | 'female',
        dob: form.dob,
        time_of_birth: form.time_accuracy === 'unknown' ? null : (form.time_of_birth || null),
        time_accuracy: form.time_accuracy,
        place_query: form.place_query,
        latitude: form.selected_place.latitude,
        longitude: form.selected_place.longitude,
        tz_iana: form.selected_place.tz_iana,
      });
      router.push(`/kundali/${result.id}`);
    } catch (e: unknown) {
      setLoading(false);
      setError(e instanceof Error ? e.message : mr('तांत्रिक समस्या आली. पुन्हा प्रयत्न करा.', 'A technical error occurred. Please try again.'));
    }
  };

  // Close dropdown on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (placeInputRef.current && !placeInputRef.current.contains(e.target as Node)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  // ─── Loading screen ───────────────────────────────────
  if (loading) {
    return (
      <div style={{ minHeight: '100dvh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: 24, textAlign: 'center' }}>
        <div style={{ fontSize: '3rem', marginBottom: 20, animation: 'spin-slow 4s linear infinite' }}>🪐</div>
        <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '1.2rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: 8, animation: 'pulse-glow 1.5s ease infinite' }}>
          {LOAD_STEPS_MR[loadStep] ?? LOAD_STEPS_MR[3]}
        </div>
        <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: 8, fontFamily: 'var(--font-devanagari)' }}>
          {mr('कृपया थांबा...', 'Please wait...')}
        </div>
        <div style={{ marginTop: 32, width: 220, height: 4, background: 'rgba(255,255,255,0.08)', borderRadius: 999, overflow: 'hidden' }}>
          <div style={{ height: '100%', background: 'linear-gradient(90deg, var(--saffron-500), var(--gold-400))', borderRadius: 999, width: `${((loadStep + 1) / 4) * 100}%`, transition: 'width 0.6s ease' }} />
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100dvh', paddingBottom: 48 }}>
      {/* Navbar */}
      <nav className="navbar">
        <div style={{ maxWidth: 680, margin: '0 auto', padding: '0 16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: 56 }}>
          <button onClick={() => router.back()} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: 6, fontFamily: 'var(--font-devanagari)' }}>
            ‹ {mr('मागे', 'Back')}
          </button>
          <span style={{ fontFamily: 'var(--font-devanagari)', fontWeight: 700, color: 'var(--saffron-400)', fontSize: '1rem' }}>
            🪐 {mr('कुंडली बनवा', 'New Kundali')}
          </span>
          <div className="lang-toggle">
            <button className={`lang-btn${lang === 'mr' ? ' active' : ''}`} onClick={() => setLang('mr')}>मराठी</button>
            <button className={`lang-btn${lang === 'en' ? ' active' : ''}`} onClick={() => setLang('en')}>EN</button>
          </div>
        </div>
      </nav>

      <div className="page-container" style={{ paddingTop: 24 }}>
        {/* Step progress bar */}
        <div className="step-bar">
          {[1, 2, 3].map(s => (
            <div key={s} className={`step-segment${step > s ? ' done' : step === s ? ' active' : ''}`} />
          ))}
        </div>

        {/* Step labels */}
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 28, fontFamily: 'var(--font-devanagari)', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
          <span style={{ color: step === 1 ? 'var(--saffron-400)' : undefined }}>{mr('नाव व लिंग', 'Name & Gender')}</span>
          <span style={{ color: step === 2 ? 'var(--saffron-400)' : undefined }}>{mr('जन्म वेळ', 'Birth Time')}</span>
          <span style={{ color: step === 3 ? 'var(--saffron-400)' : undefined }}>{mr('जन्म ठिकाण', 'Birth Place')}</span>
        </div>

        {/* ─── STEP 1: Name & Gender ─────────────────────── */}
        {step === 1 && (
          <div className="animate-fade-up">
            <h1 style={{ fontFamily: 'var(--font-devanagari)', fontSize: '1.4rem', fontWeight: 800, marginBottom: 6, color: 'var(--text-primary)' }}>
              {mr('नाव सांगा', 'Your Name')}
            </h1>
            <p style={{ fontFamily: 'var(--font-devanagari)', color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: 28 }}>
              {mr('ज्याची कुंडली हवी त्याचे नाव व लिंग', 'Name and gender of the person')}
            </p>

            <div style={{ marginBottom: 20 }}>
              <label className="input-label">{mr('नाव', 'Full Name')} <span className="required" style={{ fontSize: '0.75rem', marginLeft: 4, fontWeight: 'normal' }}>{mr('(आवश्यक)', '(Required)')}</span></label>
              <input
                id="kundali-name"
                className={`input-field${fieldErrors.name ? ' error' : ''}`}
                type="text"
                placeholder={mr('पूर्ण नाव लिहा', 'Enter full name')}
                value={form.name}
                onChange={e => set('name', e.target.value)}
                autoFocus
                autoComplete="given-name"
              />
              {fieldErrors.name && <div className="input-error">{fieldErrors.name}</div>}
            </div>

            <div style={{ marginBottom: 28 }}>
              <label className="input-label">{mr('लिंग', 'Gender')} <span className="required" style={{ fontSize: '0.75rem', marginLeft: 4, fontWeight: 'normal' }}>{mr('(आवश्यक)', '(Required)')}</span></label>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                {(['male', 'female'] as const).map(g => (
                  <button
                    id={`gender-${g}`}
                    key={g}
                    onClick={() => set('gender', g)}
                    style={{
                      padding: '16px',
                      border: `2px solid ${form.gender === g ? 'var(--saffron-500)' : 'rgba(255,255,255,0.1)'}`,
                      borderRadius: 'var(--radius-md)',
                      background: form.gender === g ? 'rgba(240,124,0,0.12)' : 'rgba(255,255,255,0.03)',
                      color: form.gender === g ? 'var(--saffron-400)' : 'var(--text-secondary)',
                      fontFamily: 'var(--font-devanagari)',
                      fontSize: '1rem',
                      fontWeight: 600,
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      minHeight: 56,
                    }}
                  >
                    {g === 'male' ? `♂ ${mr('मुलगा', 'Male')}` : `♀ ${mr('मुलगी', 'Female')}`}
                  </button>
                ))}
              </div>
              {fieldErrors.gender && <div className="input-error">{fieldErrors.gender}</div>}
            </div>

            <button className="btn-primary" style={{ width: '100%' }} onClick={nextStep}>
              {mr('पुढे जा →', 'Next →')}
            </button>
          </div>
        )}

        {/* ─── STEP 2: Date & Time ──────────────────────── */}
        {step === 2 && (
          <div className="animate-fade-up">
            <h1 style={{ fontFamily: 'var(--font-devanagari)', fontSize: '1.4rem', fontWeight: 800, marginBottom: 6, color: 'var(--text-primary)' }}>
              {mr('जन्म तारीख व वेळ', 'Date & Time of Birth')}
            </h1>
            <p style={{ fontFamily: 'var(--font-devanagari)', color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: 28 }}>
              {mr(`${form.name || 'जातका'}चे जन्म तपशील`, `Birth details for ${form.name || 'the person'}`)}
            </p>

            <div style={{ marginBottom: 20 }}>
              <label className="input-label">{mr('जन्म तारीख', 'Date of Birth')} <span className="required" style={{ fontSize: '0.75rem', marginLeft: 4, fontWeight: 'normal' }}>{mr('(आवश्यक)', '(Required)')}</span></label>
              <input
                id="dob"
                className={`input-field${fieldErrors.dob ? ' error' : ''}`}
                type="date"
                max={new Date().toISOString().split('T')[0]}
                min="1900-01-01"
                value={form.dob}
                onChange={e => set('dob', e.target.value)}
                style={{ colorScheme: 'dark' }}
              />
              {fieldErrors.dob && <div className="input-error">{fieldErrors.dob}</div>}
            </div>

            {/* Time accuracy selector */}
            <div style={{ marginBottom: 16 }}>
              <label className="input-label">{mr('जन्म वेळ', 'Birth Time')} <span className="required" style={{ fontSize: '0.75rem', marginLeft: 4, fontWeight: 'normal' }}>{mr('(आवश्यक)', '(Required)')}</span></label>
              <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
                {([
                  ['exact',       mr('अचूक', 'Exact')],
                  ['approximate', mr('अंदाजे', 'Approx')],
                  ['unknown',     mr('माहित नाही', 'Unknown')],
                ] as [TimeAccuracy, string][]).map(([val, label]) => (
                  <button
                    id={`time-accuracy-${val}`}
                    key={val}
                    onClick={() => set('time_accuracy', val)}
                    style={{
                      flex: 1,
                      padding: '10px 6px',
                      border: `1.5px solid ${form.time_accuracy === val ? 'var(--saffron-500)' : 'rgba(255,255,255,0.1)'}`,
                      borderRadius: 'var(--radius-md)',
                      background: form.time_accuracy === val ? 'rgba(240,124,0,0.12)' : 'rgba(255,255,255,0.03)',
                      color: form.time_accuracy === val ? 'var(--saffron-400)' : 'var(--text-secondary)',
                      fontFamily: 'var(--font-devanagari)',
                      fontSize: '0.82rem',
                      fontWeight: 500,
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      minHeight: 44,
                    }}
                  >
                    {label}
                  </button>
                ))}
              </div>

              {form.time_accuracy !== 'unknown' && (
                <div className="animate-fade-in" style={{ marginTop: 8 }}>
                  <input
                    id="tob"
                    className={`input-field${fieldErrors.time_of_birth ? ' error' : ''}`}
                    type="time"
                    value={form.time_of_birth}
                    onChange={e => set('time_of_birth', e.target.value)}
                    style={{ colorScheme: 'dark' }}
                  />
                  {fieldErrors.time_of_birth && <div className="input-error" style={{ marginTop: 4 }}>{fieldErrors.time_of_birth}</div>}
                  <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px', textAlign: 'right' }}>
                    {mr('(उदा. दुपारी २:०० वाजता = 14:00)', '(e.g. 2:00 PM = 14:00)')}
                  </div>
                </div>
              )}
              
              {form.time_accuracy === 'unknown' && (
                <div style={{ padding: '12px 14px', background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.2)', borderRadius: 'var(--radius-md)', fontFamily: 'var(--font-devanagari)', fontSize: '0.82rem', color: 'var(--warning)' }}>
                  ⚠️ {mr('वेळ माहित नसल्यास लग्न अचूक मिळणार नाही. फक्त रास-नक्षत्र मिळेल.', 'Without birth time, Lagna cannot be computed. Only Rashi & Nakshatra will be available.')}
                </div>
              )}

              {form.time_accuracy === 'approximate' && (
                <div style={{ marginTop: 8, fontFamily: 'var(--font-devanagari)', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                  {mr('अंदाजे वेळ — लग्न अचूक नसेल, पण गणना होईल.', 'Approximate time — Lagna noted as unreliable.')}
                </div>
              )}
            </div>

            <div style={{ display: 'flex', gap: 10, marginTop: 28 }}>
              <button className="btn-ghost" style={{ flex: '0 0 auto', minWidth: 90 }} onClick={prevStep}>
                {mr('‹ मागे', '‹ Back')}
              </button>
              <button className="btn-primary" style={{ flex: 1 }} onClick={nextStep}>
                {mr('पुढे जा →', 'Next →')}
              </button>
            </div>
          </div>
        )}

        {/* ─── STEP 3: Place ────────────────────────────── */}
        {step === 3 && (
          <div className="animate-fade-up">
            <h1 style={{ fontFamily: 'var(--font-devanagari)', fontSize: '1.4rem', fontWeight: 800, marginBottom: 6, color: 'var(--text-primary)' }}>
              {mr('जन्म ठिकाण', 'Birth Place')}
            </h1>
            <p style={{ fontFamily: 'var(--font-devanagari)', color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: 28 }}>
              {mr('जन्म झालेले शहर किंवा गाव शोधा', 'Search for the city or village of birth')}
            </p>

            <div style={{ position: 'relative', marginBottom: 20 }} ref={placeInputRef as React.RefObject<HTMLDivElement>}>
              <label className="input-label">{mr('जन्म ठिकाण', 'Birth Place')} <span className="required" style={{ fontSize: '0.75rem', marginLeft: 4, fontWeight: 'normal' }}>{mr('(आवश्यक)', '(Required)')}</span></label>
              <div style={{ position: 'relative' }}>
                <input
                  id="birth-place"
                  className={`input-field${fieldErrors.place_query ? ' error' : ''}`}
                  type="text"
                  placeholder={mr('शहर किंवा गाव शोधा...', 'Search city or village...')}
                  value={form.place_query}
                  onChange={e => handlePlaceInput(e.target.value)}
                  onFocus={() => placeSuggestions.length > 0 && setShowDropdown(true)}
                  autoComplete="off"
                />
                {placeSearching && (
                  <span style={{ position: 'absolute', right: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)', fontSize: '0.8rem', fontFamily: 'var(--font-devanagari)' }}>
                    {mr('शोधत...', 'Searching...')}
                  </span>
                )}
                {form.selected_place && (
                  <span style={{ position: 'absolute', right: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--success)', fontSize: '1rem' }}>✓</span>
                )}
              </div>
              {fieldErrors.place_query && <div className="input-error">{fieldErrors.place_query}</div>}

              {/* Dropdown */}
              {showDropdown && placeSuggestions.length > 0 && (
                <div className="autocomplete-dropdown">
                  {placeSuggestions.map((p, i) => (
                    <div
                      key={i}
                      className="autocomplete-item"
                      onMouseDown={e => { e.preventDefault(); selectPlace(p); }}
                    >
                      <div style={{ fontWeight: 500, color: 'var(--text-primary)', fontSize: '0.9rem', marginBottom: 2 }}>
                        {p.display_name.split(',')[0]}
                      </div>
                      <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                        {p.display_name.split(',').slice(1).join(',').trim()} · {p.tz_iana}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Selected place summary */}
            {form.selected_place && (
              <div style={{ padding: '12px 16px', background: 'rgba(34,197,94,0.07)', border: '1px solid rgba(34,197,94,0.2)', borderRadius: 'var(--radius-md)', marginBottom: 20, fontFamily: 'var(--font-devanagari)', fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Lat: {form.selected_place.latitude.toFixed(4)}</span>
                  <span>Lng: {form.selected_place.longitude.toFixed(4)}</span>
                  <span>TZ: {form.selected_place.tz_iana}</span>
                </div>
              </div>
            )}

            {/* Summary before submit */}
            <div className="card" style={{ padding: '16px 18px', marginBottom: 24 }}>
              <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: 8 }}>
                {mr('सारांश', 'Summary')}
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px 16px', fontFamily: 'var(--font-devanagari)', fontSize: '0.9rem' }}>
                <div><span style={{ color: 'var(--text-muted)' }}>{mr('नाव:', 'Name:')}</span> <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{form.name}</span></div>
                <div><span style={{ color: 'var(--text-muted)' }}>{mr('लिंग:', 'Gender:')}</span> <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{form.gender === 'male' ? mr('मुलगा', 'Male') : mr('मुलगी', 'Female')}</span></div>
                <div><span style={{ color: 'var(--text-muted)' }}>{mr('तारीख:', 'DOB:')}</span> <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{form.dob}</span></div>
                <div><span style={{ color: 'var(--text-muted)' }}>{mr('वेळ:', 'Time:')}</span> <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{form.time_accuracy === 'unknown' ? mr('माहित नाही', 'Unknown') : (form.time_of_birth || mr('दिली नाही', 'Not given'))}</span></div>
              </div>
            </div>

            {error && (
              <div style={{ padding: '12px 16px', background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: 'var(--radius-md)', marginBottom: 16, fontFamily: 'var(--font-devanagari)', fontSize: '0.88rem', color: '#f87171' }}>
                ⚠️ {error}
              </div>
            )}

            <div style={{ display: 'flex', gap: 10 }}>
              <button className="btn-ghost" style={{ flex: '0 0 auto', minWidth: 90 }} onClick={prevStep}>
                {mr('‹ मागे', '‹ Back')}
              </button>
              <button
                className="btn-primary"
                style={{ flex: 1, fontSize: '1.05rem' }}
                onClick={handleSubmit}
                disabled={!form.selected_place}
              >
                {mr('🪐 कुंडली बनवा', '🪐 Generate Kundali')}
              </button>
            </div>

            <p className="disclaimer" style={{ marginTop: 16 }}>
              {mr('डेटा सुरक्षित. फक्त गणनेसाठी वापरला जातो.', 'Data is secure and used only for computation.')}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

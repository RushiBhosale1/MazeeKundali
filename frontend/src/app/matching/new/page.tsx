'use client';
import { useState, useRef, useCallback, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { geocodePlace, type PlaceCandidate } from '@/lib/api';

type Lang = 'mr' | 'en';

interface PersonInput {
  name: string;
  gender: 'male' | 'female' | '';
  dob: string;
  time_of_birth: string;
  time_accuracy: 'exact' | 'approximate' | 'unknown';
  place_query: string;
  selected_place: PlaceCandidate | null;
}

const emptyPerson = (): PersonInput => ({
  name: '', gender: '', dob: '', time_of_birth: '',
  time_accuracy: 'exact', place_query: '', selected_place: null,
});

interface PersonFormProps {
  label: string;
  data: PersonInput;
  onChange: (data: PersonInput) => void;
  lang: Lang;
  icon: string;
}

function PersonForm({ label, data, onChange, lang, icon }: PersonFormProps) {
  const mr = (m: string, e: string) => lang === 'mr' ? m : e;
  const [suggestions, setSuggestions] = useState<PlaceCandidate[]>([]);
  const [searching, setSearching] = useState(false);
  const [showDrop, setShowDrop] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const wrapRef = useRef<HTMLDivElement>(null);

  const set = (field: keyof PersonInput, value: string) =>
    onChange({ ...data, [field]: value });

  const handlePlace = useCallback((val: string) => {
    onChange({ ...data, place_query: val, selected_place: null });
    if (timer.current) clearTimeout(timer.current);
    if (val.trim().length < 2) { setSuggestions([]); setShowDrop(false); return; }
    timer.current = setTimeout(async () => {
      setSearching(true);
      try {
        const res = await geocodePlace(val);
        setSuggestions(res);
        setShowDrop(res.length > 0);
      } catch { setSuggestions([]); }
      finally { setSearching(false); }
    }, 350);
  }, [data, onChange]);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (wrapRef.current && !wrapRef.current.contains(e.target as Node)) setShowDrop(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  return (
    <div className="card" style={{ padding: '20px', marginBottom: 16 }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16, borderBottom: '1px solid var(--border-subtle)', paddingBottom: 12 }}>
        <span style={{ fontSize: '1.6rem' }}>{icon}</span>
        <div>
          <div style={{ fontFamily: 'var(--font-devanagari)', fontWeight: 700, fontSize: '1rem', color: 'var(--text-primary)' }}>{label}</div>
        </div>
      </div>

      {/* Name */}
      <div style={{ marginBottom: 14 }}>
        <label className="input-label">{mr('नाव', 'Name')} <span className="required" style={{ fontSize: '0.75rem', marginLeft: 4, fontWeight: 'normal' }}>{mr('(आवश्यक)', '(Required)')}</span></label>
        <input className="input-field" type="text" placeholder={mr('पूर्ण नाव', 'Full name')}
          value={data.name} onChange={e => set('name', e.target.value)} />
      </div>

      {/* Gender */}
      <div style={{ marginBottom: 14 }}>
        <label className="input-label">{mr('लिंग', 'Gender')}</label>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
          {(['male', 'female'] as const).map(g => (
            <button key={g} onClick={() => onChange({ ...data, gender: g })} style={{
              padding: '10px', border: `2px solid ${data.gender === g ? 'var(--saffron-500)' : 'rgba(255,255,255,0.1)'}`,
              borderRadius: 'var(--radius-md)', background: data.gender === g ? 'rgba(240,124,0,0.12)' : 'transparent',
              color: data.gender === g ? 'var(--saffron-400)' : 'var(--text-secondary)',
              fontFamily: 'var(--font-devanagari)', fontSize: '0.9rem', fontWeight: 600, cursor: 'pointer', minHeight: 44,
            }}>
              {g === 'male' ? `♂ ${mr('मुलगा', 'Male')}` : `♀ ${mr('मुलगी', 'Female')}`}
            </button>
          ))}
        </div>
      </div>

      {/* DOB */}
      <div style={{ marginBottom: 14 }}>
        <label className="input-label">{mr('जन्म तारीख', 'Date of Birth')} <span className="required" style={{ fontSize: '0.75rem', marginLeft: 4, fontWeight: 'normal' }}>{mr('(आवश्यक)', '(Required)')}</span></label>
        <input className="input-field" type="date" max={new Date().toISOString().split('T')[0]} min="1900-01-01"
          value={data.dob} onChange={e => set('dob', e.target.value)} style={{ colorScheme: 'dark' }} />
      </div>

      {/* Time */}
      <div style={{ marginBottom: 14 }}>
        <label className="input-label">{mr('जन्म वेळ', 'Birth Time')}</label>
        <div style={{ display: 'flex', gap: 6, marginBottom: 8 }}>
          {([['exact', mr('अचूक', 'Exact')], ['approximate', mr('अंदाजे', 'Approx')], ['unknown', mr('माहित नाही', 'Unknown')]] as [string, string][]).map(([v, l]) => (
            <button key={v} onClick={() => onChange({ ...data, time_accuracy: v as PersonInput['time_accuracy'] })} style={{
              flex: 1, padding: '8px 4px', border: `1.5px solid ${data.time_accuracy === v ? 'var(--saffron-500)' : 'rgba(255,255,255,0.1)'}`,
              borderRadius: 'var(--radius-md)', background: data.time_accuracy === v ? 'rgba(240,124,0,0.12)' : 'transparent',
              color: data.time_accuracy === v ? 'var(--saffron-400)' : 'var(--text-secondary)',
              fontFamily: 'var(--font-devanagari)', fontSize: '0.75rem', cursor: 'pointer', minHeight: 40,
            }}>{l}</button>
          ))}
        </div>
        {data.time_accuracy !== 'unknown' && (
          <div className="animate-fade-in">
            <input className="input-field" type="time" value={data.time_of_birth}
              onChange={e => set('time_of_birth', e.target.value)} style={{ colorScheme: 'dark' }} />
            <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '4px', textAlign: 'right' }}>
              {mr('(उदा. दुपारी २:०० = 14:00)', '(e.g. 2:00 PM = 14:00)')}
            </div>
          </div>
        )}
      </div>

      {/* Place */}
      <div style={{ position: 'relative' }} ref={wrapRef}>
        <label className="input-label">{mr('जन्म ठिकाण', 'Birth Place')} <span className="required" style={{ fontSize: '0.75rem', marginLeft: 4, fontWeight: 'normal' }}>{mr('(आवश्यक)', '(Required)')}</span></label>
        <div style={{ position: 'relative' }}>
          <input className="input-field" type="text" placeholder={mr('शहर किंवा गाव...', 'City or village...')}
            value={data.place_query} autoComplete="off"
            onChange={e => handlePlace(e.target.value)}
            onFocus={() => suggestions.length > 0 && setShowDrop(true)} />
          {searching && <span style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', fontSize: '0.75rem', color: 'var(--text-muted)' }}>...</span>}
          {data.selected_place && <span style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--success)' }}>✓</span>}
        </div>
        {showDrop && suggestions.length > 0 && (
          <div className="autocomplete-dropdown">
            {suggestions.map((p, i) => (
              <div key={i} className="autocomplete-item"
                onMouseDown={e => { e.preventDefault(); onChange({ ...data, place_query: p.display_name, selected_place: p }); setShowDrop(false); }}>
                <div style={{ fontWeight: 500, color: 'var(--text-primary)', fontSize: '0.88rem' }}>{p.display_name.split(',')[0]}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{p.display_name.split(',').slice(1).join(',').trim()}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function NewMatchPage() {
  const router = useRouter();
  const [lang, setLang] = useState<Lang>('mr');
  const [bride, setBride] = useState<PersonInput>(emptyPerson());
  const [groom, setGroom] = useState<PersonInput>(emptyPerson());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const mr = (m: string, e: string) => lang === 'mr' ? m : e;

  const validate = () => {
    const today = new Date();
    
    // Bride
    const brideName = bride.name.trim();
    if (!brideName) { setError(mr('मुलीचे नाव आवश्यक आहे', "Bride's name is required")); return false; }
    if (brideName.length < 2) { setError(mr('मुलीचे नाव किमान २ अक्षरांचे असावे', "Bride's name must be at least 2 characters")); return false; }
    if (/[0-9!@#$%^&*()_+=\[\]{};':"\\|,.<>\/?]+/.test(brideName)) { setError(mr('मुलीच्या नावात फक्त अक्षरे असावीत', "Bride's name can only contain letters")); return false; }
    
    if (!bride.dob) { setError(mr('मुलीची जन्म तारीख द्या', "Enter bride's date of birth")); return false; }
    if (new Date(bride.dob) > today) { setError(mr('मुलीची जन्म तारीख भविष्यातील असू शकत नाही', "Bride's DOB cannot be in the future")); return false; }
    
    if (!bride.selected_place) { setError(mr('मुलीचे जन्म ठिकाण निवडा', "Select bride's birth place")); return false; }

    // Groom
    const groomName = groom.name.trim();
    if (!groomName) { setError(mr('मुलाचे नाव आवश्यक आहे', "Groom's name is required")); return false; }
    if (groomName.length < 2) { setError(mr('मुलाचे नाव किमान २ अक्षरांचे असावे', "Groom's name must be at least 2 characters")); return false; }
    if (/[0-9!@#$%^&*()_+=\[\]{};':"\\|,.<>\/?]+/.test(groomName)) { setError(mr('मुलाच्या नावात फक्त अक्षरे असावीत', "Groom's name can only contain letters")); return false; }

    if (!groom.dob) { setError(mr('मुलाची जन्म तारीख द्या', "Enter groom's date of birth")); return false; }
    if (new Date(groom.dob) > today) { setError(mr('मुलाची जन्म तारीख भविष्यातील असू शकत नाही', "Groom's DOB cannot be in the future")); return false; }

    if (!groom.selected_place) { setError(mr('मुलाचे जन्म ठिकाण निवडा', "Select groom's birth place")); return false; }
    return true;
  };

  const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

  const handleSubmit = async () => {
    setError('');
    if (!validate()) return;
    setLoading(true);
    try {
      const body = {
        bride: {
          name: bride.name.trim(),
          gender: bride.gender || 'female',
          dob: bride.dob,
          time_of_birth: bride.time_accuracy !== 'unknown' ? (bride.time_of_birth || null) : null,
          time_accuracy: bride.time_accuracy,
          place_query: bride.place_query,
          latitude: bride.selected_place!.latitude,
          longitude: bride.selected_place!.longitude,
          tz_iana: bride.selected_place!.tz_iana,
          rahu_mode: 'true_node',
        },
        groom: {
          name: groom.name.trim(),
          gender: groom.gender || 'male',
          dob: groom.dob,
          time_of_birth: groom.time_accuracy !== 'unknown' ? (groom.time_of_birth || null) : null,
          time_accuracy: groom.time_accuracy,
          place_query: groom.place_query,
          latitude: groom.selected_place!.latitude,
          longitude: groom.selected_place!.longitude,
          tz_iana: groom.selected_place!.tz_iana,
          rahu_mode: 'true_node',
        },
      };
      const resp = await fetch(`${API_URL}/api/v1/matchings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}));
        throw new Error(err.detail ?? 'Server error');
      }
      const data = await resp.json();
      router.push(`/matching/${data.id}`);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : '';
      setError(msg || mr('गणना अयशस्वी झाली. पुन्हा प्रयत्न करा.', 'Calculation failed. Please try again.'));
      setLoading(false);
    }
  };

  if (loading) return (
    <div style={{ minHeight: '100dvh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', padding: 24 }}>
      <div style={{ fontSize: '2.5rem', marginBottom: 16, animation: 'spin-slow 3s linear infinite' }}>💍</div>
      <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '1.1rem', color: 'var(--text-primary)' }}>
        {mr('गुण मिलन तपासत आहोत...', 'Calculating Guna Milan...')}
      </div>
    </div>
  );

  return (
    <div style={{ minHeight: '100dvh', paddingBottom: 48 }}>
      <nav className="navbar">
        <div style={{ maxWidth: 680, margin: '0 auto', padding: '0 16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: 56 }}>
          <button onClick={() => router.push('/')} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', fontFamily: 'var(--font-devanagari)' }}>
            ‹ {mr('मागे', 'Back')}
          </button>
          <span style={{ fontFamily: 'var(--font-devanagari)', fontWeight: 700, color: 'var(--saffron-400)', fontSize: '1rem' }}>
            💍 {mr('पत्रिका जुळणी', 'Kundali Matching')}
          </span>
          <div className="lang-toggle">
            <button className={`lang-btn${lang === 'mr' ? ' active' : ''}`} onClick={() => setLang('mr')}>मराठी</button>
            <button className={`lang-btn${lang === 'en' ? ' active' : ''}`} onClick={() => setLang('en')}>EN</button>
          </div>
        </div>
      </nav>

      <div className="page-container" style={{ paddingTop: 24 }}>
        <div style={{ textAlign: 'center', marginBottom: 28 }}>
          <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: 6 }}>
            {mr('अष्टकूट गुण मिलन', 'Ashtakoot Guna Milan')}
          </div>
          <p style={{ fontFamily: 'var(--font-devanagari)', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            {mr('मुलगी व मुलगा दोघांची माहिती भरा', 'Enter details for both bride and groom')}
          </p>
        </div>

        {/* Free score preview badge */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: 10, marginBottom: 24 }}>
          <span className="chip chip-green">{mr('✓ मोफत स्कोअर', '✓ Free Score Preview')}</span>
          <span className="chip chip-gold">{mr('₹49 मध्ये संपूर्ण', 'Full report ₹49')}</span>
        </div>

        <PersonForm label={mr('मुलीची माहिती', "Bride's Details")} data={bride} onChange={setBride} lang={lang} icon="👰" />
        <PersonForm label={mr('मुलाची माहिती', "Groom's Details")} data={groom} onChange={setGroom} lang={lang} icon="🤵" />

        {error && (
          <div style={{ padding: '12px 16px', background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: 'var(--radius-md)', marginBottom: 16, fontFamily: 'var(--font-devanagari)', fontSize: '0.88rem', color: '#f87171' }}>
            ⚠️ {error}
          </div>
        )}

        <button className="btn-primary" style={{ width: '100%', fontSize: '1.05rem', marginBottom: 16 }} onClick={handleSubmit}>
          {mr('💍 गुण मिलन तपासा', '💍 Check Compatibility')}
        </button>

        <p className="disclaimer">
          {mr('अष्टकूट पद्धतीनुसार ३६ गुणांपैकी गुण मोजले जातात. हे मार्गदर्शनासाठी आहे.', 'Scored out of 36 points using the Ashtakoot method. For guidance only.')}
        </p>
      </div>
    </div>
  );
}

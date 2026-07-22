'use client';
import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import PaywallButton from '@/components/PaywallButton';
import { whatsappShareUrl } from '@/lib/share';

type Lang = 'mr' | 'en';

interface KootaRow {
  name_en: string;
  name_mr: string;
  points_earned: number;
  points_max: number;
  notes_mr: string;
  notes_en: string;
  interpretation_mr?: string;
  interpretation_en?: string;
  boy_trait?: string;
  girl_trait?: string;
  area_of_life_mr?: string;
}

interface DoshaInfo {
  dosha_name: string;
  is_present: boolean;
  is_cancelled: boolean;
  cancellation_rule_mr: string | null;
  explanation_mr: string;
  explanation_en: string;
}

interface PersonDetails {
  name?: string;
  dob?: string;
  time_of_birth?: string;
  place?: string;
  rashi?: string;
  rashi_lord?: string;
  nakshatra?: string;
  nakshatra_lord?: string;
  pada?: number | string;
  lagna?: string;
  lagna_lord?: string;
  varna?: string;
  vashya?: string;
  yoni?: string;
  gana?: string;
  nadi?: string;
}

interface MatchResult {
  id: string;
  bride_name: string;
  groom_name: string;
  total_score: number;
  total_max: number;
  bride_manglik: boolean | null;
  groom_manglik: boolean | null;
  bride_manglik_severity?: string;
  groom_manglik_severity?: string;
  bride_manglik_explanation?: string;
  groom_manglik_explanation?: string;
  paid: boolean;
  resume_token: string;
  locked: Record<string, boolean>;
  verdict_mr?: string;
  verdict_en?: string;
  koota_breakdown?: KootaRow[];
  nadi_dosha?: DoshaInfo;
  bhakoot_dosha?: DoshaInfo;
  bride_details?: PersonDetails;
  groom_details?: PersonDetails;
  // Chart SVGs (paid only)
  bride_chart_svg?: string | null;
  bride_d9_chart_svg?: string | null;
  bride_moon_chart_svg?: string | null;
  groom_chart_svg?: string | null;
  groom_d9_chart_svg?: string | null;
  groom_moon_chart_svg?: string | null;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

function ScoreRing({ score, max }: { score: number; max: number }) {
  const pct = score / max;
  const r = 44;
  const circ = 2 * Math.PI * r;
  const dash = circ * pct;
  const color = pct >= 0.88 ? '#22c55e' : pct >= 0.69 ? '#f59e0b' : pct >= 0.5 ? '#f07c00' : '#ef4444';
  return (
    <svg width={100} height={100} viewBox="0 0 100 100">
      <circle cx={50} cy={50} r={r} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth={8} />
      <circle cx={50} cy={50} r={r} fill="none" stroke={color} strokeWidth={8}
        strokeDasharray={`${dash} ${circ}`} strokeLinecap="round"
        transform="rotate(-90 50 50)"
        style={{ transition: 'stroke-dasharray 1.2s cubic-bezier(0.4,0,0.2,1)' }} />
      <text x="50%" y="50%" dominantBaseline="middle" textAnchor="middle"
        fontSize={22} fontWeight={800} fill={color}>{score}</text>
      <text x="50%" y="68%" dominantBaseline="middle" textAnchor="middle"
        fontSize={10} fill="rgba(255,255,255,0.4)">/{max}</text>
    </svg>
  );
}

function KootaBar({ earned, max }: { earned: number; max: number }) {
  const pct = max > 0 ? (earned / max) * 100 : 0;
  return (
    <div className="koota-bar" style={{ flex: 1 }}>
      <div className="koota-bar-fill" style={{ width: `${pct}%` }} />
    </div>
  );
}

export default function MatchingResultPage() {
  const params = useParams();
  const router = useRouter();
  const id = params?.id as string;
  const [lang, setLang] = useState<Lang>('mr');
  const [result, setResult] = useState<MatchResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const mr = (m: string, e: string) => lang === 'mr' ? m : e;

  useEffect(() => {
    if (!id) return;
    fetch(`${API_URL}/api/v1/matchings/${id}`)
      .then(r => r.ok ? r.json() : Promise.reject(r))
      .then(setResult)
      .catch(() => setError(mr('जुळणी सापडली नाही.', 'Matching not found.')))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return (
    <div style={{ minHeight: '100dvh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: '2.5rem', animation: 'spin-slow 3s linear infinite', marginBottom: 16 }}>💍</div>
        <div style={{ fontFamily: 'var(--font-devanagari)', color: 'var(--text-secondary)' }}>
          {mr('लोड होत आहे...', 'Loading...')}
        </div>
      </div>
    </div>
  );

  if (error || !result) return (
    <div style={{ minHeight: '100dvh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24, textAlign: 'center' }}>
      <div>
        <div style={{ fontSize: '2rem', marginBottom: 12 }}>⚠️</div>
        <p style={{ fontFamily: 'var(--font-devanagari)', color: 'var(--danger)' }}>
          {mr('जुळणी सापडली नाही.', 'Matching not found.')}
        </p>
        <button className="btn-secondary" style={{ marginTop: 20 }} onClick={() => router.push('/matching/new')}>
          {mr('पुन्हा तपासा', 'Try Again')}
        </button>
      </div>
    </div>
  );

  // ─── UNPAID VIEW: Completely locked behind paywall ─────────────────────
  if (!result.paid) {
    return (
      <div style={{ minHeight: '100dvh', paddingBottom: 60 }}>
        {/* Navbar */}
        <nav className="navbar">
          <div style={{ maxWidth: 680, margin: '0 auto', padding: '0 16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: 56 }}>
            <button onClick={() => router.push('/matching/new')} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', fontFamily: 'var(--font-devanagari)' }}>
              ‹ {mr('मागे', 'Back')}
            </button>
            <span style={{ fontFamily: 'var(--font-devanagari)', fontWeight: 700, color: 'var(--saffron-400)' }}>
              💍 {mr('पत्रिका जुळणी', 'Kundali Matching')}
            </span>
            <div className="lang-toggle">
              <button className={`lang-btn${lang === 'mr' ? ' active' : ''}`} onClick={() => setLang('mr')}>मराठी</button>
              <button className={`lang-btn${lang === 'en' ? ' active' : ''}`} onClick={() => setLang('en')}>EN</button>
            </div>
          </div>
        </nav>

        <div className="page-container" style={{ paddingTop: 32, maxWidth: 600, margin: '0 auto' }}>
          <div className="card animate-fade-up" style={{ padding: '28px 24px', textAlign: 'center', background: 'linear-gradient(135deg, rgba(240,124,0,0.08) 0%, rgba(201,162,39,0.06) 100%)', borderColor: 'rgba(240,124,0,0.3)', boxShadow: '0 10px 30px rgba(0,0,0,0.2)' }}>
            <div style={{ fontSize: '3rem', marginBottom: 12 }}>🔒</div>
            <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '1.25rem', fontWeight: 800, color: 'var(--saffron-400)', marginBottom: 8 }}>
              {mr('पत्रिका जुळणी अहवाल तयार आहे!', 'Kundali Matching Report is Ready!')}
            </div>
            <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '1rem', color: 'var(--text-secondary)', marginBottom: 16 }}>
              👰 {result.bride_name} <span style={{ color: 'var(--saffron-400)' }}>↔</span> 🤵 {result.groom_name}
            </div>

            <div style={{ padding: '16px', background: 'rgba(0,0,0,0.2)', borderRadius: 12, border: '1px dashed rgba(240,124,0,0.3)', marginBottom: 24, textAlign: 'left' }}>
              <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: 1.6, marginBottom: 14 }}>
                {mr('तुमचा सविस्तर गुण मिलान, दोष निवारण अहवाल व ६ कुंडळ्या तयार झाल्या आहेत. संपूर्ण अहवाल व आकृत्या (Kundali Diagrams) पाहण्यासाठी खालील बटणावर क्लिक करून अनलॉक करा.',
                    'Your detailed Gun Milan, Dosha analysis report and 6 birth charts are ready. Unlock below to view full report, diagrams and complete astrological guidance.')}
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 16px' }}>
                {[
                  mr('✓ ८-कूट सविस्तर गुण तक्ता', '✓ 8-Koota breakdown'),
                  mr('✓ ६ कुंडळ्या (D1, D9, चंद्र)', '✓ 6 Charts (D1, D9, Moon)'),
                  mr('✓ वधू-वर माहिती तुलना', '✓ Planetary Comparison'),
                  mr('✓ नाडी व भकूट दोष निवारण', '✓ Nadi & Bhakoot Dosha'),
                  mr('✓ मंगळ दोष सुसंगतता', '✓ Manglik Compatibility'),
                  mr('✓ तज्ञ ज्योतिषीय निष्कर्ष', '✓ Expert Astrological Verdict'),
                  mr('✓ PDF रिपोर्ट डाउनलोड', '✓ Download Printable PDF'),
                  mr('✓ WhatsApp वर शेअर करा', '✓ WhatsApp Share')
                ].map((item, idx) => (
                  <div key={idx} style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.82rem', color: '#fbbf24', fontWeight: 500 }}>
                    {item}
                  </div>
                ))}
              </div>
            </div>

            <PaywallButton
              productType="matching"
              recordId={id}
              resumeToken={result.resume_token ?? ''}
              buyerName={`${result.bride_name} / ${result.groom_name}`}
              label={mr('संपूर्ण जुळणी अहवाल अनलॉक करा (₹४९)', 'Unlock Full Matching Report (₹49)')}
              sublabel={mr('एकदाच पेमेंट · संपूर्ण अहवाल + ६ कुंडळ्या + PDF', 'One-time payment · Instant access')}
              description={`पत्रिका जुळणी — ${result.bride_name} ↔ ${result.groom_name}`}
              pollUrl={`/api/v1/matchings/${id}`}
              onUnlocked={() => window.location.reload()}
              fullWidth
            />
          </div>
        </div>
      </div>
    );
  }

  // ─── PAID VIEW: Show all details, 6 charts, breakdown & conclusion ──────────
  const pct = result.total_score / result.total_max;
  const verdictColor = pct >= 0.88 ? 'var(--success)' : pct >= 0.69 ? '#f59e0b' : pct >= 0.5 ? 'var(--saffron-400)' : 'var(--danger)';

  const bd = result.bride_details || {};
  const gd = result.groom_details || {};

  const detailsRows = [
    { label: mr('नाव', 'Name'), bride: bd.name || result.bride_name || '-', groom: gd.name || result.groom_name || '-' },
    { label: mr('जन्म तारीख', 'Date of Birth'), bride: bd.dob || '-', groom: gd.dob || '-' },
    { label: mr('जन्म वेळ (१२ तास)', 'Time of Birth (12h)'), bride: bd.time_of_birth || '-', groom: gd.time_of_birth || '-' },
    { label: mr('राशी', 'Rashi'), bride: bd.rashi || '-', groom: gd.rashi || '-' },
    { label: mr('राशीपती', 'Rashi Lord'), bride: bd.rashi_lord || '-', groom: gd.rashi_lord || '-' },
    { label: mr('नक्षत्र व पद', 'Nakshatra & Pada'), bride: `${bd.nakshatra || '-'} (${bd.pada || '-'})`, groom: `${gd.nakshatra || '-'} (${gd.pada || '-'})` },
    { label: mr('नक्षत्रपती', 'Nakshatra Lord'), bride: bd.nakshatra_lord || '-', groom: gd.nakshatra_lord || '-' },
    { label: mr('लग्न राशी', 'Lagna Sign'), bride: bd.lagna || '-', groom: gd.lagna || '-' },
    { label: mr('लग्नपती', 'Lagna Lord'), bride: bd.lagna_lord || '-', groom: gd.lagna_lord || '-' },
    { label: mr('वर्ण', 'Varna'), bride: bd.varna || '-', groom: gd.varna || '-' },
    { label: mr('वश्य', 'Vashya'), bride: bd.vashya || '-', groom: gd.vashya || '-' },
    { label: mr('योनी', 'Yoni'), bride: bd.yoni || '-', groom: gd.yoni || '-' },
    { label: mr('गण', 'Gana'), bride: bd.gana || '-', groom: gd.gana || '-' },
    { label: mr('नाडी', 'Nadi'), bride: bd.nadi || '-', groom: gd.nadi || '-' },
  ];

  return (
    <div style={{ minHeight: '100dvh', paddingBottom: 60 }}>
      {/* Navbar */}
      <nav className="navbar">
        <div style={{ maxWidth: 680, margin: '0 auto', padding: '0 16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: 56 }}>
          <button onClick={() => router.push('/matching/new')} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', fontFamily: 'var(--font-devanagari)' }}>
            ‹ {mr('मागे', 'Back')}
          </button>
          <span style={{ fontFamily: 'var(--font-devanagari)', fontWeight: 700, color: 'var(--saffron-400)' }}>
            💍 {mr('पत्रिका जुळणी अहवाल', 'Matching Report')}
          </span>
          <div className="lang-toggle">
            <button className={`lang-btn${lang === 'mr' ? ' active' : ''}`} onClick={() => setLang('mr')}>मराठी</button>
            <button className={`lang-btn${lang === 'en' ? ' active' : ''}`} onClick={() => setLang('en')}>EN</button>
          </div>
        </div>
      </nav>

      <div className="page-container" style={{ paddingTop: 24 }}>

        {/* ─── Hero score card ───────────────────────────────── */}
        <div className="card animate-fade-up" style={{ padding: '24px', marginBottom: 16, textAlign: 'center', background: 'linear-gradient(135deg, rgba(240,124,0,0.08) 0%, rgba(201,162,39,0.06) 100%)', borderColor: 'rgba(240,124,0,0.25)' }}>
          <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-secondary)', marginBottom: 8 }}>
            👰 {result.bride_name} <span style={{ color: 'var(--saffron-400)' }}>↔</span> 🤵 {result.groom_name}
          </div>
          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 12 }}>
            <ScoreRing score={result.total_score} max={result.total_max} />
          </div>
          <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '1.1rem', fontWeight: 700, color: verdictColor, marginBottom: 4 }}>
            {pct >= 0.88 ? mr('उत्तम जुळणी 🌟', 'Excellent Match 🌟') :
             pct >= 0.69 ? mr('चांगली जुळणी ✅', 'Good Match ✅') :
             pct >= 0.5  ? mr('साधारण जुळणी ⚠️', 'Average Match ⚠️') :
             mr('अल्प जुळणी ❗', 'Low Compatibility ❗')}
          </div>
          <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            {mr(`${result.total_score} गुण / ३६ पैकी`, `${result.total_score} points out of 36`)}
          </div>
        </div>

        {/* ─── Astrological Conclusion Box ──────────────────────── */}
        {(result.verdict_mr || result.verdict_en) && (
          <div className="card animate-fade-up" style={{ padding: '20px', marginBottom: 16, background: 'linear-gradient(135deg, rgba(20,40,70,0.9) 0%, rgba(10,20,40,0.95) 100%)', borderColor: 'rgba(240,124,0,0.4)', color: '#fff' }}>
            <h2 style={{ fontFamily: 'var(--font-devanagari)', fontSize: '1.15rem', fontWeight: 700, marginBottom: 10, color: 'var(--saffron-400)', textAlign: 'center' }}>
              📜 {mr('ज्योतिषीय निष्कर्ष', 'Astrological Conclusion')}
            </h2>
            <p style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.95rem', lineHeight: 1.65, textAlign: 'center', opacity: 0.95 }}>
              {lang === 'mr' ? result.verdict_mr : (result.verdict_en || result.verdict_mr)}
            </p>
          </div>
        )}

        {/* ─── Birth Details Comparison Table ───────────────────── */}
        <div style={{ marginBottom: 20 }}>
          <h2 style={{ fontFamily: 'var(--font-devanagari)', fontSize: '1.05rem', fontWeight: 700, marginBottom: 12, color: 'var(--text-primary)' }}>
            📋 {mr('ग्रहीय व जन्म तपशील', 'Planetary & Birth Details')}
          </h2>
          <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
              <thead>
                <tr style={{ background: 'rgba(240,124,0,0.12)', borderBottom: '1px solid rgba(240,124,0,0.2)' }}>
                  <th style={{ padding: '10px 14px', fontFamily: 'var(--font-devanagari)', fontSize: '0.85rem', color: 'var(--saffron-400)', width: '36%' }}>
                    {mr('घटक', 'Attribute')}
                  </th>
                  <th style={{ padding: '10px 14px', fontFamily: 'var(--font-devanagari)', fontSize: '0.85rem', color: 'var(--text-primary)', width: '32%' }}>
                    👰 {result.bride_name}
                  </th>
                  <th style={{ padding: '10px 14px', fontFamily: 'var(--font-devanagari)', fontSize: '0.85rem', color: 'var(--text-primary)', width: '32%' }}>
                    🤵 {result.groom_name}
                  </th>
                </tr>
              </thead>
              <tbody>
                {detailsRows.map((row, idx) => (
                  <tr key={idx} style={{ borderBottom: idx < detailsRows.length - 1 ? '1px solid var(--border-subtle)' : 'none', background: idx % 2 === 1 ? 'rgba(255,255,255,0.02)' : 'transparent' }}>
                    <td style={{ padding: '9px 14px', fontFamily: 'var(--font-devanagari)', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                      {row.label}
                    </td>
                    <td style={{ padding: '9px 14px', fontFamily: 'var(--font-devanagari)', fontSize: '0.85rem', color: 'var(--text-primary)', fontWeight: 500 }}>
                      {row.bride}
                    </td>
                    <td style={{ padding: '9px 14px', fontFamily: 'var(--font-devanagari)', fontSize: '0.85rem', color: 'var(--text-primary)', fontWeight: 500 }}>
                      {row.groom}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* ─── 6 Kundali Diagrams (D1, D9, Moon for Bride & Groom) ─ */}
        <div style={{ marginBottom: 20 }}>
          <h2 style={{ fontFamily: 'var(--font-devanagari)', fontSize: '1.05rem', fontWeight: 700, marginBottom: 12, color: 'var(--text-primary)' }}>
            📊 {mr('सविस्तर ६ कुंडळ्या', '6 Kundali Diagrams (D1, D9 & Moon)')}
          </h2>

          {/* Bride 3 charts */}
          <div className="card" style={{ padding: '16px', marginBottom: 14 }}>
            <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.95rem', fontWeight: 700, color: 'var(--saffron-400)', marginBottom: 12, textAlign: 'center', borderBottom: '1px solid var(--border-subtle)', paddingBottom: 8 }}>
              👰 {result.bride_name} - {mr('कुंडल्या', 'Charts')}
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 14, justifyContent: 'center' }}>
              {result.bride_chart_svg && (
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 6, fontWeight: 600 }}>
                    {mr('लग्न कुंडळी (D1)', 'Janma Kundali (D1)')}
                  </div>
                  <div dangerouslySetInnerHTML={{ __html: result.bride_chart_svg }} style={{ display: 'flex', justifyContent: 'center' }} />
                </div>
              )}
              {result.bride_d9_chart_svg && (
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 6, fontWeight: 600 }}>
                    {mr('नवमांश कुंडळी (D9)', 'Navamsha Kundali (D9)')}
                  </div>
                  <div dangerouslySetInnerHTML={{ __html: result.bride_d9_chart_svg }} style={{ display: 'flex', justifyContent: 'center' }} />
                </div>
              )}
              {result.bride_moon_chart_svg && (
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 6, fontWeight: 600 }}>
                    {mr('चंद्र कुंडळी', 'Chandra Kundali')}
                  </div>
                  <div dangerouslySetInnerHTML={{ __html: result.bride_moon_chart_svg }} style={{ display: 'flex', justifyContent: 'center' }} />
                </div>
              )}
            </div>
          </div>

          {/* Groom 3 charts */}
          <div className="card" style={{ padding: '16px' }}>
            <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.95rem', fontWeight: 700, color: 'var(--saffron-400)', marginBottom: 12, textAlign: 'center', borderBottom: '1px solid var(--border-subtle)', paddingBottom: 8 }}>
              🤵 {result.groom_name} - {mr('कुंडल्या', 'Charts')}
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 14, justifyContent: 'center' }}>
              {result.groom_chart_svg && (
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 6, fontWeight: 600 }}>
                    {mr('लग्न कुंडळी (D1)', 'Janma Kundali (D1)')}
                  </div>
                  <div dangerouslySetInnerHTML={{ __html: result.groom_chart_svg }} style={{ display: 'flex', justifyContent: 'center' }} />
                </div>
              )}
              {result.groom_d9_chart_svg && (
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 6, fontWeight: 600 }}>
                    {mr('नवमांश कुंडळी (D9)', 'Navamsha Kundali (D9)')}
                  </div>
                  <div dangerouslySetInnerHTML={{ __html: result.groom_d9_chart_svg }} style={{ display: 'flex', justifyContent: 'center' }} />
                </div>
              )}
              {result.groom_moon_chart_svg && (
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 6, fontWeight: 600 }}>
                    {mr('चंद्र कुंडळी', 'Chandra Kundali')}
                  </div>
                  <div dangerouslySetInnerHTML={{ __html: result.groom_moon_chart_svg }} style={{ display: 'flex', justifyContent: 'center' }} />
                </div>
              )}
            </div>
          </div>
        </div>

        {/* ─── Manglik status ────────────────────────────────── */}
        <div className="card" style={{ padding: '18px 20px', marginBottom: 16 }}>
          <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.9rem', fontWeight: 700, color: 'var(--saffron-400)', marginBottom: 12 }}>
            🔴 {mr('मंगळ दोष सुसंगतता व विश्लेषण', 'Mangal Dosha Analysis & Compatibility')}
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 14 }}>
            {/* Bride Mangal */}
            <div style={{ padding: '12px 14px', background: 'rgba(0,0,0,0.15)', borderRadius: 10, border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: 6 }}>
                👰 {result.bride_name}
              </div>
              <span className={`chip ${result.bride_manglik_severity === 'HIGH' ? 'chip-red' : result.bride_manglik_severity === 'MILD' ? 'chip-orange' : result.bride_manglik_severity === 'CANCELLED' ? 'chip-green' : 'chip-green'}`} style={{ fontSize: '0.8rem', marginBottom: 8, display: 'inline-block' }}>
                {result.bride_manglik === null ? mr('अज्ञात', 'Unknown') :
                 result.bride_manglik_severity === 'HIGH' ? mr('कडक मंगळ दोष ⚠️', 'High Manglik ⚠️') :
                 result.bride_manglik_severity === 'MILD' ? mr('अंशिक/सौम्य मंगळ ⚠️', 'Mild Manglik ⚠️') :
                 result.bride_manglik_severity === 'CANCELLED' ? mr('मंगळ दोष रद्द (परिहार लागू) ✅', 'Dosha Cancelled ✅') :
                 mr('दोष नाही ✅', 'No Dosha ✅')}
              </span>
              {result.bride_manglik_explanation && (
                <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.5, marginTop: 6, borderTop: '1px dashed rgba(255,255,255,0.1)', paddingTop: 6 }}>
                  {result.bride_manglik_explanation}
                </div>
              )}
            </div>

            {/* Groom Mangal */}
            <div style={{ padding: '12px 14px', background: 'rgba(0,0,0,0.15)', borderRadius: 10, border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: 6 }}>
                🤵 {result.groom_name}
              </div>
              <span className={`chip ${result.groom_manglik_severity === 'HIGH' ? 'chip-red' : result.groom_manglik_severity === 'MILD' ? 'chip-orange' : result.groom_manglik_severity === 'CANCELLED' ? 'chip-green' : 'chip-green'}`} style={{ fontSize: '0.8rem', marginBottom: 8, display: 'inline-block' }}>
                {result.groom_manglik === null ? mr('अज्ञात', 'Unknown') :
                 result.groom_manglik_severity === 'HIGH' ? mr('कडक मंगळ दोष ⚠️', 'High Manglik ⚠️') :
                 result.groom_manglik_severity === 'MILD' ? mr('अंशिक/सौम्य मंगळ ⚠️', 'Mild Manglik ⚠️') :
                 result.groom_manglik_severity === 'CANCELLED' ? mr('मंगळ दोष रद्द (परिहार लागू) ✅', 'Dosha Cancelled ✅') :
                 mr('दोष नाही ✅', 'No Dosha ✅')}
              </span>
              {result.groom_manglik_explanation && (
                <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.5, marginTop: 6, borderTop: '1px dashed rgba(255,255,255,0.1)', paddingTop: 6 }}>
                  {result.groom_manglik_explanation}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* ─── 8-Koota Breakdown Table ───────────────────────── */}
        {result.koota_breakdown && (
          <div style={{ marginBottom: 16 }}>
            <h2 style={{ fontFamily: 'var(--font-devanagari)', fontSize: '1.05rem', fontWeight: 700, marginBottom: 12, color: 'var(--text-primary)' }}>
              🎯 {mr('८-कूट सविस्तर गुण तक्ता', '8-Koota Breakdown Table')}
            </h2>
            <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
              {result.koota_breakdown.map((k, i) => (
                <div key={i} style={{ padding: '14px 16px', borderBottom: i < result.koota_breakdown!.length - 1 ? '1px solid var(--border-subtle)' : 'none' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
                    <div style={{ flex: '0 0 110px', fontFamily: 'var(--font-devanagari)', fontSize: '0.88rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                      {lang === 'mr' ? k.name_mr : k.name_en}
                    </div>
                    <KootaBar earned={k.points_earned} max={k.points_max} />
                    <div style={{ flex: '0 0 48px', textAlign: 'right', fontFamily: 'Inter', fontSize: '0.85rem', fontWeight: 700, color: k.points_earned === k.points_max ? 'var(--success)' : k.points_earned === 0 ? 'var(--danger)' : 'var(--saffron-400)' }}>
                      {k.points_earned}/{k.points_max}
                    </div>
                  </div>
                  {k.notes_mr && (
                    <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.78rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
                      {lang === 'mr' ? k.notes_mr : k.notes_en}
                    </div>
                  )}
                  {k.interpretation_mr && (
                    <div style={{ marginTop: 8, padding: '10px 12px', background: 'rgba(240,124,0,0.05)', borderRadius: 6, border: '1px solid rgba(240,124,0,0.1)' }}>
                      <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.85rem', color: 'var(--text-primary)', lineHeight: 1.5, marginBottom: 4 }}>
                        {k.interpretation_mr}
                      </div>
                      {k.interpretation_en && (
                        <div style={{ fontFamily: 'Inter', fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: 1.4, fontStyle: 'italic' }}>
                          {k.interpretation_en}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
              {/* Total row */}
              <div style={{ padding: '14px 16px', background: 'rgba(240,124,0,0.06)', borderTop: '1.5px solid rgba(240,124,0,0.2)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontFamily: 'var(--font-devanagari)', fontWeight: 700, color: 'var(--text-primary)' }}>
                  {mr('एकूण गुण (Total Score)', 'Total Score')}
                </span>
                <span style={{ fontFamily: 'Inter', fontSize: '1.15rem', fontWeight: 800, color: 'var(--gold-400)' }}>
                  {result.total_score}/{result.total_max}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* ─── Dosha analysis ───────────────────────────────── */}
        {(result.nadi_dosha || result.bhakoot_dosha) && (
          <div style={{ marginBottom: 20 }}>
            <h2 style={{ fontFamily: 'var(--font-devanagari)', fontSize: '1.05rem', fontWeight: 700, marginBottom: 10, color: 'var(--text-primary)' }}>
              ⚡ {mr('नाडी व भकूट दोष विश्लेषण', 'Dosha Analysis')}
            </h2>
            {[result.nadi_dosha, result.bhakoot_dosha].filter(Boolean).map((d, i) => d && (
              <div key={i} className="card" style={{ padding: '14px 16px', marginBottom: 8, borderColor: d.is_present && !d.is_cancelled ? 'rgba(239,68,68,0.3)' : 'rgba(34,197,94,0.3)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                  <span style={{ fontSize: '1.1rem' }}>{d.is_present && !d.is_cancelled ? '⚠️' : '✅'}</span>
                  <span style={{ fontFamily: 'var(--font-devanagari)', fontWeight: 700, fontSize: '0.95rem', color: 'var(--text-primary)' }}>{d.dosha_name}</span>
                  <span className={`chip ${d.is_present && !d.is_cancelled ? 'chip-red' : 'chip-green'}`} style={{ fontSize: '0.72rem' }}>
                    {d.is_present ? (d.is_cancelled ? mr('रद्द (Parihara) ✅', 'Cancelled ✅') : mr('आहे ⚠️', 'Present ⚠️')) : mr('नाही ✅', 'Not Present ✅')}
                  </span>
                </div>
                <p style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                  {lang === 'mr' ? d.explanation_mr : d.explanation_en}
                </p>
                {d.is_cancelled && d.cancellation_rule_mr && (
                  <div style={{ marginTop: 6, padding: '6px 10px', background: 'rgba(34,197,94,0.08)', borderRadius: 8, fontFamily: 'var(--font-devanagari)', fontSize: '0.78rem', color: '#4ade80' }}>
                    📌 {mr('रद्दीकरण (परिहार) नियम:', 'Cancellation rule:')} {d.cancellation_rule_mr}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* ─── Paid actions: PDF + WhatsApp ──────────────── */}
        <div style={{ display: 'flex', gap: 10, marginBottom: 20, flexWrap: 'wrap' }}>
          <a
            href={`${process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'}/api/v1/matchings/${id}/pdf`}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              flex: 1, minWidth: 140, display: 'flex', alignItems: 'center', justifyContent: 'center',
              gap: 8, padding: '14px 18px', borderRadius: 'var(--radius-lg)',
              background: 'linear-gradient(135deg, var(--saffron-500) 0%, var(--saffron-600) 100%)',
              color: '#fff', fontFamily: 'var(--font-devanagari)',
              fontWeight: 700, fontSize: '0.95rem', textDecoration: 'none', cursor: 'pointer',
              boxShadow: '0 4px 12px rgba(240,124,0,0.3)',
            }}
          >
            📄 {mr('PDF अहवाल डाउनलोड करा', 'Download PDF Report')}
          </a>
          <a
            href={whatsappShareUrl({
              type: 'matching',
              id: id as string,
              score: result.total_score,
            })}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              flex: 1, minWidth: 140, display: 'flex', alignItems: 'center', justifyContent: 'center',
              gap: 8, padding: '14px 18px', borderRadius: 'var(--radius-lg)',
              background: 'rgba(37,211,102,0.12)', border: '1px solid rgba(37,211,102,0.35)',
              color: '#25d366', fontFamily: 'var(--font-devanagari)',
              fontWeight: 700, fontSize: '0.95rem', textDecoration: 'none', cursor: 'pointer',
            }}
          >
            💬 {mr('WhatsApp वर शेअर करा', 'Share on WhatsApp')}
          </a>
        </div>

        <p className="disclaimer">
          {mr('हे परिणाम मार्गदर्शनासाठी आहेत. वैयक्तिक सल्ल्यासाठी तज्ञ ज्योतिषांचा सल्ला घ्या.', 'Results are for guidance only. Consult an expert astrologer for personal advice.')}
          <br/>
          {mr('वापरलेला अयनांश: लाहिरी (चित्रपक्ष)', 'Ayanamsha used: Lahiri (Chitrapaksha)')}
        </p>
      </div>
    </div>
  );
}

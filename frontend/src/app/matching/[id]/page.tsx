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
}

interface DoshaInfo {
  dosha_name: string;
  is_present: boolean;
  is_cancelled: boolean;
  cancellation_rule_mr: string | null;
  explanation_mr: string;
  explanation_en: string;
}

interface MatchResult {
  id: string;
  bride_name: string;
  groom_name: string;
  total_score: number;
  total_max: number;
  bride_manglik: boolean | null;
  groom_manglik: boolean | null;
  paid: boolean;
  resume_token: string;
  locked: Record<string, boolean>;
  verdict_mr?: string;
  verdict_en?: string;
  koota_breakdown?: KootaRow[];
  nadi_dosha?: DoshaInfo;
  bhakoot_dosha?: DoshaInfo;
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

  const pct = result.total_score / result.total_max;
  const verdictColor = pct >= 0.88 ? 'var(--success)' : pct >= 0.69 ? '#f59e0b' : pct >= 0.5 ? 'var(--saffron-400)' : 'var(--danger)';

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

      <div className="page-container" style={{ paddingTop: 24 }}>

        {/* ─── Hero score card ───────────────────────────────── */}
        <div className="card animate-fade-up" style={{ padding: '24px', marginBottom: 16, textAlign: 'center', background: 'linear-gradient(135deg, rgba(240,124,0,0.08) 0%, rgba(201,162,39,0.06) 100%)', borderColor: 'rgba(240,124,0,0.25)' }}>
          <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '1rem', color: 'var(--text-secondary)', marginBottom: 6 }}>
            {result.bride_name} <span style={{ color: 'var(--saffron-400)' }}>↔</span> {result.groom_name}
          </div>
          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 12 }}>
            <ScoreRing score={result.total_score} max={result.total_max} />
          </div>
          <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '1rem', fontWeight: 600, color: verdictColor, marginBottom: 4 }}>
            {result.paid && result.verdict_mr ? (lang === 'mr' ? result.verdict_mr : (result.verdict_en ?? result.verdict_mr)) : (
              pct >= 0.88 ? mr('उत्तम जुळणी 🌟', 'Excellent Match 🌟') :
              pct >= 0.69 ? mr('चांगली जुळणी ✅', 'Good Match ✅') :
              pct >= 0.5  ? mr('साधारण जुळणी ⚠️', 'Average Match ⚠️') :
              mr('अल्प जुळणी ❗', 'Low Compatibility ❗')
            )}
          </div>
          <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            {mr(`${result.total_score} गुण / ३६ पैकी`, `${result.total_score} points out of 36`)}
          </div>
        </div>

        {/* ─── Manglik status ────────────────────────────────── */}
        <div className="card" style={{ padding: '16px 20px', marginBottom: 16 }}>
          <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: 10 }}>
            🔴 {mr('मंगळ दोष', 'Mangal Dosha')}
          </div>
          <div style={{ display: 'flex', gap: 12 }}>
            <div style={{ flex: 1, textAlign: 'center' }}>
              <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: 4 }}>👰 {result.bride_name}</div>
              <span className={`chip ${result.bride_manglik ? 'chip-red' : 'chip-green'}`} style={{ fontSize: '0.8rem' }}>
                {result.bride_manglik === null ? mr('अज्ञात', 'Unknown') : result.bride_manglik ? mr('मंगळ दोष ⚠️', 'Manglik ⚠️') : mr('दोष नाही ✅', 'No Dosha ✅')}
              </span>
            </div>
            <div style={{ width: 1, background: 'var(--border-subtle)' }} />
            <div style={{ flex: 1, textAlign: 'center' }}>
              <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: 4 }}>🤵 {result.groom_name}</div>
              <span className={`chip ${result.groom_manglik ? 'chip-red' : 'chip-green'}`} style={{ fontSize: '0.8rem' }}>
                {result.groom_manglik === null ? mr('अज्ञात', 'Unknown') : result.groom_manglik ? mr('मंगळ दोष ⚠️', 'Manglik ⚠️') : mr('दोष नाही ✅', 'No Dosha ✅')}
              </span>
            </div>
          </div>
        </div>

        {/* ─── Paid: Koota breakdown ─────────────────────────── */}
        {result.paid && result.koota_breakdown ? (
          <div style={{ marginBottom: 16 }}>
            <h2 style={{ fontFamily: 'var(--font-devanagari)', fontSize: '1rem', fontWeight: 700, marginBottom: 12, color: 'var(--text-primary)' }}>
              {mr('८-कूट तक्ता', '8-Koota Table')}
            </h2>
            <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
              {result.koota_breakdown.map((k, i) => (
                <div key={i} style={{ padding: '12px 16px', borderBottom: i < result.koota_breakdown!.length - 1 ? '1px solid var(--border-subtle)' : 'none' }}>
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
                    <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
                      {lang === 'mr' ? k.notes_mr : k.notes_en}
                    </div>
                  )}
                </div>
              ))}
              {/* Total row */}
              <div style={{ padding: '12px 16px', background: 'rgba(240,124,0,0.06)', borderTop: '1.5px solid rgba(240,124,0,0.2)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontFamily: 'var(--font-devanagari)', fontWeight: 700, color: 'var(--text-primary)' }}>
                  {mr('एकूण गुण', 'Total Score')}
                </span>
                <span style={{ fontFamily: 'Inter', fontSize: '1.1rem', fontWeight: 800, color: 'var(--gold-400)' }}>
                  {result.total_score}/{result.total_max}
                </span>
              </div>
            </div>
          </div>
        ) : (
          /* Locked koota teaser */
          <div className="locked-overlay" style={{ marginBottom: 16 }}>
            <div className="locked-blur">
              <div className="card" style={{ padding: '14px 16px' }}>
                <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: 10 }}>८-कूट तक्ता</div>
                {['वर्ण', 'वश्य', 'तारा', 'योनी', 'ग्रह मैत्री', 'गण', 'भकूट', 'नाडी'].map((k, i) => (
                  <div key={i} style={{ display: 'flex', gap: 8, marginBottom: 6, alignItems: 'center' }}>
                    <span style={{ fontFamily: 'var(--font-devanagari)', flex: '0 0 90px', fontSize: '0.82rem', color: 'var(--text-secondary)' }}>{k}</span>
                    <div style={{ flex: 1, height: 6, background: 'rgba(255,255,255,0.06)', borderRadius: 999 }} />
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.78rem' }}>●/●</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ─── Paid: Dosha analysis ──────────────────────────── */}
        {result.paid && (result.nadi_dosha || result.bhakoot_dosha) && (
          <div style={{ marginBottom: 16 }}>
            <h2 style={{ fontFamily: 'var(--font-devanagari)', fontSize: '1rem', fontWeight: 700, marginBottom: 10, color: 'var(--text-primary)' }}>
              {mr('दोष विश्लेषण', 'Dosha Analysis')}
            </h2>
            {[result.nadi_dosha, result.bhakoot_dosha].filter(Boolean).map((d, i) => d && (
              <div key={i} className="card" style={{ padding: '14px 16px', marginBottom: 8, borderColor: d.is_present && !d.is_cancelled ? 'rgba(239,68,68,0.3)' : 'rgba(34,197,94,0.3)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                  <span style={{ fontSize: '1.1rem' }}>{d.is_present && !d.is_cancelled ? '⚠️' : '✅'}</span>
                  <span style={{ fontFamily: 'var(--font-devanagari)', fontWeight: 700, fontSize: '0.95rem', color: 'var(--text-primary)' }}>{d.dosha_name}</span>
                  <span className={`chip ${d.is_present && !d.is_cancelled ? 'chip-red' : 'chip-green'}`} style={{ fontSize: '0.72rem' }}>
                    {d.is_present ? (d.is_cancelled ? mr('रद्द ✅', 'Cancelled ✅') : mr('आहे ⚠️', 'Present ⚠️')) : mr('नाही ✅', 'Not Present ✅')}
                  </span>
                </div>
                <p style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                  {lang === 'mr' ? d.explanation_mr : d.explanation_en}
                </p>
                {d.is_cancelled && d.cancellation_rule_mr && (
                  <div style={{ marginTop: 6, padding: '6px 10px', background: 'rgba(34,197,94,0.08)', borderRadius: 8, fontFamily: 'var(--font-devanagari)', fontSize: '0.75rem', color: '#4ade80' }}>
                    📌 {mr('रद्दीकरण नियम:', 'Cancellation rule:')} {d.cancellation_rule_mr}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* ─── Paywall CTA ───────────────────────────────────── */}
        {!result.paid && (
          <div className="paywall-card" style={{ marginBottom: 20 }}>
            <div style={{ fontSize: '1.3rem', marginBottom: 8 }}>🔓</div>
            <h2 style={{ fontFamily: 'var(--font-devanagari)', fontSize: '1.1rem', fontWeight: 800, marginBottom: 12, color: 'var(--text-primary)' }}>
              {mr('संपूर्ण जुळणी अहवाल', 'Full Matching Report')}
            </h2>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px 16px', marginBottom: 16, textAlign: 'left' }}>
              {[
                mr('✓ ८-कूट तपशील', '✓ 8-Koota breakdown'),
                mr('✓ नाडी दोष विश्लेषण', '✓ Nadi Dosha analysis'),
                mr('✓ भकूट दोष तपशील', '✓ Bhakoot Dosha detail'),
                mr('✓ मंगळ सुसंगतता', '✓ Mangal compatibility'),
                mr('✓ मराठी निकाल', '✓ Marathi verdict'),
                mr('✓ PDF + WhatsApp', '✓ PDF + WhatsApp share'),
              ].map((f, i) => (
                <div key={i} style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.82rem', color: 'var(--text-secondary)' }}>{f}</div>
              ))}
            </div>
            <PaywallButton
              productType="matching"
              recordId={id as string}
              resumeToken={result.resume_token ?? ''}
              buyerName={`${result.bride_name} / ${result.groom_name}`}
              label={mr('संपूर्ण जुळणी अहवाल', 'Full Matching Report')}
              sublabel={mr('एकदाच पेमेंट · आजन्म अ‍ॅक्सेस', 'One-time payment')}
              description={`पत्रिका जुळणी — ${result.bride_name} ↔ ${result.groom_name}`}
              pollUrl={`/api/v1/matchings/${id}`}
              onUnlocked={() => window.location.reload()}
              fullWidth
            />
          </div>
        )}

                {/* ─── Paid actions: PDF + WhatsApp ──────────────── */}
        {result.paid && (
          <div style={{ display: 'flex', gap: 10, marginBottom: 20, flexWrap: 'wrap' }}>
            <a
              href={`${process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'}/api/v1/matchings/${id}/pdf`}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                flex: 1, minWidth: 140, display: 'flex', alignItems: 'center', justifyContent: 'center',
                gap: 8, padding: '12px 18px', borderRadius: 'var(--radius-lg)',
                background: 'rgba(240,124,0,0.1)', border: '1px solid rgba(240,124,0,0.3)',
                color: 'var(--saffron-400)', fontFamily: 'var(--font-devanagari)',
                fontWeight: 700, fontSize: '0.9rem', textDecoration: 'none', cursor: 'pointer',
              }}
            >
              📄 {mr('PDF डाउनलोड', 'Download PDF')}
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
                gap: 8, padding: '12px 18px', borderRadius: 'var(--radius-lg)',
                background: 'rgba(37,211,102,0.1)', border: '1px solid rgba(37,211,102,0.3)',
                color: '#25d366', fontFamily: 'var(--font-devanagari)',
                fontWeight: 700, fontSize: '0.9rem', textDecoration: 'none', cursor: 'pointer',
              }}
            >
              💬 {mr('WhatsApp वर शेअर करा', 'Share on WhatsApp')}
            </a>
          </div>
        )}

        <p className="disclaimer">
          {mr('हे परिणाम मार्गदर्शनासाठी आहेत. वैयक्तिक सल्ल्यासाठी तज्ञ ज्योतिषांचा सल्ला घ्या.', 'Results are for guidance only. Consult an expert astrologer for personal advice.')}
        </p>
      </div>
    </div>
  );
}

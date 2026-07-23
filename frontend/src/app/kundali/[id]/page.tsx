'use client';
import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { getKundali, type KundaliResponse, type PlanetPosition } from '@/lib/api';
import PaywallButton from '@/components/PaywallButton';
import { whatsappShareUrl } from '@/lib/share';

type Lang = 'mr' | 'en';

// Helper: ordinal suffix in Marathi
const ORDINAL_MR = ['', 'पहिल्या', 'दुसऱ्या', 'तिसऱ्या', 'चौथ्या', 'पाचव्या', 'सहाव्या', 'सातव्या', 'आठव्या', 'नवव्या', 'दहाव्या', 'अकराव्या', 'बाराव्या'];

function formatDate(dateStr: string) {
  try {
    return new Date(dateStr).toLocaleDateString('mr-IN', { year: 'numeric', month: 'long', day: 'numeric' });
  } catch { return dateStr; }
}

function ScoreRing({ score, max }: { score: number; max: number }) {
  const pct = (score / max) * 100;
  const color = pct >= 90 ? '#22c55e' : pct >= 70 ? '#f59e0b' : pct >= 50 ? '#f07c00' : '#ef4444';
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <svg width={80} height={80} viewBox="0 0 80 80">
        <circle cx={40} cy={40} r={34} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth={7} />
        <circle cx={40} cy={40} r={34} fill="none" stroke={color} strokeWidth={7}
          strokeDasharray={`${2 * Math.PI * 34 * pct / 100} ${2 * Math.PI * 34}`}
          strokeLinecap="round" transform="rotate(-90 40 40)" style={{ transition: 'stroke-dasharray 1s ease' }} />
        <text x="50%" y="50%" dominantBaseline="middle" textAnchor="middle" fontSize={18} fontWeight={800} fill={color}>{score}</text>
      </svg>
      <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: 2 }}>/ {max}</span>
    </div>
  );
}

export default function KundaliResultPage() {
  const params = useParams();
  const router = useRouter();
  const id = params?.id as string;
  const [lang, setLang] = useState<Lang>('mr');
  const [activeChart, setActiveChart] = useState<'d1' | 'd9' | 'chalit' | 'moon'>('d1');
  const [kundali, setKundali] = useState<KundaliResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const mr = (m: string, e: string) => lang === 'mr' ? m : e;

  useEffect(() => {
    if (!id) return;
    getKundali(id)
      .then(setKundali)
      .catch(e => setError(e.message ?? 'Error'))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return (
    <div style={{ minHeight: '100dvh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: '2.5rem', animation: 'spin-slow 3s linear infinite', marginBottom: 16 }}>🪐</div>
        <div style={{ fontFamily: 'var(--font-devanagari)', color: 'var(--text-secondary)' }}>
          {mr('लोड होत आहे...', 'Loading...')}
        </div>
      </div>
    </div>
  );

  if (error || !kundali) return (
    <div style={{ minHeight: '100dvh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24, textAlign: 'center' }}>
      <div>
        <div style={{ fontSize: '2rem', marginBottom: 12 }}>⚠️</div>
        <div style={{ fontFamily: 'var(--font-devanagari)', color: 'var(--danger)' }}>
          {mr('कुंडली सापडली नाही.', 'Kundali not found.')}
        </div>
        <button className="btn-secondary" style={{ marginTop: 20 }} onClick={() => router.push('/')}>
          {mr('मुख्य पृष्ठावर जा', 'Go Home')}
        </button>
      </div>
    </div>
  );

  const locked = kundali.locked;

  return (
    <div style={{ minHeight: '100dvh', paddingBottom: 60 }}>
      {/* Navbar */}
      <nav className="navbar">
        <div style={{ maxWidth: 680, margin: '0 auto', padding: '0 16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: 56 }}>
          <button onClick={() => router.push('/')} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', fontFamily: 'var(--font-devanagari)' }}>
            ‹ {mr('मुख्य', 'Home')}
          </button>
          <span style={{ fontFamily: 'var(--font-devanagari)', fontWeight: 700, color: 'var(--saffron-400)', fontSize: '1rem' }}>
            🪐 {mr('जन्मकुंडली', 'Kundali')}
          </span>
          <div className="lang-toggle">
            <button className={`lang-btn${lang === 'mr' ? ' active' : ''}`} onClick={() => setLang('mr')}>मराठी</button>
            <button className={`lang-btn${lang === 'en' ? ' active' : ''}`} onClick={() => setLang('en')}>EN</button>
          </div>
        </div>
      </nav>

      <div className="page-container" style={{ paddingTop: 24 }}>

        {/* ─── Hero card ─────────────────────────────────── */}
        <div className="card animate-fade-up" style={{ padding: '24px', marginBottom: 16, background: 'linear-gradient(135deg, rgba(240,124,0,0.08) 0%, rgba(201,162,39,0.05) 100%)', borderColor: 'rgba(240,124,0,0.2)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: 4 }}>
                {kundali.name}
              </div>
              <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                {kundali.gender === 'male' ? mr('♂ मुलगा', '♂ Male') : mr('♀ मुलगी', '♀ Female')} &nbsp;·&nbsp;
                {formatDate(kundali.dob)} &nbsp;·&nbsp;
                {kundali.time_of_birth ?? mr('वेळ नाही', 'No time')}
              </div>
              <div style={{ fontFamily: 'var(--font-sans)', fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: 4 }}>
                📍 {kundali.place_text}
              </div>
            </div>
            <span style={{ fontSize: '2rem', opacity: 0.5 }}>ॐ</span>
          </div>

          {kundali.time_accuracy === 'approximate' && (
            <div style={{ marginTop: 10, padding: '8px 12px', background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.2)', borderRadius: 8, fontFamily: 'var(--font-devanagari)', fontSize: '0.78rem', color: 'var(--warning)' }}>
              ⚠️ {mr('अंदाजे वेळ — लग्न अचूक नसू शकते', 'Approximate time — Lagna may be inaccurate')}
            </div>
          )}
          {kundali.time_accuracy === 'unknown' && (
            <div style={{ marginTop: 10, padding: '8px 12px', background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.2)', borderRadius: 8, fontFamily: 'var(--font-devanagari)', fontSize: '0.78rem', color: 'var(--warning)' }}>
              ⚠️ {mr('वेळ माहित नाही — फक्त रास-नक्षत्र उपलब्ध', 'Time unknown — only Rashi & Nakshatra available')}
            </div>
          )}
        </div>

        {/* ─── Free fields grid ──────────────────────────── */}
        <div className="animate-children" style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 10, marginBottom: 16 }}>
          {[
            { labelMr: 'रास (Rashi)', labelEn: 'Rashi (Moon Sign)', valueMr: kundali.rashi?.name_mr, valueEn: kundali.rashi?.name_en },
            { labelMr: 'नक्षत्र (Nakshatra)', labelEn: 'Nakshatra', valueMr: kundali.nakshatra?.name_mr, valueEn: kundali.nakshatra?.name_en, extra: `पाद ${kundali.nakshatra?.pada ?? ''}` },
            { labelMr: 'लग्न (Lagna)', labelEn: 'Ascendant', valueMr: kundali.lagna?.name_mr ?? (kundali.time_accuracy === 'unknown' ? '—' : '—'), valueEn: kundali.lagna?.name_en ?? '—' },
            { labelMr: 'गण (Gana)', labelEn: 'Gana', valueMr: kundali.gana?.name_mr, valueEn: kundali.gana?.value },
            { labelMr: 'नाडी (Nadi)', labelEn: 'Nadi', valueMr: kundali.nadi?.name_mr, valueEn: kundali.nadi?.value },
            { labelMr: 'वर्ण (Varna)', labelEn: 'Varna', valueMr: kundali.varna?.name_mr, valueEn: kundali.varna?.value },
          ].map(({ labelMr, labelEn, valueMr, valueEn, extra }, i) => (
            <div key={i} className="result-card animate-fade-up">
              <div className="result-card-label">{lang === 'mr' ? labelMr : labelEn}</div>
              <div className="result-card-value">
                {lang === 'mr' ? (valueMr ?? '—') : (valueEn ?? '—')}
                {extra && <span className="en">{extra}</span>}
              </div>
            </div>
          ))}
        </div>

        {/* ─── Avakahada Chakra (अवकहडा चक्र) ────────────────────── */}
        {kundali.avakahada && (
          <div className="card animate-fade-up" style={{ padding: '18px 20px', marginBottom: 16 }}>
            <h2 style={{ fontFamily: 'var(--font-devanagari)', fontSize: '1rem', fontWeight: 700, marginBottom: 14, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: 8 }}>
              ☸️ {mr('अवकहडा चक्र (Avakahada Chakra)', 'Avakahada Chakra')}
            </h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px 14px' }}>
              {[
                { label: mr('वर्ण', 'Varna'), val: kundali.avakahada.varna_mr },
                { label: mr('वश्य', 'Vashya'), val: kundali.avakahada.vashya_mr },
                { label: mr('तत्व', 'Tatva'), val: kundali.avakahada.tatva_mr },
                { label: mr('योनि', 'Yoni'), val: kundali.avakahada.yoni_mr },
                { label: mr('गण', 'Gana'), val: kundali.avakahada.gana_mr },
                { label: mr('नाडी', 'Nadi'), val: kundali.avakahada.nadi_mr },
                { label: mr('करण', 'Karana'), val: kundali.avakahada.karana_mr || '—' },
                { label: mr('लग्न राशी', 'Lagna'), val: kundali.avakahada.lagna_mr || '—' },
              ].map((item, idx) => (
                <div key={idx} style={{ padding: '8px 10px', background: 'rgba(255,255,255,0.03)', borderRadius: 8, border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 2 }}>{item.label}</div>
                  <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.9rem', fontWeight: 600, color: 'var(--gold-400)' }}>{item.val}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ─── Divider ───────────────────────────────────── */}
        <div className="divider-gold" />

        {/* ─── PAID: Planet Table ────────────────────────── */}
        {kundali.paid && kundali.planet_positions && kundali.planet_positions.length > 0 ? (
          <div style={{ marginBottom: 16 }}>
            <h2 style={{ fontFamily: 'var(--font-devanagari)', fontSize: '1.1rem', fontWeight: 700, marginBottom: 12, color: 'var(--text-primary)' }}>
              🪐 {mr('ग्रह स्थिती', 'Planet Positions')}
            </h2>
            <div className="card" style={{ overflow: 'hidden', padding: 0 }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: 'var(--font-devanagari)', fontSize: '0.82rem' }}>
                <thead>
                  <tr style={{ background: 'rgba(255,255,255,0.04)', borderBottom: '1px solid var(--border-subtle)' }}>
                    {[mr('ग्रह', 'Planet'), mr('राशी', 'Sign'), mr('घर', 'House'), mr('नक्षत्र', 'Nakshatra'), mr('वक्री', 'R')].map(h => (
                      <th key={h} style={{ padding: '10px 10px', textAlign: 'left', color: 'var(--text-muted)', fontWeight: 600, fontSize: '0.75rem', letterSpacing: '0.04em' }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {kundali.planet_positions.map((p: PlanetPosition, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                      <td style={{ padding: '10px 10px', fontWeight: 600, color: p.is_exalted ? 'var(--success)' : p.is_debilitated ? 'var(--danger)' : 'var(--text-primary)' }}>
                        {lang === 'mr' ? p.planet_mr : p.planet_en}
                        {p.is_exalted && <span title={mr('उच्च', 'Exalted')} style={{ fontSize: '0.65rem', marginLeft: 3 }}>⬆</span>}
                        {p.is_debilitated && <span title={mr('नीच', 'Debilitated')} style={{ fontSize: '0.65rem', marginLeft: 3 }}>⬇</span>}
                      </td>
                      <td style={{ padding: '10px 10px', color: 'var(--text-secondary)' }}>{lang === 'mr' ? p.rashi.name_mr : p.rashi.name_en}</td>
                      <td style={{ padding: '10px 10px', color: 'var(--text-secondary)' }}>{p.house}</td>
                      <td style={{ padding: '10px 10px', color: 'var(--text-secondary)' }}>{lang === 'mr' ? p.nakshatra.name_mr : p.nakshatra.name_en}</td>
                      <td style={{ padding: '10px 10px', color: p.retrograde ? 'var(--warning)' : 'var(--text-muted)' }}>
                        {p.retrograde ? mr('वक्री', 'R') : '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : locked.planet_positions && (
          /* Locked planet table teaser */
          <div className="locked-overlay" style={{ marginBottom: 16 }}>
            <div className="locked-blur">
              <div className="card" style={{ padding: '12px 16px' }}>
                <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: 8 }}>
                  {mr('ग्रह स्थिती', 'Planet Positions')}
                </div>
                {['सूर्य', 'चंद्र', 'मंगळ', 'बुध', 'गुरु'].map((p, i) => (
                  <div key={i} style={{ padding: '8px 0', borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-secondary)', fontFamily: 'var(--font-devanagari)', fontSize: '0.85rem' }}>
                    {p} ··· ··· ···
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ─── PAID: Dasha ───────────────────────────────── */}
        {kundali.paid && kundali.dasha ? (
          <div className="card" style={{ padding: '18px 20px', marginBottom: 16 }}>
            <h2 style={{ fontFamily: 'var(--font-devanagari)', fontSize: '1rem', fontWeight: 700, marginBottom: 14, color: 'var(--text-primary)' }}>
              ⏳ {mr('सध्याची दशा', 'Current Dasha')}
            </h2>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div>
                <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 4 }}>{mr('महादशा', 'Mahadasha')}</div>
                <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '1.1rem', fontWeight: 700, color: 'var(--gold-400)' }}>
                  {lang === 'mr' ? kundali.dasha.mahadasha_lord_mr : kundali.dasha.mahadasha_lord_en}
                </div>
                <div style={{ fontFamily: 'var(--font-sans)', fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 2 }}>
                  {kundali.dasha.mahadasha_start} → {kundali.dasha.mahadasha_end}
                </div>
              </div>
              <div>
                <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 4 }}>{mr('अंतर्दशा', 'Antardasha')}</div>
                <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '1.1rem', fontWeight: 700, color: 'var(--saffron-400)' }}>
                  {lang === 'mr' ? kundali.dasha.antardasha_lord_mr : kundali.dasha.antardasha_lord_en}
                </div>
                <div style={{ fontFamily: 'var(--font-sans)', fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 2 }}>
                  {kundali.dasha.antardasha_start} → {kundali.dasha.antardasha_end}
                </div>
              </div>
            </div>

            {/* Full Vimshottari Mahadasha Table */}
            {kundali.mahadasha_table && kundali.mahadasha_table.length > 0 && (
              <div style={{ marginTop: 18, paddingTop: 14, borderTop: '1px solid var(--border-subtle)' }}>
                <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.88rem', fontWeight: 700, marginBottom: 10, color: 'var(--text-secondary)' }}>
                  📜 {mr('विंशोत्तरी महादशा सारणी (पूर्ण आयुष्य)', 'Vimshottari Mahadasha Table (Full Life)')}
                </div>
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', fontSize: '0.8rem', borderCollapse: 'collapse' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-muted)', textAlign: 'left' }}>
                        <th style={{ padding: '6px 4px' }}>{mr('स्वामी', 'Lord')}</th>
                        <th style={{ padding: '6px 4px' }}>{mr('वर्षे', 'Years')}</th>
                        <th style={{ padding: '6px 4px' }}>{mr('प्रारंभ', 'Start')}</th>
                        <th style={{ padding: '6px 4px' }}>{mr('समाप्ती', 'End')}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {kundali.mahadasha_table.map((m, idx) => (
                        <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)', color: m.lord_mr === kundali.dasha?.mahadasha_lord_mr ? 'var(--gold-400)' : 'var(--text-secondary)', fontWeight: m.lord_mr === kundali.dasha?.mahadasha_lord_mr ? 700 : 400 }}>
                          <td style={{ padding: '6px 4px' }}>{lang === 'mr' ? m.lord_mr : m.lord_en}</td>
                          <td style={{ padding: '6px 4px' }}>{m.years}y</td>
                          <td style={{ padding: '6px 4px' }}>{m.start_date}</td>
                          <td style={{ padding: '6px 4px' }}>{m.end_date}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        ) : locked.dasha && (
          <div className="locked-overlay" style={{ marginBottom: 16 }}>
            <div className="locked-blur">
              <div className="card" style={{ padding: '16px 18px' }}>
                <div style={{ fontFamily: 'var(--font-devanagari)', color: 'var(--text-muted)', fontSize: '0.82rem' }}>{mr('सध्याची दशा', 'Current Dasha')}</div>
                <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '1.3rem', color: 'var(--gold-400)', marginTop: 4 }}>●●● महादशा</div>
                <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.9rem', color: 'var(--saffron-400)', marginTop: 4 }}>●●● अंतर्दशा</div>
              </div>
            </div>
          </div>
        )}

        {/* ─── PAID: Mangal Dosha ─────────────────────────── */}
        {kundali.paid && kundali.mangal_dosha ? (
          <div className="card" style={{ padding: '18px 20px', marginBottom: 16, borderColor: kundali.mangal_dosha.is_manglik ? 'rgba(239,68,68,0.3)' : 'rgba(34,197,94,0.3)', background: kundali.mangal_dosha.is_manglik ? 'rgba(239,68,68,0.04)' : 'rgba(34,197,94,0.04)' }}>
            <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '1rem', fontWeight: 700, marginBottom: 10, color: 'var(--text-primary)' }}>
              🔴 {mr('मंगळ दोष', 'Mangal Dosha')}
            </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 10 }}>
              <span className={`chip ${kundali.mangal_dosha.severity === 'HIGH' ? 'chip-red' : kundali.mangal_dosha.severity === 'MILD' ? 'chip-orange' : kundali.mangal_dosha.is_manglik ? 'chip-red' : 'chip-green'}`} style={{ fontSize: '0.9rem' }}>
                {kundali.mangal_dosha.severity === 'HIGH' ? mr('कडक मंगळ दोष ⚠️', 'High Manglik ⚠️') : kundali.mangal_dosha.severity === 'MILD' ? mr('अंशिक/सौम्य मंगळ ⚠️', 'Mild Manglik ⚠️') : kundali.mangal_dosha.cancellation_applied ? mr('दोष रद्द ✅', 'Dosha Cancelled ✅') : mr('मंगळ दोष नाही ✅', 'Not Manglik ✅')}
              </span>
              {kundali.mangal_dosha.mars_house && (
                <span style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                  {mr(`मंगळ ${ORDINAL_MR[kundali.mangal_dosha.mars_house] ?? kundali.mangal_dosha.mars_house.toString() + 'व्या'} घरात`, `Mars in house ${kundali.mangal_dosha.mars_house}`)}
                </span>
              )}
            </div>
            <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              {lang === 'mr' ? kundali.mangal_dosha.explanation_mr : kundali.mangal_dosha.explanation_en}
            </div>
          </div>
        ) : locked.mangal_dosha && (
          <div className="locked-overlay" style={{ marginBottom: 16 }}>
            <div className="locked-blur">
              <div className="card" style={{ padding: '14px 16px', display: 'flex', alignItems: 'center', gap: 10 }}>
                <span style={{ fontSize: '1.3rem' }}>🔴</span>
                <div>
                  <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.85rem', color: 'var(--text-muted)' }}>{mr('मंगळ दोष', 'Mangal Dosha')}</div>
                  <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>●●●●●●●●</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ─── Kundali Charts (D1, D9, Chalit, Moon) ─────────── */}
        {(kundali.chart_d1_svg || kundali.navamsa_chart_svg || kundali.chalit_chart_svg || kundali.moon_chart_svg) && (
          <div className="card animate-fade-up" style={{ padding: '20px', marginBottom: 16, textAlign: 'center' }}>
            <h3 style={{ fontFamily: 'var(--font-devanagari)', fontSize: '1rem', fontWeight: 700, marginBottom: 12, color: 'var(--text-primary)' }}>
              🌌 {mr('कुंडली तक्ते (Horoscope Charts)', 'Horoscope Charts')}
            </h3>

            {/* Tab selector */}
            <div style={{ display: 'flex', justifyContent: 'center', gap: 6, flexWrap: 'wrap', marginBottom: 16 }}>
              {kundali.chart_d1_svg && (
                <button
                  className={`btn-tab ${activeChart === 'd1' ? 'active' : ''}`}
                  onClick={() => setActiveChart('d1')}
                  style={{
                    padding: '6px 12px', borderRadius: 20, border: '1px solid var(--border-subtle)',
                    background: activeChart === 'd1' ? 'var(--saffron-500)' : 'rgba(255,255,255,0.05)',
                    color: activeChart === 'd1' ? '#fff' : 'var(--text-secondary)',
                    fontFamily: 'var(--font-devanagari)', fontSize: '0.8rem', cursor: 'pointer', fontWeight: 600
                  }}
                >
                  {mr('लग्न कुंडली', 'Lagna')}
                </button>
              )}
              {kundali.navamsa_chart_svg && (
                <button
                  className={`btn-tab ${activeChart === 'd9' ? 'active' : ''}`}
                  onClick={() => setActiveChart('d9')}
                  style={{
                    padding: '6px 12px', borderRadius: 20, border: '1px solid var(--border-subtle)',
                    background: activeChart === 'd9' ? 'var(--saffron-500)' : 'rgba(255,255,255,0.05)',
                    color: activeChart === 'd9' ? '#fff' : 'var(--text-secondary)',
                    fontFamily: 'var(--font-devanagari)', fontSize: '0.8rem', cursor: 'pointer', fontWeight: 600
                  }}
                >
                  {mr('नवमांश कुंडली', 'Navamsha')}
                </button>
              )}
              {kundali.chalit_chart_svg && (
                <button
                  className={`btn-tab ${activeChart === 'chalit' ? 'active' : ''}`}
                  onClick={() => setActiveChart('chalit')}
                  style={{
                    padding: '6px 12px', borderRadius: 20, border: '1px solid var(--border-subtle)',
                    background: activeChart === 'chalit' ? 'var(--saffron-500)' : 'rgba(255,255,255,0.05)',
                    color: activeChart === 'chalit' ? '#fff' : 'var(--text-secondary)',
                    fontFamily: 'var(--font-devanagari)', fontSize: '0.8rem', cursor: 'pointer', fontWeight: 600
                  }}
                >
                  {mr('चलित कुंडली', 'Chalit')}
                </button>
              )}
              {kundali.moon_chart_svg && (
                <button
                  className={`btn-tab ${activeChart === 'moon' ? 'active' : ''}`}
                  onClick={() => setActiveChart('moon')}
                  style={{
                    padding: '6px 12px', borderRadius: 20, border: '1px solid var(--border-subtle)',
                    background: activeChart === 'moon' ? 'var(--saffron-500)' : 'rgba(255,255,255,0.05)',
                    color: activeChart === 'moon' ? '#fff' : 'var(--text-secondary)',
                    fontFamily: 'var(--font-devanagari)', fontSize: '0.8rem', cursor: 'pointer', fontWeight: 600
                  }}
                >
                  {mr('चंद्र राशी', 'Moon')}
                </button>
              )}
            </div>

            {/* Active chart SVG */}
            <div 
              style={{ 
                maxWidth: '360px', 
                margin: '0 auto', 
                background: 'rgba(255,255,255,0.02)',
                borderRadius: 'var(--radius-md)',
                padding: '10px',
                border: '1px solid var(--border-subtle)',
                display: 'flex',
                justifyContent: 'center'
              }}
              dangerouslySetInnerHTML={{ 
                __html: (activeChart === 'd9' && kundali.navamsa_chart_svg) 
                  ? kundali.navamsa_chart_svg 
                  : (activeChart === 'chalit' && kundali.chalit_chart_svg)
                  ? kundali.chalit_chart_svg
                  : (activeChart === 'moon' && kundali.moon_chart_svg)
                  ? kundali.moon_chart_svg
                  : (kundali.chart_d1_svg || '')
              }} 
            />
          </div>
        )}

        {/* ─── Divider ───────────────────────────────────── */}
        <div className="divider-gold" />

        {/* ─── PAID: Written Analysis ─────────────────────── */}
        {kundali.paid && kundali.written_analysis ? (
          <div className="card" style={{ padding: '18px 20px', marginBottom: 16 }}>
            <h2 style={{ fontFamily: 'var(--font-devanagari)', fontSize: '1rem', fontWeight: 700, marginBottom: 14, color: 'var(--text-primary)' }}>
              📝 {mr('विश्लेषण', 'Analysis')}
            </h2>
            {[
              { label: mr('रास विश्लेषण', 'Rashi Analysis'), text: kundali.written_analysis.rashi_analysis_mr },
              { label: mr('नक्षत्र', 'Nakshatra'), text: kundali.written_analysis.nakshatra_analysis_mr },
              { label: mr('लग्न विश्लेषण', 'Lagna Analysis'), text: kundali.written_analysis.lagna_analysis_mr },
              { label: mr('गण', 'Gana'), text: kundali.written_analysis.gana_analysis_mr },
              { label: mr('नाडी', 'Nadi'), text: kundali.written_analysis.nadi_analysis_mr },
              { label: mr('दशा', 'Dasha'), text: kundali.written_analysis.dasha_analysis_mr },
            ].filter(s => s.text).map(({ label, text }, i) => (
              <div key={i} style={{ marginBottom: 12, paddingBottom: 12, borderBottom: i < 5 ? '1px solid var(--border-subtle)' : 'none' }}>
                <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.75rem', color: 'var(--saffron-400)', fontWeight: 600, marginBottom: 4 }}>{label}</div>
                <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.65 }}>{text}</div>
              </div>
            ))}
          </div>
        ) : locked.written_analysis && (
          <div className="locked-overlay" style={{ marginBottom: 16 }}>
            <div className="locked-blur">
              <div className="card" style={{ padding: '16px 18px' }}>
                <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: 8 }}>📝 {mr('विश्लेषण', 'Analysis')}</div>
                <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                  वृषभ राशीचे जातक स्थिर, व्यावहारिक ●●● ●●●●●●
                </div>
                <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: 8 }}>
                  ●●●●● ●●●●● ●●●●●●●●
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ─── Paywall CTA ───────────────────────────────── */}
        {!kundali.paid && (
          <div className="paywall-card" style={{ marginBottom: 20 }}>
            <div style={{ fontSize: '1.5rem', marginBottom: 8 }}>🔓</div>
            <h2 style={{ fontFamily: 'var(--font-devanagari)', fontSize: '1.2rem', fontWeight: 800, marginBottom: 12, color: 'var(--text-primary)' }}>
              {mr('संपूर्ण अहवाल मिळवा', 'Get Full Report')}
            </h2>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px 16px', marginBottom: 18, textAlign: 'left' }}>
              {[
                mr('✓ सर्व ९ ग्रहांचे तपशील', '✓ All 9 planet positions'),
                mr('✓ मंगळ दोष विश्लेषण', '✓ Mangal Dosha analysis'),
                mr('✓ महादशा / अंतर्दशा', '✓ Mahadasha / Antardasha'),
                mr('✓ उत्तर भारतीय कुंडली चार्ट', '✓ North Indian Kundali chart'),
                mr('✓ लिखित विश्लेषण', '✓ Written analysis'),
                mr('✓ PDF + WhatsApp शेअर', '✓ PDF + WhatsApp share'),
              ].map((f, i) => (
                <div key={i} style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>{f}</div>
              ))}
            </div>
            <PaywallButton
              productType="kundali"
              recordId={id}
              resumeToken={kundali.resume_token ?? ''}
              buyerName={kundali.name}
              label={mr('संपूर्ण कुंडली अनलॉक करा', 'Unlock Full Kundali')}
              sublabel={mr('एकदाच पेमेंट · आजन्म अ‍ॅक्सेस', 'One-time payment · Lifetime access')}
              description={`जन्मकुंडली — ${kundali.name} — संपूर्ण अहवाल`}
              pollUrl={`/api/v1/kundalis/${id}`}
              onUnlocked={() => window.location.reload()}
              fullWidth
            />
          </div>
        )}

        {/* ─── Paid actions: PDF + WhatsApp ──────────────── */}
        {kundali.paid && (
          <div style={{ display: 'flex', gap: 10, marginBottom: 20, flexWrap: 'wrap' }}>
            <a
              href={`${process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'}/api/v1/kundalis/${id}/pdf`}
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
                type: 'kundali', id,
                name: kundali.name,
                rashi: kundali.rashi?.name_mr,
                nakshatra: kundali.nakshatra?.name_mr,
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
              💬 {mr('WhatsApp शेअर', 'Share on WhatsApp')}
            </a>
          </div>
        )}

        {/* ─── Upsell: Matching ──────────────────────────── */}
        <div className="card" style={{ padding: '16px 18px', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 14, cursor: 'pointer' }}
          onClick={() => router.push('/matching/new')}>
          <span style={{ fontSize: '1.8rem' }}>💍</span>
          <div style={{ flex: 1 }}>
            <div style={{ fontFamily: 'var(--font-devanagari)', fontWeight: 700, color: 'var(--text-primary)', marginBottom: 2 }}>
              {mr('पत्रिका जुळणी करा', 'Check Compatibility')}
            </div>
            <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
              {mr('ही कुंडली वापरून अष्टकूट जुळणी', 'Use this kundali for Ashtakoot matching')}
            </div>
          </div>
          <span style={{ color: 'var(--saffron-500)', fontSize: '1.2rem' }}>›</span>
        </div>

        {/* ─── Upsell: Biodata ───────────────────────────── */}
        <div className="card" style={{ padding: '16px 18px', marginBottom: 20, display: 'flex', alignItems: 'center', gap: 14, cursor: 'pointer' }}
          onClick={() => router.push('/biodata/new')}>
          <span style={{ fontSize: '1.8rem' }}>📄</span>
          <div style={{ flex: 1 }}>
            <div style={{ fontFamily: 'var(--font-devanagari)', fontWeight: 700, color: 'var(--text-primary)', marginBottom: 2 }}>
              {mr('मराठी बायोडाटा बनवा', 'Create Marathi Biodata')}
            </div>
            <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
              {mr('कुंडली माहिती आपोआप भरली जाईल!', 'Horoscope info will be auto-filled!')}
            </div>
          </div>
          <span className="chip chip-gold" style={{ fontSize: '0.72rem' }}>{mr('मोफत', 'Free')}</span>
          <span style={{ color: 'var(--saffron-500)', fontSize: '1.2rem' }}>›</span>
        </div>

        {/* Disclaimer */}
        <p className="disclaimer">
          {mr('हा अहवाल मार्गदर्शनासाठी आहे. वैयक्तिक सल्ल्यासाठी तज्ञ ज्योतिषांचा सल्ला घ्या.', 'This report is for guidance only. Consult an expert astrologer for personal advice.')}
          <br/>
          {mr('वापरलेला अयनांश: लाहिरी (चित्रपक्ष)', 'Ayanamsha used: Lahiri (Chitrapaksha)')}
        </p>
      </div>
    </div>
  );
}

'use client';
import Link from 'next/link';
import Script from 'next/script';
import { useState } from 'react';

const features = [
  { icon: '🪐', mr: 'अचूक गणना', en: 'Accurate Swiss Ephemeris calculations' },
  { icon: '🌙', mr: 'मोफत राशी-नक्षत्र', en: 'Free Rashi & Nakshatra' },
  { icon: '💍', mr: 'अष्टकूट जुळणी', en: '36-point Ashtakoot matching' },
  { icon: '📄', mr: 'सुंदर बायोडाटा', en: 'Beautiful Marathi biodata' },
];

const products = [
  {
    href: '/kundali/new',
    icon: '🪐',
    titleMr: 'जन्मकुंडली',
    titleEn: 'Kundali',
    descMr: 'रास, नक्षत्र, लग्न, दशा, मंगळ दोष',
    descEn: 'Rashi, Nakshatra, Lagna, Dasha, Mangal Dosha',
    priceMr: 'मोफत पूर्वावलोकन',
    priceEn: 'Free preview',
    paid: '₹49',
    primary: true,
  },
  {
    href: '/matching/new',
    icon: '💍',
    titleMr: 'पत्रिका जुळणी',
    titleEn: 'Kundali Matching',
    descMr: 'अष्टकूट गुण मिलन, नाडी-भकूट दोष',
    descEn: 'Ashtakoot Guna Milan, Dosha analysis',
    priceMr: 'मोफत स्कोअर',
    priceEn: 'Free score',
    paid: '₹79',
    primary: false,
  },
  {
    href: '/biodata/new',
    icon: '📄',
    titleMr: 'मराठी बायोडाटा',
    titleEn: 'Marathi Biodata',
    descMr: 'सुंदर PDF, WhatsApp रेडी',
    descEn: 'Beautiful PDF, WhatsApp ready',
    priceMr: '१००% मोफत',
    priceEn: '100% Free',
    paid: 'मोफत (Free)',
    primary: false,
  },
];

export default function HomePage() {
  const [lang, setLang] = useState<'mr' | 'en'>('mr');

  return (
    <div style={{ minHeight: '100dvh', paddingBottom: 60, overflowX: 'hidden' }}>
      <Script id="faq-schema" type="application/ld+json">
        {JSON.stringify({
          "@context": "https://schema.org",
          "@type": "FAQPage",
          "mainEntity": [
            {
              "@type": "Question",
              "name": "मराठी जन्मपत्रिका कशी तयार करावी?",
              "acceptedAnswer": {
                "@type": "Answer",
                "text": "माझी कुंडली (Mazee Kundali) वर तुम्ही तुमची जन्मतारीख, वेळ आणि ठिकाण टाकून अगदी मोफत अचूक जन्मपत्रिका तयार करू शकता."
              }
            },
            {
              "@type": "Question",
              "name": "लग्नासाठी पत्रिका कशी जुळवतात?",
              "acceptedAnswer": {
                "@type": "Answer",
                "text": "आमच्या 'पत्रिका जुळणी' टूलमध्ये वर आणि वधूची जन्म माहिती दिल्यास, सिस्टीम ३६ पैकी किती गुण जुळतात (Ashtakoot Guna Milan) हे अचूकपणे सांगते."
              }
            },
            {
              "@type": "Question",
              "name": "लग्नाचा बायोडाटा मोबाईलवर कसा बनवायचा?",
              "acceptedAnswer": {
                "@type": "Answer",
                "text": "माझी कुंडलीच्या 'बायोडाटा मेकर' मध्ये तुमची माहिती भरा आणि फक्त ५ मिनिटांत आकर्षक डिझाईनमध्ये तुमचा लग्नाचा बायोडाटा PDF स्वरूपात मिळवा."
              }
            }
          ]
        })}
      </Script>

      {/* ─── Navbar ───────────────────────────────────────── */}
      <nav className="navbar">
        <div style={{ maxWidth: 680, margin: '0 auto', padding: '0 16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: 56 }}>
          <div>
            <span style={{ fontFamily: 'var(--font-devanagari)', fontWeight: 700, fontSize: '1.15rem', color: 'var(--saffron-400)' }}>
              माझी कुंडली
            </span>
          </div>
          <div className="lang-toggle">
            <button className={`lang-btn${lang === 'mr' ? ' active' : ''}`} onClick={() => setLang('mr')}>मराठी</button>
            <button className={`lang-btn${lang === 'en' ? ' active' : ''}`} onClick={() => setLang('en')}>EN</button>
          </div>
        </div>
      </nav>

      {/* ─── Hero ─────────────────────────────────────────── */}
      <section style={{ padding: '48px 16px 32px', textAlign: 'center', maxWidth: 680, margin: '0 auto' }}>

        {/* Om symbol */}
        <div style={{ fontSize: '2.8rem', marginBottom: 12, filter: 'drop-shadow(0 0 12px rgba(240,124,0,0.6))' }}>ॐ</div>

        <h1 style={{
          fontFamily: 'var(--font-devanagari)',
          fontSize: 'clamp(1.6rem, 5vw, 2.2rem)',
          fontWeight: 800,
          lineHeight: 1.3,
          marginBottom: 12,
          color: 'var(--text-primary)',
        }}>
          {lang === 'mr' ? 'तुमची अचूक जन्मपत्रिका\nमोफत पाहा' : 'View Your Accurate Kundali\nfor Free'}
        </h1>

        <p style={{
          fontFamily: 'var(--font-devanagari)',
          color: 'var(--text-secondary)',
          fontSize: '1.05rem',
          marginBottom: 28,
          maxWidth: 460,
          margin: '0 auto 28px',
          lineHeight: 1.6,
        }}>
          {lang === 'mr'
            ? 'फक्त ५ माहिती द्या — रास, नक्षत्र, लग्न आणि बरेच काही तात्काळ मिळवा'
            : 'Enter 5 details — get Rashi, Nakshatra, Lagna & more instantly'}
        </p>

        {/* Trust badges */}
        <div style={{ display: 'flex', gap: 8, justifyContent: 'center', flexWrap: 'wrap', marginBottom: 32 }}>
          <span className="chip chip-gold">⚡ {lang === 'mr' ? 'अचूक गणना' : 'Accurate Calc'}</span>
          <span className="chip chip-saffron">⏱️ {lang === 'mr' ? '२ मिनिटांत' : 'In 2 Minutes'}</span>
          <span className="chip chip-green">✓ {lang === 'mr' ? 'मोफत पूर्वावलोकन' : 'Free Preview'}</span>
        </div>

        <Link href="/kundali/new" style={{ textDecoration: 'none' }}>
          <button className="btn-primary" style={{ fontSize: '1.1rem', padding: '16px 36px', minWidth: 220 }}>
            {lang === 'mr' ? '🪐 कुंडली बनवा' : '🪐 Generate Kundali'}
          </button>
        </Link>
      </section>

      {/* ─── Divider ──────────────────────────────────────── */}
      <div className="divider-gold" style={{ maxWidth: 400, margin: '0 auto 32px' }} />

      {/* ─── Product cards ────────────────────────────────── */}
      <section style={{ padding: '0 16px 40px', maxWidth: 680, margin: '0 auto' }}>
        <h2 style={{ fontFamily: 'var(--font-devanagari)', fontSize: '1.15rem', color: 'var(--text-secondary)', textAlign: 'center', marginBottom: 20 }}>
          {lang === 'mr' ? 'आमच्या सेवा' : 'Our Services'}
        </h2>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }} className="animate-children">
          {products.map((p) => (
            <Link href={p.href} key={p.href} style={{ textDecoration: 'none' }}>
              <div className={`card animate-fade-up`} style={{ padding: '18px 20px', display: 'flex', alignItems: 'center', gap: 16, cursor: 'pointer' }}>
                <span style={{ fontSize: '2rem', flexShrink: 0 }}>{p.icon}</span>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontFamily: 'var(--font-devanagari)', fontWeight: 700, fontSize: '1.05rem', color: 'var(--text-primary)', marginBottom: 2 }}>
                    {lang === 'mr' ? p.titleMr : p.titleEn}
                  </div>
                  <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                    {lang === 'mr' ? p.descMr : p.descEn}
                  </div>
                </div>
                <div style={{ textAlign: 'right', flexShrink: 0 }}>
                  <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.75rem', color: 'var(--success)', marginBottom: 2 }}>
                    {lang === 'mr' ? p.priceMr : p.priceEn}
                  </div>
                  <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--gold-400)' }}>{p.paid}</div>
                </div>
                <span style={{ color: 'var(--saffron-500)', fontSize: '1.2rem', marginLeft: 4 }}>›</span>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* ─── Feature grid ─────────────────────────────────── */}
      <section style={{ padding: '0 16px 48px', maxWidth: 680, margin: '0 auto' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 10 }}>
          {features.map((f, i) => (
            <div key={i} style={{
              padding: '16px',
              background: 'rgba(255,255,255,0.03)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-md)',
              display: 'flex',
              alignItems: 'flex-start',
              gap: 10,
            }}>
              <span style={{ fontSize: '1.4rem' }}>{f.icon}</span>
              <div>
                <div style={{ fontFamily: 'var(--font-devanagari)', fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-primary)', marginBottom: 2 }}>{f.mr}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{f.en}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ─── Footer with Legal Links ───────────────────────────────────── */}
      <footer style={{ padding: '0 16px 32px', textAlign: 'center' }}>
        <p className="disclaimer" style={{ marginBottom: 16 }}>
          {lang === 'mr'
            ? 'हा अहवाल मार्गदर्शनासाठी आहे. वैयक्तिक सल्ल्यासाठी तज्ञ ज्योतिषांचा सल्ला घ्या.'
            : 'This report is for guidance only. Consult an expert astrologer for personal advice.'}
        </p>
        <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '16px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          <a href="/terms" style={{ color: 'inherit', textDecoration: 'none' }}>Terms & Conditions</a>
          <a href="/privacy" style={{ color: 'inherit', textDecoration: 'none' }}>Privacy Policy</a>
          <a href="/refund" style={{ color: 'inherit', textDecoration: 'none' }}>Cancellation & Refund Policy</a>
          <a href="/contact" style={{ color: 'inherit', textDecoration: 'none' }}>Contact Us</a>
        </div>
      </footer>
    </div>
  );
}

'use client';
import { useRouter } from 'next/navigation';

export default function ContactPage() {
  const router = useRouter();
  
  return (
    <div style={{ minHeight: '100dvh', paddingBottom: 60, color: 'var(--text-primary)' }}>
      <nav className="navbar">
        <div style={{ maxWidth: 800, margin: '0 auto', padding: '0 16px', display: 'flex', alignItems: 'center', height: 56 }}>
          <button onClick={() => router.push('/')} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', fontFamily: 'var(--font-devanagari)' }}>
            ‹ मागे (Back)
          </button>
          <span style={{ marginLeft: 'auto', fontFamily: 'var(--font-devanagari)', fontWeight: 700, color: 'var(--saffron-400)' }}>
            Contact Us
          </span>
        </div>
      </nav>

      <div style={{ maxWidth: 800, margin: '0 auto', padding: '40px 16px', lineHeight: 1.6 }}>
        <h1 style={{ color: 'var(--saffron-500)', marginBottom: 20 }}>Contact Us</h1>
        <p style={{ color: 'var(--text-muted)', marginBottom: 24 }}>
          If you have any questions, face technical issues, or need assistance with your downloaded reports, please reach out to our support team. We usually respond within 24-48 hours.
        </p>

        <div style={{ background: 'rgba(255,255,255,0.03)', padding: 24, borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
          <h2 style={{ fontSize: '1.2rem', marginBottom: 16 }}>Support Information</h2>
          
          <div style={{ marginBottom: 12 }}>
            <strong>Email:</strong> support@mazeekundali.in
          </div>
          
          <div style={{ marginBottom: 12 }}>
            <strong>Operating Address:</strong><br />
            Mazee Kundali<br />
            Pune, Maharashtra, India - 411001
          </div>

          <div style={{ marginBottom: 12 }}>
            <strong>Business Hours:</strong><br />
            Monday to Saturday: 10:00 AM to 6:00 PM (IST)
          </div>
        </div>
        
        <p style={{ marginTop: 24, fontSize: '0.9rem', color: 'var(--text-muted)' }}>
          <em>Note: We only provide technical support regarding the generation of PDF files on our platform. We do not offer personal astrological readings or consultations over email or phone.</em>
        </p>
      </div>
    </div>
  );
}

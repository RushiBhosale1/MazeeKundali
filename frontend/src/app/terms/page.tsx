'use client';
import { useRouter } from 'next/navigation';

export default function TermsPage() {
  const router = useRouter();
  
  return (
    <div style={{ minHeight: '100dvh', paddingBottom: 60, color: 'var(--text-primary)' }}>
      <nav className="navbar">
        <div style={{ maxWidth: 800, margin: '0 auto', padding: '0 16px', display: 'flex', alignItems: 'center', height: 56 }}>
          <button onClick={() => router.push('/')} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', fontFamily: 'var(--font-devanagari)' }}>
            ‹ मागे (Back)
          </button>
          <span style={{ marginLeft: 'auto', fontFamily: 'var(--font-devanagari)', fontWeight: 700, color: 'var(--saffron-400)' }}>
            Terms & Conditions
          </span>
        </div>
      </nav>

      <div style={{ maxWidth: 800, margin: '0 auto', padding: '40px 16px', lineHeight: 1.6 }}>
        <h1 style={{ color: 'var(--saffron-500)', marginBottom: 20 }}>Terms & Conditions</h1>
        <p style={{ color: 'var(--text-muted)', marginBottom: 20 }}>Last updated: July 20, 2026</p>
        
        <h2 style={{ fontSize: '1.2rem', marginTop: 24, marginBottom: 12 }}>1. Introduction</h2>
        <p style={{ marginBottom: 16 }}>
          Welcome to माझी कुंडली (Mazee Kundali). These Terms and Conditions govern your use of our website and the digital astrological services provided. By accessing or using our platform, you agree to be bound by these terms.
        </p>

        <h2 style={{ fontSize: '1.2rem', marginTop: 24, marginBottom: 12 }}>2. Services Provided</h2>
        <p style={{ marginBottom: 16 }}>
          We provide computer-generated astrological reports (Kundali), horoscope matching (Patrika Milan), and Biodata creation services in PDF format. These reports are generated based on the birth details you provide.
        </p>

        <h2 style={{ fontSize: '1.2rem', marginTop: 24, marginBottom: 12 }}>3. Accuracy and Disclaimer</h2>
        <p style={{ marginBottom: 16 }}>
          The astrological calculations and predictions are based on standard Vedic astrology algorithms. However, astrology is not an exact science. The reports are provided for entertainment and guidance purposes only. We do not guarantee the accuracy, reliability, or physical realization of any predictions made in the reports. You should not rely on these reports for financial, medical, legal, or psychological decisions. We strictly disclaim any liability for actions taken based on our reports.
        </p>

        <h2 style={{ fontSize: '1.2rem', marginTop: 24, marginBottom: 12 }}>4. User Information</h2>
        <p style={{ marginBottom: 16 }}>
          You are responsible for ensuring that the birth details (Name, Date, Time, and Place) you provide are accurate. Errors in input will result in incorrect calculations. We do not offer free revisions if the error was due to incorrect user input.
        </p>

        <h2 style={{ fontSize: '1.2rem', marginTop: 24, marginBottom: 12 }}>5. Payments</h2>
        <p style={{ marginBottom: 16 }}>
          All payments are processed securely via third-party gateways (e.g., Razorpay). Prices are listed in INR (₹) and are subject to change without prior notice.
        </p>

        <h2 style={{ fontSize: '1.2rem', marginTop: 24, marginBottom: 12 }}>6. Intellectual Property</h2>
        <p style={{ marginBottom: 16 }}>
          All content, designs, and PDF templates provided by Mazee Kundali are the intellectual property of our platform and may not be resold, copied, or redistributed without explicit permission.
        </p>
      </div>
    </div>
  );
}

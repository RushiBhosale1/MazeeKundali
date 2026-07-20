'use client';
import { useRouter } from 'next/navigation';

export default function RefundPage() {
  const router = useRouter();
  
  return (
    <div style={{ minHeight: '100dvh', paddingBottom: 60, color: 'var(--text-primary)' }}>
      <nav className="navbar">
        <div style={{ maxWidth: 800, margin: '0 auto', padding: '0 16px', display: 'flex', alignItems: 'center', height: 56 }}>
          <button onClick={() => router.push('/')} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', fontFamily: 'var(--font-devanagari)' }}>
            ‹ मागे (Back)
          </button>
          <span style={{ marginLeft: 'auto', fontFamily: 'var(--font-devanagari)', fontWeight: 700, color: 'var(--saffron-400)' }}>
            Refund Policy
          </span>
        </div>
      </nav>

      <div style={{ maxWidth: 800, margin: '0 auto', padding: '40px 16px', lineHeight: 1.6 }}>
        <h1 style={{ color: 'var(--saffron-500)', marginBottom: 20 }}>Cancellation & Refund Policy</h1>
        <p style={{ color: 'var(--text-muted)', marginBottom: 20 }}>Last updated: July 20, 2026</p>
        
        <h2 style={{ fontSize: '1.2rem', marginTop: 24, marginBottom: 12 }}>1. Digital Goods</h2>
        <p style={{ marginBottom: 16 }}>
          All services offered by माझी कुंडली (Mazee Kundali) are digital in nature (automatically generated PDF reports). Due to the instant delivery and digital format of our products, we operate under a strict <strong>No Refund</strong> policy once the payment is successful and the report has been generated.
        </p>

        <h2 style={{ fontSize: '1.2rem', marginTop: 24, marginBottom: 12 }}>2. Order Cancellations</h2>
        <p style={{ marginBottom: 16 }}>
          Once an order is placed and the payment is processed, it cannot be cancelled. The generation of astrological charts and biodata is automated and occurs instantaneously upon payment confirmation.
        </p>

        <h2 style={{ fontSize: '1.2rem', marginTop: 24, marginBottom: 12 }}>3. Technical Failures</h2>
        <p style={{ marginBottom: 16 }}>
          If your payment was successfully deducted but you did not receive access to your PDF report due to a technical error, network issue, or server downtime, please contact our support team immediately. We will manually verify your payment and provide you with the PDF report. We will not issue a refund in this case, but we guarantee delivery of the purchased product.
        </p>

        <h2 style={{ fontSize: '1.2rem', marginTop: 24, marginBottom: 12 }}>4. Incorrect User Input</h2>
        <p style={{ marginBottom: 16 }}>
          We strictly do not offer refunds, revisions, or free regenerations if you provided incorrect birth details (Name, Date, Time, Place) during the form submission. Users are strongly advised to verify all inputs before making a payment.
        </p>
      </div>
    </div>
  );
}

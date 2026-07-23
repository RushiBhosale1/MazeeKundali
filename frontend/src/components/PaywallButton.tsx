'use client';
/**
 * components/PaywallButton.tsx
 * Reusable "Unlock" button for all paid features.
 *
 * Usage:
 *   <PaywallButton
 *     productType="kundali"
 *     recordId={kundaliId}
 *     resumeToken={resumeToken}
 *     buyerName={name}
 *     pollUrl={`/api/v1/kundalis/${kundaliId}`}
 *     label="₹99 मध्ये संपूर्ण कुंडली अनलॉक करा"
 *     description="जन्मकुंडली — संपूर्ण ग्रह तक्ता, दशा, विश्लेषण"
 *     onUnlocked={() => router.refresh()}
 *   />
 */
import { useState, useRef } from 'react';
import { payAndUnlock, type ProductType } from '@/lib/razorpay';

interface Props {
  productType: ProductType;
  recordId: string;
  resumeToken: string;
  buyerName: string;
  buyerEmail?: string;
  label: string;
  sublabel?: string;
  description: string;
  pollUrl: string;
  onUnlocked: () => void;
  className?: string;
  fullWidth?: boolean;
}

type State = 'idle' | 'collecting_info' | 'creating' | 'waiting_payment' | 'polling' | 'error' | 'success';

const PRICE_MAP: Record<ProductType, { inr: number; label: string }> = {
  kundali:  { inr: 49,  label: '₹49' },
  matching: { inr: 79,  label: '₹79' },
  biodata:  { inr: 0,   label: 'मोफत' },
  bundle:   { inr: 119, label: '₹119' },
};


  // Helper for Marathi/English text if needed. For now just defaulting to Marathi.
  const mr = (marathi: string, english: string) => marathi;
export default function PaywallButton({
  productType, recordId, resumeToken, buyerName, buyerEmail,
  label, sublabel, description, pollUrl, onUnlocked, className = '', fullWidth = false,
}: Props) {
  const [state, setState] = useState<State>('idle');
  const [errorMsg, setErrorMsg] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const stateRef = useRef<State>('idle');

  const updateState = (s: State) => { stateRef.current = s; setState(s); };

  const price = PRICE_MAP[productType];

  const handlePay = async () => {
    if (state === 'idle') {
      updateState('collecting_info');
      return;
    }
    if (state !== 'collecting_info' && state !== 'error') return;

    if (!phone || !/^\d{10}$/.test(phone)) {
      setErrorMsg('कृपया १० अंकी वैध फोन नंबर प्रविष्ट करा. (Please enter a valid 10-digit phone number)');
      return;
    }
    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setErrorMsg('कृपया वैध ईमेल आयडी प्रविष्ट करा. (Please enter a valid email)');
      return;
    }

    updateState('creating');
    setErrorMsg('');

    await payAndUnlock({
      payload: {
        product_type: productType,
        record_id: recordId,
        resume_token: resumeToken,
        amount_inr: price.inr,
        customer_email: email,
        customer_phone: phone,
      },
      buyerName,
      buyerEmail: email,
      buyerPhone: phone,
      description,
      pollUrl,
      onUnlocked: () => {
        updateState('success');
        onUnlocked();
      },
      onError: (msg) => {
        updateState('error');
        setErrorMsg(msg);
      },
      onDismiss: () => {
        const cur = stateRef.current;
        if (cur === 'creating' || cur === 'waiting_payment') {
          updateState('idle');
        }
      },
    });

    // After modal opens, reflect waiting state
    if (stateRef.current === 'creating') updateState('waiting_payment');
  };

  const isLoading = state === 'creating' || state === 'polling';
  const isDone    = state === 'success';

  return (
    <div style={{ width: fullWidth ? '100%' : 'auto' }}>
      {state === 'collecting_info' && (
        <div style={{ padding: '16px', border: '1px solid rgba(240,124,0,0.3)', borderRadius: '12px', background: 'rgba(255,255,255,0.03)', marginBottom: '16px', textAlign: 'left' }}>
          <h3 style={{ fontSize: '1.05rem', marginBottom: '12px', color: 'var(--text-primary)', fontFamily: 'var(--font-devanagari)' }}>संपर्क माहिती (Contact Info)</h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '16px', fontFamily: 'var(--font-devanagari)' }}>
            पेमेंट पूर्ण झाल्यावर अहवाल PDF स्वरूपात तुमच्या ईमेलवर पाठवला जाईल (पर्यायी).
          </p>
          <div style={{ marginBottom: '12px' }}>
            <label style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '6px', color: 'var(--text-primary)' }}>
              <span>ईमेल आयडी (Email)</span>
              <span style={{color: 'var(--text-muted)', fontSize: '0.75rem'}}>(Optional)</span>
            </label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--border-subtle)', background: 'rgba(0,0,0,0.2)', color: 'var(--text-primary)', fontSize: '0.95rem' }} placeholder="तुमचा ईमेल (Optional - We'll send PDF here)" />
          </div>
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '6px', color: 'var(--text-primary)' }}>फोन नंबर (Phone) <span style={{ fontSize: '0.75rem', marginLeft: 4, fontWeight: 'normal' }}>(आवश्यक)</span></label>
            <input type="tel" value={phone} onChange={e => setPhone(e.target.value.replace(/\D/g, ''))} maxLength={10} required style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--border-subtle)', background: 'rgba(0,0,0,0.2)', color: 'var(--text-primary)', fontSize: '0.95rem' }} placeholder="तुमचा मोबाईल नंबर (10 digits)" />
          </div>
          {errorMsg && (
            <div style={{ color: 'var(--danger)', fontSize: '0.85rem', marginBottom: '12px', fontFamily: 'var(--font-devanagari)' }}>
              ⚠️ {errorMsg}
            </div>
          )}
        </div>
      )}
      <button
        id={`paywall-btn-${recordId}`}
        className={`btn-primary ${className}`}
        style={{
          width: fullWidth ? '100%' : 'auto',
          display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10,
          fontSize: '1rem', padding: '14px 24px',
          opacity: (isLoading || isDone) ? 0.7 : 1,
          cursor: (isLoading || isDone) ? 'not-allowed' : 'pointer',
          position: 'relative', overflow: 'hidden',
        }}
        onClick={handlePay}
        disabled={isLoading || isDone}
        aria-busy={isLoading}
      >
        {/* Shimmer overlay while loading */}
        {isLoading && (
          <span style={{
            position: 'absolute', inset: 0,
            background: 'linear-gradient(90deg,transparent 0%,rgba(255,255,255,0.12) 50%,transparent 100%)',
            animation: 'shimmer 1.2s ease-in-out infinite',
          }} />
        )}

        {state === 'creating'        && <span>⏳ ऑर्डर तयार होत आहे...</span>}
        {state === 'waiting_payment' && <span>💳 पेमेंट विंडोमध्ये पुढे जा...</span>}
        {state === 'polling'         && <span>🔄 अनलॉक होत आहे...</span>}
        {state === 'success'         && <span>✅ अनलॉक झाले!</span>}
        {(state === 'idle' || state === 'error' || state === 'collecting_info') && (
          <>
            <span style={{ fontSize: '1.2rem' }}>{state === 'collecting_info' ? '💳' : '🔓'}</span>
            <span style={{ fontFamily: 'var(--font-devanagari)', fontWeight: 700 }}>
              {state === 'collecting_info' ? mr('पुढे जा (Proceed to Pay)', 'Proceed to Pay') : label}
            </span>
            <span style={{
              background: 'rgba(255,255,255,0.15)', borderRadius: 999,
              padding: '2px 10px', fontSize: '0.88rem', fontFamily: 'Inter',
            }}>{price.label}</span>
          </>
        )}
      </button>

      {sublabel && state === 'idle' && (
        <p style={{
          textAlign: 'center', marginTop: 6, fontFamily: 'var(--font-devanagari)',
          fontSize: '0.78rem', color: 'var(--text-muted)',
        }}>{sublabel}</p>
      )}

      {state === 'error' && errorMsg && (
        <div style={{
          marginTop: 10, padding: '10px 14px',
          background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.25)',
          borderRadius: 'var(--radius-md)', fontFamily: 'var(--font-devanagari)',
          fontSize: '0.82rem', color: '#f87171',
        }}>
          ⚠️ {errorMsg}
          <button
            onClick={() => { setState('idle'); setErrorMsg(''); }}
            style={{ marginLeft: 10, background: 'none', border: 'none',
                     color: 'var(--saffron-400)', cursor: 'pointer', fontSize: '0.82rem' }}
          >
            पुन्हा प्रयत्न करा →
          </button>
        </div>
      )}

      {/* UPI hint */}
      {(state === 'idle' || state === 'error') && (
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          gap: 8, marginTop: 10, flexWrap: 'wrap',
        }}>
          {['UPI', 'GPay', 'PhonePe', 'Card'].map(m => (
            <span key={m} style={{
              fontFamily: 'Inter', fontSize: '0.72rem', color: 'var(--text-muted)',
              background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border-subtle)',
              borderRadius: 6, padding: '2px 8px',
            }}>{m}</span>
          ))}
          <span style={{ fontFamily: 'Inter', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
            🔒 100% सुरक्षित
          </span>
        </div>
      )}

      <style>{`
        @keyframes shimmer {
          0%   { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
      `}</style>
    </div>
  );
}

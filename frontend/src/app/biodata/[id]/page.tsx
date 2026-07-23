'use client';
import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import PaywallButton from '@/components/PaywallButton';

export default function BiodataResultPage() {
    const { id } = useParams();
    const router = useRouter();
    const [biodata, setBiodata] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchBiodata() {
            try {
                const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/biodatas/${id}`);
                if (res.ok) {
                    setBiodata(await res.json());
                }
            } finally {
                setLoading(false);
            }
        }
        if (id) fetchBiodata();
    }, [id]);

    if (loading) return <div style={{ color: 'white', padding: 40, textAlign: 'center' }}>लोड करत आहे... (Loading...)</div>;
    if (!biodata) return <div style={{ color: 'white', padding: 40, textAlign: 'center' }}>बायोडाटा सापडला नाही. (Biodata not found)</div>;

    const downloadPDF = () => {
        window.open(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/biodatas/${id}/pdf`, '_blank');
    };

    const shareWhatsApp = () => {
        const imageUrl = `${process.env.NEXT_PUBLIC_API_URL}/api/v1/biodatas/${id}/image`;
        const text = `नमस्कार, हे माझे विवाह बायोडाटा (Biodata) पाहा: ${imageUrl}`;
        window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, '_blank');
    };

    return (
        <div style={{ minHeight: '100dvh', paddingBottom: 120 }}>
            <nav className="navbar">
                <div style={{ maxWidth: 680, margin: '0 auto', padding: '0 16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: 56 }}>
                <button onClick={() => router.push('/biodata/new')} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', fontFamily: 'var(--font-devanagari)' }}>
                    ‹ संपादित करा (Edit)
                </button>
                <span style={{ fontFamily: 'var(--font-devanagari)', fontWeight: 700, color: 'var(--saffron-400)', fontSize: '1rem' }}>
                    बायोडाटा तयार आहे
                </span>
                </div>
            </nav>

            <div className="page-container" style={{ paddingTop: 24 }}>
                <div style={{ textAlign: 'center', marginBottom: 32 }} className="animate-fade-up">
                    <h2 style={{ color: 'var(--text-primary)', fontFamily: 'var(--font-devanagari)', marginBottom: 8, fontSize: '1.6rem' }}>🎉 तुमचा बायोडाटा तयार आहे!</h2>
                    <p style={{ color: 'var(--text-muted)' }}>तुम्ही तो डाउनलोड करू शकता किंवा थेट WhatsApp वर पाठवू शकता.</p>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }} className="animate-fade-up">
                    <button onClick={downloadPDF} className="btn-primary" style={{ padding: '16px 8px', fontSize: '1rem', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6 }}>
                        <span style={{ fontSize: '1.4rem' }}>📄</span>
                        <span>PDF डाउनलोड करा</span>
                    </button>
                    
                    <button onClick={shareWhatsApp} style={{ 
                        background: '#25D366', color: 'white', border: 'none', padding: '16px 8px', 
                        borderRadius: 'var(--radius-md)', fontSize: '1rem', fontWeight: 600, cursor: 'pointer',
                        display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6
                    }}>
                        <span style={{ fontSize: '1.4rem' }}>💬</span>
                        <span>WhatsApp वर पाठवा</span>
                    </button>
                </div>

                {/* Image Preview instead of PDF iframe because PDF iframe is often blocked on mobile devices */}
                <div style={{ marginTop: 32, border: '2px solid rgba(255,255,255,0.1)', borderRadius: 'var(--radius-lg)', overflow: 'hidden' }} className="animate-fade-up">
                    <div style={{ padding: '12px 16px', background: 'rgba(255,255,255,0.05)', color: 'var(--text-secondary)', fontSize: '0.9rem', borderBottom: '1px solid rgba(255,255,255,0.1)', fontFamily: 'var(--font-devanagari)' }}>
                        👀 प्रिव्ह्यू (Preview)
                    </div>
                    <div style={{ width: '100%', background: '#111', padding: 8 }}>
                        <img 
                            src={`${process.env.NEXT_PUBLIC_API_URL}/api/v1/biodatas/${id}/image?preview=true`} 
                            alt="Biodata Preview"
                            style={{ width: '100%', height: 'auto', borderRadius: '4px' }}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}

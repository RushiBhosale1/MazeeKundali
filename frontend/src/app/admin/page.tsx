'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

interface Order {
  id: string;
  product_type: string;
  amount_inr: number;
  status: string;
  paid: boolean;
  razorpay_order_id?: string;
  record_unlocked: boolean;
}

interface Webhook {
  id: string;
  event_id: string;
  event_type: string;
  processed: boolean;
  created_at: string;
  error?: string;
}

export default function AdminPage() {
  const router = useRouter();
  const [authed, setAuthed] = useState(false);
  const [password, setPassword] = useState('');
  const [orders, setOrders] = useState<Order[]>([]);
  const [webhooks, setWebhooks] = useState<Webhook[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);

  const checkAuth = async () => {
    setLoading(true);
    try {
      const resp = await fetch(`${API_URL}/api/v1/admin/orders`, {
        headers: { 'X-Admin-Token': password },
      });
      if (resp.ok) {
        setAuthed(true);
        const data = await resp.json();
        setOrders(data.orders ?? []);
        loadWebhooks(password);
      } else {
        alert('चुकीचा पासवर्ड (Invalid Token)');
      }
    } catch {
      alert('Error connecting to backend');
    } finally {
      setLoading(false);
    }
  };

  const loadData = async () => {
    setLoading(true);
    try {
      const resp = await fetch(`${API_URL}/api/v1/admin/orders`, {
        headers: { 'X-Admin-Token': password },
      });
      if (resp.ok) {
        const data = await resp.json();
        setOrders(data.orders ?? []);
      }
      await loadWebhooks(password);
    } catch {
      console.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const loadWebhooks = async (token: string) => {
    try {
      const resp = await fetch(`${API_URL}/api/v1/admin/webhooks`, {
        headers: { 'X-Admin-Token': token },
      });
      if (resp.ok) {
        const data = await resp.json();
        setWebhooks(data.webhooks ?? []);
      }
    } catch {}
  };

  const forceUnlock = async (orderId: string) => {
    if (!confirm(`Are you sure you want to FORCE UNLOCK order ${orderId}? This will mark it as paid and trigger emails.`)) return;
    try {
      const resp = await fetch(`${API_URL}/api/v1/admin/orders/${orderId}/force-unlock`, {
        method: 'POST',
        headers: { 'X-Admin-Token': password },
      });
      if (resp.ok) {
        alert('Order force unlocked successfully!');
        loadData();
      } else {
        const data = await resp.json();
        alert(`Failed: ${data.detail || data.msg}`);
      }
    } catch (e) {
      alert('Error calling force-unlock endpoint');
    }
  };

  const filtered = orders.filter(o =>
    !search ||
    o.id.includes(search) ||
    (o.razorpay_order_id ?? '').includes(search) ||
    o.status.includes(search) ||
    o.product_type.includes(search)
  );

  const PRODUCT_LABELS: Record<string, string> = {
    kundali: '🪐 कुंडली', matching: '💍 जुळणी',
    biodata: '📄 बायोडाटा', bundle: '💎 बंडल',
  };

  if (!authed) return (
    <div style={{ minHeight: '100dvh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--navy-900)', padding: 24 }}>
      <div className="card" style={{ width: '100%', maxWidth: 360, padding: 32, textAlign: 'center' }}>
        <div style={{ fontSize: '2rem', marginBottom: 16 }}>🔐</div>
        <h1 style={{ fontFamily: 'var(--font-devanagari)', fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: 20 }}>
          Admin Access
        </h1>
        <input type="password" className="input-field" placeholder="Admin token"
          value={password} onChange={e => setPassword(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && checkAuth()}
          style={{ marginBottom: 14 }} />
        <button className="btn-primary" style={{ width: '100%' }} onClick={checkAuth} disabled={loading}>
          {loading ? 'Verifying...' : 'Login'}
        </button>
        <button className="btn-ghost" style={{ width: '100%', marginTop: 8 }} onClick={() => router.push('/')}>← मुख्य</button>
      </div>
    </div>
  );

  return (
    <div style={{ minHeight: '100dvh', background: 'var(--navy-900)', paddingBottom: 60 }}>
      <nav className="navbar" style={{ borderBottom: '1px solid rgba(239,68,68,0.2)' }}>
        <div style={{ maxWidth: 900, margin: '0 auto', padding: '0 16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: 56 }}>
          <button onClick={() => router.push('/')} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', fontFamily: 'var(--font-devanagari)' }}>
            ← मुख्य
          </button>
          <span style={{ fontFamily: 'var(--font-devanagari)', fontWeight: 700, color: '#ef4444', fontSize: '0.95rem' }}>
            🔐 Admin Dashboard
          </span>
          <button onClick={loadData} className="btn-ghost" style={{ fontSize: '0.8rem', padding: '6px 12px' }}>
            🔄 Refresh
          </button>
        </div>
      </nav>

      <div style={{ maxWidth: 900, margin: '0 auto', padding: '20px 16px' }}>
        {/* Stats */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 12, marginBottom: 24 }}>
          {[
            { label: 'एकूण Orders', value: orders.length, color: 'var(--text-primary)' },
            { label: 'Paid', value: orders.filter(o => o.paid).length, color: 'var(--success)' },
            { label: 'Pending', value: orders.filter(o => !o.paid && o.status !== 'failed').length, color: 'var(--warning)' },
            { label: 'Failed', value: orders.filter(o => o.status === 'failed').length, color: 'var(--danger)' },
            { label: 'Revenue', value: `₹${orders.filter(o => o.paid).reduce((s, o) => s + o.amount_inr, 0)}`, color: 'var(--gold-400)' },
          ].map((s, i) => (
            <div key={i} className="card" style={{ padding: '14px 16px', textAlign: 'center' }}>
              <div style={{ fontFamily: 'Inter', fontSize: '1.4rem', fontWeight: 800, color: s.color }}>{s.value}</div>
              <div style={{ fontFamily: 'var(--font-devanagari)', fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 4 }}>{s.label}</div>
            </div>
          ))}
        </div>

        {/* Search */}
        <div style={{ marginBottom: 16 }}>
          <input className="input-field" type="text" placeholder="Order ID, Razorpay ID, status, product type..."
            value={search} onChange={e => setSearch(e.target.value)} />
        </div>

        {/* Orders table */}
        {loading ? (
          <div style={{ textAlign: 'center', padding: 40, color: 'var(--text-muted)', fontFamily: 'var(--font-devanagari)' }}>Loading...</div>
        ) : (
          <div className="card" style={{ overflow: 'hidden', padding: 0, marginBottom: 32 }}>
            <div style={{ padding: '16px', borderBottom: '1px solid var(--border-subtle)', background: 'rgba(255,255,255,0.02)' }}>
              <h2 style={{ fontFamily: 'Inter', fontSize: '1rem', color: 'var(--text-primary)' }}>🛒 Recent Orders</h2>
            </div>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: 'Inter', fontSize: '0.82rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-subtle)', background: 'rgba(255,255,255,0.01)' }}>
                    {['Order ID', 'Product', 'Amount', 'Status', 'Razorpay ID', 'Unlocked', 'Actions'].map(h => (
                      <th key={h} style={{ padding: '10px 14px', textAlign: 'left', color: 'var(--text-muted)', fontWeight: 600, whiteSpace: 'nowrap' }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {filtered.length === 0 ? (
                    <tr><td colSpan={7} style={{ padding: 32, textAlign: 'center', color: 'var(--text-muted)', fontFamily: 'var(--font-devanagari)' }}>कोणतेही orders सापडले नाहीत.</td></tr>
                  ) : filtered.map((o, i) => (
                    <tr key={o.id} style={{ borderBottom: i < filtered.length - 1 ? '1px solid var(--border-subtle)' : 'none' }}>
                      <td style={{ padding: '10px 14px', color: 'var(--text-secondary)', fontFamily: 'monospace', fontSize: '0.75rem' }}>{o.id.slice(0, 8)}…</td>
                      <td style={{ padding: '10px 14px', color: 'var(--text-primary)', whiteSpace: 'nowrap' }}>{PRODUCT_LABELS[o.product_type] ?? o.product_type}</td>
                      <td style={{ padding: '10px 14px', color: 'var(--gold-400)', fontWeight: 700 }}>₹{o.amount_inr}</td>
                      <td style={{ padding: '10px 14px' }}>
                        <span className={`chip ${o.status === 'paid' ? 'chip-green' : o.status === 'failed' ? 'chip-red' : 'chip-saffron'}`} style={{ fontSize: '0.72rem' }}>
                          {o.status}
                        </span>
                      </td>
                      <td style={{ padding: '10px 14px', color: 'var(--text-muted)', fontFamily: 'monospace', fontSize: '0.75rem' }}>
                        {o.razorpay_order_id ? `${o.razorpay_order_id.slice(0, 16)}…` : '—'}
                      </td>
                      <td style={{ padding: '10px 14px' }}>
                        <span style={{ color: o.record_unlocked ? 'var(--success)' : 'var(--text-muted)' }}>
                          {o.record_unlocked ? '✅' : '—'}
                        </span>
                      </td>
                      <td style={{ padding: '10px 14px' }}>
                        {!o.paid && (
                          <button
                            onClick={() => forceUnlock(o.id)}
                            style={{ padding: '4px 10px', background: 'rgba(245,158,11,0.12)', border: '1px solid rgba(245,158,11,0.3)', borderRadius: 6, color: 'var(--warning)', fontSize: '0.72rem', cursor: 'pointer', whiteSpace: 'nowrap' }}>
                            Force Unlock
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Webhooks Section */}
        <div className="card" style={{ overflow: 'hidden', padding: 0 }}>
          <div style={{ padding: '16px', borderBottom: '1px solid var(--border-subtle)', background: 'rgba(255,255,255,0.02)' }}>
            <h2 style={{ fontFamily: 'Inter', fontSize: '1rem', color: 'var(--text-primary)' }}>🪝 Recent Razorpay Webhooks</h2>
          </div>
          <div style={{ overflowX: 'auto', maxHeight: '400px', overflowY: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: 'Inter', fontSize: '0.8rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                  <th style={{ padding: '10px 14px', textAlign: 'left', color: 'var(--text-muted)' }}>Time</th>
                  <th style={{ padding: '10px 14px', textAlign: 'left', color: 'var(--text-muted)' }}>Event</th>
                  <th style={{ padding: '10px 14px', textAlign: 'left', color: 'var(--text-muted)' }}>Event ID</th>
                  <th style={{ padding: '10px 14px', textAlign: 'left', color: 'var(--text-muted)' }}>Processed</th>
                  <th style={{ padding: '10px 14px', textAlign: 'left', color: 'var(--text-muted)' }}>Error</th>
                </tr>
              </thead>
              <tbody>
                {webhooks.length === 0 ? (
                  <tr><td colSpan={5} style={{ padding: 20, textAlign: 'center', color: 'var(--text-muted)' }}>No webhooks recorded.</td></tr>
                ) : webhooks.map((w, i) => (
                  <tr key={w.id} style={{ borderBottom: i < webhooks.length - 1 ? '1px solid var(--border-subtle)' : 'none' }}>
                    <td style={{ padding: '8px 14px', color: 'var(--text-secondary)' }}>{new Date(w.created_at).toLocaleString()}</td>
                    <td style={{ padding: '8px 14px', color: 'var(--text-primary)', fontWeight: 600 }}>{w.event_type}</td>
                    <td style={{ padding: '8px 14px', color: 'var(--text-muted)', fontFamily: 'monospace' }}>{w.event_id}</td>
                    <td style={{ padding: '8px 14px', color: w.processed ? 'var(--success)' : 'var(--warning)' }}>{w.processed ? 'Yes' : 'No'}</td>
                    <td style={{ padding: '8px 14px', color: 'var(--danger)', maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={w.error}>{w.error || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  );
}

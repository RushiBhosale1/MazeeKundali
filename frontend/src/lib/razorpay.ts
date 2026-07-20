/**
 * lib/razorpay.ts
 * Razorpay checkout integration for माझी कुंडली.
 *
 * Flow:
 *  1. Call createOrder() → backend creates Razorpay order, returns {order_id, amount, currency, key_id}
 *  2. Open Razorpay checkout modal with returned params
 *  3. On success: backend webhook (payment.captured) unlocks the record
 *  4. Frontend polls /api/v1/kundalis/:id or /api/v1/matchings/:id until paid=true
 *
 * Never trust client-side payment_id as proof of payment — the webhook does the unlock.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

export type ProductType = 'kundali' | 'matching' | 'biodata' | 'bundle';

export interface OrderPayload {
  product_type: ProductType;
  record_id: string;       // kundali_id / matching_id / biodata_id
  resume_token: string;    // anti-CSRF idempotency token
  amount_inr?: number;     // optional override; backend validates final price
  customer_email?: string;
  customer_phone?: string;
}

export interface RazorpayOrderResponse {
  razorpay_order_id: string;
  amount_paise: number;
  currency: string;
  key_id: string;
  order_id: string;        // our internal order UUID
}

/** Create a payment order on our backend */
export async function createOrder(payload: OrderPayload): Promise<RazorpayOrderResponse> {
  const resp = await fetch(`${API_URL}/api/v1/orders`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({}));
    throw new Error(err.detail ?? `Order creation failed (${resp.status})`);
  }
  return resp.json();
}

/** Dynamically load Razorpay checkout.js (only once) */
function loadRazorpayScript(): Promise<void> {
  return new Promise((resolve, reject) => {
    if ((window as unknown as Record<string, unknown>).Razorpay) {
      resolve();
      return;
    }
    const script = document.createElement('script');
    script.src = 'https://checkout.razorpay.com/v1/checkout.js';
    script.async = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error('Razorpay script failed to load'));
    document.head.appendChild(script);
  });
}

export interface CheckoutOptions {
  order: RazorpayOrderResponse;
  name: string;                // buyer's name (prefill)
  email?: string;
  phone?: string;
  description: string;         // shown in Razorpay modal
  onSuccess: (paymentId: string, orderId: string, signature: string) => void;
  onError: (error: string) => void;
  onDismiss?: () => void;
}

/** Open Razorpay checkout modal */
export async function openCheckout(opts: CheckoutOptions): Promise<void> {
  await loadRazorpayScript();

  const RazorpayClass = (window as unknown as Record<string, unknown>).Razorpay as new (opts: unknown) => { open(): void };
  const rzp = new RazorpayClass({
    key: opts.order.key_id,
    order_id: opts.order.razorpay_order_id,
    amount: opts.order.amount_paise,
    currency: opts.order.currency ?? 'INR',
    name: 'माझी कुंडली',
    description: opts.description,
    // NOTE: No 'image' field — localhost image causes CORS errors in Razorpay's CDN
    prefill: {
      name: opts.name,
      email: opts.email ?? '',
      contact: opts.phone ?? '',
    },
    theme: {
      color: '#f07c00',       // saffron to match brand
      backdrop_color: '#0d1b2a',
    },
    modal: {
      escape: true,
      backdropclose: false,
      ondismiss: opts.onDismiss ?? (() => {}),
    },
    handler: (response: { razorpay_payment_id: string; razorpay_order_id: string; razorpay_signature: string }) => {
      opts.onSuccess(
        response.razorpay_payment_id,
        response.razorpay_order_id,
        response.razorpay_signature,
      );
    },
  });

  rzp.open();
}

/**
 * Poll backend until record is unlocked (paid=true).
 * The actual unlock happens via Razorpay webhook — this just waits for it.
 *
 * @param url  Full URL to GET (e.g. /api/v1/kundalis/:id)
 * @param maxWaitMs  Max wait time in ms (default 30s)
 * @returns true if unlocked within timeout, false otherwise
 */
export async function pollUntilUnlocked(
  url: string,
  maxWaitMs = 30_000,
): Promise<boolean> {
  const deadline = Date.now() + maxWaitMs;
  const INTERVALS = [1000, 1500, 2000, 2500, 3000]; // progressive backoff
  let attempt = 0;
  while (Date.now() < deadline) {
    await new Promise(r => setTimeout(r, INTERVALS[Math.min(attempt, INTERVALS.length - 1)]));
    attempt++;
    try {
      const resp = await fetch(`${API_URL}${url}`);
      if (resp.ok) {
        const data = await resp.json();
        if (data.paid === true) return true;
      }
    } catch (_) {
      // network hiccup — keep polling
    }
  }
  return false;
}

/** Call backend to verify payment signature and unlock the product */
export async function verifyPayment(
  razorpay_payment_id: string,
  razorpay_order_id: string,
  razorpay_signature: string,
): Promise<{ unlocked: boolean }> {
  const resp = await fetch(`${API_URL}/api/v1/orders/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ razorpay_payment_id, razorpay_order_id, razorpay_signature }),
  });
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({}));
    throw new Error(err.detail ?? `Payment verification failed (${resp.status})`);
  }
  const data = await resp.json();
  return { unlocked: data.unlocked === true };
}

/** Convenience: create order + open checkout + verify + unlock in one call */
export async function payAndUnlock(opts: {
  payload: OrderPayload;
  buyerName: string;
  buyerEmail?: string;
  buyerPhone?: string;
  description: string;
  pollUrl: string;              // e.g. '/api/v1/kundalis/:id'
  onUnlocked: () => void;
  onError: (msg: string) => void;
  onDismiss?: () => void;
}) {
  let order: RazorpayOrderResponse;
  try {
    order = await createOrder(opts.payload);
  } catch (e) {
    opts.onError(e instanceof Error ? e.message : 'Payment order creation failed.');
    return;
  }

  await openCheckout({
    order,
    name: opts.buyerName,
    email: opts.buyerEmail,
    phone: opts.buyerPhone,
    description: opts.description,
    onDismiss: opts.onDismiss,
    onError: opts.onError,
    onSuccess: async (pid, oid, sig) => {
      try {
        // Step 1: Verify signature + unlock on backend (works without webhook)
        await verifyPayment(pid, oid, sig);

        // Step 2: Call onUnlocked immediately — no polling needed
        opts.onUnlocked();
      } catch (verifyErr) {
        // Fallback: if verify fails, try polling (in case webhook already fired)
        const unlocked = await pollUntilUnlocked(opts.pollUrl, 15_000);
        if (unlocked) {
          opts.onUnlocked();
        } else {
          opts.onError(
            verifyErr instanceof Error
              ? verifyErr.message
              : 'पेमेंट मिळाले पण अनलॉक करताना त्रुटी आली. पान रीफ्रेश करा.'
          );
        }
      }
    },
  });
}

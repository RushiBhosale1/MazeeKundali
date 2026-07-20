# Payment Integration

## Recommended Gateway: Razorpay
- Best India-first UX: UPI, cards, netbanking, wallets all in one checkout.
- Has a hosted Checkout.js widget that's fast to integrate.

## Important — Verify Before Building
Astrology/prediction services are sometimes flagged under stricter KYC or category review by Indian payment gateways. **Before writing integration code:**
1. Sign up and go through Razorpay's (or chosen gateway's) business KYC/activation flow early — this can take days and may require business registration documents.
2. Check current MCC (Merchant Category Code) rules for "astrology"/"prediction"/"religious services" — ask Razorpay support directly whether your specific use case (kundali generation, matchmaking reports) needs special approval. Rules change, so verify current status with Razorpay directly rather than relying on older information.
3. Have a fallback gateway in mind (PayU, Cashfree) in case of rejection.

## Pricing Structure (from requirements)
| Product | Price |
|---|---|
| Kundali (detailed) | ₹100 |
| Patrika Matching | ₹50 |
| Bundle (Kundali + Matching) | consider ₹130–140 to incentivize bundling vs ₹150 separately |
| Biodata standalone (no kundali link) | consider ₹0 (loss-leader) or small fee — decide based on whether it's meant to drive kundali upsell or stand alone |

## Payment Flow
1. Frontend requests `POST /api/v1/orders` with product type + related record id.
2. Backend creates a Razorpay Order server-side (amount, currency, receipt id = internal order id), stores `orders` row with status=`created`.
3. Frontend opens Razorpay Checkout with the `gateway_order_id`.
4. On success, Razorpay returns a payment id + signature to frontend — **frontend sends this to backend for verification, but this is NOT what unlocks content.**
5. Razorpay also sends a **server-to-server webhook** (`payment.captured`) — backend verifies the webhook signature using the webhook secret, and only then flips `orders.status=paid` and unlocks the related record.
6. Frontend polls or listens for unlock confirmation, then reveals the full report.

**Why webhook, not just frontend callback**: frontend callbacks can be spoofed, dropped on network failure, or bypassed by a technical user manipulating client state. The webhook is server-verified and is the only trustworthy signal. Frontend callback is used purely to show a fast "processing..." UX state.

## Refund / Trust Policy
- Digital reports are typically non-refundable once generated, but state this clearly at checkout.
- Offer a **free regeneration** if the user reports wrong birth details were entered (typo in DOB/time/place) — this is a low-cost trust builder that avoids most legitimate refund requests without opening a refund floodgate.
- Add a visible disclaimer near the payment button: "हा अहवाल मार्गदर्शनासाठी आहे. वैयक्तिक सल्ल्यासाठी तज्ञ ज्योतिषांचा सल्ला घ्या." (For guidance only; consult an expert astrologer for personal advice.) — reduces liability and matches standard practice across existing tools.

## Order Reconciliation
- Build a simple internal admin view (even a basic authenticated page) to look up: order id → payment status → which record it unlocked. Payment support queries ("I paid but didn't get my report") are inevitable at any transaction volume, and you need a fast way to check state instead of digging through Razorpay dashboard + DB manually each time.
- Log all webhook events raw (even ones you don't act on) for at least 90 days — needed for dispute resolution.

## Security Checklist
- Never expose Razorpay secret key to frontend — only the public key id.
- Verify webhook signature on every webhook call (Razorpay provides an HMAC signature scheme) — don't process unverified payloads.
- Idempotency: webhook may fire more than once for the same event — use the payment id to ensure you don't double-process (e.g., double-unlock or double-count revenue) on retries.

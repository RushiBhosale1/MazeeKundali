/**
 * lib/share.ts
 * WhatsApp & native share utilities for माझी कुंडली
 */

const APP_URL = process.env.NEXT_PUBLIC_APP_URL ?? 'https://mazeekundali.in';

/** Build a WhatsApp share URL with pre-filled Marathi message */
export function whatsappShareUrl(opts: {
  type: 'kundali' | 'matching' | 'manglik';
  id?: string;
  name?: string;
  rashi?: string;
  nakshatra?: string;
  score?: number;
  isManglik?: boolean;
}): string {
  let msg = '';
  const link = opts.id
    ? `${APP_URL}/${opts.type === 'matching' ? 'matching' : 'kundali'}/${opts.id}`
    : `${APP_URL}`;

  switch (opts.type) {
    case 'kundali':
      msg =
        `🪐 *${opts.name || 'माझी'} जन्मकुंडली*\n` +
        (opts.rashi ? `🌙 राशी: *${opts.rashi}*\n` : '') +
        (opts.nakshatra ? `⭐ नक्षत्र: *${opts.nakshatra}*\n` : '') +
        `\nमाझी संपूर्ण कुंडली पाहा 👇\n${link}\n\n` +
        `📲 _माझी कुंडली_ — मोफत मराठी जन्मपत्रिका`;
      break;
    case 'matching':
      msg =
        `💍 *आमची पत्रिका जुळणी*\n` +
        (opts.score !== undefined ? `✨ गुण: *${opts.score}/36*\n` : '') +
        `\nसंपूर्ण अष्टकूट निकाल पाहा 👇\n${link}\n\n` +
        `📲 _माझी कुंडली_ — मोफत पत्रिका जुळणी`;
      break;
    case 'manglik':
      msg =
        `🔴 *मंगळ दोष तपासणी*\n` +
        (opts.name ? `👤 नाव: ${opts.name}\n` : '') +
        (opts.isManglik !== undefined
          ? `मंगळ दोष: *${opts.isManglik ? 'आहे ⚠️' : 'नाही ✅'}*\n`
          : '') +
        `\nतुमचा मंगळ दोष तपासा 👇\n${APP_URL}/manglik-checker\n\n` +
        `📲 _माझी कुंडली_ — मोफत मंगळ दोष तपासणी`;
      break;
  }

  return `https://wa.me/?text=${encodeURIComponent(msg)}`;
}

/** Copy URL to clipboard with fallback */
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    // Fallback for older browsers
    const el = document.createElement('textarea');
    el.value = text;
    el.style.position = 'fixed';
    el.style.opacity = '0';
    document.body.appendChild(el);
    el.select();
    const ok = document.execCommand('copy');
    document.body.removeChild(el);
    return ok;
  }
}

/** Use Web Share API if available, fall back to WhatsApp URL */
export async function nativeShare(opts: {
  title: string;
  text: string;
  url: string;
}): Promise<'native' | 'whatsapp' | 'clipboard'> {
  if (typeof navigator !== 'undefined' && navigator.share) {
    try {
      await navigator.share(opts);
      return 'native';
    } catch {
      // User cancelled or not supported
    }
  }
  // Fall back: open WhatsApp
  const waUrl = `https://wa.me/?text=${encodeURIComponent(`${opts.text}\n${opts.url}`)}`;
  window.open(waUrl, '_blank', 'noopener,noreferrer');
  return 'whatsapp';
}

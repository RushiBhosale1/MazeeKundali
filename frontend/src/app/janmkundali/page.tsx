import type { Metadata } from 'next';
import { redirect } from 'next/navigation';

export const metadata: Metadata = {
  title: 'जन्मकुंडली — मराठीत मोफत पत्रिका | माझी कुंडली',
  description: 'मराठीत मोफत जन्मकुंडली बनवा. रास, नक्षत्र, लग्न, गण, नाडी — सर्व माहिती तात्काळ मिळवा. अचूक वैदिक गणना.',
  keywords: 'जन्मकुंडली, जन्मपत्रिका, kundali marathi, marathi kundali, पत्रिका मराठी, free kundali marathi',
  alternates: { canonical: 'https://mazeekundali.in/janmkundali' },
  openGraph: {
    title: 'जन्मकुंडली — मोफत मराठी पत्रिका',
    description: 'मोफत अचूक जन्मकुंडली. रास, नक्षत्र, लग्न तात्काळ.',
    locale: 'mr_IN',
  },
};

// This page is a thin SEO entry point — redirects to the actual form.
// The metadata above is indexed by search engines; users land here via Marathi search.
export default function JanmkundaliPage() {
  redirect('/kundali/new');
}

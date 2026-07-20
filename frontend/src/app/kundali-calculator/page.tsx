import type { Metadata } from 'next';
import { redirect } from 'next/navigation';

export const metadata: Metadata = {
  title: 'Kundali Calculator — Free Vedic Birth Chart | Mazee Kundali',
  description: 'Free Vedic kundali calculator in Marathi and English. Get Rashi, Nakshatra, Lagna, Dasha and full birth chart instantly.',
  keywords: 'kundali calculator, free kundali, vedic birth chart, marathi kundali calculator, janmakundali online',
  alternates: { canonical: 'https://mazeekundali.in/kundali-calculator' },
  openGraph: {
    title: 'Free Kundali Calculator — Vedic Birth Chart',
    description: 'Free Vedic kundali in Marathi. Rashi, Nakshatra, Lagna instant results.',
    locale: 'en_IN',
  },
};

export default function KundaliCalculatorPage() {
  redirect('/kundali/new');
}

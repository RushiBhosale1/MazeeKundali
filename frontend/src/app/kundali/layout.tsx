import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'मराठी जन्मपत्रिका (Kundali) | Mazee Kundali',
  description: 'तुमची अचूक मराठी जन्मपत्रिका (Kundali) विनामूल्य तयार करा. ग्रहांची स्थिती, रास, नक्षत्र आणि बरेच काही.',
  openGraph: {
    title: 'मराठी जन्मपत्रिका (Kundali) | Mazee Kundali',
    description: 'तुमची अचूक मराठी जन्मपत्रिका विनामूल्य तयार करा.',
  }
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}

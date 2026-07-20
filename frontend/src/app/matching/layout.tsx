import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'पत्रिका जुळणी (Kundali Matching) | Ashtakoot Guna Milan',
  description: 'लग्नासाठी पत्रिका जुळणी करा. ३६ पैकी किती गुण जुळतात ते पहा (Ashtakoot Guna Milan).',
  openGraph: {
    title: 'पत्रिका जुळणी (Kundali Matching) | Mazee Kundali',
    description: 'लग्नासाठी पत्रिका जुळणी करा. अष्टकूट गुण मिलन.',
  }
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}

import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'मंगळ दोष तपासा — मोफत मांगलिक चेकर | माझी कुंडली',
  description: 'तुमचा मंगळ दोष मोफत तपासा. जन्म तारीख, वेळ आणि ठिकाण द्या आणि लगेच जाणून घ्या. मंगळ दोष रद्दीकरण नियम पण पाहा.',
  keywords: 'मंगळ दोष, mangal dosha check, am i manglik, manglik calculator, मांगलिक तपासा',
  openGraph: {
    title: 'मंगळ दोष तपासा — मोफत',
    description: 'मोफत मंगळ दोष चेकर. जन्म माहिती द्या, लगेच उत्तर मिळवा.',
  },
};

export default function ManglikLayout({ children }: { children: React.ReactNode }) {
  return children;
}

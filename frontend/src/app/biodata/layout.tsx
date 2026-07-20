import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'लग्नाचा बायोडाटा (Marriage Biodata Maker) | Marathi Biodata',
  description: 'लग्नासाठी सुंदर आणि व्यावसायिक मराठी बायोडाटा (Biodata) ५ मिनिटांत तयार करा. विविध डिझाईन्स उपलब्ध.',
  openGraph: {
    title: 'लग्नाचा बायोडाटा (Marriage Biodata) | Mazee Kundali',
    description: 'लग्नासाठी सुंदर मराठी बायोडाटा तयार करा.',
  }
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}

import type { Metadata } from 'next';
import Script from 'next/script';
import './globals.css';

export const metadata: Metadata = {
  title: 'माझी कुंडली — मराठी जन्मपत्रिका, पत्रिका जुळणी व बायोडाटा',
  description: 'अचूक मराठी कुंडली, अष्टकूट गुण मिलन आणि व्यावसायिक बायोडाटा. विनामूल्य जन्मपत्रिका पाहा.',
  keywords: 'मराठी कुंडली, kundali marathi, patrika julanee, kundali matching marathi, biodata marathi, mangal dosha',
  openGraph: {
    title: 'माझी कुंडली — मराठी जन्मपत्रिका',
    description: 'अचूक मराठी कुंडली, अष्टकूट गुण मिलन आणि व्यावसायिक बायोडाटा.',
    locale: 'mr_IN',
    type: 'website',
    url: 'https://mazeekundali.in',
    siteName: 'Mazee Kundali',
    images: [
      {
        url: 'https://mazeekundali.in/logo.png',
        width: 1200,
        height: 630,
        alt: 'Mazee Kundali Logo',
      },
    ],
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="mr">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
        <meta name="theme-color" content="#0d1b2a" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
        {process.env.NEXT_PUBLIC_GA_ID && (
          <>
            <Script src={`https://www.googletagmanager.com/gtag/js?id=${process.env.NEXT_PUBLIC_GA_ID}`} strategy="afterInteractive" />
            <Script id="google-analytics" strategy="afterInteractive">
              {`
                window.dataLayer = window.dataLayer || [];
                function gtag(){dataLayer.push(arguments);}
                gtag('js', new Date());
                gtag('config', '${process.env.NEXT_PUBLIC_GA_ID}');
              `}
            </Script>
          </>
        )}
      </head>
      <body>
        {children}
      </body>
    </html>
  );
}

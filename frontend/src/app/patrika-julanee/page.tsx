import type { Metadata } from 'next';
import { redirect } from 'next/navigation';

export const metadata: Metadata = {
  title: 'पत्रिका जुळणी — मोफत गुण मिलन | माझी कुंडली',
  description: 'मोफत पत्रिका जुळणी तपासा. अष्टकूट गुण मिलन — वर्ण, वश्य, तारा, योनी, ग्रह मैत्री, गण, भकूट, नाडी. लगेच निकाल.',
  keywords: 'पत्रिका जुळणी, kundali matching marathi, guna milan, patrika julanee, अष्टकूट',
  alternates: { canonical: 'https://mazeekundali.in/patrika-julanee' },
  openGraph: {
    title: 'पत्रिका जुळणी — मोफत अष्टकूट गुण मिलन',
    description: 'मोफत पत्रिका जुळणी — ३६ पैकी गुण मोजा.',
    locale: 'mr_IN',
  },
};

export default function PatrikaJulaneePage() {
  redirect('/matching/new');
}

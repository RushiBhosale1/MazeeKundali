import type { MetadataRoute } from 'next';

const BASE_URL = 'https://mazeekundali.in';

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    // Core pages
    { url: BASE_URL,                          lastModified: new Date(), changeFrequency: 'daily',   priority: 1.0 },
    { url: `${BASE_URL}/kundali/new`,         lastModified: new Date(), changeFrequency: 'weekly',  priority: 0.9 },
    { url: `${BASE_URL}/matching/new`,        lastModified: new Date(), changeFrequency: 'weekly',  priority: 0.9 },
    { url: `${BASE_URL}/biodata/new`,         lastModified: new Date(), changeFrequency: 'weekly',  priority: 0.8 },

    // SEO entry points — Marathi keywords
    { url: `${BASE_URL}/janmkundali`,         lastModified: new Date(), changeFrequency: 'monthly', priority: 0.8 },
    { url: `${BASE_URL}/kundali-calculator`,  lastModified: new Date(), changeFrequency: 'monthly', priority: 0.7 },
    { url: `${BASE_URL}/patrika-julanee`,     lastModified: new Date(), changeFrequency: 'monthly', priority: 0.8 },
    { url: `${BASE_URL}/manglik-checker`,     lastModified: new Date(), changeFrequency: 'monthly', priority: 0.8 },
  ];
}

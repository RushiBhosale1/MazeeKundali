import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'Noto Sans Devanagari', 'system-ui', 'sans-serif'],
        devanagari: ['Noto Sans Devanagari', 'Tiro Devanagari Marathi', 'serif'],
      },
      colors: {
        saffron: {
          400: '#ff9b1f',
          500: '#f07c00',
          600: '#cc6200',
          700: '#a04d00',
        },
        gold: {
          300: '#f6d860',
          400: '#e8c22a',
          500: '#c9a227',
        },
        navy: {
          600: '#234069',
          700: '#1a3050',
          800: '#132337',
          900: '#0d1b2a',
        },
      },
    },
  },
  plugins: [],
};

export default config;

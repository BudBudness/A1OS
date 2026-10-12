import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        stramos: {
          black: '#0A0A0A',
          red: '#D62828',
          white: '#FFFFFF',
        },
      },
    },
  },
  plugins: [],
};

export default config;

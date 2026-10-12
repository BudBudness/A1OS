import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Stramos Wisdom Charity',
  description: 'James 1:27 in Action. Love Wins.',
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

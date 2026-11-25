import "./globals.css";

export const metadata = {
  title: "A1OS",
  description: "A1OS platform control and research interface"
};

export default function RootLayout({ children }) {
  return <html lang="en"><body>{children}</body></html>;
}

import "./globals.css";

export const metadata = {
  title: "Little Oaks Montessori Nursery & Kindergarten",
  description: "Little Oaks Montessori Kindergarten & Day Care Centre, Nyamitanga, Mbarara."
};

export default function RootLayout({ children }) {
  return <html lang="en"><body>{children}</body></html>;
}

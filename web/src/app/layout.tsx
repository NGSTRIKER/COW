import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/Navbar";

export const metadata: Metadata = {
  title: "Hu Immortal Control Panel — Discord Bot Web Dashboard",
  description: "Advanced Discord Server Administration, Security, and Analytics Dashboard.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-[#070a12] text-slate-100 antialiased selection:bg-purple-500/30 selection:text-purple-200">
        <Navbar />
        <main>{children}</main>
      </body>
    </html>
  );
}

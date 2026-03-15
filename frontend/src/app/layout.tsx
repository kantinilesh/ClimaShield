import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "ClimaShield – AI Parametric Insurance",
  description: "Decentralized climate insurance platform powered by GOAT Network",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} font-sans bg-[#060a13] text-gray-100 antialiased`}>
        {children}
      </body>
    </html>
  );
}

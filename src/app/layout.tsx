import type { Metadata } from "next";
import { Fraunces, Work_Sans } from "next/font/google";
import { SiteHeader } from "@/components/site-header";
import { BottomNav } from "@/components/bottom-nav";
import { CartProvider } from "@/lib/cart/context";
import "./globals.css";

const fraunces = Fraunces({
  variable: "--font-fraunces",
  subsets: ["latin"],
  style: ["normal", "italic"],
});

const workSans = Work_Sans({
  variable: "--font-work-sans",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Beauty House",
  description:
    "Makeup, skincare and handbags — everyday essentials plus by-reservation luxury pieces from Louis Vuitton, Chanel and Dior.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${fraunces.variable} ${workSans.variable} h-full`}>
      <body className="flex min-h-full flex-col font-sans antialiased">
        <CartProvider>
          <SiteHeader />
          <main className="flex-1 pb-20 lg:pb-0">{children}</main>
          <BottomNav />
        </CartProvider>
      </body>
    </html>
  );
}

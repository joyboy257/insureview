import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/layout/Providers";
import { MASDisclaimer } from "@/components/MASDisclaimer";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Insureview -- See Your Full Insurance Picture",
  description:
    "Upload your Singapore insurance policies and get plain-English analysis of gaps, overlaps, and conflicts in your coverage.",
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          <div className="fixed bottom-0 left-0 right-0 z-50">
            <MASDisclaimer />
          </div>
          {children}
        </Providers>
      </body>
    </html>
  );
}

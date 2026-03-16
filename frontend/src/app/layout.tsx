import type { Metadata } from "next";
import { Outfit, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const outfit = Outfit({
  variable: "--font-outfit",
  subsets: ["latin"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "SwingFish | Ocean Terminal",
  description: "Advanced Multiagent Swing Trading Analysis",
};

import AuthorSeal from "@/components/AuthorSeal";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${outfit.variable} ${jetbrainsMono.variable} antialiased bg-abyssal text-primary-text min-h-screen selection:bg-accent selection:text-abyssal`}
      >
        {children}
        <AuthorSeal />
      </body>
    </html>
  );
}

import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Vibe - Social Media",
  description: "A premium social media application for sharing vibes.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Silver Alpha",
  description: "Narrative intelligence for silver market analysis.",
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

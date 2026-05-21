import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DeskMate",
  description: "AI-powered IT helpdesk chatbot POC",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

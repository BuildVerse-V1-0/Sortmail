import type { Metadata } from "next";
import { Fraunces, Syne, JetBrains_Mono } from "next/font/google";
import "@/styles/globals.css";
import { Providers } from "@/app/providers";

const fraunces = Fraunces({
    subsets: ["latin"],
    variable: "--font-fraunces",
    display: "swap",
});

const syne = Syne({
    subsets: ["latin"],
    variable: "--font-syne",
    display: "swap",
});

const jetbrains = JetBrains_Mono({
    subsets: ["latin"],
    variable: "--font-jetbrains",
    display: "swap",
});

export const metadata: Metadata = {
    title: "SortMail — AI Email Intelligence for Gmail & Outlook",
    description:
        "AI-powered intelligence layer that summarizes threads, extracts tasks, and drafts replies. Your inbox, finally under control.",
    keywords: ["email", "AI", "Gmail", "Outlook", "productivity", "task management"],
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html
            lang="en"
            className={`${fraunces.variable} ${syne.variable} ${jetbrains.variable}`}
        >
            <body className="font-body antialiased bg-paper text-ink">
                <Providers>
                    {children}
                </Providers>
            </body>
        </html>
    );
}

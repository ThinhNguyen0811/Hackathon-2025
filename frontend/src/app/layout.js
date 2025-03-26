import React, { ReactNode } from "react";
import "../app/globals.css";
import Navbar from "../components/Navbar";
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'] });

export default function RootLayout({ children }) {
    return (
        <html lang="en">
        <body className={`bg-gray-100 p-6 ${inter.className}`}>
            <div className="max-w-6xl mx-auto bg-white shadow-md rounded-lg p-6">
                <Navbar />
                <div id="content">
                    {children}
                </div>
            </div>
        </body>
        </html>
    );
}
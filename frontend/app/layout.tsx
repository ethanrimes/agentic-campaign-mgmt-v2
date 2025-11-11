// frontend/app/layout.tsx

import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import '@/styles/globals.css'
import Navigation from '@/components/layout/Navigation'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Social Media Knowledge Database',
  description: 'Living Knowledge Database for autonomous social media management',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="smooth-scroll">
      <body className={inter.className}>
        <div className="min-h-screen">
          <Navigation />
          <main className="container mx-auto px-4 py-8 animate-fade-in">
            {children}
          </main>
        </div>
      </body>
    </html>
  )
}

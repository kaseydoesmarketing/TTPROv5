import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'TitleTesterPro - A/B Test Your YouTube Titles',
  description: 'Optimize your YouTube titles with data-driven A/B testing. Increase views, engagement, and subscribers with TitleTesterPro.',
  keywords: 'YouTube, A/B testing, titles, optimization, views, engagement',
  authors: [{ name: 'TitleTesterPro' }],
  openGraph: {
    title: 'TitleTesterPro - A/B Test Your YouTube Titles',
    description: 'Optimize your YouTube titles with data-driven A/B testing.',
    type: 'website',
    url: 'https://titletesterpro.com',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'TitleTesterPro - A/B Test Your YouTube Titles',
    description: 'Optimize your YouTube titles with data-driven A/B testing.',
  }
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
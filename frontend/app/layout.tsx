import type { Metadata, Viewport } from 'next'
import { Inter, Space_Grotesk } from 'next/font/google'
import { AuthProvider } from '@/lib/auth-context'
import { ThemeProvider } from '@/components/theme-provider'
import { Toaster } from 'sonner'

import './globals.css'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
})

const spaceGrotesk = Space_Grotesk({
  subsets: ['latin'],
  variable: '--font-space-grotesk',
})

export const metadata: Metadata = {
  title: 'Agrovee - AI-Powered Smart Farming Assistant',
  description:
    'Monitor crop health, detect diseases, and get AI-powered farming advice with Agrovee.',
  keywords: ['agriculture', 'crop health', 'disease detection', 'AI farming', 'smart agriculture', 'plant disease'],
  authors: [{ name: 'Agrovee' }],
  manifest: '/manifest.json',
  icons: {
    icon: '/icon.svg',
  },
  openGraph: {
    title: 'Agrovee - AI-Powered Smart Farming Assistant',
    description: 'Upload crop images, detect diseases, get treatment recommendations, and chat with an AI farming assistant.',
    siteName: 'Agrovee',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Agrovee',
    description: 'AI-Powered Crop Health Monitoring & Disease Detection',
  },
}

export const viewport: Viewport = {
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#16a34a' },
    { media: '(prefers-color-scheme: dark)', color: '#0a0a0a' },
  ],
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${inter.variable} ${spaceGrotesk.variable} font-sans antialiased`}
      >
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <AuthProvider>
            {children}
          </AuthProvider>
          <Toaster position="top-right" richColors closeButton />
        </ThemeProvider>
      </body>
    </html>
  )
}

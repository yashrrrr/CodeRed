import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'upGrad® Education - India\'s Top Upskilling Platform Online',
  description: 'upGrad®, Choose from top online programs in AI, Data Science, MBA, Marketing, Tech. ✔ Trusted by 100+Academic & Industry Partners ✔ Career support ✔ Flexible learning.',
  keywords: ['education', 'upskilling', 'online courses', 'AI', 'Data Science', 'MBA', 'Marketing', 'Tech'],
  authors: [{ name: 'upGrad Team' }],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-white">
          {children}
        </div>
      </body>
    </html>
  )
}

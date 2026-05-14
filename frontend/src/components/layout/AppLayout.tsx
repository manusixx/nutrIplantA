import { useRef, useEffect, useState } from 'react'
import TopNavBar from './TopNavBar'

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const headerRef = useRef<HTMLDivElement>(null)
  const [headerHeight, setHeaderHeight] = useState(80)

  useEffect(() => {
    const header = headerRef.current
    if (!header) return

    // Mide el header al cargar
    setHeaderHeight(header.offsetHeight)

    // Remide si el header cambia de tamaño (responsive)
    const observer = new ResizeObserver(() => {
      setHeaderHeight(header.offsetHeight)
    })
    observer.observe(header)
    return () => observer.disconnect()
  }, [])

  return (
    <div className="min-h-screen bg-surface">
      <div ref={headerRef} className="fixed top-0 left-0 right-0 z-50">
        <TopNavBar />
      </div>
      <main
        style={{ paddingTop: `${headerHeight + 32}px` }}
        className="max-w-container mx-auto px-6 lg:px-12 pb-12"
      >
        {children}
      </main>
    </div>
  )
}
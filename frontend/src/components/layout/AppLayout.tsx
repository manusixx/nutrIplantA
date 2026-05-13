import TopNavBar from './TopNavBar'

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-surface">
      <TopNavBar />
      <main className="pt-20 max-w-container mx-auto px-6 lg:px-12 py-10 lg:py-12">
        {children}
      </main>
    </div>
  )
}

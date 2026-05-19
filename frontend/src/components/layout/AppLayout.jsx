import Sidebar from './Sidebar'

export default function AppLayout({ children }) {
  return (
    <div className="flex bg-gray-950 min-h-screen">
      <Sidebar />
      <main className="ml-64 flex-1 p-6 bg-gray-950 min-h-screen overflow-x-auto">
        {children}
      </main>
    </div>
  )
}
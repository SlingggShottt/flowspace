import { useLocation } from 'react-router-dom'
import Sidebar from './Sidebar'
import NotificationBell from './NotificationBell'

export default function AppLayout({ children }) {
  const location = useLocation()
  const projectIdMatch = location.pathname.match(/\/board\/([^/]+)/)
  const currentProjectId = projectIdMatch ? projectIdMatch[1] : null

  return (
    <div className="flex bg-gray-950 min-h-screen">
      <Sidebar />
      <main className="flex-1 p-6 bg-gray-950 min-h-screen overflow-x-auto transition-all duration-300 ml-72">
        <div className="fixed top-6 right-6 z-50">
          <NotificationBell projectId={currentProjectId} />
        </div>
        {children}
      </main>
    </div>
  )
}
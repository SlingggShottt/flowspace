import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Users, Settings, LogOut, Plus, LayoutGrid, Pencil } from 'lucide-react'
import { getProjects } from '../../api/projects'
import { logout } from '../../api/auth'
import useAuthStore from '../../store/authStore'

export default function Sidebar() {
  const location = useLocation()
  const navigate = useNavigate()
  const clearAuth = useAuthStore((state) => state.clearAuth)

  const { data: projectsData } = useQuery({
    queryKey: ['projects'],
    queryFn: getProjects,
  })

  const projects = projectsData?.data || []

  const handleLogout = async () => {
    await logout()
    clearAuth()
    navigate('/login')
  }

  return (
    <div className="w-64 bg-gray-900 text-white h-screen flex flex-col fixed left-0 top-0">
      <div className="p-4 border-b border-gray-700">
        <h1 className="text-xl font-bold text-indigo-400">Flowspace</h1>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">Projects</p>
        {projects.map((project) => (
          <div
            key={project.id}
            className={`flex items-center gap-1 mb-1 rounded-lg group ${
              location.pathname === `/board/${project.id}` ? 'bg-indigo-600' : 'hover:bg-gray-800'
            }`}
          >
            <Link
              to={`/board/${project.id}`}
              className="flex items-center gap-2 px-3 py-2 text-sm flex-1 min-w-0"
            >
              <span
                className="w-3 h-3 rounded-full flex-shrink-0"
                style={{ backgroundColor: project.color }}
              />
              <span className="truncate text-gray-200">{project.name}</span>
            </Link>
            <Link
              to={`/projects/${project.id}/edit`}
              className="pr-2 text-gray-500 hover:text-gray-300 opacity-0 group-hover:opacity-100 transition-opacity"
            >
              <Pencil size={12} />
            </Link>
          </div>
        ))}

        <Link
          to="/projects/new"
          className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-gray-400 hover:bg-gray-800 mt-1"
        >
          <Plus size={16} />
          New Project
        </Link>
      </div>

      <div className="p-4 border-t border-gray-700 space-y-1">
        <Link
          to="/members"
          className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
            location.pathname === '/members'
              ? 'bg-gray-700 text-white'
              : 'text-gray-300 hover:bg-gray-800'
          }`}
        >
          <Users size={16} />
          Members
        </Link>
        <Link
          to="/teams"
          className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
            location.pathname === '/teams'
              ? 'bg-gray-700 text-white'
              : 'text-gray-300 hover:bg-gray-800'
          }`}
        >
          <LayoutGrid size={16} />
          Teams
        </Link>
        <Link
          to="/settings"
          className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
            location.pathname === '/settings'
              ? 'bg-gray-700 text-white'
              : 'text-gray-300 hover:bg-gray-800'
          }`}
        >
          <Settings size={16} />
          Settings
        </Link>
        <button
          onClick={handleLogout}
          className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-gray-300 hover:bg-gray-800 w-full"
        >
          <LogOut size={16} />
          Logout
        </button>
      </div>
    </div>
  )
}
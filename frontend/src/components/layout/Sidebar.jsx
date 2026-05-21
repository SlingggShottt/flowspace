import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Users, Settings, LogOut, Plus, LayoutGrid, Pencil, ChevronLeft, ChevronRight, CreditCard } from 'lucide-react'
import { getProjects } from '../../api/projects'
import { getBillingInfo } from '../../api/billing'
import { logout } from '../../api/auth'
import useAuthStore from '../../store/authStore'

const planColors = {
  free: 'bg-gray-700 text-gray-300',
  pro: 'bg-indigo-900/60 text-indigo-300',
  enterprise: 'bg-purple-900/60 text-purple-300',
}

export default function Sidebar() {
  const location = useLocation()
  const navigate = useNavigate()
  const clearAuth = useAuthStore((state) => state.clearAuth)
  const user = useAuthStore((state) => state.user)
  const isAdmin = user?.role === 'admin'
  const [collapsed, setCollapsed] = useState(false)

  const { data: projectsData } = useQuery({
    queryKey: ['projects'],
    queryFn: getProjects,
  })

  const { data: billingData } = useQuery({
    queryKey: ['billing'],
    queryFn: getBillingInfo,
  })

  const projects = projectsData?.data || []
  const plan = billingData?.data?.current_plan || 'free'

  const handleLogout = async () => {
    await logout()
    clearAuth()
    navigate('/login')
  }

  const getInitials = (name) => {
    if (!name) return '?'
    return name.split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2)
  }

  return (
    <div
      className={`bg-gray-900 text-white h-screen flex flex-col fixed left-0 top-0 transition-all duration-300 ${
        collapsed ? 'w-16' : 'w-72'
      }`}
    >
      <div className="p-4 border-b border-gray-700 flex items-center justify-between">
        {!collapsed && (
          <div>
            <h1 className="text-2xl font-bold text-indigo-400">Flowspace</h1>
            <span className={`text-xs px-2 py-0.5 rounded-full capitalize font-medium ${planColors[plan]}`}>
              {plan} plan
            </span>
          </div>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="text-gray-400 hover:text-white transition-colors ml-auto"
        >
          {collapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-3">
        {!collapsed && (
          <p className="text-sm text-gray-500 uppercase tracking-wider mb-2 px-2">Projects</p>
        )}
        {projects.map((project) => (
          <div
            key={project.id}
            className={`flex items-center gap-1 mb-1 rounded-lg group ${
              location.pathname === `/board/${project.id}` ? 'bg-indigo-600' : 'hover:bg-gray-800'
            }`}
          >
            <Link
              to={`/board/${project.id}`}
              className="flex items-center gap-2 px-3 py-2 text-base flex-1 min-w-0"
              title={collapsed ? project.name : ''}
            >
              <span
                className="w-3.5 h-3.5 rounded-full flex-shrink-0"
                style={{ backgroundColor: project.color }}
              />
              {!collapsed && (
                <span className="truncate text-gray-200 text-base">{project.name}</span>
              )}
            </Link>
            {!collapsed && (
              <Link
                to={`/projects/${project.id}/edit`}
                className="pr-2 text-gray-500 hover:text-white opacity-0 group-hover:opacity-100 transition-all"
              >
                <Pencil size={14} />
              </Link>
            )}
          </div>
        ))}

        {!collapsed && (
          <Link
            to="/projects/new"
            className="flex items-center gap-2 px-3 py-2 rounded-lg text-base text-gray-400 hover:bg-gray-800 mt-1"
          >
            <Plus size={18} />
            New Project
          </Link>
        )}

        {collapsed && (
          <Link
            to="/projects/new"
            className="flex items-center justify-center py-2 rounded-lg text-gray-400 hover:bg-gray-800 mt-1"
            title="New Project"
          >
            <Plus size={18} />
          </Link>
        )}
      </div>

      <div className="p-3 border-t border-gray-700 space-y-1">
        {!collapsed && (
          <Link
            to="/profile"
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-base transition-colors ${
              location.pathname === '/profile' ? 'bg-gray-700 text-white' : 'text-gray-300 hover:bg-gray-800'
            }`}
          >
            <div className="w-6 h-6 bg-indigo-600 rounded-full flex items-center justify-center text-white text-xs font-semibold flex-shrink-0">
              {getInitials(user?.name)}
            </div>
            <span className="truncate">{user?.name || 'My Profile'}</span>
          </Link>
        )}
        <Link
          to="/members"
          className={`flex items-center gap-2 px-3 py-2 rounded-lg text-base transition-colors ${
            location.pathname === '/members' ? 'bg-gray-700 text-white' : 'text-gray-300 hover:bg-gray-800'
          }`}
          title={collapsed ? 'Members' : ''}
        >
          <Users size={18} />
          {!collapsed && 'Members'}
        </Link>
        {isAdmin && (
          <Link
            to="/teams"
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-base transition-colors ${
              location.pathname === '/teams' ? 'bg-gray-700 text-white' : 'text-gray-300 hover:bg-gray-800'
            }`}
            title={collapsed ? 'Teams' : ''}
          >
            <LayoutGrid size={18} />
            {!collapsed && 'Teams'}
          </Link>
        )}
        {isAdmin && (
          <Link
            to="/billing"
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-base transition-colors ${
              location.pathname === '/billing' ? 'bg-gray-700 text-white' : 'text-gray-300 hover:bg-gray-800'
            }`}
            title={collapsed ? 'Billing' : ''}
          >
            <CreditCard size={18} />
            {!collapsed && 'Billing'}
          </Link>
        )}
        <Link
          to="/settings"
          className={`flex items-center gap-2 px-3 py-2 rounded-lg text-base transition-colors ${
            location.pathname === '/settings' ? 'bg-gray-700 text-white' : 'text-gray-300 hover:bg-gray-800'
          }`}
          title={collapsed ? 'Settings' : ''}
        >
          <Settings size={18} />
          {!collapsed && 'Settings'}
        </Link>
        <button
          onClick={handleLogout}
          className="flex items-center gap-2 px-3 py-2 rounded-lg text-base text-gray-300 hover:bg-gray-800 w-full"
          title={collapsed ? 'Logout' : ''}
        >
          <LogOut size={18} />
          {!collapsed && 'Logout'}
        </button>
      </div>
    </div>
  )
}
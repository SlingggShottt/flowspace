import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { AlertTriangle, CheckCircle, Clock, Users, FolderOpen, ListTodo, TrendingUp, Activity } from 'lucide-react'
import { getDashboard } from '../api/dashboard'
import AppLayout from '../components/layout/AppLayout'
import useAuthStore from '../store/authStore'

const SORT_OPTIONS = [
  { value: 'name', label: 'Name (A-Z)' },
  { value: 'overdue', label: 'Most Overdue' },
  { value: 'tasks', label: 'Most Tasks' },
]

function timeAgo(isoString) {
  if (!isoString) return ''
  const diff = Math.floor((Date.now() - new Date(isoString)) / 1000)
  if (diff < 60) return `${diff}s ago`
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
  return `${Math.floor(diff / 86400)}d ago`
}

function SummaryCard({ icon: Icon, label, value, color }) {
  return (
    <div className="bg-gray-800 rounded-xl p-5 flex items-center gap-4">
      <div className={`p-3 rounded-lg ${color}`}>
        <Icon size={22} className="text-white" />
      </div>
      <div>
        <p className="text-gray-400 text-sm">{label}</p>
        <p className="text-white text-2xl font-bold">{value}</p>
      </div>
    </div>
  )
}

function ProjectCard({ project, isAdmin, onClick }) {
  const hasOverdue = project.overdue_tasks > 0

  return (
    <div
      onClick={onClick}
      className="bg-gray-800 rounded-xl p-5 cursor-pointer hover:bg-gray-750 hover:ring-1 hover:ring-indigo-500 transition-all relative overflow-hidden group"
    >
      {/* color strip */}
      <div
        className="absolute left-0 top-0 bottom-0 w-1 rounded-l-xl"
        style={{ backgroundColor: project.color }}
      />

      <div className="pl-3">
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1 min-w-0">
            <h3 className="text-white font-semibold text-base truncate group-hover:text-indigo-300 transition-colors">
              {project.name}
            </h3>
            {project.description && (
              <p className="text-gray-500 text-xs mt-0.5 truncate">{project.description}</p>
            )}
          </div>
          {hasOverdue && (
            <span className="ml-2 flex-shrink-0 bg-red-500/20 text-red-400 text-xs font-medium px-2 py-0.5 rounded-full flex items-center gap-1">
              <AlertTriangle size={10} />
              {project.overdue_tasks} overdue
            </span>
          )}
        </div>

        <div className="grid grid-cols-3 gap-2 mt-4">
          {isAdmin ? (
            <>
              <Stat label="Total" value={project.total_tasks} color="text-gray-300" />
              <Stat label="Done" value={project.completed_tasks} color="text-green-400" />
              <Stat label="Overdue" value={project.overdue_tasks} color="text-red-400" />
            </>
          ) : (
            <>
              <Stat label="Assigned" value={project.assigned_tasks} color="text-indigo-400" />
              <Stat label="Done" value={project.completed_tasks} color="text-green-400" />
              <Stat label="Overdue" value={project.overdue_tasks} color="text-red-400" />
            </>
          )}
        </div>
      </div>
    </div>
  )
}

function Stat({ label, value, color }) {
  return (
    <div className="text-center">
      <p className={`text-lg font-bold ${color}`}>{value}</p>
      <p className="text-gray-500 text-xs">{label}</p>
    </div>
  )
}

export default function DashboardPage() {
  const navigate = useNavigate()
  const user = useAuthStore((state) => state.user)
  const isAdmin = user?.role === 'admin'
  const [sortBy, setSortBy] = useState('name')

  const { data, isLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: getDashboard,
  })

  const dashboard = data?.data

  const sortedProjects = [...(dashboard?.projects || [])].sort((a, b) => {
    if (sortBy === 'name') return a.name.localeCompare(b.name)
    if (sortBy === 'overdue') return b.overdue_tasks - a.overdue_tasks
    if (sortBy === 'tasks') return (b.total_tasks ?? b.assigned_tasks ?? 0) - (a.total_tasks ?? a.assigned_tasks ?? 0)
    return 0
  })

  if (isLoading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-400">Loading dashboard...</div>
        </div>
      </AppLayout>
    )
  }

  const summary = dashboard?.summary || {}
  const recentActivity = dashboard?.recent_activity || []

  return (
    <AppLayout>
      <div className="p-6 max-w-7xl mx-auto">

        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-white">Dashboard</h1>
          <p className="text-gray-400 text-sm mt-1">
            {isAdmin ? 'Workspace overview' : 'Your work at a glance'}
          </p>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {isAdmin ? (
            <>
              <SummaryCard icon={FolderOpen} label="Projects" value={summary.total_projects ?? 0} color="bg-indigo-600" />
              <SummaryCard icon={Users} label="Members" value={summary.total_members ?? 0} color="bg-blue-600" />
              <SummaryCard icon={ListTodo} label="Total Tasks" value={summary.total_tasks ?? 0} color="bg-purple-600" />
              <SummaryCard icon={AlertTriangle} label="Overdue" value={summary.total_overdue ?? 0} color="bg-red-600" />
            </>
          ) : (
            <>
              <SummaryCard icon={ListTodo} label="Assigned to You" value={summary.total_assigned ?? 0} color="bg-indigo-600" />
              <SummaryCard icon={Clock} label="Due Soon" value={summary.due_soon ?? 0} color="bg-yellow-600" />
              <SummaryCard icon={AlertTriangle} label="Overdue" value={summary.total_overdue ?? 0} color="bg-red-600" />
              <SummaryCard icon={CheckCircle} label="Projects" value={sortedProjects.length} color="bg-green-600" />
            </>
          )}
        </div>

        {/* Recent Activity */}
        {recentActivity.length > 0 && (
          <div className="bg-gray-800 rounded-xl p-5 mb-6">
            <div className="flex items-center gap-2 mb-4">
              <Activity size={16} className="text-indigo-400" />
              <h2 className="text-white font-semibold text-sm">Recent Activity</h2>
            </div>
            <div className="space-y-2">
              {recentActivity.map((item, i) => (
                <div key={i} className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2 min-w-0">
                    <div className="w-1.5 h-1.5 rounded-full bg-indigo-400 flex-shrink-0" />
                    <span className="text-indigo-300 font-medium flex-shrink-0">{item.user_name}</span>
                    <span className="text-gray-400 truncate">{item.action}{item.detail ? ` — ${item.detail}` : ''}</span>
                  </div>
                  <span className="text-gray-600 text-xs flex-shrink-0 ml-4">{timeAgo(item.created_at)}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <hr className="border-gray-700 mb-6" />

        {/* Projects Section Header */}
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-white font-semibold">Projects</h2>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="bg-gray-800 text-gray-300 text-sm border border-gray-700 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            {SORT_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
        </div>

        {/* Project Cards */}
        {sortedProjects.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 text-center">
            <FolderOpen size={48} className="text-gray-600 mb-4" />
            {isAdmin ? (
              <>
                <h3 className="text-white font-semibold text-lg mb-2">No projects yet</h3>
                <p className="text-gray-400 text-sm mb-4">Create your first project to get started</p>
                <button
                  onClick={() => navigate('/projects/new')}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm transition-colors"
                >
                  Create Project
                </button>
              </>
            ) : (
              <>
                <h3 className="text-white font-semibold text-lg mb-2">No projects assigned</h3>
                <p className="text-gray-400 text-sm">Ask your admin to add you to a team with projects</p>
              </>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {sortedProjects.map((project) => (
              <ProjectCard
                key={project.id}
                project={project}
                isAdmin={isAdmin}
                onClick={() => navigate(`/board/${project.id}`)}
              />
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  )
}
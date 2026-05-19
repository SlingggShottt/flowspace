import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query'
import { getProject, updateProject, deleteProject } from '../api/projects'
import { getTeams } from '../api/teams'
import AppLayout from '../components/layout/AppLayout'
import { Trash2 } from 'lucide-react'

const colorOptions = [
  '#6366f1', '#8b5cf6', '#ec4899', '#ef4444',
  '#f97316', '#eab308', '#22c55e', '#06b6d4',
]

export default function EditProjectPage() {
  const { projectId } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [form, setForm] = useState({ name: '', description: '', color: '#6366f1', team_id: '' })
  const [error, setError] = useState('')

  const { data: projectData } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => getProject(projectId),
  })

  const { data: teamsData } = useQuery({ queryKey: ['teams'], queryFn: getTeams })
  const teams = teamsData?.data || []

  useEffect(() => {
    if (projectData?.data) {
      const p = projectData.data
      setForm({
        name: p.name || '',
        description: p.description || '',
        color: p.color || '#6366f1',
        team_id: p.team_id || '',
      })
    }
  }, [projectData])

  const updateMutation = useMutation({
    mutationFn: (data) => updateProject(projectId, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['projects'])
      queryClient.invalidateQueries(['project', projectId])
      navigate(`/board/${projectId}`)
    },
    onError: (err) => setError(err.response?.data?.detail || 'Failed to update project'),
  })

  const deleteMutation = useMutation({
    mutationFn: () => deleteProject(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries(['projects'])
      navigate('/')
    },
  })

  const handleSubmit = () => {
    if (!form.name.trim()) {
      setError('Project name is required')
      return
    }
    const payload = { ...form }
    if (!payload.team_id) delete payload.team_id
    updateMutation.mutate(payload)
  }

  return (
    <AppLayout>
      <div className="max-w-lg">
        <h1 className="text-2xl font-bold text-white mb-6">Edit Project</h1>

        <div className="bg-gray-800 rounded-xl p-6 space-y-4">
          {error && <p className="text-red-400 text-sm">{error}</p>}

          <div>
            <label className="block text-sm text-gray-400 mb-1">Project name</label>
            <input
              type="text"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="w-full bg-gray-700 text-white px-3 py-2 rounded-lg text-sm focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-1">Description</label>
            <textarea
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              rows={3}
              className="w-full bg-gray-700 text-white px-3 py-2 rounded-lg text-sm focus:outline-none resize-none"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-1">Assign to team</label>
            <select
              value={form.team_id}
              onChange={(e) => setForm({ ...form, team_id: e.target.value })}
              className="w-full bg-gray-700 text-white px-3 py-2 rounded-lg text-sm focus:outline-none"
            >
              <option value="">No team (visible to all)</option>
              {teams.map((team) => (
                <option key={team.id} value={team.id}>
                  {team.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">Color</label>
            <div className="flex gap-2">
              {colorOptions.map((color) => (
                <button
                  key={color}
                  onClick={() => setForm({ ...form, color })}
                  className={`w-7 h-7 rounded-full border-2 transition-transform ${
                    form.color === color ? 'border-white scale-110' : 'border-transparent'
                  }`}
                  style={{ backgroundColor: color }}
                />
              ))}
            </div>
          </div>

          <div className="flex gap-3 pt-2">
            <button
              onClick={() => navigate(-1)}
              className="flex-1 bg-gray-700 hover:bg-gray-600 text-white py-2 rounded-lg text-sm"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={updateMutation.isPending}
              className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white py-2 rounded-lg text-sm font-medium disabled:opacity-50"
            >
              {updateMutation.isPending ? 'Saving...' : 'Save changes'}
            </button>
          </div>

          <div className="border-t border-gray-700 pt-4">
            <button
              onClick={() => {
                if (window.confirm('Archive this project? All tasks will be preserved.')) {
                  deleteMutation.mutate()
                }
              }}
              className="flex items-center gap-2 text-red-400 hover:text-red-300 text-sm"
            >
              <Trash2 size={16} />
              Archive project
            </button>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
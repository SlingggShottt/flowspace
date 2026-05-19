import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { X, Trash2 } from 'lucide-react'
import { updateTask, deleteTask } from '../../api/tasks'

const priorityOptions = ['low', 'medium', 'high', 'critical']

export default function TaskModal({ task, onClose, projectId }) {
  const queryClient = useQueryClient()
  const [form, setForm] = useState({
    title: task.title,
    description: task.description || '',
    priority: task.priority,
  })

  const updateMutation = useMutation({
    mutationFn: (data) => updateTask(task.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['tasks', projectId])
      onClose()
    },
  })

  const deleteMutation = useMutation({
    mutationFn: () => deleteTask(task.id),
    onSuccess: () => {
      queryClient.invalidateQueries(['tasks', projectId])
      onClose()
    },
  })

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-xl w-full max-w-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-white">Task Details</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X size={20} />
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Title</label>
            <input
              type="text"
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
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
            <label className="block text-sm text-gray-400 mb-1">Priority</label>
            <select
              value={form.priority}
              onChange={(e) => setForm({ ...form, priority: e.target.value })}
              className="w-full bg-gray-700 text-white px-3 py-2 rounded-lg text-sm focus:outline-none"
            >
              {priorityOptions.map((p) => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex items-center justify-between mt-6">
          <button
            onClick={() => deleteMutation.mutate()}
            className="flex items-center gap-2 text-red-400 hover:text-red-300 text-sm"
          >
            <Trash2 size={16} />
            Delete task
          </button>
          <div className="flex gap-2">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-400 hover:text-white text-sm"
            >
              Cancel
            </button>
            <button
              onClick={() => updateMutation.mutate(form)}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm"
            >
              Save changes
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
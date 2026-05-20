import { useState } from 'react'
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query'
import { X, Trash2, Send, MessageSquare, Activity } from 'lucide-react'
import { updateTask, deleteTask } from '../../api/tasks'
import { getComments, createComment, deleteComment, getActivity } from '../../api/comments'
import useAuthStore from '../../store/authStore'

const priorityOptions = ['low', 'medium', 'high', 'critical']

const priorityColors = {
  low: 'bg-green-900/40 text-green-400',
  medium: 'bg-yellow-900/40 text-yellow-400',
  high: 'bg-orange-900/40 text-orange-400',
  critical: 'bg-red-900/40 text-red-400',
}

export default function TaskModal({ task, onClose, projectId }) {
  const queryClient = useQueryClient()
  const user = useAuthStore((state) => state.user)
  const [form, setForm] = useState({
    title: task.title,
    description: task.description || '',
    priority: task.priority,
    due_date: task.due_date ? task.due_date.slice(0, 10) : '',
  })
  const [commentText, setCommentText] = useState('')
  const [activeTab, setActiveTab] = useState('comments')

  const isOverdue = task.due_date && new Date(task.due_date) < new Date() && !task.deleted_at

  const { data: commentsData } = useQuery({
    queryKey: ['comments', task.id],
    queryFn: () => getComments(task.id),
  })

  const { data: activityData } = useQuery({
    queryKey: ['activity', task.id],
    queryFn: () => getActivity(task.id),
  })

  const comments = commentsData?.data || []
  const activities = activityData?.data || []

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

  const createCommentMutation = useMutation({
    mutationFn: (data) => createComment(task.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['comments', task.id])
      queryClient.invalidateQueries(['activity', task.id])
      setCommentText('')
    },
  })

  const deleteCommentMutation = useMutation({
    mutationFn: (commentId) => deleteComment(task.id, commentId),
    onSuccess: () => queryClient.invalidateQueries(['comments', task.id]),
  })

  const handleSave = () => {
    const payload = {
      title: form.title,
      description: form.description || null,
      priority: form.priority,
      due_date: form.due_date ? new Date(form.due_date).toISOString() : null,
    }
    updateMutation.mutate(payload)
  }

  const handleComment = () => {
    if (!commentText.trim()) return
    createCommentMutation.mutate({ body: commentText })
  }

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 rounded-2xl w-full max-w-2xl max-h-[90vh] flex flex-col">
        <div className="flex items-center justify-between p-6 border-b border-gray-700">
          <div className="flex items-center gap-3">
            <h2 className="text-xl font-semibold text-white">Task Details</h2>
            {isOverdue && (
              <span className="text-xs bg-red-900/40 text-red-400 px-2 py-1 rounded-full">
                Overdue
              </span>
            )}
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X size={20} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-4">
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

          <div className="flex gap-4">
            <div className="flex-1">
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
            <div className="flex-1">
              <label className="block text-sm text-gray-400 mb-1">Due date</label>
              <input
                type="date"
                value={form.due_date}
                onChange={(e) => setForm({ ...form, due_date: e.target.value })}
                className={`w-full bg-gray-700 px-3 py-2 rounded-lg text-sm focus:outline-none ${
                  isOverdue ? 'text-red-400' : 'text-white'
                }`}
              />
            </div>
          </div>

          <div className="border-t border-gray-700 pt-4">
            <div className="flex gap-4 mb-4">
              <button
                onClick={() => setActiveTab('comments')}
                className={`flex items-center gap-2 text-sm pb-2 border-b-2 transition-colors ${
                  activeTab === 'comments'
                    ? 'border-indigo-500 text-white'
                    : 'border-transparent text-gray-400'
                }`}
              >
                <MessageSquare size={14} />
                Comments ({comments.length})
              </button>
              <button
                onClick={() => setActiveTab('activity')}
                className={`flex items-center gap-2 text-sm pb-2 border-b-2 transition-colors ${
                  activeTab === 'activity'
                    ? 'border-indigo-500 text-white'
                    : 'border-transparent text-gray-400'
                }`}
              >
                <Activity size={14} />
                Activity ({activities.length})
              </button>
            </div>

            {activeTab === 'comments' && (
              <div className="space-y-3">
                {comments.map((comment) => (
                  <div key={comment.id} className="bg-gray-700 rounded-lg p-3">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-indigo-400">
                        {comment.user_name}
                      </span>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-gray-500">
                          {new Date(comment.created_at).toLocaleDateString()}
                        </span>
                        {user?.id === comment.user_id && (
                          <button
                            onClick={() => deleteCommentMutation.mutate(comment.id)}
                            className="text-gray-500 hover:text-red-400"
                          >
                            <Trash2 size={12} />
                          </button>
                        )}
                      </div>
                    </div>
                    <p className="text-gray-300 text-sm">{comment.body}</p>
                  </div>
                ))}

                <div className="flex gap-2 mt-3">
                  <input
                    type="text"
                    value={commentText}
                    onChange={(e) => setCommentText(e.target.value)}
                    placeholder="Write a comment..."
                    className="flex-1 bg-gray-700 text-white px-3 py-2 rounded-lg text-sm focus:outline-none"
                    onKeyDown={(e) => e.key === 'Enter' && handleComment()}
                  />
                  <button
                    onClick={handleComment}
                    disabled={!commentText.trim()}
                    className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-40 text-white px-3 py-2 rounded-lg"
                  >
                    <Send size={16} />
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'activity' && (
              <div className="space-y-2">
                {activities.length === 0 && (
                  <p className="text-gray-500 text-sm">No activity yet.</p>
                )}
                {activities.map((activity) => (
                  <div key={activity.id} className="flex items-start gap-2 text-sm">
                    <div className="w-2 h-2 bg-indigo-500 rounded-full mt-1.5 flex-shrink-0" />
                    <div>
                      <span className="text-indigo-400 font-medium">{activity.user_name}</span>
                      <span className="text-gray-400"> {activity.action}</span>
                      {activity.detail && (
                        <span className="text-gray-500"> — {activity.detail}</span>
                      )}
                      <p className="text-gray-600 text-xs">
                        {new Date(activity.created_at).toLocaleString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center justify-between p-6 border-t border-gray-700">
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
              onClick={handleSave}
              disabled={updateMutation.isPending}
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
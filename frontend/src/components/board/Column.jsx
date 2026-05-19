import { useState } from 'react'
import { useDroppable } from '@dnd-kit/core'
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable'
import { Plus, Pencil, Trash2, Check, X } from 'lucide-react'
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query'
import { createTask } from '../../api/tasks'
import { updateColumn, deleteColumn } from '../../api/columns'
import { getMembers } from '../../api/workspace'
import TaskCard from './TaskCard'

export default function Column({ column, tasks, projectId, onTaskClick, isTaskOver }) {
  const queryClient = useQueryClient()
  const [showInput, setShowInput] = useState(false)
  const [taskForm, setTaskForm] = useState({
    title: '',
    description: '',
    priority: 'medium',
    assignee_id: '',
  })
  const [isEditing, setIsEditing] = useState(false)
  const [editName, setEditName] = useState(column.name)
  const [selectedMember, setSelectedMember] = useState('')

  const { setNodeRef, isOver } = useDroppable({ id: column.id })

  const isHighlighted = isOver || isTaskOver

  const { data: membersData } = useQuery({
    queryKey: ['members'],
    queryFn: getMembers,
  })
  const members = membersData?.data || []

  const createTaskMutation = useMutation({
    mutationFn: (data) => createTask(projectId, column.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['tasks', projectId])
      setTaskForm({ title: '', description: '', priority: 'medium', assignee_id: '' })
      setShowInput(false)
    },
  })

  const updateColumnMutation = useMutation({
    mutationFn: (data) => updateColumn(projectId, column.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['columns', projectId])
      setIsEditing(false)
    },
  })

  const deleteColumnMutation = useMutation({
    mutationFn: () => deleteColumn(projectId, column.id),
    onSuccess: () => queryClient.invalidateQueries(['columns', projectId]),
  })

  const handleCreateTask = () => {
    if (!taskForm.title.trim()) return
    const payload = {
      title: taskForm.title,
      description: taskForm.description || null,
      priority: taskForm.priority,
      position: tasks.length,
    }
    if (taskForm.assignee_id) payload.assignee_id = taskForm.assignee_id
    createTaskMutation.mutate(payload)
  }

  return (
    <div className="flex-shrink-0 w-72">
      <div
        ref={setNodeRef}
        className={`rounded-xl p-3 transition-all duration-200 ${
          isHighlighted
            ? 'bg-indigo-900/40 border-2 border-indigo-500 scale-[1.02]'
            : 'bg-gray-800 border-2 border-transparent'
        }`}
        style={{ minHeight: '8rem' }}
      >
        <div className="flex items-center justify-between mb-3">
          {isEditing ? (
            <div className="flex items-center gap-1 flex-1">
              <input
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                className="bg-gray-700 text-white px-2 py-1 rounded text-sm flex-1 focus:outline-none"
                autoFocus
              />
              <button
                onClick={() => updateColumnMutation.mutate({ name: editName })}
                className="text-green-400 hover:text-green-300"
              >
                <Check size={14} />
              </button>
              <button
                onClick={() => setIsEditing(false)}
                className="text-gray-400 hover:text-white"
              >
                <X size={14} />
              </button>
            </div>
          ) : (
            <>
              <h3 className="text-sm font-semibold text-gray-200">{column.name}</h3>
              <div className="flex items-center gap-1">
                <span className="text-xs text-gray-500 bg-gray-700 px-2 py-0.5 rounded-full">
                  {tasks.length}
                </span>
                <button
                  onClick={() => setIsEditing(true)}
                  className="text-gray-500 hover:text-gray-300 ml-1"
                >
                  <Pencil size={12} />
                </button>
                <button
                  onClick={() => {
                    if (window.confirm('Delete this column and all its tasks?')) {
                      deleteColumnMutation.mutate()
                    }
                  }}
                  className="text-gray-500 hover:text-red-400"
                >
                  <Trash2 size={12} />
                </button>
              </div>
            </>
          )}
        </div>

        <SortableContext
          items={tasks.map((t) => t.id)}
          strategy={verticalListSortingStrategy}
        >
          <div className="space-y-2">
            {tasks.map((task) => (
              <TaskCard key={task.id} task={task} onClick={() => onTaskClick(task)} />
            ))}
          </div>
        </SortableContext>

        {showInput ? (
          <div className="mt-2 space-y-2">
            <input
              type="text"
              value={taskForm.title}
              onChange={(e) => setTaskForm({ ...taskForm, title: e.target.value })}
              placeholder="Task title"
              className="w-full bg-gray-700 text-white px-3 py-2 rounded-lg text-sm focus:outline-none"
              autoFocus
            />
            <textarea
              value={taskForm.description}
              onChange={(e) => setTaskForm({ ...taskForm, description: e.target.value })}
              placeholder="Description (optional)"
              rows={2}
              className="w-full bg-gray-700 text-white px-3 py-2 rounded-lg text-sm focus:outline-none resize-none"
            />
            <select
              value={taskForm.priority}
              onChange={(e) => setTaskForm({ ...taskForm, priority: e.target.value })}
              className="w-full bg-gray-700 text-white px-3 py-2 rounded-lg text-sm focus:outline-none"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
            <select
              value={taskForm.assignee_id}
              onChange={(e) => setTaskForm({ ...taskForm, assignee_id: e.target.value })}
              className="w-full bg-gray-700 text-white px-3 py-2 rounded-lg text-sm focus:outline-none"
            >
              <option value="">Unassigned</option>
              {members.map((m) => (
                <option key={m.user_id} value={m.user_id}>
                  {m.user?.name || m.user?.email || m.user_id}
                </option>
              ))}
            </select>
            <div className="flex gap-2">
              <button
                onClick={handleCreateTask}
                className="bg-indigo-600 text-white px-3 py-1 rounded text-sm"
              >
                Add
              </button>
              <button
                onClick={() => setShowInput(false)}
                className="text-gray-400 px-3 py-1 rounded text-sm"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <button
            onClick={() => setShowInput(true)}
            className="flex items-center gap-1 text-gray-500 hover:text-gray-300 text-sm mt-2 w-full px-1 py-1"
          >
            <Plus size={14} />
            Add task
          </button>
        )}
      </div>
    </div>
  )
}
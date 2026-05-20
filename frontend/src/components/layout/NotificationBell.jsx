import { useState } from 'react'
import { Bell } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { getTasks } from '../../api/tasks'

export default function NotificationBell({ projectId }) {
  const [isOpen, setIsOpen] = useState(false)

  const { data: tasksData } = useQuery({
    queryKey: ['tasks', projectId],
    queryFn: () => getTasks(projectId),
    enabled: !!projectId,
  })

  const tasks = tasksData?.data || []
  const overdueTasks = tasks.filter(
    (t) => t.due_date && new Date(t.due_date) < new Date() && !t.deleted_at
  )

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative text-gray-400 hover:text-white transition-colors"
      >
        <Bell size={20} />
        {overdueTasks.length > 0 && (
          <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full text-white text-xs flex items-center justify-center">
            {overdueTasks.length}
          </span>
        )}
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />
          <div className="fixed left-4 top-14 w-64 bg-gray-800 rounded-xl shadow-xl z-50 overflow-hidden border border-gray-700">
            <div className="p-3 border-b border-gray-700">
              <p className="text-white text-sm font-medium">Notifications</p>
            </div>
            {overdueTasks.length === 0 ? (
              <p className="text-gray-400 text-sm p-4">No overdue tasks</p>
            ) : (
              overdueTasks.map((task) => (
                <div key={task.id} className="px-4 py-3 border-b border-gray-700 last:border-0">
                  <p className="text-white text-sm">{task.title}</p>
                  <p className="text-red-400 text-xs mt-0.5">
                    Overdue — {new Date(task.due_date).toLocaleDateString()}
                  </p>
                </div>
              ))
            )}
          </div>
        </>
      )}
    </div>
  )
}
import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  DndContext,
  DragOverlay,
  closestCorners,
  PointerSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core'
import { Plus } from 'lucide-react'
import { getColumns, createColumn } from '../api/columns'
import { getTasks, moveTask } from '../api/tasks'
import { getProject } from '../api/projects'
import AppLayout from '../components/layout/AppLayout'
import Column from '../components/board/Column'
import TaskCard from '../components/board/TaskCard'
import TaskModal from '../components/board/TaskModal'
import SearchBar from '../components/board/SearchBar'

export default function BoardPage() {
  const { projectId } = useParams()
  const queryClient = useQueryClient()
  const [activeTask, setActiveTask] = useState(null)
  const [selectedTask, setSelectedTask] = useState(null)
  const [newColumnName, setNewColumnName] = useState('')
  const [showColumnInput, setShowColumnInput] = useState(false)
  const [overColumnId, setOverColumnId] = useState(null)

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } })
  )

  const { data: projectData } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => getProject(projectId),
  })

  const { data: columnsData } = useQuery({
    queryKey: ['columns', projectId],
    queryFn: () => getColumns(projectId),
  })

  const { data: tasksData } = useQuery({
    queryKey: ['tasks', projectId],
    queryFn: () => getTasks(projectId),
  })

  const project = projectData?.data
  const columns = columnsData?.data || []
  const tasks = tasksData?.data || []

  const moveTaskMutation = useMutation({
    mutationFn: ({ taskId, data }) => moveTask(taskId, data),
    onSuccess: () => queryClient.invalidateQueries(['tasks', projectId]),
  })

  const createColumnMutation = useMutation({
    mutationFn: (data) => createColumn(projectId, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['columns', projectId])
      setNewColumnName('')
      setShowColumnInput(false)
    },
  })

  const handleDragStart = (event) => {
    const task = tasks.find((t) => t.id === event.active.id)
    setActiveTask(task)
  }

  const handleDragOver = (event) => {
    const { over } = event
    if (!over) { setOverColumnId(null); return }
    const overColumn = columns.find((c) => c.id === over.id)
    const overTask = tasks.find((t) => t.id === over.id)
    if (overColumn) setOverColumnId(overColumn.id)
    else if (overTask) setOverColumnId(overTask.column_id)
    else setOverColumnId(null)
  }

  const handleDragEnd = (event) => {
    const { active, over } = event
    setActiveTask(null)
    setOverColumnId(null)
    if (!over) return
    const taskId = active.id
    const task = tasks.find((t) => t.id === taskId)
    if (!task) return
    const overColumn = columns.find((c) => c.id === over.id)
    const overTask = tasks.find((t) => t.id === over.id)
    const targetColumnId = overColumn ? overColumn.id : overTask ? overTask.column_id : null
    if (!targetColumnId || task.column_id === targetColumnId) return
    moveTaskMutation.mutate({ taskId, data: { column_id: targetColumnId, position: 0 } })
  }

  const handleCreateColumn = () => {
    if (!newColumnName.trim()) return
    createColumnMutation.mutate({ name: newColumnName, position: columns.length })
  }

  const getTasksForColumn = (columnId) => tasks.filter((t) => t.column_id === columnId)

  return (
    <AppLayout>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white">
            {project?.name || 'Loading...'}
          </h1>
          {project?.description && (
            <p className="text-gray-400 text-sm mt-1">{project.description}</p>
          )}
        </div>
        <SearchBar onTaskClick={setSelectedTask} />
      </div>

      <DndContext
        sensors={sensors}
        collisionDetection={closestCorners}
        onDragStart={handleDragStart}
        onDragOver={handleDragOver}
        onDragEnd={handleDragEnd}
      >
        <div className="flex gap-4 pb-4" style={{ minHeight: 'calc(100vh - 10rem)' }}>
          {columns.map((column) => (
            <Column
              key={column.id}
              column={column}
              tasks={getTasksForColumn(column.id)}
              projectId={projectId}
              onTaskClick={setSelectedTask}
              isTaskOver={overColumnId === column.id}
            />
          ))}

          <div className="flex-shrink-0 w-72">
            {showColumnInput ? (
              <div className="bg-gray-800 rounded-xl p-3">
                <input
                  type="text"
                  value={newColumnName}
                  onChange={(e) => setNewColumnName(e.target.value)}
                  placeholder="Column name"
                  className="w-full bg-gray-700 text-white px-3 py-2 rounded-lg text-sm mb-2 focus:outline-none"
                  autoFocus
                  onKeyDown={(e) => e.key === 'Enter' && handleCreateColumn()}
                />
                <div className="flex gap-2">
                  <button onClick={handleCreateColumn} className="bg-indigo-600 text-white px-3 py-1 rounded text-sm">Add</button>
                  <button onClick={() => setShowColumnInput(false)} className="text-gray-400 px-3 py-1 rounded text-sm">Cancel</button>
                </div>
              </div>
            ) : (
              <button
                onClick={() => setShowColumnInput(true)}
                className="flex items-center gap-2 text-gray-400 hover:text-white w-full px-3 py-2 rounded-xl hover:bg-gray-800 transition-colors"
              >
                <Plus size={16} />
                Add column
              </button>
            )}
          </div>
        </div>

        <DragOverlay>
          {activeTask && <TaskCard task={activeTask} isDragging />}
        </DragOverlay>
      </DndContext>

      {selectedTask && (
        <TaskModal
          task={selectedTask}
          onClose={() => setSelectedTask(null)}
          projectId={projectId}
        />
      )}
    </AppLayout>
  )
}
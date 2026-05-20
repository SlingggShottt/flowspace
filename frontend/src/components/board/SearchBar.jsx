import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Search, X } from 'lucide-react'
import { searchTasks } from '../../api/tasks'

export default function SearchBar({ onTaskClick }) {
  const [query, setQuery] = useState('')
  const [isOpen, setIsOpen] = useState(false)

  const { data: searchData } = useQuery({
    queryKey: ['search', query],
    queryFn: () => searchTasks(query),
    enabled: query.length >= 2,
  })

  const results = searchData?.data || []

  return (
    <div className="relative">
      <div className="flex items-center gap-2 bg-gray-800 rounded-xl px-3 py-2">
        <Search size={16} className="text-gray-400" />
        <input
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value)
            setIsOpen(true)
          }}
          onFocus={() => setIsOpen(true)}
          placeholder="Search tasks..."
          className="bg-transparent text-white text-sm focus:outline-none w-48"
        />
        {query && (
          <button
            onClick={() => { setQuery(''); setIsOpen(false) }}
            className="text-gray-400 hover:text-white"
          >
            <X size={14} />
          </button>
        )}
      </div>

      {isOpen && query.length >= 2 && (
        <div className="absolute top-full mt-2 left-0 w-80 bg-gray-800 rounded-xl shadow-xl z-50 overflow-hidden">
          {results.length === 0 ? (
            <p className="text-gray-400 text-sm p-4">No tasks found</p>
          ) : (
            results.map((task) => (
              <button
                key={task.id}
                onClick={() => {
                  onTaskClick(task)
                  setIsOpen(false)
                  setQuery('')
                }}
                className="w-full text-left px-4 py-3 hover:bg-gray-700 border-b border-gray-700 last:border-0"
              >
                <p className="text-white text-sm">{task.title}</p>
                <p className="text-gray-400 text-xs capitalize">{task.priority} priority</p>
              </button>
            ))
          )}
        </div>
      )}
    </div>
  )
}
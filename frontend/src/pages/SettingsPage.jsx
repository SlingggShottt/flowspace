import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getWorkspace, updateWorkspace } from '../api/workspace'
import AppLayout from '../components/layout/AppLayout'

export default function SettingsPage() {
  const queryClient = useQueryClient()
  const [name, setName] = useState('')
  const [saved, setSaved] = useState(false)

  const { data: workspaceData } = useQuery({
    queryKey: ['workspace'],
    queryFn: getWorkspace,
    onSuccess: (data) => setName(data.data.name),
  })

  const workspace = workspaceData?.data

  const updateMutation = useMutation({
    mutationFn: () => updateWorkspace({ name }),
    onSuccess: () => {
      queryClient.invalidateQueries(['workspace'])
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    },
  })

  return (
    <AppLayout>
      <div className="max-w-lg">
        <h1 className="text-2xl font-bold text-white mb-6">Settings</h1>

        <div className="bg-gray-800 rounded-xl p-6 space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Workspace name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full bg-gray-700 text-white px-3 py-2 rounded-lg text-sm focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-1">Slug</label>
            <input
              type="text"
              value={workspace?.slug || ''}
              disabled
              className="w-full bg-gray-700/50 text-gray-500 px-3 py-2 rounded-lg text-sm"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-1">Plan</label>
            <span className="inline-block bg-indigo-900/40 text-indigo-400 px-3 py-1 rounded-full text-sm capitalize">
              {workspace?.plan}
            </span>
          </div>

          <button
            onClick={() => updateMutation.mutate()}
            className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm"
          >
            {saved ? 'Saved!' : 'Save changes'}
          </button>
        </div>
      </div>
    </AppLayout>
  )
}
// frontend/src/pages/SettingsPage.jsx

import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getWorkspace, updateWorkspace } from '../api/workspace'
import AppLayout from '../components/layout/AppLayout'
import useAuthStore from '../store/authStore'
import { Link } from 'react-router-dom'

export default function SettingsPage() {
  const queryClient = useQueryClient()
  const user = useAuthStore((state) => state.user)
  const isAdmin = user?.role === 'admin'
  const [name, setName] = useState('')
  const [saved, setSaved] = useState(false)

  const { data: workspaceData } = useQuery({
    queryKey: ['workspace'],
    queryFn: getWorkspace,
  })

  const workspace = workspaceData?.data

  useEffect(() => {
    if (workspace?.name) {
      setName(workspace.name)
    }
  }, [workspace])

  const updateMutation = useMutation({
    mutationFn: () => updateWorkspace({ name }),
    onSuccess: () => {
      queryClient.invalidateQueries(['workspace'])
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    },
  })

  if (!isAdmin) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-[80vh]">
          <div className="w-full max-w-2xl">
            <h1 className="text-4xl font-bold text-white mb-8 text-center">Settings</h1>
            <div className="bg-gray-800 rounded-2xl p-10 text-center">
              <p className="text-gray-400 text-lg mb-2">Workspace settings are only available to admins.</p>
              <p className="text-gray-500">To update your personal settings, go to your Profile page.</p>
              <Link
                to="/profile"
                className="inline-block mt-4 bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-xl text-base"
              >
                Go to Profile
              </Link>
            </div>
          </div>
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className="flex items-center justify-center min-h-[80vh]">
        <div className="w-full max-w-2xl">
          <h1 className="text-4xl font-bold text-white mb-8 text-center">Settings</h1>
          <div className="bg-gray-800 rounded-2xl p-10 space-y-6">
            <div>
              <label className="block text-lg text-gray-400 mb-2">Workspace name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full bg-gray-700 text-white px-5 py-3 rounded-xl text-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-lg text-gray-400 mb-2">Slug</label>
              <input
                type="text"
                value={workspace?.slug || ''}
                disabled
                className="w-full bg-gray-700/50 text-gray-500 px-5 py-3 rounded-xl text-lg"
              />
              <p className="text-gray-500 text-sm mt-1">Slug cannot be changed</p>
            </div>
            <div>
              <label className="block text-lg text-gray-400 mb-2">Plan</label>
              <span className="inline-block bg-indigo-900/40 text-indigo-400 px-4 py-2 rounded-full text-lg capitalize">
                {workspace?.plan}
              </span>
            </div>
            <button
              onClick={() => updateMutation.mutate()}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-3 rounded-xl text-lg font-medium transition-colors"
            >
              {saved ? 'Saved!' : 'Save changes'}
            </button>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}

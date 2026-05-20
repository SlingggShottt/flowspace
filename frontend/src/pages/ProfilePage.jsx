import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getMe, updateMe } from '../api/users'
import AppLayout from '../components/layout/AppLayout'
import useAuthStore from '../store/authStore'

const getInitials = (name) => {
  if (!name) return '?'
  return name.split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2)
}

export default function ProfilePage() {
  const queryClient = useQueryClient()
  const setAuth = useAuthStore((state) => state.setAuth)
  const token = useAuthStore((state) => state.token)
  const [form, setForm] = useState({ name: '', avatar_url: '' })
  const [saved, setSaved] = useState(false)

  const { data: meData } = useQuery({
    queryKey: ['me'],
    queryFn: getMe,
  })

  const me = meData?.data

  useEffect(() => {
    if (me) {
      setForm({
        name: me.name || '',
        avatar_url: me.avatar_url || '',
      })
    }
  }, [me])

  const updateMutation = useMutation({
    mutationFn: () => updateMe({ name: form.name, avatar_url: form.avatar_url || null }),
    onSuccess: (res) => {
      queryClient.invalidateQueries(['me'])
      setAuth(res.data, token)
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    },
  })

  return (
    <AppLayout>
      <div className="flex items-center justify-center min-h-[80vh]">
        <div className="w-full max-w-lg">
          <h1 className="text-4xl font-bold text-white mb-8 text-center">My Profile</h1>

          <div className="bg-gray-800 rounded-2xl p-10 space-y-6">
            <div className="flex justify-center mb-2">
              {me?.avatar_url ? (
                <img
                  src={me.avatar_url}
                  alt="avatar"
                  className="w-20 h-20 rounded-full object-cover"
                />
              ) : (
                <div className="w-20 h-20 bg-indigo-600 rounded-full flex items-center justify-center text-white text-2xl font-bold">
                  {getInitials(me?.name)}
                </div>
              )}
            </div>

            <div>
              <label className="block text-lg text-gray-400 mb-2">Full name</label>
              <input
                type="text"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                className="w-full bg-gray-700 text-white px-5 py-3 rounded-xl text-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-lg text-gray-400 mb-2">Avatar URL</label>
              <input
                type="text"
                value={form.avatar_url}
                onChange={(e) => setForm({ ...form, avatar_url: e.target.value })}
                placeholder="https://example.com/avatar.jpg"
                className="w-full bg-gray-700 text-white px-5 py-3 rounded-xl text-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-lg text-gray-400 mb-2">Email</label>
              <input
                type="text"
                value={me?.email || ''}
                disabled
                className="w-full bg-gray-700/50 text-gray-500 px-5 py-3 rounded-xl text-lg"
              />
              <p className="text-gray-500 text-sm mt-1">Email cannot be changed</p>
            </div>

            <button
              onClick={() => updateMutation.mutate()}
              disabled={updateMutation.isPending}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-3 rounded-xl text-lg font-medium disabled:opacity-50"
            >
              {saved ? 'Saved!' : updateMutation.isPending ? 'Saving...' : 'Save changes'}
            </button>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
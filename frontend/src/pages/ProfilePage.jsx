// frontend/src/pages/ProfilePage.jsx

import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getMe, updateMe } from '../api/users'
import AppLayout from '../components/layout/AppLayout'
import useAuthStore from '../store/authStore'
import api from '../api/axios'

const getInitials = (name) => {
  if (!name) return '?'
  return name.split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2)
}

export default function ProfilePage() {
  const queryClient = useQueryClient()
  const setAuth = useAuthStore((state) => state.setAuth)
  const token = useAuthStore((state) => state.token)
  const user = useAuthStore((state) => state.user)

  const [form, setForm] = useState({ name: '', avatar_url: '' })
  const [passwordForm, setPasswordForm] = useState({ current_password: '', new_password: '', confirm_password: '' })
  const [saved, setSaved] = useState(false)
  const [passwordError, setPasswordError] = useState('')
  const [passwordSuccess, setPasswordSuccess] = useState('')
  const [passwordLoading, setPasswordLoading] = useState(false)

  const { data: meData } = useQuery({
    queryKey: ['me'],
    queryFn: getMe,
  })

  const me = meData?.data

  useEffect(() => {
    if (me) {
      setForm({ name: me.name || '', avatar_url: me.avatar_url || '' })
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

  const handleChangePassword = async (e) => {
    e.preventDefault()
    setPasswordError('')
    setPasswordSuccess('')
    if (passwordForm.new_password !== passwordForm.confirm_password) {
      setPasswordError('Passwords do not match')
      return
    }
    if (passwordForm.new_password.length < 8) {
      setPasswordError('Password must be at least 8 characters')
      return
    }
    setPasswordLoading(true)
    try {
      await api.post('/users/me/change-password', {
        current_password: passwordForm.current_password,
        new_password: passwordForm.new_password,
      })
      setPasswordSuccess('Password changed successfully')
      setPasswordForm({ current_password: '', new_password: '', confirm_password: '' })
    } catch (err) {
      setPasswordError(err.response?.data?.detail || 'Failed to change password')
    } finally {
      setPasswordLoading(false)
    }
  }

  return (
    <AppLayout>
      <div className="flex items-center justify-center min-h-[80vh]">
        <div className="w-full max-w-lg space-y-6">
          <h1 className="text-4xl font-bold text-white text-center">My Profile</h1>

          <div className="bg-gray-800 rounded-2xl p-10 space-y-6">
            <div className="flex justify-center mb-2">
              {me?.avatar_url ? (
                <img src={me.avatar_url} alt="avatar" className="w-20 h-20 rounded-full object-cover" />
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
            </div>

            <div>
              <label className="block text-lg text-gray-400 mb-2">Role</label>
              <span className="inline-block bg-indigo-900/40 text-indigo-400 px-4 py-2 rounded-full text-lg capitalize">
                {me?.role}
              </span>
            </div>

            <button
              onClick={() => updateMutation.mutate()}
              disabled={updateMutation.isPending}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-3 rounded-xl text-lg font-medium disabled:opacity-50"
            >
              {saved ? 'Saved!' : updateMutation.isPending ? 'Saving...' : 'Save changes'}
            </button>
          </div>

          <div className="bg-gray-800 rounded-2xl p-10 space-y-6">
            <h2 className="text-2xl font-bold text-white">Change Password</h2>

            {passwordError && (
              <div className="bg-red-900/30 border border-red-500 text-red-400 px-4 py-3 rounded-lg text-sm">
                {passwordError}
              </div>
            )}
            {passwordSuccess && (
              <div className="bg-green-900/30 border border-green-500 text-green-400 px-4 py-3 rounded-lg text-sm">
                {passwordSuccess}
              </div>
            )}

            <form onSubmit={handleChangePassword} className="space-y-4">
              <div>
                <label className="block text-lg text-gray-400 mb-2">Current password</label>
                <input
                  type="password"
                  value={passwordForm.current_password}
                  onChange={(e) => setPasswordForm({ ...passwordForm, current_password: e.target.value })}
                  placeholder="........"
                  className="w-full bg-gray-700 text-white px-5 py-3 rounded-xl text-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  required
                />
              </div>
              <div>
                <label className="block text-lg text-gray-400 mb-2">New password</label>
                <input
                  type="password"
                  value={passwordForm.new_password}
                  onChange={(e) => setPasswordForm({ ...passwordForm, new_password: e.target.value })}
                  placeholder="........"
                  className="w-full bg-gray-700 text-white px-5 py-3 rounded-xl text-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  required
                />
              </div>
              <div>
                <label className="block text-lg text-gray-400 mb-2">Confirm new password</label>
                <input
                  type="password"
                  value={passwordForm.confirm_password}
                  onChange={(e) => setPasswordForm({ ...passwordForm, confirm_password: e.target.value })}
                  placeholder="........"
                  className="w-full bg-gray-700 text-white px-5 py-3 rounded-xl text-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  required
                />
              </div>
              <button
                type="submit"
                disabled={passwordLoading}
                className="w-full bg-gray-600 hover:bg-gray-500 text-white px-5 py-3 rounded-xl text-lg font-medium disabled:opacity-50"
              >
                {passwordLoading ? 'Changing...' : 'Change password'}
              </button>
            </form>

            <div className="border-t border-gray-700 pt-4">
              <a href="/forgot-password" className="text-indigo-400 hover:underline text-sm">
                Forgot your password? Reset via email
              </a>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}

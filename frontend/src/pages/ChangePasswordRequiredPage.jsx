import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/axios'
import useAuthStore from '../store/authStore'

export default function ChangePasswordRequiredPage() {
  const navigate = useNavigate()
  const setAuth = useAuthStore((state) => state.setAuth)
  const token = useAuthStore((state) => state.token)
  const user = useAuthStore((state) => state.user)
  const [form, setForm] = useState({ current_password: '', new_password: '', confirm_password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (form.new_password !== form.confirm_password) {
      setError('Passwords do not match')
      return
    }
    if (form.new_password.length < 8) {
      setError('Password must be at least 8 characters')
      return
    }
    setLoading(true)
    setError('')
    try {
      await api.post('/users/me/change-password', {
        current_password: form.current_password,
        new_password: form.new_password,
      })
      setAuth({ ...user, must_change_password: false }, token)
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to change password')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center">
      <div className="bg-gray-900 p-8 rounded-xl w-full max-w-md">
        <div className="bg-yellow-900/30 border border-yellow-500 text-yellow-400 px-4 py-3 rounded-lg mb-6 text-sm">
          You must change your temporary password before continuing.
        </div>
        <h1 className="text-2xl font-bold text-white mb-2">Change your password</h1>
        <p className="text-gray-400 mb-6">Set a new secure password for your account</p>

        {error && (
          <div className="bg-red-900/30 border border-red-500 text-red-400 px-4 py-3 rounded-lg mb-4 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Temporary password</label>
            <input
              type="password"
              value={form.current_password}
              onChange={(e) => setForm({ ...form, current_password: e.target.value })}
              placeholder="Your temporary password"
              className="w-full bg-gray-800 text-white px-4 py-2 rounded-lg border border-gray-700 focus:outline-none focus:border-indigo-500"
              required
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">New password</label>
            <input
              type="password"
              value={form.new_password}
              onChange={(e) => setForm({ ...form, new_password: e.target.value })}
              placeholder="••••••••"
              className="w-full bg-gray-800 text-white px-4 py-2 rounded-lg border border-gray-700 focus:outline-none focus:border-indigo-500"
              required
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Confirm new password</label>
            <input
              type="password"
              value={form.confirm_password}
              onChange={(e) => setForm({ ...form, confirm_password: e.target.value })}
              placeholder="••••••••"
              className="w-full bg-gray-800 text-white px-4 py-2 rounded-lg border border-gray-700 focus:outline-none focus:border-indigo-500"
              required
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-2 rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            {loading ? 'Changing...' : 'Change password'}
          </button>
        </form>
      </div>
    </div>
  )
}
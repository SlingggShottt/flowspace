import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import api from '../api/axios'

export default function ForgotPasswordPage() {
  const [searchParams] = useSearchParams()
  const [form, setForm] = useState({
    email: '',
    tenant_slug: searchParams.get('slug') || '',
  })
  const [submitted, setSubmitted] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await api.post('/users/forgot-password', form)
      setSubmitted(true)
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  if (submitted) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="bg-gray-900 p-8 rounded-xl w-full max-w-md text-center">
          <div className="w-16 h-16 bg-green-900/40 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-green-400 text-2xl">✓</span>
          </div>
          <h1 className="text-2xl font-bold text-white mb-2">Check your email</h1>
          <p className="text-gray-400 mb-6">
            If that email exists in our system you will receive a password reset link shortly.
          </p>
          <a href="/login" className="text-indigo-400 hover:underline text-sm">
            Back to login
          </a>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center">
      <div className="bg-gray-900 p-8 rounded-xl w-full max-w-md">
        <h1 className="text-2xl font-bold text-white mb-2">Forgot password</h1>
        <p className="text-gray-400 mb-6">Enter your email and workspace slug to reset your password</p>

        {error && (
          <div className="bg-red-900/30 border border-red-500 text-red-400 px-4 py-3 rounded-lg mb-4 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Workspace slug</label>
            <input
              type="text"
              value={form.tenant_slug}
              onChange={(e) => setForm({ ...form, tenant_slug: e.target.value })}
              placeholder="your-company"
              className="w-full bg-gray-800 text-white px-4 py-2 rounded-lg border border-gray-700 focus:outline-none focus:border-indigo-500"
              required
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Email</label>
            <input
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              placeholder="you@company.com"
              className="w-full bg-gray-800 text-white px-4 py-2 rounded-lg border border-gray-700 focus:outline-none focus:border-indigo-500"
              required
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-2 rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            {loading ? 'Sending...' : 'Send reset link'}
          </button>
        </form>

        <p className="text-gray-400 text-sm mt-4 text-center">
          <a href="/login" className="text-indigo-400 hover:underline">Back to login</a>
        </p>
      </div>
    </div>
  )
}
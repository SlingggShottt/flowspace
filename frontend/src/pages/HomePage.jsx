import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import AppLayout from '../components/layout/AppLayout'

export default function HomePage() {
  const navigate = useNavigate()

  useEffect(() => {
    navigate('/dashboard')
  }, [navigate])

  return (
    <AppLayout>
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400">Redirecting...</div>
      </div>
    </AppLayout>
  )
}
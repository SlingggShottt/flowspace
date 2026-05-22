// frontend/src/App.jsx

import { useEffect, useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import AuthGuard from './components/layout/AuthGuard'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import HomePage from './pages/HomePage'
import BoardPage from './pages/BoardPage'
import MembersPage from './pages/MembersPage'
import TeamsPage from './pages/TeamsPage'
import SettingsPage from './pages/SettingsPage'
import BillingPage from './pages/BillingPage'
import NewProjectPage from './pages/NewProjectPage'
import EditProjectPage from './pages/EditProjectPage'
import ProfilePage from './pages/ProfilePage'
import ForgotPasswordPage from './pages/ForgotPasswordPage'
import ResetPasswordPage from './pages/ResetPasswordPage'
import ChangePasswordRequiredPage from './pages/ChangePasswordRequiredPage'
import NotificationsPage from './pages/NotificationsPage'
import DashboardPage from './pages/DashboardPage'


const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30000,
    },
  },
})

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function App() {
  const [apiStatus, setApiStatus] = useState('checking')

  useEffect(() => {
    const checkApi = async () => {
      try {
        const res = await fetch(`${API_URL}/health`, {
          method: 'GET',
          signal: AbortSignal.timeout(8000),
        })
        if (res.ok || res.type === 'opaque') {
          setApiStatus('online')
        } else {
          setApiStatus('offline')
        }
      } catch (err) {
        setApiStatus('offline')
      }
    }
    checkApi()
  }, [])

  if (apiStatus === 'checking') {
    return (
      <div style={{
        minHeight: '100vh',
        background: '#030712',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: '#6366f1',
        fontFamily: 'sans-serif',
        fontSize: '18px',
      }}>
        Loading Flowspace...
      </div>
    )
  }

  if (apiStatus === 'offline') {
    window.location.href = '/offline.html'
    return null
  }

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />
          <Route path="/change-password-required" element={<ChangePasswordRequiredPage />} />
          <Route path="/" element={<AuthGuard><HomePage /></AuthGuard>} />
          <Route path="/board/:projectId" element={<AuthGuard><BoardPage /></AuthGuard>} />
          <Route path="/projects/new" element={<AuthGuard><NewProjectPage /></AuthGuard>} />
          <Route path="/projects/:projectId/edit" element={<AuthGuard><EditProjectPage /></AuthGuard>} />
          <Route path="/members" element={<AuthGuard><MembersPage /></AuthGuard>} />
          <Route path="/teams" element={<AuthGuard><TeamsPage /></AuthGuard>} />
          <Route path="/settings" element={<AuthGuard><SettingsPage /></AuthGuard>} />
          <Route path="/billing" element={<AuthGuard><BillingPage /></AuthGuard>} />
          <Route path="/profile" element={<AuthGuard><ProfilePage /></AuthGuard>} />
          <Route path="/notifications" element={<AuthGuard><NotificationsPage /></AuthGuard>} />
          <Route path="*" element={<Navigate to="/" replace />} />
          <Route path="/dashboard" element={<AuthGuard><DashboardPage /></AuthGuard>} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

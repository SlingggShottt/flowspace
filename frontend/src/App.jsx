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

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30000,
    },
  },
})

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/" element={<AuthGuard><HomePage /></AuthGuard>} />
          <Route path="/board/:projectId" element={<AuthGuard><BoardPage /></AuthGuard>} />
          <Route path="/projects/new" element={<AuthGuard><NewProjectPage /></AuthGuard>} />
          <Route path="/projects/:projectId/edit" element={<AuthGuard><EditProjectPage /></AuthGuard>} />
          <Route path="/members" element={<AuthGuard><MembersPage /></AuthGuard>} />
          <Route path="/teams" element={<AuthGuard><TeamsPage /></AuthGuard>} />
          <Route path="/settings" element={<AuthGuard><SettingsPage /></AuthGuard>} />
          <Route path="/billing" element={<AuthGuard><BillingPage /></AuthGuard>} />
          <Route path="/profile" element={<AuthGuard><ProfilePage /></AuthGuard>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
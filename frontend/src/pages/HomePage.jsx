import { useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getProjects } from '../api/projects'
import AppLayout from '../components/layout/AppLayout'

export default function HomePage() {
  const navigate = useNavigate()

  const { data: projectsData } = useQuery({
    queryKey: ['projects'],
    queryFn: getProjects,
  })

  const projects = projectsData?.data || []

  useEffect(() => {
    if (projects.length > 0) {
      navigate(`/board/${projects[0].id}`)
    }
  }, [projects, navigate])

  return (
    <AppLayout>
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-white mb-2">No projects yet</h2>
          <p className="text-gray-400 mb-4">Create your first project to get started</p>
          <Link
            to="/projects/new"
            className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm"
          >
            Create project
          </Link>
        </div>
      </div>
    </AppLayout>
  )
}
import api from './axios'

export const getTasks = (projectId) =>
  api.get(`/projects/${projectId}/tasks`)

export const createTask = (projectId, columnId, data) =>
  api.post(`/projects/${projectId}/columns/${columnId}/tasks`, data)

export const updateTask = (taskId, data) =>
  api.patch(`/tasks/${taskId}`, data)

export const moveTask = (taskId, data) =>
  api.patch(`/tasks/${taskId}/move`, data)

export const deleteTask = (taskId) =>
  api.delete(`/tasks/${taskId}`)

export const searchTasks = (query) =>
  api.get(`/tasks/search?q=${query}`)
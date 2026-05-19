import api from './axios'

export const getColumns = (projectId) =>
  api.get(`/projects/${projectId}/columns`)

export const createColumn = (projectId, data) =>
  api.post(`/projects/${projectId}/columns`, data)

export const updateColumn = (projectId, columnId, data) =>
  api.patch(`/projects/${projectId}/columns/${columnId}`, data)

export const deleteColumn = (projectId, columnId) =>
  api.delete(`/projects/${projectId}/columns/${columnId}`)
import api from './axios'

export const getComments = (taskId) => api.get(`/tasks/${taskId}/comments`)
export const createComment = (taskId, data) => api.post(`/tasks/${taskId}/comments`, data)
export const deleteComment = (taskId, commentId) => api.delete(`/tasks/${taskId}/comments/${commentId}`)
export const getActivity = (taskId) => api.get(`/tasks/${taskId}/activity`)
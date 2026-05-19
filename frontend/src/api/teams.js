import api from './axios'

export const getTeams = () => api.get('/teams')
export const createTeam = (data) => api.post('/teams', data)
export const updateTeam = (id, data) => api.patch(`/teams/${id}`, data)
export const deleteTeam = (id) => api.delete(`/teams/${id}`)
export const addTeamMember = (teamId, data) => api.post(`/teams/${teamId}/members`, data)
export const removeTeamMember = (teamId, userId) => api.delete(`/teams/${teamId}/members/${userId}`)
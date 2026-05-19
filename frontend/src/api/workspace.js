import api from './axios'

export const getWorkspace = () => api.get('/workspace/settings')
export const updateWorkspace = (data) => api.patch('/workspace/settings', data)
export const getMembers = () => api.get('/workspace/members')
export const inviteMember = (data) => api.post('/workspace/invite', data)
export const updateMemberRole = (membershipId, data) =>
  api.patch(`/workspace/members/${membershipId}/role`, data)
export const removeMember = (membershipId) =>
  api.delete(`/workspace/members/${membershipId}`)
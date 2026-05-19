import api from './axios'

export const register = (data) => api.post('/auth/register', data)

export const login = (tenantSlug, data) =>
  api.post(`/auth/login?tenant_slug=${tenantSlug}`, data)

export const logout = () => api.post('/auth/logout')

export const refreshToken = () => api.post('/auth/refresh')
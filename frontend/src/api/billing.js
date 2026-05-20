import api from './axios'

export const getBillingInfo = () => api.get('/billing')
export const createOrder = (data) => api.post('/billing/order', data)
export const verifyPayment = (data) => api.post('/billing/verify', data)
export const downgradeToFree = () => api.post('/billing/downgrade')
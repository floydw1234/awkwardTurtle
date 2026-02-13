import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
})

export const authAPI = {
  register: (username: string, password: string) =>
    api.post('/auth/register', { username, password }),
  login: (username: string, password: string) =>
    api.post('/auth/login', { username, password }),
  logout: () => api.post('/auth/logout'),
}

export const friendsAPI = {
  add: (username: string) => api.post(`/friends/add/${username}`),
  remove: (username: string) => api.post(`/friends/remove/${username}`),
  get: () => api.get('/friends'),
}

export const messagesAPI = {
  send: (toUserId: number, content: string) =>
    api.post('/messages/send', { to_user_id: toUserId, content }),
  inbox: () => api.get('/messages/inbox'),
  outbox: () => api.get('/messages/outbox'),
  markAsRead: (messageId: number) => api.post(`/messages/${messageId}/read`),
}

export const notificationsAPI = {
  get: () => api.get('/notifications'),
}

export default api

import axios from 'axios'

const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/'

const http = axios.create({
  baseURL: apiBase,
  timeout: Number(import.meta.env.VITE_HTTP_TIMEOUT || 20000)
})

http.interceptors.request.use(config => {
  const token = window.localStorage.getItem('gw_token')
  if (token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Token ${token}`
  }
  return config
})

http.interceptors.response.use(
  response => response,
  error => {
    const message = error.response?.data?.error || error.response?.data?.detail || error.message
    return Promise.reject(new Error(message))
  }
)

export default http


import http from './http'

export const login = async ({ username, password }) => {
  const { data } = await http.post('login/', { username, password })
  return data
}

export const register = async ({ username, password }) => {
  const { data } = await http.post('register/', { username, password })
  return data
}

export const fetchUserProfile = async () => {
  const { data } = await http.get('userinfo/')
  return data
}


import http from './http'

export const fetchSteamGames = async ({ force = false } = {}) => {
  const config = force ? { params: { force: '1' } } : undefined
  const { data } = await http.get('steamgameinfo/', config)
  return data
}

export const bindSteamAccount = async payload => {
  await http.post('bindsteam/', payload)
}

export const unbindSteamAccount = async () => {
  await http.get('unbindsteam/')
}

export const fetchDiscountedGames = async () => {
  const { data } = await http.get('steamdiscounts/')
  return data
}


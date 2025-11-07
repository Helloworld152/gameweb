import http from './http'

export const fetchSteamGames = async () => {
  const { data } = await http.get('steamgameinfo/')
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


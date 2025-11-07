import { defineStore } from 'pinia'
import { login as loginApi, register as registerApi, fetchUserProfile } from '../api/auth'

const TOKEN_KEY = 'gw_token'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: '',
    user: null,
    loading: false,
    error: ''
  }),
  getters: {
    isAuthenticated: state => Boolean(state.token),
    steamUserName: state => state.user?.steamUserName || ''
  },
  actions: {
    initFromStorage() {
      const storedToken = window.localStorage.getItem(TOKEN_KEY)
      if (storedToken) {
        this.token = storedToken
        this.refreshProfile()
      }
    },
    async login(credentials) {
      this.loading = true
      this.error = ''
      try {
        const { token } = await loginApi(credentials)
        this.token = token
        window.localStorage.setItem(TOKEN_KEY, token)
        await this.refreshProfile()
      } catch (err) {
        this.error = err.message || '登录失败'
        throw err
      } finally {
        this.loading = false
      }
    },
    async register(payload) {
      this.loading = true
      this.error = ''
      try {
        await registerApi(payload)
      } catch (err) {
        this.error = err.message || '注册失败'
        throw err
      } finally {
        this.loading = false
      }
    },
    async refreshProfile() {
      if (!this.token) return
      try {
        this.user = await fetchUserProfile()
      } catch (err) {
        console.error('Failed to fetch user profile', err)
      }
    },
    logout() {
      this.token = ''
      this.user = null
      window.localStorage.removeItem(TOKEN_KEY)
    }
  }
})


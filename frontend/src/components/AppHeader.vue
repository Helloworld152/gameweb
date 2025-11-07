<script setup>
import { computed } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const isAuthenticated = computed(() => authStore.isAuthenticated)
const username = computed(() => authStore.user?.username || '')

const logout = () => {
  authStore.logout()
  if (route.meta.requiresAuth) {
    router.push({ name: 'login' })
  }
}
</script>

<template>
  <header class="app-header">
    <div class="brand">Steam 游戏社区</div>
    <nav class="nav-links">
      <RouterLink :to="{ name: 'posts' }">社区</RouterLink>
      <RouterLink :to="{ name: 'dashboard' }">个人中心</RouterLink>
    </nav>
    <div class="user-panel">
      <template v-if="isAuthenticated">
        <span class="username">{{ username }}</span>
        <button class="link-button" type="button" @click="logout">退出</button>
      </template>
      <template v-else>
        <RouterLink class="link-button" :to="{ name: 'login' }">登录</RouterLink>
        <RouterLink class="link-button" :to="{ name: 'register' }">注册</RouterLink>
      </template>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(9, 28, 45, 0.9);
  padding: 1.25rem 2rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  position: sticky;
  top: 0;
  z-index: 10;
  backdrop-filter: blur(10px);
}

.brand {
  font-size: 1.25rem;
  font-weight: 600;
}

.nav-links {
  display: flex;
  gap: 1rem;
}

.nav-links a {
  color: inherit;
  text-decoration: none;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  transition: background 0.2s ease;
}

.nav-links a.router-link-active {
  background: rgba(24, 108, 210, 0.5);
}

.nav-links a:hover {
  background: rgba(24, 108, 210, 0.3);
}

.user-panel {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.username {
  font-size: 0.95rem;
  color: rgba(210, 220, 242, 0.9);
}

.link-button {
  background: none;
  border: 1px solid rgba(24, 108, 210, 0.5);
  color: inherit;
  border-radius: 6px;
  padding: 0.4rem 0.9rem;
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease;
  text-decoration: none;
}

.link-button:hover {
  background: rgba(24, 108, 210, 0.3);
  border-color: rgba(24, 108, 210, 0.7);
}
</style>


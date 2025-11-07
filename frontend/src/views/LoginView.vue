<script setup>
import { reactive, ref } from 'vue'
import { useRouter, useRoute, RouterLink } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const form = reactive({
  username: route.query.username || '',
  password: ''
})

const submitting = ref(false)
const error = ref('')

const handleSubmit = async () => {
  if (submitting.value) return
  submitting.value = true
  error.value = ''
  try {
    await authStore.login(form)
    const redirect = route.query.redirect || { name: 'posts' }
    router.push(redirect)
  } catch (err) {
    error.value = err.message || '登录失败'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <section class="auth-card">
    <h1>欢迎回来</h1>
    <p class="subtitle">使用账号登录，参与 Steam 游戏社区交流</p>

    <form class="form" @submit.prevent="handleSubmit">
      <label>
        <span>用户名</span>
        <input v-model="form.username" type="text" required autocomplete="username" />
      </label>
      <label>
        <span>密码</span>
        <input v-model="form.password" type="password" required autocomplete="current-password" />
      </label>
      <button class="primary" type="submit" :disabled="submitting">{{ submitting ? '登录中…' : '登录' }}</button>
      <p v-if="error" class="error">{{ error }}</p>
    </form>

    <p class="switch">没有账号？<RouterLink :to="{ name: 'register' }">立即注册</RouterLink></p>
  </section>
</template>

<style scoped>
.auth-card {
  background: rgba(13, 32, 51, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  padding: 2.5rem;
  max-width: 420px;
  margin: 0 auto;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.25);
}

h1 {
  margin: 0 0 0.5rem;
  font-size: 1.9rem;
}

.subtitle {
  margin: 0 0 2rem;
  color: rgba(210, 220, 242, 0.7);
  font-size: 0.95rem;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

label {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  font-size: 0.95rem;
}

input {
  padding: 0.75rem 1rem;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(8, 21, 34, 0.8);
  color: inherit;
}

input:focus {
  outline: none;
  border-color: rgba(66, 160, 255, 0.6);
  box-shadow: 0 0 0 3px rgba(66, 160, 255, 0.2);
}

.primary {
  margin-top: 0.5rem;
  padding: 0.75rem;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  background: linear-gradient(135deg, #2a7de1, #5b3df0);
  color: #fff;
  font-weight: 600;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 24px rgba(46, 128, 222, 0.25);
}

.primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.error {
  color: #ff6b81;
  font-size: 0.9rem;
  margin: 0;
}

.switch {
  margin-top: 1.5rem;
  text-align: center;
  color: rgba(210, 220, 242, 0.7);
}

.switch a {
  color: #7fa9ff;
}
</style>


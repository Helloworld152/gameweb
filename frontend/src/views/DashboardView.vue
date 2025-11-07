<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import {
  fetchSteamGames,
  bindSteamAccount,
  unbindSteamAccount
} from '../api/steam'

const authStore = useAuthStore()
const router = useRouter()

const user = computed(() => authStore.user)
const steamGames = ref([])
const loadingGames = ref(false)
const error = ref('')

const form = reactive({
  steamUserName: ''
})

const loadGames = async () => {
  if (!authStore.steamUserName) {
    steamGames.value = []
    return
  }

  loadingGames.value = true
  error.value = ''
  try {
    const data = await fetchSteamGames()
    steamGames.value = Array.isArray(data) ? data : []
  } catch (err) {
    error.value = err.message || '获取 Steam 数据失败'
  } finally {
    loadingGames.value = false
  }
}

onMounted(() => {
  if (!authStore.isAuthenticated) {
    router.push({ name: 'login', query: { redirect: '/dashboard' } })
    return
  }
  form.steamUserName = authStore.steamUserName
  loadGames()
})

const binding = ref(false)

const handleBind = async () => {
  if (!form.steamUserName.trim()) {
    error.value = '请输入 Steam Vanity 名称'
    return
  }
  binding.value = true
  error.value = ''
  try {
    await bindSteamAccount({ steamUserName: form.steamUserName.trim() })
    await authStore.refreshProfile()
    await loadGames()
  } catch (err) {
    error.value = err.message || '绑定失败'
  } finally {
    binding.value = false
  }
}

const handleUnbind = async () => {
  if (!confirm('确定解绑 Steam 账号？')) return
  binding.value = true
  error.value = ''
  try {
    await unbindSteamAccount()
    await authStore.refreshProfile()
    form.steamUserName = ''
    steamGames.value = []
  } catch (err) {
    error.value = err.message || '解绑失败'
  } finally {
    binding.value = false
  }
}

const formattedGames = computed(() =>
  steamGames.value
    .map(game => ({
      appid: game.appid,
      name: game.name,
      playtime: Math.round((game.playtime_forever || 0) / 60)
    }))
    .sort((a, b) => b.playtime - a.playtime)
    .slice(0, 12)
)
</script>

<template>
  <section class="dashboard">
    <header class="profile-card">
      <h1>个人中心</h1>
      <div class="profile-info">
        <div>
          <p><span class="label">用户名：</span>{{ user?.username }}</p>
          <p>
            <span class="label">Steam</span>
            <span v-if="authStore.steamUserName">{{ authStore.steamUserName }}</span>
            <span v-else class="muted">未绑定</span>
          </p>
        </div>
      </div>

      <div class="steam-bind">
        <label>
          <span>Steam Vanity 名称</span>
          <input v-model="form.steamUserName" type="text" placeholder="例如：gaben" />
        </label>
        <div class="actions">
          <button class="primary" type="button" :disabled="binding" @click="handleBind">
            {{ binding ? '提交中…' : '绑定 / 更新' }}
          </button>
          <button
            v-if="authStore.steamUserName"
            class="outline"
            type="button"
            :disabled="binding"
            @click="handleUnbind"
          >
            解绑
          </button>
        </div>
      </div>
      <p v-if="error" class="error">{{ error }}</p>
    </header>

    <section class="steam-section">
      <div class="section-header">
        <h2>Steam 游戏游玩时长</h2>
        <button class="outline" type="button" :disabled="loadingGames" @click="loadGames">
          {{ loadingGames ? '刷新中…' : '刷新' }}
        </button>
      </div>

      <p v-if="!authStore.steamUserName" class="hint">绑定 Steam 账号后即可查看游戏数据。</p>
      <div v-else-if="loadingGames" class="loading">正在加载 Steam 数据…</div>
      <ul v-else-if="formattedGames.length" class="game-grid">
        <li v-for="game in formattedGames" :key="game.appid" class="game-card">
          <h3>{{ game.name }}</h3>
          <p>{{ game.playtime }} 小时</p>
        </li>
      </ul>
      <p v-else class="hint">未获取到游戏数据，检查 Steam 名称是否正确或稍后重试。</p>
    </section>
  </section>
</template>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.profile-card {
  background: rgba(12, 30, 49, 0.85);
  border-radius: 18px;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.06);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.profile-card h1 {
  margin: 0;
}

.profile-info p {
  margin: 0.3rem 0;
  font-size: 1rem;
}

.label {
  color: rgba(210, 220, 242, 0.6);
  margin-right: 0.5rem;
}

.muted {
  color: rgba(210, 220, 242, 0.5);
}

.steam-bind {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.steam-bind label {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
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

.actions {
  display: flex;
  gap: 1rem;
}

.primary,
.outline {
  padding: 0.6rem 1.4rem;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  font-weight: 600;
}

.primary {
  background: linear-gradient(135deg, #2a7de1, #5b3df0);
  color: #fff;
}

.outline {
  border: 1px solid rgba(90, 136, 255, 0.5);
  background: transparent;
  color: inherit;
}

.error {
  color: #ff6b81;
}

.steam-section {
  background: rgba(12, 30, 49, 0.75);
  border-radius: 18px;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.game-grid {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 1.25rem;
}

.game-card {
  background: rgba(9, 24, 39, 0.9);
  border-radius: 14px;
  padding: 1.1rem;
  border: 1px solid rgba(255, 255, 255, 0.04);
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.game-card h3 {
  margin: 0;
  font-size: 1rem;
}

.game-card p {
  margin: 0;
  color: rgba(210, 220, 242, 0.75);
}

.hint {
  color: rgba(210, 220, 242, 0.6);
}

.loading {
  color: rgba(210, 220, 242, 0.8);
}

@media (max-width: 768px) {
  .steam-section,
  .profile-card {
    padding: 1.5rem;
  }
  .actions {
    flex-direction: column;
    gap: 0.75rem;
  }
  .primary,
  .outline {
    width: 100%;
  }
}
</style>


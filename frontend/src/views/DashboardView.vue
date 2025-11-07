<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import {
  fetchSteamGames,
  bindSteamAccount,
  unbindSteamAccount
} from '../api/steam'
import SteamGameCard from '../components/SteamGameCard.vue'

const CACHE_PREFIX = 'steam-games-cache-'
const CACHE_TTL = Number(import.meta.env.VITE_STEAM_GAME_CACHE_TTL || 10 * 60 * 1000)

const authStore = useAuthStore()
const router = useRouter()

const user = computed(() => authStore.user)
const steamGames = ref([])
const loadingGames = ref(false)
const error = ref('')
const search = ref('')
const sortKey = ref('hours')
const viewMode = ref('grid')
const hasLoaded = ref(false)

const cacheKey = computed(() => {
  const id = authStore.user?.id
  return id ? `${CACHE_PREFIX}${id}` : ''
})

const readCache = () => {
  if (!cacheKey.value) return null
  try {
    const cached = window.localStorage.getItem(cacheKey.value)
    if (!cached) return null
    const parsed = JSON.parse(cached)
    if (!parsed || !Array.isArray(parsed.data)) return null
    const expired = Date.now() - parsed.timestamp > CACHE_TTL
    return { data: parsed.data, expired }
  } catch (err) {
    console.warn('Failed to read Steam cache', err)
    return null
  }
}

const writeCache = data => {
  if (!cacheKey.value) return
  try {
    window.localStorage.setItem(
      cacheKey.value,
      JSON.stringify({ timestamp: Date.now(), data })
    )
  } catch (err) {
    console.warn('Failed to write Steam cache', err)
  }
}

const clearCache = () => {
  if (!cacheKey.value) return
  window.localStorage.removeItem(cacheKey.value)
}

const form = reactive({
  steamUserName: ''
})

const loadGames = async ({ force = false } = {}) => {
  if (!authStore.steamUserName) {
    steamGames.value = []
    hasLoaded.value = false
    clearCache()
    return
  }

  const force_refresh = force
  const cached = readCache()
  if (cached) {
    steamGames.value = cached.data
    hasLoaded.value = true
    if (!force_refresh && !cached.expired) {
      return
    }
  } else if (hasLoaded.value && !force_refresh) {
    return
  }

  loadingGames.value = true
  error.value = ''
  try {
    const data = await fetchSteamGames({ force: force_refresh })
    steamGames.value = Array.isArray(data) ? data : []
    hasLoaded.value = true
    writeCache(steamGames.value)
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
    clearCache()
    await loadGames({ force: true })
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
    hasLoaded.value = false
    clearCache()
  } catch (err) {
    error.value = err.message || '解绑失败'
  } finally {
    binding.value = false
  }
}

const mappedGames = computed(() =>
  steamGames.value.map(game => {
    const hours = Math.round(((game.playtime_forever || 0) / 60) * 10) / 10
    const recentHours = game.playtime_2weeks
      ? Math.round(((game.playtime_2weeks || 0) / 60) * 10) / 10
      : null
    const cover = `https://cdn.cloudflare.steamstatic.com/steam/apps/${game.appid}/capsule_616x353.jpg`
    const genres = Array.isArray(game.genres)
      ? game.genres.map(item => (typeof item === 'string' ? item : item.description)).filter(Boolean)
      : []
    const price = game.price_overview?.final
    const release = game.release_date?.date
    return {
      ...game,
      hours,
      recent: recentHours,
      cover,
      genres,
      price,
      release_date: release
    }
  })
)

const filteredGames = computed(() => {
  const keyword = search.value.trim().toLowerCase()
  let list = mappedGames.value
  if (keyword) {
    list = list.filter(item => item.name?.toLowerCase().includes(keyword))
  }

  if (sortKey.value === 'alphabet') {
    list = [...list].sort((a, b) => a.name.localeCompare(b.name))
  } else if (sortKey.value === 'recent') {
    list = [...list].sort((a, b) => (b.recent || 0) - (a.recent || 0))
  } else {
    list = [...list].sort((a, b) => b.hours - a.hours)
  }

  return list
})

const summary = computed(() => {
  const totalGames = steamGames.value.length
  const totalHours = steamGames.value.reduce((sum, game) => sum + (game.playtime_forever || 0), 0)
  const topGame = filteredGames.value[0]
  return {
    totalGames,
    totalHours: Math.round((totalHours / 60) * 10) / 10,
    topGame
  }
})
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
        <div>
          <h2>Steam 游戏市场概览</h2>
          <p class="section-subtitle" v-if="summary.topGame">
            最常游玩的游戏：<strong>{{ summary.topGame.name }}</strong>（{{ summary.topGame.hours }} 小时）
          </p>
        </div>
        <div class="section-actions">
          <button class="outline" type="button" :disabled="loadingGames" @click="loadGames({ force: true })">
            {{ loadingGames ? '刷新中…' : '刷新' }}
          </button>
          <div class="view-toggle">
            <button
              :class="['chip', { active: viewMode === 'grid' }]"
              type="button"
              @click="viewMode = 'grid'"
            >
              网格
            </button>
            <button
              :class="['chip', { active: viewMode === 'list' }]"
              type="button"
              @click="viewMode = 'list'"
            >
              列表
            </button>
          </div>
        </div>
      </div>

      <div class="stats" v-if="authStore.steamUserName">
        <div class="stat-card">
          <span class="label">总游戏数</span>
          <strong>{{ summary.totalGames }}</strong>
        </div>
        <div class="stat-card">
          <span class="label">累计时长</span>
          <strong>{{ summary.totalHours }} 小时</strong>
        </div>
        <div class="stat-card" v-if="summary.topGame">
          <span class="label">当前最热</span>
          <strong>{{ summary.topGame.name }}</strong>
        </div>
      </div>

      <div class="controls" v-if="authStore.steamUserName && filteredGames.length">
        <input
          v-model="search"
          type="search"
          placeholder="搜索游戏名称..."
          class="search"
        />
        <div class="sort-group">
          <button
            type="button"
            :class="['chip', { active: sortKey === 'hours' }]"
            @click="sortKey = 'hours'"
          >
            按时长排序
          </button>
          <button
            type="button"
            :class="['chip', { active: sortKey === 'recent' }]"
            @click="sortKey = 'recent'"
          >
            最近游玩
          </button>
          <button
            type="button"
            :class="['chip', { active: sortKey === 'alphabet' }]"
            @click="sortKey = 'alphabet'"
          >
            按名称排序
          </button>
        </div>
      </div>

      <p v-if="!authStore.steamUserName" class="hint">绑定 Steam 账号后即可查看游戏数据。</p>
      <div v-else-if="loadingGames" class="loading">正在加载 Steam 数据…</div>
      <div v-else-if="filteredGames.length" :class="['game-container', viewMode]">
        <SteamGameCard v-for="game in filteredGames" :key="game.appid" :game="game" />
      </div>
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
  gap: 1rem;
}

.section-subtitle {
  margin: 0.35rem 0 0;
  color: rgba(210, 220, 242, 0.65);
  font-size: 0.95rem;
}

.section-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.view-toggle {
  display: inline-flex;
  gap: 0.5rem;
  background: rgba(14, 36, 56, 0.8);
  padding: 0.3rem;
  border-radius: 999px;
  border: 1px solid rgba(148, 202, 255, 0.15);
}

.view-toggle .chip {
  padding: 0.35rem 0.95rem;
  border-radius: 999px;
  border: none;
  background: transparent;
  color: rgba(210, 220, 242, 0.7);
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease;
}

.view-toggle .chip.active {
  background: rgba(90, 160, 255, 0.25);
  color: #dce6ff;
}

.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1rem;
}

.stat-card {
  padding: 1.1rem 1.25rem;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(25, 57, 92, 0.85), rgba(14, 36, 56, 0.9));
  border: 1px solid rgba(148, 202, 255, 0.12);
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.stat-card .label {
  color: rgba(210, 220, 242, 0.6);
  font-size: 0.85rem;
}

.stat-card strong {
  font-size: 1.4rem;
  color: #f4f8ff;
}

.controls {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: space-between;
  align-items: center;
}

.search {
  flex: 1 1 240px;
  padding: 0.65rem 1rem;
  border-radius: 999px;
  border: 1px solid rgba(148, 202, 255, 0.2);
  background: rgba(10, 26, 43, 0.85);
  color: inherit;
}

.search:focus {
  outline: none;
  border-color: rgba(90, 160, 255, 0.55);
  box-shadow: 0 0 0 3px rgba(90, 160, 255, 0.15);
}

.sort-group {
  display: flex;
  gap: 0.6rem;
}

.sort-group .chip {
  padding: 0.45rem 1rem;
  border-radius: 999px;
  border: 1px solid rgba(148, 202, 255, 0.25);
  background: transparent;
  color: rgba(210, 220, 242, 0.75);
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease;
}

.sort-group .chip.active {
  background: rgba(90, 160, 255, 0.2);
  color: #dce6ff;
}

.game-container {
  display: grid;
  gap: 1.5rem;
}

.game-container.grid {
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
}

.game-container.list {
  grid-template-columns: repeat(auto-fill, minmax(460px, 1fr));
}

.hint {
  color: rgba(210, 220, 242, 0.68);
  text-align: center;
}

.loading {
  text-align: center;
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
  .section-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .section-actions {
    width: 100%;
    justify-content: space-between;
  }
  .controls {
    flex-direction: column;
    align-items: stretch;
  }
  .sort-group {
    width: 100%;
    justify-content: space-between;
  }
}
</style>


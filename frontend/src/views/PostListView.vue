<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import {
  fetchAllPosts,
  fetchMyPosts,
  createPost,
  deletePost
} from '../api/posts'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const posts = ref([])
const loading = ref(false)
const error = ref('')
const filter = ref('all')

const form = reactive({
  title: '',
  content: ''
})

const fetchPosts = async () => {
  loading.value = true
  error.value = ''
  try {
    posts.value = filter.value === 'mine' ? await fetchMyPosts() : await fetchAllPosts()
  } catch (err) {
    error.value = err.message || '加载帖子失败'
  } finally {
    loading.value = false
  }
}

const syncFilterFromRoute = () => {
  const routeFilter = route.query.filter === 'mine' ? 'mine' : 'all'
  if (filter.value !== routeFilter) {
    filter.value = routeFilter
  }
}

onMounted(() => {
  syncFilterFromRoute()
  fetchPosts()
})

watch(
  () => route.query.filter,
  () => {
    syncFilterFromRoute()
  }
)

watch(filter, () => {
  if (filter.value === 'mine' && !authStore.isAuthenticated) {
    filter.value = 'all'
    router.push({ name: 'login', query: { redirect: '/posts?filter=mine' } })
    return
  }
  router.replace({ name: 'posts', query: filter.value === 'mine' ? { filter: 'mine' } : {} })
  fetchPosts()
})

const submitting = ref(false)

const handleCreate = async () => {
  if (!authStore.isAuthenticated) {
    router.push({ name: 'login', query: { redirect: '/posts' } })
    return
  }

  submitting.value = true
  try {
    await createPost({ title: form.title, content: form.content })
    form.title = ''
    form.content = ''
    filter.value = authStore.isAuthenticated ? filter.value : 'all'
    await fetchPosts()
  } catch (err) {
    error.value = err.message || '发帖失败'
  } finally {
    submitting.value = false
  }
}

const handleDelete = async post => {
  if (!confirm(`确认删除帖子「${post.title}」?`)) return
  try {
    await deletePost(post.id)
    await fetchPosts()
  } catch (err) {
    error.value = err.message || '删除失败'
  }
}

const goDetail = postId => {
  if (!authStore.isAuthenticated) {
    router.push({ name: 'login', query: { redirect: `/posts/${postId}` } })
    return
  }
  router.push({ name: 'post-detail', params: { postId } })
}
</script>

<template>
  <section class="stack">
    <header class="page-header">
      <div>
        <h1>社区帖子</h1>
        <p class="subtitle">分享游戏体验，讨论策略，发现同好</p>
      </div>
      <div class="filter">
        <button
          class="chip"
          :class="{ active: filter === 'all' }"
          type="button"
          @click="filter = 'all'"
        >
          全部帖子
        </button>
        <button
          class="chip"
          :class="{ active: filter === 'mine' }"
          type="button"
          @click="filter = 'mine'"
        >
          我的帖子
        </button>
      </div>
    </header>

    <article v-if="authStore.isAuthenticated" class="composer">
      <h2>快速发帖</h2>
      <form class="composer-form" @submit.prevent="handleCreate">
        <input v-model="form.title" type="text" required placeholder="标题" />
        <textarea v-model="form.content" rows="4" required placeholder="分享你的游戏经历…" />
        <button class="primary" type="submit" :disabled="submitting">
          {{ submitting ? '发布中…' : '发布' }}
        </button>
      </form>
    </article>

    <p v-if="error" class="error">{{ error }}</p>

    <div v-if="loading" class="loading">加载中…</div>

    <ul v-else class="post-list">
      <li v-for="post in posts" :key="post.id" class="post-card">
        <div class="post-meta">
          <h3>{{ post.title }}</h3>
          <div class="meta-line">
            <span>{{ post.author_username }}</span>
            <span>·</span>
            <span>{{ post.create_time }}</span>
          </div>
        </div>
        <p class="post-content">{{ post.content.slice(0, 180) }}<span v-if="post.content.length > 180">…</span></p>
        <div class="post-actions">
          <button class="outline" type="button" @click="goDetail(post.id)">查看详情</button>
          <button
            v-if="authStore.user?.id === post.author"
            class="danger"
            type="button"
            @click="handleDelete(post)"
          >
            删除
          </button>
        </div>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.stack {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1rem;
}

.page-header h1 {
  margin: 0;
  font-size: 2rem;
}

.subtitle {
  margin: 0.35rem 0 0;
  color: rgba(210, 220, 242, 0.7);
}

.filter {
  display: flex;
  gap: 0.75rem;
}

.chip {
  padding: 0.5rem 0.9rem;
  border-radius: 999px;
  background: rgba(17, 43, 66, 0.8);
  border: 1px solid transparent;
  color: inherit;
  cursor: pointer;
}

.chip.active {
  background: rgba(90, 136, 255, 0.35);
  border-color: rgba(90, 136, 255, 0.6);
}

.composer {
  background: rgba(12, 30, 49, 0.85);
  border-radius: 18px;
  padding: 1.75rem;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.composer h2 {
  margin: 0 0 1rem;
}

.composer-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.composer-form input,
.composer-form textarea {
  padding: 0.8rem 1rem;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(7, 19, 32, 0.9);
  color: inherit;
  resize: vertical;
}

.composer-form input:focus,
.composer-form textarea:focus {
  outline: none;
  border-color: rgba(66, 160, 255, 0.6);
  box-shadow: 0 0 0 3px rgba(66, 160, 255, 0.2);
}

.primary {
  align-self: flex-end;
  padding: 0.7rem 1.6rem;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #2a7de1, #5b3df0);
  color: #fff;
  font-weight: 600;
  cursor: pointer;
}

.post-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.post-card {
  background: rgba(12, 30, 49, 0.75);
  border-radius: 16px;
  padding: 1.6rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.post-meta h3 {
  margin: 0;
  font-size: 1.4rem;
}

.meta-line {
  display: flex;
  gap: 0.5rem;
  color: rgba(210, 220, 242, 0.6);
  font-size: 0.9rem;
}

.post-content {
  margin: 0;
  color: rgba(210, 220, 242, 0.85);
  line-height: 1.7;
}

.post-actions {
  display: flex;
  gap: 0.75rem;
}

.outline,
.danger {
  padding: 0.55rem 1.1rem;
  border-radius: 8px;
  border: 1px solid rgba(90, 136, 255, 0.5);
  background: transparent;
  color: inherit;
  cursor: pointer;
}

.danger {
  border-color: rgba(255, 107, 129, 0.6);
  color: #ff8299;
}

.error {
  color: #ff6b81;
}

.loading {
  text-align: center;
  color: rgba(210, 220, 242, 0.8);
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .filter {
    width: 100%;
  }
  .post-actions {
    flex-direction: column;
    align-items: flex-start;
  }
  .outline,
  .danger {
    width: 100%;
  }
}
</style>


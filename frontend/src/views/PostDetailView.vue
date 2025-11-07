<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import {
  fetchPostDetail,
  fetchComments,
  addComment,
  deleteComment
} from '../api/posts'

const props = defineProps({
  postId: {
    type: [String, Number],
    required: true
  }
})

const authStore = useAuthStore()
const router = useRouter()

const post = ref(null)
const comments = ref([])
const loading = ref(true)
const error = ref('')
const commentText = ref('')
const busy = ref(false)

const isOwner = computed(() => post.value?.author === authStore.user?.id)

const load = async () => {
  loading.value = true
  error.value = ''
  try {
    const id = Number(props.postId)
    post.value = await fetchPostDetail(id)
    comments.value = await fetchComments(id)
  } catch (err) {
    error.value = err.message || '加载失败'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (!authStore.isAuthenticated) {
    router.push({ name: 'login', query: { redirect: `/posts/${props.postId}` } })
    return
  }
  load()
})

const handleSubmit = async () => {
  if (!commentText.value.trim()) return
  busy.value = true
  try {
    const created = await addComment(Number(props.postId), { content: commentText.value.trim() })
    comments.value.unshift(created)
    commentText.value = ''
  } catch (err) {
    error.value = err.message || '发表评论失败'
  } finally {
    busy.value = false
  }
}

const handleDeleteComment = async commentId => {
  if (!confirm('确定删除该评论？')) return
  try {
    await deleteComment(commentId)
    comments.value = comments.value.filter(item => item.id !== commentId)
  } catch (err) {
    error.value = err.message || '删除评论失败'
  }
}
</script>

<template>
  <section class="detail">
    <button class="back" type="button" @click="router.back()">← 返回</button>

    <div v-if="loading" class="loading">加载中…</div>
    <p v-else-if="error" class="error">{{ error }}</p>

    <article v-else class="post">
      <header>
        <h1>{{ post.title }}</h1>
        <div class="meta">
          <span>{{ post.author_username }}</span>
          <span>·</span>
          <span>{{ post.create_time }}</span>
        </div>
      </header>
      <p class="content">{{ post.content }}</p>
      <p v-if="isOwner" class="hint">你是该帖作者，可在列表页删除帖子。</p>
    </article>

    <section class="comments">
      <h2>评论</h2>
      <form class="comment-form" @submit.prevent="handleSubmit">
        <textarea
          v-model="commentText"
          rows="3"
          placeholder="分享你的想法…"
          required
        />
        <button class="primary" type="submit" :disabled="busy">
          {{ busy ? '提交中…' : '发表评论' }}
        </button>
      </form>

      <ul v-if="comments.length" class="comment-list">
        <li v-for="comment in comments" :key="comment.id" class="comment-item">
          <div class="comment-head">
            <div>
              <span class="author">{{ comment.author_username }}</span>
              <span class="time">{{ comment.create_time }}</span>
            </div>
            <button
              v-if="comment.author === authStore.user?.id"
              class="danger"
              type="button"
              @click="handleDeleteComment(comment.id)"
            >
              删除
            </button>
          </div>
          <p class="comment-content">{{ comment.content }}</p>
        </li>
      </ul>
      <p v-else class="empty">还没有评论，抢先留言吧！</p>
    </section>
  </section>
</template>

<style scoped>
.detail {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.back {
  align-self: flex-start;
  background: none;
  border: none;
  color: rgba(210, 220, 242, 0.75);
  cursor: pointer;
  font-size: 0.95rem;
}

.post {
  background: rgba(12, 30, 49, 0.85);
  border-radius: 18px;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.post h1 {
  margin: 0 0 0.75rem;
  font-size: 2rem;
}

.meta {
  display: flex;
  gap: 0.5rem;
  color: rgba(210, 220, 242, 0.6);
  font-size: 0.9rem;
}

.content {
  white-space: pre-wrap;
  line-height: 1.8;
  margin: 1.5rem 0 0;
  color: rgba(210, 220, 242, 0.9);
}

.hint {
  margin-top: 1rem;
  font-size: 0.85rem;
  color: rgba(210, 220, 242, 0.6);
}

.comments {
  background: rgba(12, 30, 49, 0.75);
  border-radius: 18px;
  padding: 1.75rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.comment-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

textarea {
  padding: 0.8rem 1rem;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(7, 19, 32, 0.9);
  color: inherit;
  resize: vertical;
}

textarea:focus {
  outline: none;
  border-color: rgba(66, 160, 255, 0.6);
  box-shadow: 0 0 0 3px rgba(66, 160, 255, 0.2);
}

.primary {
  align-self: flex-end;
  padding: 0.6rem 1.4rem;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #2a7de1, #5b3df0);
  color: #fff;
  cursor: pointer;
}

.comment-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.comment-item {
  background: rgba(10, 25, 40, 0.85);
  border-radius: 14px;
  padding: 1rem 1.25rem;
  border: 1px solid rgba(255, 255, 255, 0.04);
}

.comment-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.author {
  font-weight: 600;
}

.time {
  margin-left: 0.5rem;
  color: rgba(210, 220, 242, 0.6);
  font-size: 0.85rem;
}

.comment-content {
  margin: 0.75rem 0 0;
  color: rgba(210, 220, 242, 0.85);
  line-height: 1.7;
}

.danger {
  border: 1px solid rgba(255, 107, 129, 0.6);
  border-radius: 8px;
  padding: 0.4rem 0.9rem;
  background: transparent;
  color: #ff7b96;
  cursor: pointer;
}

.empty {
  text-align: center;
  color: rgba(210, 220, 242, 0.7);
}

.loading {
  color: rgba(210, 220, 242, 0.8);
}

.error {
  color: #ff6b81;
}

@media (max-width: 768px) {
  .post,
  .comments {
    padding: 1.25rem;
  }
  .post h1 {
    font-size: 1.6rem;
  }
}
</style>


<script setup>
const props = defineProps({
  game: {
    type: Object,
    required: true
  }
})

const onImageError = event => {
  event.target.classList.add('fallback')
  event.target.src = ''
}
</script>

<template>
  <article class="game-card">
    <div class="cover">
      <img :src="game.cover" :alt="game.name" loading="lazy" @error="onImageError" />
      <div class="cover-overlay">
        <span class="badge">{{ game.hours }} 小时</span>
        <span v-if="game.recent" class="badge recent">近两周 {{ game.recent }} 小时</span>
      </div>
    </div>
    <div class="content">
      <header>
        <h3>{{ game.name }}</h3>
        <span class="meta" v-if="game.release_date">发行：{{ game.release_date }}</span>
      </header>
      <p v-if="game.genres?.length" class="genres">
        <span v-for="genre in game.genres" :key="genre" class="tag">{{ genre }}</span>
      </p>
      <footer>
        <span class="price" v-if="typeof game.price === 'number'">
          ￥{{ (game.price / 100).toFixed(0) }}
        </span>
        <a
          :href="`https://store.steampowered.com/app/${game.appid}`"
          target="_blank"
          rel="noopener"
          class="link"
        >前往商店</a>
      </footer>
    </div>
  </article>
</template>

<style scoped>
.game-card {
  display: flex;
  flex-direction: column;
  background: rgba(9, 21, 36, 0.92);
  border: 1px solid rgba(148, 202, 255, 0.08);
  border-radius: 18px;
  overflow: hidden;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.game-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 16px 40px rgba(30, 94, 191, 0.35);
}

.cover {
  position: relative;
  aspect-ratio: 16 / 9;
  background: radial-gradient(circle at top, rgba(66, 160, 255, 0.3), rgba(9, 21, 36, 0.9));
}

.cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: opacity 0.3s ease;
}

.cover img.fallback {
  opacity: 0.15;
}

.cover-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 0.75rem;
}

.badge {
  align-self: flex-start;
  background: rgba(30, 120, 255, 0.85);
  color: #f4f8ff;
  padding: 0.35rem 0.7rem;
  border-radius: 999px;
  font-size: 0.85rem;
  backdrop-filter: blur(8px);
}

.badge.recent {
  background: rgba(90, 230, 180, 0.75);
  margin-top: auto;
}

.content {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
  padding: 1.25rem 1.4rem 1.3rem;
}

header {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

h3 {
  margin: 0;
  font-size: 1.1rem;
  letter-spacing: 0.02em;
}

.meta {
  color: rgba(210, 220, 242, 0.6);
  font-size: 0.85rem;
}

.genres {
  margin: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.tag {
  border-radius: 999px;
  border: 1px solid rgba(148, 202, 255, 0.25);
  padding: 0.25rem 0.7rem;
  font-size: 0.75rem;
  color: rgba(210, 220, 242, 0.8);
}

footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
}

.price {
  font-weight: 600;
  color: #ffd78a;
}

.link {
  color: #8fbaff;
  text-decoration: none;
  font-weight: 600;
  border: 1px solid rgba(148, 202, 255, 0.35);
  padding: 0.4rem 0.85rem;
  border-radius: 999px;
  transition: background 0.2s ease, color 0.2s ease;
}

.link:hover {
  background: rgba(148, 202, 255, 0.15);
  color: #cfe1ff;
}
</style>


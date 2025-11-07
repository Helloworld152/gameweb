<script setup>
import { computed } from 'vue'

const props = defineProps({
  deal: {
    type: Object,
    required: true
  }
})

const cover = computed(() => props.deal.header_image || props.deal.capsule_image)

const originalPrice = computed(() => formatPrice(props.deal.original_price))
const finalPrice = computed(() => formatPrice(props.deal.final_price))

const hasPrice = computed(() => props.deal.final_price !== undefined && props.deal.final_price >= 0)

function formatPrice(value) {
  if (value === null || value === undefined || value < 0) {
    return '免费'
  }
  const amount = value / 100
  return `￥${amount.toFixed(amount >= 100 ? 0 : 2)}`
}

const reviewText = computed(() => props.deal.reviews_summary?.review_score_desc)

const reviewCount = computed(() => props.deal.reviews_summary?.total_reviews)
</script>

<template>
  <article class="deal-card">
    <div class="media">
      <img v-if="cover" :src="cover" :alt="deal.name" loading="lazy" />
      <div class="discount-badge">-{{ deal.discount_percent }}%</div>
    </div>
    <div class="body">
      <header>
        <h3>{{ deal.name }}</h3>
        <p v-if="reviewText" class="reviews">
          {{ reviewText }}<span v-if="reviewCount"> · {{ reviewCount }} 条评价</span>
        </p>
      </header>
      <div class="price-block" v-if="hasPrice">
        <span class="final">{{ finalPrice }}</span>
        <span class="original">{{ originalPrice }}</span>
      </div>
      <footer>
        <a :href="deal.url" target="_blank" rel="noopener" class="cta">立即抢购</a>
      </footer>
    </div>
  </article>
</template>

<style scoped>
.deal-card {
  display: flex;
  flex-direction: column;
  background: rgba(9, 21, 36, 0.88);
  border-radius: 20px;
  border: 1px solid rgba(148, 202, 255, 0.12);
  overflow: hidden;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.deal-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 24px 48px rgba(26, 93, 180, 0.35);
}

.media {
  position: relative;
  aspect-ratio: 16 / 9;
  background: linear-gradient(135deg, rgba(26, 93, 180, 0.6), rgba(9, 21, 36, 0.95));
}

.media img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.discount-badge {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: linear-gradient(135deg, #ff4676, #ff9f3d);
  color: #fff;
  padding: 0.4rem 0.75rem;
  border-radius: 999px;
  font-weight: 700;
  font-size: 0.95rem;
  box-shadow: 0 12px 24px rgba(255, 90, 120, 0.45);
}

.body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.5rem 1.6rem 1.4rem;
}

header {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

h3 {
  margin: 0;
  font-size: 1.2rem;
  line-height: 1.4;
}

.reviews {
  margin: 0;
  color: rgba(210, 220, 242, 0.75);
  font-size: 0.85rem;
}

.price-block {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
}

.final {
  font-size: 1.4rem;
  font-weight: 700;
  color: #ffeea8;
}

.original {
  text-decoration: line-through;
  color: rgba(210, 220, 242, 0.5);
  font-size: 0.9rem;
}

footer {
  margin-top: auto;
}

.cta {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #2a7de1, #5b3df0);
  color: #fff;
  text-decoration: none;
  padding: 0.6rem 1.4rem;
  border-radius: 999px;
  font-weight: 600;
  transition: opacity 0.2s ease;
}

.cta:hover {
  opacity: 0.9;
}

@media (max-width: 768px) {
  .body {
    padding: 1.25rem 1.35rem 1.2rem;
  }
  .final {
    font-size: 1.2rem;
  }
}
</style>


<script setup>
import { computed, onMounted, ref } from 'vue'
import DiscountGameCard from '../components/DiscountGameCard.vue'
import { fetchDiscountedGames } from '../api/steam'

const deals = ref([])
const loading = ref(true)
const error = ref('')
const search = ref('')
const sortKey = ref('discount')
const priceFilter = ref('all')
const viewMode = ref('grid')

const loadDeals = async () => {
  loading.value = true
  error.value = ''
  try {
    const data = await fetchDiscountedGames()
    deals.value = Array.isArray(data) ? data : []
  } catch (err) {
    error.value = err.message || '获取促销数据失败'
  } finally {
    loading.value = false
  }
}

onMounted(loadDeals)

const filteredDeals = computed(() => {
  const keyword = search.value.trim().toLowerCase()
  let list = deals.value

  if (keyword) {
    list = list.filter(item => item.name?.toLowerCase().includes(keyword))
  }

  if (priceFilter.value === 'free') {
    list = list.filter(item => (item.final_price || 0) <= 0)
  } else if (priceFilter.value === 'under100') {
    list = list.filter(item => item.final_price >= 0 && item.final_price <= 10000)
  }

  if (sortKey.value === 'discount') {
    list = [...list].sort((a, b) => (b.discount_percent || 0) - (a.discount_percent || 0))
  } else if (sortKey.value === 'price') {
    list = [...list].sort((a, b) => (a.final_price || 0) - (b.final_price || 0))
  } else if (sortKey.value === 'popular') {
    list = [...list].sort((a, b) => (b.reviews_summary?.total_reviews || 0) - (a.reviews_summary?.total_reviews || 0))
  }

  return list
})

const heroDeals = computed(() => filteredDeals.value.slice(0, 3))

const restDeals = computed(() => filteredDeals.value.slice(3))
</script>

<template>
  <section class="deals">
    <header class="hero">
      <div class="hero-text">
        <p class="eyebrow">限时特惠</p>
        <h1>发现 Steam 最新折扣</h1>
        <p class="sub">精选全球热门游戏促销，实时同步 Steam 商店，抓住每一次划算机会。</p>
        <div class="hero-actions">
          <button class="primary" type="button" :disabled="loading" @click="loadDeals">
            {{ loading ? '刷新中…' : '重新同步' }}
          </button>
          <button class="outline" type="button" @click="viewMode = viewMode === 'grid' ? 'list' : 'grid'">
            {{ viewMode === 'grid' ? '切换列表视图' : '切换网格视图' }}
          </button>
        </div>
      </div>
      <div class="hero-showcase" v-if="heroDeals.length">
        <DiscountGameCard v-for="deal in heroDeals" :key="deal.appid" :deal="deal" />
      </div>
    </header>

    <section class="toolbar">
      <input v-model="search" type="search" placeholder="搜索促销游戏" />
      <div class="filters">
        <select v-model="sortKey">
          <option value="discount">按折扣排序</option>
          <option value="price">按价格排序</option>
          <option value="popular">最受好评</option>
        </select>
        <select v-model="priceFilter">
          <option value="all">所有价格</option>
          <option value="under100">￥100 以下</option>
          <option value="free">免费/试玩</option>
        </select>
      </div>
    </section>

    <p v-if="error" class="state error">{{ error }}</p>
    <p v-else-if="loading" class="state loading">正在同步 Steam 促销数据…</p>
    <p v-else-if="!filteredDeals.length" class="state empty">暂无符合条件的促销，换个关键词试试吧。</p>

    <div v-if="restDeals.length" :class="['deals-grid', viewMode]">
      <DiscountGameCard v-for="deal in restDeals" :key="deal.appid" :deal="deal" />
    </div>
  </section>
</template>

<style scoped>
.deals {
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
}

.hero {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  background: radial-gradient(circle at 20% 20%, rgba(66, 160, 255, 0.25), transparent), rgba(9, 21, 36, 0.92);
  border-radius: 24px;
  padding: 2.6rem 2.8rem;
  border: 1px solid rgba(148, 202, 255, 0.12);
  box-shadow: 0 24px 60px rgba(12, 42, 86, 0.35);
}

.hero-text {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.eyebrow {
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.25em;
  font-size: 0.8rem;
  color: rgba(173, 208, 255, 0.75);
}

h1 {
  margin: 0;
  font-size: clamp(2rem, 4vw, 2.8rem);
  letter-spacing: 0.02em;
}

.sub {
  margin: 0;
  color: rgba(210, 220, 242, 0.78);
  line-height: 1.7;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.hero-showcase {
  display: grid;
  gap: 1.25rem;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: space-between;
  align-items: center;
}

.toolbar input {
  flex: 1 1 260px;
  padding: 0.7rem 1rem;
  border-radius: 999px;
  border: 1px solid rgba(148, 202, 255, 0.2);
  background: rgba(9, 23, 37, 0.85);
  color: inherit;
}

.toolbar input:focus {
  outline: none;
  border-color: rgba(90, 160, 255, 0.55);
  box-shadow: 0 0 0 3px rgba(90, 160, 255, 0.2);
}

.filters {
  display: flex;
  gap: 0.75rem;
}

.filters select {
  background: rgba(9, 23, 37, 0.9);
  color: inherit;
  border: 1px solid rgba(148, 202, 255, 0.25);
  border-radius: 999px;
  padding: 0.6rem 1.1rem;
}

.deals-grid {
  display: grid;
  gap: 1.8rem;
}

.deals-grid.grid {
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
}

.deals-grid.list {
  grid-template-columns: repeat(auto-fill, minmax(480px, 1fr));
}

.state {
  text-align: center;
  color: rgba(210, 220, 242, 0.75);
}

.state.error {
  color: #ff8b9a;
}

.primary,
.outline {
  border-radius: 999px;
  padding: 0.6rem 1.4rem;
  font-weight: 600;
  cursor: pointer;
  border: none;
}

.primary {
  background: linear-gradient(135deg, #2a7de1, #5b3df0);
  color: #fff;
}

.outline {
  border: 1px solid rgba(148, 202, 255, 0.35);
  background: transparent;
  color: inherit;
}

@media (max-width: 768px) {
  .hero {
    padding: 2rem;
  }
  .filters {
    width: 100%;
    justify-content: space-between;
  }
  .filters select {
    flex: 1;
  }
}
</style>


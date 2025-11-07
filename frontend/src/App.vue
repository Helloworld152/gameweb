<script setup>
import { RouterView } from 'vue-router'
import AppHeader from './components/AppHeader.vue'
</script>

<template>
  <div class="app-shell">
    <AppHeader />
    <main class="app-main">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #0b1725;
  color: #d2dcf2;
}

.app-main {
  flex: 1;
  width: min(1080px, 100%);
  margin: 2rem auto;
  padding: 0 1.5rem 3rem;
}
</style>

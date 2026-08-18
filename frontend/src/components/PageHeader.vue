<script setup lang="ts">
import { ref } from 'vue'
import { useScrollReveal } from '../composables/useGsapReveal'

defineProps<{
  eyebrow: string
  title: string
  desc?: string
}>()

const root = ref<HTMLElement | null>(null)
useScrollReveal(root)
</script>

<template>
  <div ref="root" class="page-head">
    <p class="eyebrow" data-reveal>{{ eyebrow }}</p>
    <h1 class="page-title" data-reveal>{{ title }}</h1>
    <p v-if="desc" class="page-desc" data-reveal>{{ desc }}</p>
  </div>
</template>

<style scoped>
.page-head {
  padding: calc(var(--nav-h) + 70px) 70px 18px;
  max-width: 900px;
}
.page-title {
  margin-top: 22px;
  font-size: clamp(2rem, 4.5vw, 3.5rem);
  line-height: 1.2;
}
.page-desc { margin-top: 18px; color: var(--ink-dim); font-size: 1.02rem; }

@media (max-width: 640px) {
  .page-head { padding: calc(var(--nav-h) + 48px) 24px 12px; }
}
</style>

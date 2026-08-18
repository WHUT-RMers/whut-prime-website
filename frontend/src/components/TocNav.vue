<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

const items = [
  { id: 'event', no: '01', label: '赛事' },
  { id: 'news', no: '02', label: '资讯' },
  { id: 'history', no: '03', label: '历史' },
  { id: 'groups', no: '04', label: '组别' },
  { id: 'recruit', no: '05', label: '投递' },
  { id: 'cooperate', no: '06', label: '合作' },
]

const activeId = ref('')
let triggers: ScrollTrigger[] = []

onMounted(() => {
  triggers = items
    .map((it) => {
      const el = document.getElementById(it.id)
      if (!el) return null
      return ScrollTrigger.create({
        trigger: el,
        start: 'top 45%',
        end: 'bottom 45%',
        onToggle: (self) => {
          if (self.isActive) activeId.value = it.id
        },
      })
    })
    .filter((t): t is ScrollTrigger => t !== null)
})

onBeforeUnmount(() => {
  triggers.forEach((t) => t.kill())
})
</script>

<template>
  <nav class="toc" aria-label="页面目录">
    <a
      v-for="it in items"
      :key="it.id"
      :href="'#' + it.id"
      class="toc-item"
      :class="{ active: activeId === it.id }"
    >
      <span class="toc-no">{{ it.no }}</span>
      <span class="toc-label">{{ it.label }}</span>
    </a>
  </nav>
</template>

<style scoped>
.toc {
  position: fixed;
  left: 20px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 55;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.toc-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 14px 8px 12px;
  border-left: 2px solid var(--line);
  border-radius: 0 8px 8px 0;
  font-family: var(--mono);
  font-size: 0.68rem;
  letter-spacing: 0.18em;
  color: #5b6673;
  text-decoration: none;
  transition: color 0.3s, border-color 0.3s, background 0.3s;
}
.toc-no { opacity: 0.55; }
.toc-item:hover {
  color: var(--ink);
  border-left-color: rgba(45, 226, 166, 0.5);
}
.toc-item.active {
  color: var(--accent);
  border-left-color: var(--accent);
  background: rgba(45, 226, 166, 0.06);
}

@media (max-width: 1150px) {
  .toc { display: none; }
}
</style>

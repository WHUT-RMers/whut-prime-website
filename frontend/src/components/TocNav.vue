<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

const railFill = ref<HTMLElement | null>(null)

const items = [
  { id: 'event', no: '01', label: '赛事' },
  { id: 'news', no: '02', label: '资讯' },
  { id: 'history', no: '03', label: '历史' },
  { id: 'groups', no: '04', label: '组别' },
  { id: 'recruit', no: '05', label: '投递' },
  { id: 'cooperate', no: '06', label: '合作' },
]

const activeId = ref('')
let cleanup: (() => void) | undefined

onMounted(() => {
  const triggers = items
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

  /* 章节进度光柱 */
  const st = ScrollTrigger.create({
    start: 0,
    end: 'max',
    onUpdate: (self) => {
      if (railFill.value) gsap.set(railFill.value, { scaleY: self.progress })
    },
  })

  cleanup = () => {
    triggers.forEach((t) => t.kill())
    st.kill()
  }
})

onBeforeUnmount(() => cleanup?.())
</script>

<template>
  <nav class="toc" aria-label="页面目录">
    <div class="toc-rail" aria-hidden="true"><span ref="railFill"></span></div>
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
  left: 18px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 55;
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding-left: 10px;
}
.toc-rail {
  position: absolute;
  left: 0;
  top: 8px;
  bottom: 8px;
  width: 2px;
  border-radius: 2px;
  background: var(--line);
  overflow: hidden;
}
.toc-rail span {
  display: block;
  height: 100%;
  transform: scaleY(0);
  transform-origin: top;
  background: var(--accent);
}
.toc-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 7px 12px 7px 16px;
  border-radius: 0 10px 10px 0;
  font-family: var(--mono);
  font-size: 0.68rem;
  letter-spacing: 0.18em;
  color: var(--ink-dim);
  text-decoration: none;
  transition: color 0.3s, background 0.3s;
}
.toc-no { opacity: 0.8; transition: opacity 0.3s; }
.toc-item::before {
  content: "";
  position: absolute;
  left: 0;
  top: 50%;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--ink-faint);
  transform: translate(-70%, -50%) scale(0.6);
  transition: background 0.3s, transform 0.4s var(--ease-expo), box-shadow 0.3s;
}
.toc-item:hover { color: var(--ink); background: rgba(255, 255, 255, 0.02); }
.toc-item.active {
  color: var(--accent);
  background: rgba(45, 226, 166, 0.07);
}
.toc-item.active .toc-no { opacity: 1; }
.toc-item.active::before {
  background: var(--accent);
  transform: translate(-70%, -50%) scale(1);
}

@media (max-width: 1150px) {
  .toc { display: none; }
}
</style>
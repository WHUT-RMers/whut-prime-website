<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
import { api, type NewsItem } from '../api'
import { useScrollReveal } from '../composables/useGsapReveal'
import { useMouseFx } from '../composables/useMouseFx'

const props = withDefaults(defineProps<{ limit?: number }>(), { limit: 4 })
const root = ref<HTMLElement | null>(null)
const items = ref<NewsItem[]>([])
const loading = ref(true)
const { reveal } = useScrollReveal(root, { stagger: 0.08, blur: 4 })
useMouseFx(root)
const shown = computed(() => items.value.slice(0, props.limit))
onMounted(async () => {
  try {
    const featured = await api.news(`?featured=1&limit=${props.limit}`)
    items.value = featured.items.length ? featured.items : (await api.news(`?limit=${props.limit}`)).items
  } finally {
    loading.value = false
    // 卡片为异步渲染：等 DOM 更新后补跑入场（头部已在挂载时入场）
    await nextTick()
    reveal()
  }
})
</script>

<template>
  <section id="news" ref="root" class="news"><div class="container">
    <div class="news-head"><p class="eyebrow" data-reveal>02 / 战队资讯</p><h2 class="news-title" data-reveal>最新动态</h2></div>
    <p v-if="loading" class="news-state">正在获取最新资讯…</p><p v-else-if="!shown.length" class="news-state">资讯正在整理中，敬请期待。</p>
    <div v-else class="news-grid" :class="{ fewer: shown.length <= 2 }"><article v-for="n in shown" :key="n.slug" class="news-card" data-reveal data-tilt data-spot>
      <RouterLink :to="`/news/${n.slug}`" class="news-inner"><div class="news-media"><img :src="n.cover_url" :alt="n.title" :style="{ objectPosition: n.image_focus }" /></div><div class="news-body"><div class="news-meta"><span class="news-tag">{{ n.category }}</span><time>{{ n.published_at?.slice(0, 10) }}</time></div><h3>{{ n.title }}</h3><p>{{ n.summary }}</p><span class="news-more">阅读全文 →</span></div></RouterLink>
    </article></div><RouterLink to="/news" class="all-news">全部资讯 →</RouterLink>
  </div></section>
</template>

<style scoped>
.news{padding:0 0 130px}.news-title{margin-top:22px;font-size:clamp(1.9rem,4vw,3.1rem)}.news-state{margin-top:42px;color:var(--ink-dim)}.news-grid{margin-top:54px;display:grid;grid-template-columns:repeat(4,1fr);gap:16px}.news-grid.fewer{grid-template-columns:repeat(2,1fr)}.news-card{border:1px solid var(--line);border-radius:var(--radius);background:var(--surface);overflow:hidden;transition:border-color .3s,transform .35s var(--ease-expo)}.news-card:hover{border-color:var(--accent);transform:translateY(-5px)}.news-inner{display:flex;flex-direction:column;height:100%}.news-media{aspect-ratio:16/10;overflow:hidden;border-bottom:1px solid var(--line)}.news-media img{width:100%;height:100%;object-fit:cover;transition:transform .8s var(--ease-expo)}.news-card:hover img{transform:scale(1.06)}.news-body{display:flex;flex-direction:column;gap:12px;padding:20px;flex:1}.news-meta{display:flex;justify-content:space-between;align-items:center}.news-tag{font-family:var(--mono);font-size:.66rem;color:var(--accent);background:rgba(45,226,166,.1);border-radius:999px;padding:3px 10px}time,.news-more{font-family:var(--mono);font-size:.72rem;color:var(--ink-faint)}h3{font-size:1.08rem}.news-body p{color:var(--ink-dim);font-size:.88rem;flex:1}.news-card:hover .news-more,.all-news{color:var(--accent)}.all-news{display:inline-block;margin-top:26px;font-family:var(--mono);font-size:.8rem;letter-spacing:.08em}@media(max-width:1080px){.news-grid,.news-grid.fewer{grid-template-columns:repeat(2,1fr)}}@media(max-width:560px){.news-grid,.news-grid.fewer{grid-template-columns:1fr}.news{padding-bottom:90px}}
</style>

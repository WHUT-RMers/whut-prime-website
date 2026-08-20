<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
import { api, type NewsItem } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { useScrollReveal } from '../composables/useGsapReveal'

const items = ref<NewsItem[]>([]), categories = ref<string[]>([]), current = ref(''), loading = ref(true), error = ref('')

/** 列表区滚动入场：卡片为异步渲染，数据就绪后由 reveal() 补跑 */
const list = ref<HTMLElement | null>(null)
const { reveal } = useScrollReveal(list, { stagger: 0.06, blur: 4 })

async function load() {
  loading.value = true
  error.value = ''
  try {
    const q = current.value ? `?category=${encodeURIComponent(current.value)}` : ''
    const result = await api.news(q)
    items.value = result.items
    categories.value = result.categories
  } catch {
    error.value = '暂时无法获取资讯，请稍后重试。'
  } finally {
    loading.value = false
    // 等 DOM 更新后再扫描新渲染的 [data-reveal] 卡片
    await nextTick()
    reveal()
  }
}
onMounted(load)
const display = computed(() => items.value)
</script>
<template>
  <div class="page"><div class="container"><PageHeader eyebrow="02 / 战队资讯" title="最新动态" desc="赛场战报、技术研发、招新与合作动态，第一时间了解 PRIME。" />
    <div class="news-watermark" aria-hidden="true">NEWS</div>
    <div ref="list">
      <div class="filters" data-reveal><button :class="{ active: !current }" @click="current='';load()">全部</button><button v-for="category in categories" :key="category" :class="{ active: current===category }" @click="current=category;load()">{{ category }}</button></div>
      <p v-if="loading" class="state">正在加载资讯…</p><p v-else-if="error" class="state error">{{ error }}</p><p v-else-if="!display.length" class="state">暂时没有已发布资讯。</p>
      <div v-else class="grid"><RouterLink v-for="article in display" :key="article.slug" :to="`/news/${article.slug}`" class="card" data-reveal><div class="media"><img :src="article.cover_url" :alt="article.title" :style="{objectPosition:article.image_focus}" /></div><div class="copy"><div><span>{{ article.category }}</span><time>{{ article.published_at?.slice(0,10) }}</time></div><h2>{{ article.title }}</h2><p>{{ article.summary }}</p><b>查看详情 →</b></div></RouterLink></div>
    </div>
  </div></div>
</template>
<style scoped>
.page{padding-bottom:150px;position:relative}.news-watermark{position:absolute;top:136px;left:max(24px,calc((100% - var(--maxw))/2));font-family:var(--display);font-size:clamp(7rem,20vw,18rem);line-height:1;color:transparent;-webkit-text-stroke:1px rgba(238,242,249,.055);pointer-events:none}.filters{position:relative;display:flex;gap:10px;flex-wrap:wrap;margin-top:56px}.filters button{color:var(--ink-dim);background:transparent;border:1px solid var(--line);border-radius:999px;padding:7px 14px;font:700 .76rem var(--mono)}.filters button.active,.filters button:hover{color:var(--accent);border-color:var(--accent)}.state{margin:48px 0;color:var(--ink-dim)}.error{color:var(--accent-warm)}.grid{position:relative;margin-top:28px;display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.card{border:1px solid var(--line);background:var(--surface);transition:transform .35s var(--ease-expo),border-color .3s;overflow:hidden}.card:hover{transform:translateY(-5px);border-color:var(--accent)}.media{aspect-ratio:16/9;overflow:hidden}.media img{width:100%;height:100%;object-fit:cover;transition:transform .7s var(--ease-expo)}.card:hover img{transform:scale(1.05)}.copy{padding:20px;display:flex;min-height:235px;flex-direction:column;gap:13px}.copy>div{display:flex;justify-content:space-between}.copy span,.copy b{font:700 .7rem var(--mono);letter-spacing:.1em;color:var(--accent)}time{font:.7rem var(--mono);color:var(--ink-faint)}h2{font-size:1.18rem}.copy p{font-size:.88rem;color:var(--ink-dim);flex:1}@media(max-width:900px){.grid{grid-template-columns:repeat(2,1fr)}}@media(max-width:560px){.grid{grid-template-columns:1fr}.page{padding-bottom:90px}}
</style>

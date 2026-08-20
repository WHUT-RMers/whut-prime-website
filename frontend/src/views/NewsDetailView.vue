<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { api, type NewsDetail } from '../api'

const route = useRoute()
const article = ref<NewsDetail | null>(null)
const error = ref('')
const slide = ref(0)
let timer: number | undefined

function startCarousel() {
  window.clearInterval(timer)
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
  timer = window.setInterval(() => {
    if (article.value && article.value.cover_images.length > 1) {
      slide.value = (slide.value + 1) % article.value.cover_images.length
    }
  }, 5000)
}

function pauseCarousel() {
  window.clearInterval(timer)
}

async function load() {
  article.value = null
  slide.value = 0
  error.value = ''
  try {
    const slug = String(route.params.slug)
    article.value = await api.article(slug)
    api.countView(slug).then((value) => {
      if (article.value) article.value.view_count = value.view_count
    })
    startCarousel()
  } catch {
    error.value = '这篇资讯不存在或暂未发布。'
  }
}

onMounted(load)
watch(() => route.params.slug, load)
onUnmounted(() => window.clearInterval(timer))
</script>

<template>
  <div class="page">
    <div v-if="error" class="container state">
      <RouterLink to="/news">← 返回资讯</RouterLink>
      <p>{{ error }}</p>
    </div>

    <article v-else-if="article" class="article">
      <header class="article-head">
        <RouterLink to="/news" class="back">← 返回资讯</RouterLink>
        <div class="meta">
          <span>{{ article.category }}</span>
          <time>{{ article.published_at?.slice(0, 10) }}</time>
          <small>{{ article.view_count }} 浏览</small>
        </div>
        <h1>{{ article.title }}</h1>
        <p class="summary">{{ article.summary }}</p>
      </header>

      <main class="content">
        <figure class="hero" @mouseenter="pauseCarousel" @mouseleave="startCarousel">
          <div class="hero-frame">
            <img v-for="(image, index) in article.cover_images" :key="image.id" :src="image.url" :alt="image.caption || article.title" :class="{ active: index === slide }" :style="{ objectPosition: article.image_focus }" />
            <div v-if="article.cover_images.length > 1" class="dots">
              <button v-for="(_, index) in article.cover_images" :key="index" :class="{ active: index === slide }" :aria-label="`显示第 ${index + 1} 张封面`" @click="slide = index; startCarousel()" />
            </div>
          </div>
          <figcaption v-if="article.cover_images[slide]?.caption" aria-live="polite">{{ article.cover_images[slide].caption }}</figcaption>
        </figure>
        <div class="reading-mark"><span>PRIME · NEWS</span><i /></div>
        <div class="article-body" v-html="article.body" />
        <a v-if="article.external_url" :href="article.external_url" target="_blank" rel="noopener" class="external">阅读原文 ↗</a>
        <nav class="siblings">
          <RouterLink v-if="article.previous" :to="`/news/${article.previous.slug}`">← {{ article.previous.title }}</RouterLink>
          <RouterLink v-if="article.next" :to="`/news/${article.next.slug}`">{{ article.next.title }} →</RouterLink>
        </nav>
      </main>
    </article>

    <p v-else class="container state">正在加载资讯…</p>
  </div>
</template>

<style scoped>
.page{padding:calc(var(--nav-h) + clamp(26px,4vw,46px)) 0 var(--section-space)}
.article-head,.content{width:min(820px,calc(100% - (var(--page-gutter) * 2)));margin-inline:auto}
.back{display:inline-flex;align-items:center;min-height:44px;margin-bottom:30px;color:var(--accent);font:700 .76rem var(--mono);letter-spacing:.1em}
.meta{display:flex;align-items:center;gap:14px;color:var(--ink-faint);font:.72rem var(--mono);letter-spacing:.055em}
.meta span{padding:4px 10px;border:1px solid rgba(45,226,166,.3);color:var(--accent)}
.meta small{font:inherit}
h1{max-width:100%;margin-top:20px;font-size:clamp(2.15rem,4.5vw,3.55rem);line-height:1.18;letter-spacing:.005em;text-wrap:balance;overflow-wrap:anywhere}
.summary{max-width:720px;margin-top:20px;color:#a5b0c1;font-size:clamp(1rem,.4vw + .96rem,1.08rem);line-height:1.82;text-wrap:pretty}
.content{margin-top:36px}
.hero{width:100%;margin:0}
.hero-frame{position:relative;width:100%;aspect-ratio:16/9;border:1px solid var(--line-strong);border-radius:8px;overflow:hidden;background:var(--surface)}
.hero-frame>img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:0;transform:scale(1.025);transition:opacity .68s var(--ease),transform 5s linear}
.hero-frame>img.active{opacity:1;transform:scale(1)}
.hero>figcaption{padding:10px 4px 0;color:#8490a3;font-size:13px;line-height:1.65;text-align:center}
.dots{position:absolute;display:flex;gap:2px;left:13px;bottom:7px}
.dots button{position:relative;width:34px;height:36px;border:0;background:transparent}
.dots button::after{content:'';position:absolute;left:5px;right:5px;top:17px;height:2px;background:rgba(255,255,255,.45);transition:background .2s,transform .2s}
.dots button.active{width:48px}
.dots button.active::after{background:var(--accent);transform:scaleY(1.5)}
.reading-mark{display:flex;align-items:center;gap:16px;margin:30px 0 36px;color:var(--ink-faint);font:600 .64rem var(--mono);letter-spacing:.18em}
.reading-mark i{display:block;flex:1;height:1px;background:var(--line)}
.article-body{color:#b9c3d1;font-size:clamp(1rem,.2vw + .98rem,1.07rem);line-height:1.98;word-break:break-word;overflow-wrap:anywhere}
.article-body :deep(p){margin:1.12em 0}
.article-body :deep(h2){margin:2.35em 0 .78em;color:var(--ink);font-size:clamp(1.42rem,2.3vw,1.78rem);line-height:1.42}
.article-body :deep(h3){margin:2em 0 .68em;color:#e2e8f1;font-size:clamp(1.17rem,1.8vw,1.34rem);line-height:1.48}
.article-body :deep(ul),.article-body :deep(ol){margin:1.2em 0;padding-left:1.55em}
.article-body :deep(li){margin:.48em 0;padding-left:.2em}
.article-body :deep(blockquote){margin:2em 0;padding:.65em 1.3em;border-left:3px solid var(--accent);background:rgba(45,226,166,.055);color:#ced6e1}
.article-body :deep(a){color:var(--accent);text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:4px}
.article-body :deep(strong){color:#e9eef5;font-weight:700}
.article-body :deep(hr){margin:2.7em 0;border:0;border-top:1px solid var(--line-strong)}
.article-body :deep(figure.table){display:block;max-width:100%;overflow-x:auto}
.article-body :deep(table){min-width:560px;border-collapse:collapse}
.article-body :deep(th),.article-body :deep(td){padding:10px 12px;border:1px solid var(--line-strong)}
.article-body :deep(iframe),.article-body :deep(video){display:block;max-width:100%;margin-inline:auto}
.article-body :deep(figure.image),.article-body :deep(figure.news-inline-image){display:block;max-width:100%;margin:clamp(30px,5vw,46px) auto}
.article-body :deep(figure.image_resized){display:block}
.article-body :deep(figure img){display:block;width:100%;height:auto;max-height:min(76vh,760px);object-fit:contain;border:1px solid var(--line-strong);border-radius:6px;background:#080a10}
.article-body :deep(figcaption){padding:10px 4px 0;color:#8490a3;font-size:13px;line-height:1.65;text-align:center;background:transparent}
.external{display:inline-flex;align-items:center;min-height:44px;margin-top:38px;color:var(--accent);font:700 .8rem var(--mono);letter-spacing:.06em}
.siblings{display:flex;justify-content:space-between;gap:28px;margin-top:72px;padding-top:24px;border-top:1px solid var(--line)}
.siblings a{display:flex;align-items:center;min-height:48px;max-width:46%;color:var(--ink-dim);font-size:.88rem;line-height:1.6}
.siblings a:hover{color:var(--accent)}
.state{padding-top:100px;color:var(--ink-dim)}
.state p{margin-top:20px}
@media(max-width:600px){
  .page{padding-top:calc(var(--nav-h) + 18px);padding-bottom:90px}
  .article-head,.content{width:calc(100% - 32px)}
  .back{margin-bottom:22px}
  .meta{gap:8px;flex-wrap:wrap;font-size:.68rem}
  .meta span{padding:4px 8px}
  h1{margin-top:17px;font-size:clamp(2rem,10vw,2.65rem);line-height:1.2}
  .summary{margin-top:16px;font-size:.98rem;line-height:1.78}
  .content{margin-top:28px}
  .hero-frame{border-radius:6px}
  .hero>figcaption{font-size:12px}
  .dots{left:7px;bottom:3px}
  .reading-mark{margin:24px 0 28px}
  .article-body{font-size:1rem;line-height:1.9}
  .article-body :deep(figure.image),.article-body :deep(figure.news-inline-image){width:100%!important;margin:28px 0}
  .article-body :deep(figcaption){font-size:12px;line-height:1.65}
  .article-body :deep(blockquote){padding:.65em 1em}
  .siblings{flex-direction:column;gap:8px;margin-top:52px}
  .siblings a{max-width:100%}
}
@media(prefers-reduced-motion:reduce){.hero-frame>img{transition:none;transform:none}}
</style>

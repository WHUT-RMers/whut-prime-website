<script setup lang="ts">
import { computed, ref } from 'vue'
import { useScrollReveal } from '../composables/useGsapReveal'
import PlaceholderImage from './PlaceholderImage.vue'

const props = withDefaults(defineProps<{ limit?: number }>(), { limit: 4 })

const root = ref<HTMLElement | null>(null)
useScrollReveal(root, { stagger: 0.08, blur: 8 })

const news = [
  {
    date: '2026.08',
    tag: '招商',
    title: '2027 赛季招商开启：五档赞助席位开放',
    desc: '冠名赞助商 1 席、特约 4 席、高级 7 席、合作伙伴与行业支持若干，队服、车体、社媒全场景品牌露出。',
    to: '/cooperate',
  },
  {
    date: '2026.07',
    tag: '赛报',
    title: '高校联盟赛再传捷报：全国二等奖累计 9 次',
    desc: '连续四年征战全国大学生机器人大赛 RoboMaster 机甲大师高校联盟赛，累计获全国二等奖 9 次、全国三等奖 17 次。',
    to: '/history',
  },
  {
    date: '2026.06',
    tag: '媒体',
    title: '全媒体矩阵粉丝突破 1500，累计流量 31w+',
    desc: '微信公众号、视频号、B 站、抖音、小红书五大账号同步运营，内容聚焦赛事高光、技术研发与科创故事。',
    to: '/news',
  },
  {
    date: '2026.05',
    tag: '招新',
    title: '新赛季招新启动：四大组别开放投递',
    desc: '机械 / 电控 / 视觉算法 / 商业运营，简历投递通道已开启。',
    to: '/recruit',
  },
]

const shown = computed(() => news.slice(0, props.limit))
</script>

<template>
  <section id="news" ref="root" class="news">
    <div class="container">
      <div class="news-head">
        <p class="eyebrow" data-reveal>02 / 战队资讯</p>
        <h2 class="news-title" data-reveal>最新动态</h2>
      </div>

      <div class="news-grid" :class="{ fewer: shown.length <= 2 }">
        <article v-for="n in shown" :key="n.date + n.title" class="news-card" data-reveal>
          <RouterLink :to="n.to" class="news-inner">
            <div class="news-media">
              <PlaceholderImage :label="'资讯图片 / ' + n.tag" ratio="16 / 10" />
            </div>
            <div class="news-body">
              <div class="news-meta">
                <span class="news-tag">{{ n.tag }}</span>
                <time class="news-date" :datetime="n.date">{{ n.date }}</time>
              </div>
              <h3 class="news-card-title">{{ n.title }}</h3>
              <p class="news-desc">{{ n.desc }}</p>
              <span class="news-more">阅读全文 <span aria-hidden="true">→</span></span>
            </div>
          </RouterLink>
        </article>
      </div>
    </div>
  </section>
</template>

<style scoped>
.news { padding: 0 0 130px; }
.news-title {
  margin-top: 22px;
  font-size: clamp(1.9rem, 4vw, 3.1rem);
}

.news-grid {
  margin-top: 54px;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
.news-grid.fewer { grid-template-columns: repeat(2, 1fr); }

.news-card {
  position: relative;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: linear-gradient(160deg, rgba(255, 255, 255, 0.03), transparent 70%);
  overflow: hidden;
  transition: transform 0.45s var(--ease-expo), border-color 0.4s, box-shadow 0.45s var(--ease-expo);
}
.news-card:hover {
  transform: translateY(-6px);
  border-color: rgba(45, 226, 166, 0.5);
  box-shadow: 0 24px 56px -22px rgba(45, 226, 166, 0.28);
}
/* 高光扫过 */
.news-card::after {
  content: "";
  position: absolute;
  inset: 0;
  z-index: 2;
  pointer-events: none;
  background: linear-gradient(115deg, transparent 30%, rgba(255, 255, 255, 0.06) 46%, transparent 62%);
  transform: translateX(-120%);
  transition: transform 0.85s var(--ease-expo);
}
.news-card:hover::after { transform: translateX(120%); }

.news-inner { display: flex; flex-direction: column; height: 100%; }
.news-media { overflow: hidden; aspect-ratio: 16 / 10; }
.news-media :deep(.ph) {
  height: 100%;
  border-radius: 0;
  transition: transform 0.9s var(--ease-expo);
}
.news-card:hover .news-media :deep(.ph) { transform: scale(1.08); }

.news-body { display: flex; flex-direction: column; gap: 12px; padding: 22px 20px 20px; flex: 1; }
.news-meta { display: flex; align-items: center; justify-content: space-between; }
.news-tag {
  font-family: var(--mono);
  font-size: 0.66rem;
  letter-spacing: 0.12em;
  color: var(--accent);
  border: 1px solid rgba(45, 226, 166, 0.4);
  border-radius: 999px;
  padding: 3px 10px;
  background: rgba(45, 226, 166, 0.05);
}
.news-date { font-family: var(--mono); font-size: 0.72rem; color: var(--ink-faint); }
.news-card-title { font-size: 1.08rem; line-height: 1.4; }
.news-desc { font-size: 0.88rem; color: var(--ink-dim); flex: 1; }
.news-more {
  font-family: var(--mono);
  font-size: 0.72rem;
  letter-spacing: 0.1em;
  color: var(--ink-dim);
  transition: color 0.3s, letter-spacing 0.4s var(--ease-expo);
}
.news-card:hover .news-more { color: var(--accent); letter-spacing: 0.16em; }

@media (max-width: 1080px) {
  .news-grid, .news-grid.fewer { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 560px) {
  .news-grid, .news-grid.fewer { grid-template-columns: 1fr; }
  .news { padding: 0 0 90px; }
}
</style>

<script setup lang="ts">
import { ref } from 'vue'
import { useScrollReveal } from '../composables/useGsapReveal'
import PlaceholderImage from './PlaceholderImage.vue'

const root = ref<HTMLElement | null>(null)
useScrollReveal(root, { stagger: 0.08 })

const news = [
  {
    date: '2026.08',
    tag: '招商',
    title: '2027 赛季招商开启：五档赞助席位开放',
    desc: '冠名赞助商 1 席、特约 4 席、高级 7 席、合作伙伴与行业支持若干，队服、车体、社媒全场景品牌露出。',
    href: '#cooperate',
  },
  {
    date: '2026.07',
    tag: '赛报',
    title: '高校联盟赛再传捷报：全国二等奖累计 9 次',
    desc: '连续四年征战全国大学生机器人大赛 RoboMaster 机甲大师高校联盟赛，累计获全国二等奖 9 次、全国三等奖 17 次。',
    href: '#history',
  },
  {
    date: '2026.06',
    tag: '媒体',
    title: '全媒体矩阵粉丝突破 1500，累计流量 31w+',
    desc: '微信公众号、视频号、B 站、抖音、小红书五大账号同步运营，内容聚焦赛事高光、技术研发与科创故事。',
    href: '#news',
  },
  {
    date: '2026.05',
    tag: '招新',
    title: '新赛季招新启动：四大组别开放投递',
    desc: '机械 / 电控 / 视觉算法 / 商业运营，简历投递通道已开启。',
    href: '#recruit',
  },
]
</script>

<template>
  <section id="news" ref="root" class="news">
    <div class="container">
      <div class="news-head">
        <p class="eyebrow" data-reveal>02 / 战队资讯</p>
        <h2 class="news-title" data-reveal>最新动态</h2>
      </div>

      <div class="news-grid">
        <article v-for="n in news" :key="n.date + n.title" class="news-card" data-reveal>
          <a :href="n.href" class="news-inner">
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
          </a>
        </article>
      </div>
    </div>
  </section>
</template>

<style scoped>
.news { padding: 0 0 150px; }
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

.news-card {
  border: 1px solid var(--line);
  border-radius: 14px;
  background: var(--bg-soft);
  overflow: hidden;
  transition: transform 0.35s var(--ease), border-color 0.35s;
}
.news-card:hover {
  transform: translateY(-5px);
  border-color: rgba(45, 226, 166, 0.45);
}
.news-inner { display: flex; flex-direction: column; height: 100%; }

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
}
.news-date { font-family: var(--mono); font-size: 0.72rem; color: #5b6673; }
.news-card-title { font-size: 1.08rem; line-height: 1.4; }
.news-desc {
  font-size: 0.88rem;
  color: var(--ink-dim);
  flex: 1;
}
.news-more {
  font-family: var(--mono);
  font-size: 0.72rem;
  letter-spacing: 0.1em;
  color: var(--ink-dim);
  transition: color 0.3s;
}
.news-card:hover .news-more { color: var(--accent); }

@media (max-width: 1080px) {
  .news-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 560px) {
  .news-grid { grid-template-columns: 1fr; }
  .news { padding: 0 0 110px; }
}
</style>

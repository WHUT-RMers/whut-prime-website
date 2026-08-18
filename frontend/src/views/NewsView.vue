<script setup lang="ts">
import { ref } from 'vue'
import PageHeader from '../components/PageHeader.vue'
import PlaceholderImage from '../components/PlaceholderImage.vue'
import { useScrollReveal } from '../composables/useGsapReveal'

const root = ref<HTMLElement | null>(null)
useScrollReveal(root, { stagger: 0.06 })

const featured = {
  date: '2026.08',
  tag: '招商',
  title: '2027 赛季招商开启：五档赞助席位正式开放',
  desc: '冠名赞助商 1 席、特约 4 席、高级 7 席，合作伙伴与行业支持若干。队服、机器人车体、赛季纪录片、社媒矩阵全场景品牌露出，具体权益可由双方洽谈定制。',
}

const list = [
  { date: '2026.07', tag: '赛报', title: '高校联盟赛再传捷报：全国二等奖累计 9 次', desc: '连续四年征战全国大学生机器人大赛 RoboMaster 机甲大师高校联盟赛，累计获全国二等奖 9 次、全国三等奖 17 次。' },
  { date: '2026.06', tag: '媒体', title: '全媒体矩阵粉丝突破 1500，累计流量 31w+', desc: '微信公众号、视频号、B 站、抖音、小红书五大账号同步运营，内容聚焦赛事高光、技术研发与科创故事。' },
  { date: '2026.05', tag: '招新', title: '新赛季招新启动：四大组别开放投递', desc: '机械、电控、视觉算法、商业运营，零基础也可以，简历投递通道已开启。' },
  { date: '2026.03', tag: '备赛', title: '赛季整备：机器人进入赛场适配与压测阶段', desc: '出发之前，进行最后一轮稳定性压测与赛场环境适配，把问题留在实验室。' },
  { date: '2025.12', tag: '总结', title: '2025 赛季答谢年会：年度技术复盘与展望', desc: '赛季收官，发布年度技术复盘与新赛季规划，感谢每一位队员的付出。' },
  { date: '2025.09', tag: '纳新', title: '宣讲会回顾：五大赛场，四支组别，一个 PRIME', desc: '面向全校新生的赛季宣讲会落幕，收到了来自近二十个学院的同学报名。' },
]
</script>

<template>
  <div class="page">
    <div class="container">
      <PageHeader
        eyebrow="02 / 战队资讯"
        title="最新动态"
        desc="招商动态、赛场战报、媒体报道与招新信息——第一时间掌握 PRIME 的声音。"
      />
    </div>

    <div ref="root" class="container">
      <RouterLink to="/cooperate" class="featured" data-reveal>
        <div class="featured-media">
          <PlaceholderImage label="2027 赛季招商主视觉" ratio="16 / 9" accent />
        </div>
        <div class="featured-body">
          <div class="featured-meta">
            <span class="tag">{{ featured.tag }}</span>
            <time :datetime="featured.date">{{ featured.date }}</time>
          </div>
          <h2 class="featured-title">{{ featured.title }}</h2>
          <p class="featured-desc">{{ featured.desc }}</p>
          <span class="link-more">查看招商详情 <span aria-hidden="true">→</span></span>
        </div>
      </RouterLink>

      <div class="news-list">
        <article v-for="(n, i) in list" :key="n.date + n.title" class="news-row" data-reveal>
          <span class="news-index">{{ String(i + 1).padStart(2, '0') }}</span>
          <div class="news-row-media">
            <PlaceholderImage :label="'新闻配图 / ' + n.tag" ratio="16 / 9" />
          </div>
          <div class="news-row-body">
            <div class="row-meta">
              <span class="tag">{{ n.tag }}</span>
              <time :datetime="n.date">{{ n.date }}</time>
            </div>
            <h3 class="row-title">{{ n.title }}</h3>
            <p class="row-desc">{{ n.desc }}</p>
          </div>
        </article>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page { padding-bottom: 150px; }

.featured {
  margin-top: 56px;
  display: grid;
  grid-template-columns: minmax(0, 7fr) minmax(0, 5fr);
  border: 1px solid var(--line);
  border-radius: 18px;
  overflow: hidden;
  background: var(--bg-soft);
  transition: border-color 0.35s, transform 0.35s var(--ease);
}
.featured:hover { border-color: rgba(45, 226, 166, 0.45); transform: translateY(-4px); }
.featured-body { display: flex; flex-direction: column; gap: 16px; padding: 36px 34px; justify-content: center; }
.featured-meta, .row-meta { display: flex; align-items: center; justify-content: space-between; }
.tag {
  font-family: var(--mono);
  font-size: 0.68rem;
  letter-spacing: 0.12em;
  color: var(--accent);
  border: 1px solid rgba(45, 226, 166, 0.4);
  border-radius: 999px;
  padding: 3px 10px;
}
time { font-family: var(--mono); font-size: 0.72rem; color: #5b6673; }
.featured-title { font-size: 1.7rem; line-height: 1.35; }
.featured-desc { color: var(--ink-dim); font-size: 0.96rem; }
.link-more { font-family: var(--mono); font-size: 0.74rem; letter-spacing: 0.1em; color: var(--ink-dim); }
.featured:hover .link-more { color: var(--accent); }

.news-list { margin-top: 60px; display: flex; flex-direction: column; gap: 18px; }
.news-row {
  display: grid;
  grid-template-columns: 44px minmax(0, 3fr) minmax(0, 7fr);
  gap: 22px;
  align-items: center;
  padding: 18px;
  border: 1px solid var(--line);
  border-radius: 16px;
  background: linear-gradient(160deg, rgba(255, 255, 255, 0.025), transparent 60%);
  transition: border-color 0.35s, transform 0.35s var(--ease);
}
.news-row:hover { border-color: rgba(45, 226, 166, 0.45); transform: translateX(5px); }
.news-index { font-family: var(--mono); font-size: 0.85rem; color: var(--accent); letter-spacing: 0.1em; text-align: center; }
.news-row-media { min-width: 0; }
.news-row-body { display: flex; flex-direction: column; gap: 10px; min-width: 0; }
.row-title { font-size: 1.15rem; }
.row-desc { color: var(--ink-dim); font-size: 0.92rem; }

@media (max-width: 880px) {
  .featured { grid-template-columns: 1fr; }
  .featured-body { padding: 26px 22px; }
  .news-row { grid-template-columns: 32px 1fr; grid-template-areas: 'idx body' 'media media'; }
  .news-index { grid-area: idx; }
  .news-row-body { grid-area: body; }
  .news-row-media { grid-area: media; margin-top: 6px; }
}
</style>

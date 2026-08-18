<script setup lang="ts">
import { ref } from 'vue'
import PageHeader from '../components/PageHeader.vue'
import PlaceholderImage from '../components/PlaceholderImage.vue'
import { useScrollReveal } from '../composables/useGsapReveal'

const root = ref<HTMLElement | null>(null)
useScrollReveal(root, { stagger: 0.05 })

const tiers = [
  { name: '冠名赞助商', seats: '1 席', amount: '合计 10w+' },
  { name: '特约赞助商', seats: '4 席', amount: '合计 5w+' },
  { name: '高级赞助商', seats: '7 席', amount: '合计 3w+' },
  { name: '合作伙伴', seats: '若干', amount: '合计 1w+' },
  { name: '行业支持', seats: '若干', amount: '资金或技术支持' },
]

const matrix = [
  { b: '战队冠名权', v: [1, 0, 0, 0, 0] },
  { b: '专属战队文创广告位', v: [1, 0, 0, 0, 0] },
  { b: '赛季纪录片独家致谢片段', v: [1, 0, 0, 0, 0] },
  { b: '战队专属招聘通道', v: [1, 1, 0, 0, 0] },
  { b: '多场景渠道全域推广品牌', v: [1, 1, 0, 0, 0] },
  { b: '接受采访时致谢合作商', v: [1, 1, 0, 0, 0] },
  { b: '校内活动分发合作商物料', v: [1, 1, 0, 0, 0] },
  { b: '指定使用产品', v: [1, 1, 1, 0, 0] },
  { b: '战队文化墙展示标识', v: [1, 1, 1, 0, 0] },
  { b: '机器人车体广告位', v: [1, 1, 1, 0, 0] },
  { b: '队服广告位', v: [1, 1, 1, 1, 0] },
  { b: '赛期持合作标识旗帜合影', v: [1, 1, 1, 1, 1] },
  { b: '社媒结尾添加合作标识', v: [1, 1, 1, 1, 1] },
  { b: '提供宣传素材（照片 / 视频）', v: [1, 1, 1, 1, 1] },
  { b: '接待参观战队实验室', v: [1, 1, 1, 1, 1] },
  { b: '社媒平台发布图文视频', v: [8, 6, 4, 3, 1] },
]

const contact = {
  name: '战队经理 卞彦博',
  phone: '13326243419（微信同号）',
  email: 'whut_prime@foxmail.com',
  address: '湖北省武汉市洪山区珞狮路122号 · 武汉理工大学马房山校区东院自动化学院求实楼东附楼102室',
}
</script>

<template>
  <div class="page">
    <div class="container">
      <PageHeader
        eyebrow="06 / 商业合作"
        title="2027 赛季招商"
        desc="凡是合规合法经营的企业及社会组织，皆热忱欢迎携手成为 PRIME 战队的赞助商。合作不限地域，可单赛季或全年共建，具体权益双方洽谈定制。"
      />

      <div class="cover" data-reveal>
        <PlaceholderImage label="2027 赛季招商手册封面" ratio="21 / 9" accent />
      </div>

      <!-- 五档赞助 -->
      <div ref="root" class="tier-grid">
        <div v-for="t in tiers" :key="t.name" class="tier" data-reveal>
          <h3 class="tier-name">{{ t.name }}</h3>
          <p class="tier-seats">{{ t.seats }}</p>
          <p class="tier-amount">{{ t.amount }}</p>
        </div>
      </div>

      <!-- 权益矩阵 -->
      <div class="matrix-block">
        <h2 class="matrix-title" data-reveal>赞助权益矩阵</h2>
        <div class="matrix" data-reveal>
          <div class="matrix-head">
            <div class="mh-name">权益项目</div>
            <div v-for="t in tiers" :key="t.name" class="mh-tier">{{ t.name }}</div>
          </div>
          <div v-for="row in matrix" :key="row.b" class="matrix-row">
            <div class="mr-name">{{ row.b }}</div>
            <div v-for="(val, i) in row.v" :key="i" class="mr-cell">
              <template v-if="typeof val === 'number' && val > 0 && val <= 5">
                <span class="tick" aria-hidden="true"></span>
              </template>
              <template v-else-if="typeof val === 'number' && val > 5">
                <span class="count">≥{{ val }} 篇</span>
              </template>
              <template v-else>
                <span class="dash" aria-hidden="true">—</span>
              </template>
            </div>
          </div>
        </div>
        <p class="matrix-note" data-reveal>注：具体项目经双方洽谈商定，最终权益以双方签署的赞助协议书为准。</p>
      </div>

      <!-- 联系我们 -->
      <div class="contact" data-reveal>
        <h3 class="contact-title">联系我们</h3>
        <dl class="contact-list">
          <div><dt>联系人</dt><dd>{{ contact.name }}</dd></div>
          <div><dt>电话</dt><dd><a :href="'tel:' + contact.phone">{{ contact.phone }}</a></dd></div>
          <div><dt>邮箱</dt><dd><a href="mailto:whut_prime@foxmail.com">{{ contact.email }}</a></dd></div>
          <div><dt>地址</dt><dd>{{ contact.address }}</dd></div>
        </dl>
        <a class="btn btn-primary" href="mailto:whut_prime@foxmail.com">邮件洽谈 <span aria-hidden="true">→</span></a>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page { padding-bottom: 150px; }

.cover { margin-top: 56px; }

.tier-grid {
  margin-top: 48px;
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
}
.tier {
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 24px 18px;
  background: linear-gradient(160deg, rgba(255, 255, 255, 0.03), transparent 60%);
  transition: border-color 0.35s, transform 0.35s var(--ease);
}
.tier:hover { border-color: rgba(45, 226, 166, 0.5); transform: translateY(-4px); }
.tier-name { font-size: 1.02rem; }
.tier-seats { margin-top: 10px; font-family: var(--mono); font-size: 1.5rem; font-weight: 700; color: var(--accent); }
.tier-amount { margin-top: 6px; font-size: 0.82rem; color: var(--ink-dim); }

.matrix-block { margin-top: 70px; }
.matrix-title { font-size: clamp(1.5rem, 3vw, 2.2rem); }
.matrix {
  margin-top: 28px;
  border: 1px solid var(--line);
  border-radius: 16px;
  overflow: hidden;
}
.matrix-head,
.matrix-row {
  display: grid;
  grid-template-columns: minmax(0, 2.2fr) repeat(5, 1fr);
  align-items: center;
}
.matrix-head {
  background: rgba(45, 226, 166, 0.07);
  border-bottom: 1px solid var(--line);
}
.mh-name,
.mh-tier {
  font-family: var(--mono);
  font-size: 0.66rem;
  letter-spacing: 0.12em;
  color: var(--ink-dim);
  padding: 12px 14px;
}
.matrix-row:not(:last-child) { border-bottom: 1px solid rgba(255, 255, 255, 0.05); }
.matrix-row:hover { background: rgba(255, 255, 255, 0.02); }
.mr-name { padding: 12px 14px; font-size: 0.88rem; }
.mr-cell { padding: 12px 6px; text-align: center; }
.tick {
  display: inline-block;
  width: 9px;
  height: 9px;
  border-radius: 2px;
  background: var(--accent);
  box-shadow: 0 0 6px rgba(45, 226, 166, 0.5);
}
.count { font-family: var(--mono); font-size: 0.66rem; color: var(--accent); white-space: nowrap; }
.dash { color: #3a434f; }

.matrix-note {
  margin-top: 16px;
  font-size: 0.78rem;
  color: #5b6673;
}

.contact {
  margin-top: 70px;
  border: 1px solid rgba(45, 226, 166, 0.3);
  border-radius: 18px;
  background: rgba(45, 226, 166, 0.04);
  padding: 40px 36px;
}
.contact-title { font-size: 1.4rem; }
.contact-list { margin: 20px 0 26px; display: flex; flex-direction: column; gap: 14px; }
.contact-list div { display: flex; gap: 16px; }
.contact-list dt { flex-shrink: 0; width: 46px; font-family: var(--mono); font-size: 0.72rem; letter-spacing: 0.12em; color: var(--accent); padding-top: 2px; }
.contact-list dd { font-size: 0.96rem; }
.contact-list a { color: var(--accent); }

@media (max-width: 1000px) {
  .tier-grid { grid-template-columns: repeat(3, 1fr); }
}
@media (max-width: 760px) {
  .tier-grid { grid-template-columns: repeat(2, 1fr); }
  .matrix { overflow-x: auto; }
  .matrix-head, .matrix-row { min-width: 720px; }
}
</style>

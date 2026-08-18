<script setup lang="ts">
import { ref } from 'vue'
import { useScrollReveal } from '../composables/useGsapReveal'

const root = ref<HTMLElement | null>(null)
useScrollReveal(root, { stagger: 0.06, blur: 8 })

const tiers = [
  { name: '冠名赞助商', seats: '1 席', amount: '合计 10w+', top: true },
  { name: '特约赞助商', seats: '4 席', amount: '合计 5w+', top: false },
  { name: '高级赞助商', seats: '7 席', amount: '合计 3w+', top: false },
  { name: '合作伙伴', seats: '若干', amount: '合计 1w+', top: false },
  { name: '行业支持', seats: '若干', amount: '资金或技术支持', top: false },
]

const benefits = [
  '战队冠名权',
  '队服广告位',
  '机器人车体广告位',
  '赛季纪录片独家致谢片段',
  '社媒平台图文视频发布（最高 ≥8 篇）',
  '提供宣传素材（照片、视频）',
  '接待参观战队实验室',
  '校内活动分发品牌物料',
]

const contact = {
  name: '战队经理 卞彦博',
  phone: '13326243419（微信同号）',
  email: 'whut_prime@foxmail.com',
  address: '湖北省武汉市洪山区珞狮路122号 · 武汉理工大学马房山校区东院自动化学院求实楼东附楼102室',
}
</script>

<template>
  <section id="cooperate" ref="root" class="cooperate">
    <div class="container">
      <p class="eyebrow" data-reveal>06 / 商业合作</p>
      <h2 class="cooperate-title" data-reveal>2027 赛季招商开启</h2>
      <p class="cooperate-lead" data-reveal>
        凡是严格遵守国家法律法规、恪守商业诚信、合规合法经营的企业及社会组织，
        皆热忱欢迎携手成为武汉理工大学机甲大师 PRIME 战队的赞助商。合作不限地域，
        可选择单赛事赛季或全年深度共建模式，具体权益由双方友好洽谈。
      </p>

      <div class="tier-grid">
        <article
          v-for="t in tiers"
          :key="t.name"
          class="tier"
          :class="{ primary: t.top }"
          data-reveal
        >
          <span v-if="t.top" class="tier-flag">主力</span>
          <h3 class="tier-name">{{ t.name }}</h3>
          <p class="tier-seats">{{ t.seats }}</p>
          <p class="tier-amount">{{ t.amount }}</p>
        </article>
      </div>

      <div class="cooperate-lower">
        <div class="benefit-card" data-reveal>
          <h3 class="benefit-title">赞助权益（部分）</h3>
          <ul class="benefit-list">
            <li v-for="b in benefits" :key="b">{{ b }}</li>
          </ul>
          <p class="benefit-note">注：具体项目经双方洽谈商定，最终权益以双方签署的赞助协议书为准。</p>
        </div>

        <div class="contact-card" data-reveal>
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
  </section>
</template>

<style scoped>
.cooperate { padding: 0 0 150px; }
.cooperate-title {
  margin-top: 22px;
  font-size: clamp(1.9rem, 4vw, 3.1rem);
}
.cooperate-lead {
  margin-top: 18px;
  color: var(--ink-dim);
  max-width: 760px;
}

.tier-grid {
  margin-top: 46px;
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
}
.tier {
  position: relative;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 24px 18px;
  background: linear-gradient(160deg, rgba(255, 255, 255, 0.03), transparent 70%);
  transition: border-color 0.4s, transform 0.45s var(--ease-expo), box-shadow 0.45s var(--ease-expo);
}
.tier:hover {
  border-color: rgba(45, 226, 166, 0.55);
  transform: translateY(-6px);
  box-shadow: 0 22px 50px -22px rgba(45, 226, 166, 0.3);
}
.tier.primary {
  border-color: rgba(45, 226, 166, 0.55);
  background: radial-gradient(80% 60% at 50% 0%, rgba(45, 226, 166, 0.14), transparent 72%);
}
.tier-flag {
  position: absolute;
  top: -10px;
  left: 16px;
  font-family: var(--mono);
  font-size: 0.6rem;
  letter-spacing: 0.14em;
  color: var(--accent-ink);
  background: var(--accent);
  border-radius: 999px;
  padding: 3px 10px;
  box-shadow: 0 0 14px rgba(45, 226, 166, 0.5);
}
.tier-name { font-size: 1.05rem; }
.tier-seats {
  margin-top: 10px;
  font-family: var(--mono);
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--accent);
  text-shadow: 0 0 16px rgba(45, 226, 166, 0.4);
}
.tier-amount { margin-top: 6px; font-size: 0.82rem; color: var(--ink-dim); }

.cooperate-lower {
  margin-top: 44px;
  display: grid;
  grid-template-columns: minmax(0, 6fr) minmax(0, 6fr);
  gap: 16px;
}
.benefit-card,
.contact-card {
  border: 1px solid var(--line);
  border-radius: 20px;
  background:
    radial-gradient(70% 40% at 50% 0%, rgba(45, 226, 166, 0.05), transparent 70%),
    var(--bg-soft);
  padding: 30px 32px;
  transition: border-color 0.4s, transform 0.45s var(--ease-expo);
}
.benefit-card:hover,
.contact-card:hover { border-color: rgba(45, 226, 166, 0.35); transform: translateY(-4px); }
.benefit-title,
.contact-title { font-size: 1.3rem; }
.benefit-list { list-style: none; margin-top: 18px; display: grid; grid-template-columns: 1fr 1fr; gap: 12px 20px; }
.benefit-list li { position: relative; padding-left: 22px; font-size: 0.92rem; color: var(--ink-dim); }
.benefit-list li::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0.52em;
  width: 9px;
  height: 9px;
  border-radius: 2px;
  background: var(--accent);
  box-shadow: 0 0 8px rgba(45, 226, 166, 0.7);
  transform: rotate(45deg);
}
.benefit-note { margin-top: 20px; font-size: 0.78rem; color: var(--ink-faint); }

.contact-list { margin: 18px 0 22px; display: flex; flex-direction: column; gap: 14px; }
.contact-list div { display: flex; gap: 16px; }
.contact-list dt { flex-shrink: 0; width: 42px; font-family: var(--mono); font-size: 0.72rem; letter-spacing: 0.12em; color: var(--accent); padding-top: 2px; }
.contact-list dd { font-size: 0.95rem; color: var(--ink); transition: color 0.3s; }
.contact-list div:hover dd { color: var(--ink); }
.contact-list a { color: var(--accent); transition: opacity 0.3s, text-shadow 0.3s; }
.contact-list a:hover { opacity: 0.85; text-shadow: 0 0 12px rgba(45, 226, 166, 0.5); }

@media (max-width: 1000px) {
  .tier-grid { grid-template-columns: repeat(3, 1fr); }
  .cooperate-lower { grid-template-columns: 1fr; }
}
@media (max-width: 620px) {
  .tier-grid { grid-template-columns: repeat(2, 1fr); }
  .benefit-list { grid-template-columns: 1fr; }
  .cooperate { padding: 0 0 110px; }
}
</style>

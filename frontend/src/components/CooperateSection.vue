<script setup lang="ts">
import { ref } from 'vue'
import { useScrollReveal } from '../composables/useGsapReveal'
import { useMouseFx } from '../composables/useMouseFx'

const root = ref<HTMLElement | null>(null)
useScrollReveal(root, { stagger: 0.06, blur: 4 })
useMouseFx(root)

const tiers = [
  { name: '冠名赞助商', seats: '1 席', amount: '合计 10w+', top: true },
  { name: '特约赞助商', seats: '4 席', amount: '合计 5w+', top: false },
  { name: '高级赞助商', seats: '7 席', amount: '合计 3w+', top: false },
  { name: '合作伙伴', seats: '若干', amount: '合计 1w+', top: false },
  { name: '行业支持', seats: '若干', amount: '资金或技术支持', top: false },
]

/**
 * 已合作赞助伙伴（logo 在 frontend/public/sponsors/）
 * alt 为厂商名；url 为其官网，点击 logo 新标签页打开；没有官网时留空则不跳转。
 * ⚠️ 森虹官网为搜索所得（泉州森虹科技 senhom.com），瓦力增材暂未找到官网，请核对。
 */
const sponsors = [
  { src: '/static/sponsors/sponsor-1.png', alt: '森虹 CENHONG', url: 'https://www.senhom.com/' },
  { src: '/static/sponsors/sponsor-2.png', alt: 'WONDERMAKER', url: 'https://www.wondermaker3d.com/' },
  { src: '/static/sponsors/sponsor-3.png', alt: '瓦力增材', url: '' },
]
</script>

<template>
  <section id="cooperate" ref="root" class="cooperate">
    <div class="container">
      <p class="eyebrow" data-reveal>05 / 商务赞助</p>
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
          data-tilt
          data-spot
        >
          <span v-if="t.top" class="tier-flag">主力</span>
          <h3 class="tier-name">{{ t.name }}</h3>
          <p class="tier-seats">{{ t.seats }}</p>
          <p class="tier-amount">{{ t.amount }}</p>
        </article>
      </div>

      <div class="sponsor-block" data-reveal>
        <div class="sponsor-head">
          <h3 class="sponsor-title">我们的赞助伙伴</h3>
          <p class="sponsor-sub">感谢每一份信任与支持 · 排名不分先后</p>
        </div>
        <ul class="sponsor-grid">
          <li v-for="s in sponsors" :key="s.src">
            <a
              v-if="s.url"
              :href="s.url"
              target="_blank"
              rel="noopener noreferrer"
              class="sponsor-item sponsor-link"
              :aria-label="s.alt + '（官网）'"
              data-tilt
            >
              <img :src="s.src" :alt="s.alt" loading="lazy" decoding="async" />
            </a>
            <span v-else class="sponsor-item" data-tilt>
              <img :src="s.src" :alt="s.alt" loading="lazy" decoding="async" />
            </span>
          </li>
        </ul>
      </div>

    </div>
  </section>
</template>

<style scoped>
.cooperate { padding: 0 0 var(--section-space); }
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
  background: var(--surface);
  transform-style: preserve-3d;
  transition: border-color 0.3s, background 0.3s;
}
.tier:hover { border-color: var(--accent); background: var(--surface-2); }
.tier.primary {
  border-color: rgba(45, 226, 166, 0.6);
  background: rgba(45, 226, 166, 0.08);
}
.tier.primary:hover { background: rgba(45, 226, 166, 0.14); }
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
}
.tier-name { font-size: 1.05rem; }
.tier-seats {
  margin-top: 10px;
  font-family: var(--mono);
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--accent);
}
.tier-amount { margin-top: 6px; font-size: 0.82rem; color: var(--ink-dim); }

.sponsor-block { margin-top: clamp(36px, 4.5vw, 56px); }
.sponsor-head { display: flex; align-items: baseline; gap: 16px; flex-wrap: wrap; }
.sponsor-title { font-size: 1.12rem; }
.sponsor-sub { font-size: 0.8rem; color: var(--ink-faint); letter-spacing: 0.06em; }
/* 白色底板：这批 logo 为深色，深色主题下也保留白卡保证可见 */
.sponsor-grid {
  list-style: none;
  margin-top: 24px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: clamp(12px, 1.8vw, 20px);
}
.sponsor-item {
  display: grid;
  place-items: center;
  min-height: 122px;
  padding: 22px 20px;
  border: 1px solid var(--line-strong);
  border-radius: var(--radius);
  background: var(--logo-chip);
  transition: border-color 0.3s, transform 0.35s var(--ease-expo);
}
.sponsor-item:hover { border-color: var(--accent); transform: translateY(-3px); }
.sponsor-link { text-decoration: none; }
.sponsor-item img {
  display: block;
  max-width: 100%;
  max-height: 68px;
  width: auto;
  height: auto;
  object-fit: contain;
}

@media (max-width: 760px) {
  .sponsor-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .sponsor-item { min-height: 96px; padding: 18px 14px; }
}

@media (max-width: 1000px) {
  .tier-grid { grid-template-columns: repeat(3, 1fr); }
}
@media (max-width: 620px) {
  .tier-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 380px) {
  .tier-grid { grid-template-columns: 1fr; }
}
</style>

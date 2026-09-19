<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { gsap } from 'gsap'
import { useScrollReveal } from '../composables/useGsapReveal'

const root = ref<HTMLElement | null>(null)
useScrollReveal(root, { blur: 8 })

const navLinks = [
  { to: '/event', label: '赛事介绍' },
  { to: '/history', label: '历史荣誉' },
  { to: '/groups', label: '组别技术' },
  { to: '/recruit', label: '投递简历' },
]

/**
 * 联系我们（首页目录 06）：摆法与字号参照 wute.club 页脚——单列竖排，
 * 小标签在上、数值在下，数值本身可点（tel: / mailto:）。
 * 队长手机号待补：拿到号码后把 value 写成 '蔡宇凡 · <号码>'、href 写成 'tel:<号码>' 即可。
 * 页脚是全站组件，所以这块联系方式每页页脚都能看到；#contact 锚点就在本组件上。
 */
const contacts = [
  { label: '车队队长', value: '蔡宇凡 · 待补充', href: '', note: '' },
  { label: '车队经理', value: '卞彦博 · 13326243419', href: 'tel:13326243419', note: '微信同号' },
  { label: '车队邮箱', value: 'whut_prime@foxmail.com', href: 'mailto:whut_prime@foxmail.com', note: '' },
]

onMounted(() => {
  const mm = gsap.matchMedia()
  mm.add('(prefers-reduced-motion: no-preference)', () => {
    gsap.fromTo(
      '.footer-mark',
      { yPercent: 30, opacity: 0 },
      { yPercent: 0, opacity: 1, ease: 'none', scrollTrigger: { trigger: '.footer', start: 'top bottom', end: 'bottom bottom', scrub: 0.8 } },
    )
  })
})
</script>

<template>
  <footer ref="root" class="footer">
    <span class="footer-mark" aria-hidden="true">PRIME</span>
    <div class="container footer-inner">
      <div class="footer-main">
        <div class="footer-brand" data-reveal>
          <img class="brand-mark" :src="'/static/mascot.png'" alt="" aria-hidden="true" />
          <span class="brand-name">WHUT·PRIME — ROBOMASTER</span>
        </div>
        <nav class="footer-nav" data-reveal>
          <RouterLink v-for="l in navLinks" :key="l.to" :to="l.to">{{ l.label }}</RouterLink>
        </nav>
        <p class="footer-line" data-reveal>
          武汉理工大学机甲大师 PRIME 战队官网 · 2027 赛季
        </p>
        <p class="footer-copy" data-reveal>© 2027 WHUT PRIME · 精研 覃思 笃志 力行</p>
      </div>

      <section id="contact" class="footer-contact" aria-label="联系我们">
        <h2 class="contact-title" data-reveal>联系我们</h2>
        <ul class="contact-list">
          <li v-for="c in contacts" :key="c.label" data-reveal>
            <span class="contact-k">{{ c.label }}</span>
            <a v-if="c.href" class="contact-v" :href="c.href">{{ c.value }}</a>
            <span v-else class="contact-v pending">{{ c.value }}</span>
            <span v-if="c.note" class="contact-note">{{ c.note }}</span>
          </li>
        </ul>
      </section>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  position: relative;
  border-top: 1px solid var(--line);
  padding: 54px 0 64px;
  background: linear-gradient(180deg, rgba(10, 13, 23, 0.55), var(--bg));
  overflow: hidden;
}
.footer-mark {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  bottom: -4%;
  font-family: var(--display);
  font-size: clamp(8rem, 26vw, 22rem);
  line-height: 1;
  color: transparent;
  -webkit-text-stroke: 1px rgba(238, 242, 249, 0.05);
  user-select: none;
  pointer-events: none;
  will-change: transform, opacity;
}
.footer-inner {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 40px clamp(48px, 8vw, 120px);
  align-items: start;
}
.footer-main { display: flex; flex-direction: column; gap: 18px; min-width: 0; }
.footer-brand { display: flex; align-items: center; gap: 12px; }
.brand-mark {
  width: 34px;
  height: 34px;
  flex: 0 0 auto;
  display: block;
  object-fit: contain;
  user-select: none;
  pointer-events: none;
}
.brand-name { font-family: var(--mono); letter-spacing: 0.14em; font-size: 0.86rem; }
.footer-nav { display: flex; gap: 24px; flex-wrap: wrap; }
.footer-nav a { font-size: 0.86rem; color: var(--ink-dim); transition: color 0.3s, letter-spacing 0.4s var(--ease-expo); }
.footer-nav a:hover { color: var(--accent); letter-spacing: 0.1em; }
.footer-line { color: var(--ink-dim); font-size: 0.95rem; max-width: 560px; }
.footer-copy { font-family: var(--mono); font-size: 0.76rem; letter-spacing: 0.1em; color: var(--ink-faint); }

/* ---- 联系我们：单列竖排，字号与间距对齐 wute.club 页脚 ---- */
.footer-contact { display: flex; flex-direction: column; }
.contact-title {
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.18em;
  color: var(--ink-dim);
  margin-bottom: 1.1rem;
}
.contact-list { list-style: none; display: flex; flex-direction: column; }
.contact-list li { margin-bottom: 0.9rem; }
.contact-list li:last-child { margin-bottom: 0; }
.contact-k {
  display: block;
  font-size: 0.62rem;
  letter-spacing: 0.14em;
  color: var(--ink-faint);
  margin-bottom: 0.2rem;
}
.contact-v {
  display: block;
  font-size: 0.86rem;
  color: var(--ink-dim);
  text-decoration: none;
  overflow-wrap: anywhere;
  transition: color 0.3s;
}
a.contact-v:hover { color: var(--accent); }
.contact-v.pending { color: var(--ink-faint); }
.contact-note { display: block; margin-top: 0.2rem; font-size: 0.7rem; color: var(--ink-faint); }

@media (max-width: 860px) {
  .footer-inner { grid-template-columns: minmax(0, 1fr); gap: 34px; }
}
</style>

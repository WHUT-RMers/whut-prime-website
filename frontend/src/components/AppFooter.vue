<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { gsap } from 'gsap'
import { useScrollReveal } from '../composables/useGsapReveal'
import { siteNav } from '../data/nav'

const root = ref<HTMLElement | null>(null)
useScrollReveal(root, { blur: 8 })

/**
 * 联系我们（首页目录 06）：摆法与字号参照 wute.club 页脚——单列竖排，
 * 小标签在上、数值在下，数值本身可点（tel: / mailto:）。
 * 页脚是全站组件，所以这块联系方式每页页脚都能看到；#contact 锚点就在本组件上。
 */
const contacts = [
  { label: '车队队长', value: '蔡宇凡 · 13758214701', href: 'tel:13758214701', note: '' },
  { label: '车队经理', value: '卞彦博 · 13326243419', href: 'tel:13326243419', note: '' },
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
      <div class="footer-brand-col">
        <div class="footer-brand" data-reveal>
          <img class="brand-mark" :src="'/static/mascot.png'" alt="" aria-hidden="true" />
          <span class="brand-name">WHUT·PRIME — ROBOMASTER</span>
        </div>
        <p class="footer-line" data-reveal>
          武汉理工大学机甲大师 PRIME 战队官网
        </p>
        <p class="footer-copy" data-reveal>© 2027 WHUT PRIME · 精研 覃思 笃志 力行</p>
      </div>

      <nav class="footer-nav" aria-label="页脚导航">
        <h2 class="col-title" data-reveal>导航</h2>
        <RouterLink v-for="l in siteNav" :key="l.to" :to="l.to" data-reveal>{{ l.label }}</RouterLink>
      </nav>

      <section id="contact" class="footer-contact" aria-label="联系我们">
        <h2 class="col-title" data-reveal>联系我们</h2>
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

/* 三列：品牌 / 导航 / 联系我们（列宽比参照 wute.club 页脚） */
.footer-inner {
  position: relative;
  display: grid;
  grid-template-columns: 1.6fr 0.9fr 1.3fr;
  gap: 40px clamp(40px, 6vw, 96px);
  align-items: start;
}
.footer-brand-col { display: flex; flex-direction: column; gap: 18px; min-width: 0; }
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
.footer-line { color: var(--ink-dim); font-size: 0.95rem; max-width: 560px; }
.footer-copy { font-family: var(--mono); font-size: 0.76rem; letter-spacing: 0.1em; color: var(--ink-faint); }

/* 列标题：字号/字距与参考站页脚一致 */
.col-title {
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.18em;
  color: var(--ink-dim);
  margin-bottom: 1.1rem;
}

/* 导航：竖排，行高与参考站页脚链接一致 */
.footer-nav { display: flex; flex-direction: column; }
.footer-nav a {
  display: block;
  font-size: 0.86rem;
  line-height: 2;
  color: var(--ink-dim);
  text-decoration: none;
  transition: color 0.3s;
}
.footer-nav a:hover { color: var(--accent); }

/* ---- 联系我们：单列竖排，小标签在上、数值在下 ---- */
.footer-contact { display: flex; flex-direction: column; }
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

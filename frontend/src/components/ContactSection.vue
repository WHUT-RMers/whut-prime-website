<script setup lang="ts">
import { ref } from 'vue'
import { useScrollReveal } from '../composables/useGsapReveal'

/**
 * 06 联系我们：参照 wute.club 页脚的摆法——小标签在上、数值在下，不用卡片框，数值本身可点。
 * 队长手机号待补：把 value 填上、href 补成 'tel:<号码>' 即可（同经理手机）。
 */
const root = ref<HTMLElement | null>(null)
useScrollReveal(root, { blur: 8, stagger: 0.07 })

const contacts = [
  { label: '队长手机', value: '待补充', href: '', note: '' },
  { label: '经理手机', value: '13326243419', href: 'tel:13326243419', note: '微信同号' },
  { label: '战队邮箱', value: 'whut_prime@foxmail.com', href: 'mailto:whut_prime@foxmail.com', note: '' },
]
</script>

<template>
  <section id="contact" ref="root" class="contact">
    <div class="container">
      <p class="eyebrow" data-reveal>06 / 联系我们</p>
      <h2 class="contact-title" data-reveal>联系方式</h2>

      <ul class="contact-list">
        <li v-for="c in contacts" :key="c.label" data-reveal>
          <span class="contact-k">{{ c.label }}</span>
          <a v-if="c.href" class="contact-v" :href="c.href">{{ c.value }}</a>
          <span v-else class="contact-v pending">{{ c.value }}</span>
          <span v-if="c.note" class="contact-note">{{ c.note }}</span>
        </li>
      </ul>
    </div>
  </section>
</template>

<style scoped>
.contact { padding: 0 0 var(--section-space); }
.contact-title { margin-top: 22px; font-size: clamp(1.9rem, 4vw, 3.1rem); }

.contact-list {
  list-style: none;
  margin-top: clamp(34px, 4.4vw, 48px);
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: clamp(28px, 4vw, 64px);
}
.contact-list li {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-width: 0;
}
.contact-k {
  font-size: 0.78rem;
  letter-spacing: 0.14em;
  color: var(--ink-faint);
}
.contact-v {
  font-family: var(--mono);
  font-size: clamp(1.02rem, 1.35vw, 1.3rem);
  color: var(--ink);
  text-decoration: none;
  overflow-wrap: anywhere;
  transition: color 0.3s;
}
a.contact-v:hover { color: var(--accent); }
.contact-v.pending { color: var(--ink-faint); }
.contact-note { font-size: 0.78rem; color: var(--ink-faint); }

@media (max-width: 760px) {
  .contact-list { grid-template-columns: minmax(0, 1fr); gap: 26px; }
}
</style>

<script setup lang="ts">
import { ref } from 'vue'
import { useScrollReveal } from '../composables/useGsapReveal'

/**
 * 06 联系我们：只放三条联系通道。
 * 队长手机号待补：把 value 填上、href 补成 'tel:<号码>' 即可变成可点拨号（同经理手机）。
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

      <ul class="contact-grid">
        <li v-for="c in contacts" :key="c.label" data-reveal>
          <a v-if="c.href" class="contact-card" :href="c.href">
            <span class="contact-k">{{ c.label }}</span>
            <span class="contact-v">{{ c.value }}</span>
            <span v-if="c.note" class="contact-note">{{ c.note }}</span>
          </a>
          <div v-else class="contact-card">
            <span class="contact-k">{{ c.label }}</span>
            <span class="contact-v pending">{{ c.value }}</span>
            <span v-if="c.note" class="contact-note">{{ c.note }}</span>
          </div>
        </li>
      </ul>
    </div>
  </section>
</template>

<style scoped>
.contact { padding: 0 0 var(--section-space); }
.contact-title { margin-top: 22px; font-size: clamp(1.9rem, 4vw, 3.1rem); }

.contact-grid {
  list-style: none;
  margin-top: clamp(38px, 5vw, 54px);
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: clamp(14px, 2vw, 18px);
}
.contact-card {
  display: flex;
  flex-direction: column;
  gap: 10px;
  height: 100%;
  padding: 28px 26px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--surface);
  color: inherit;
  text-decoration: none;
  transition: border-color 0.3s, background 0.3s, transform 0.35s var(--ease-expo);
}
a.contact-card:hover {
  border-color: var(--accent);
  background: var(--surface-2);
  transform: translateY(-4px);
}
.contact-k {
  font-family: var(--mono);
  font-size: 0.68rem;
  letter-spacing: 0.18em;
  color: var(--accent);
}
.contact-v {
  font-family: var(--mono);
  font-size: 1.06rem;
  color: var(--ink);
  overflow-wrap: anywhere;
}
.contact-v.pending { color: var(--ink-faint); letter-spacing: 0.12em; }
.contact-note { font-size: 0.78rem; color: var(--ink-faint); }

@media (max-width: 900px) {
  .contact-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 560px) {
  .contact-grid { grid-template-columns: minmax(0, 1fr); }
}
</style>

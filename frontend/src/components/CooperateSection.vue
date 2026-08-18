<script setup lang="ts">
import { ref } from 'vue'
import { useScrollReveal } from '../composables/useGsapReveal'

const root = ref<HTMLElement | null>(null)
useScrollReveal(root, { stagger: 0.08 })

const partners = [
  {
    t: '技术合作',
    en: 'R&D PARTNERSHIP',
    d: '联合实验室、课题合作与技术人才对接。',
  },
  {
    t: '商业赞助',
    en: 'SPONSORSHIP',
    d: '冠名、联名与赛季赞助，让品牌出现在赛场与镜头前。',
  },
  {
    t: '媒体传播',
    en: 'MEDIA & CONTENT',
    d: '内容共创、赛事直播与校园传播合作。',
  },
]
</script>

<template>
  <section id="cooperate" ref="root" class="cooperate">
    <div class="container">
      <p class="eyebrow" data-reveal>06 / 商业合作</p>
      <h2 class="cooperate-title" data-reveal>与 PRIME 同行</h2>

      <div class="partner-grid">
        <article v-for="p in partners" :key="p.t" class="partner" data-reveal>
          <span class="partner-en">{{ p.en }}</span>
          <h3 class="partner-title">{{ p.t }}</h3>
          <p class="partner-desc">{{ p.d }}</p>
        </article>
      </div>

      <div class="cooperate-contact" data-reveal>
        <div>
          <p class="cc-label">合作邮箱</p>
          <a class="cc-mail" href="mailto:cooperation@whut-prime.demo">
            cooperation@whut-prime.demo
          </a>
        </div>
        <a class="btn btn-ghost" href="mailto:cooperation@whut-prime.demo">发邮件洽谈 <span aria-hidden="true">→</span></a>
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

.partner-grid {
  margin-top: 54px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
.partner {
  padding: 30px 28px;
  border: 1px solid var(--line);
  border-radius: 14px;
  background: linear-gradient(160deg, rgba(255, 255, 255, 0.03), transparent 70%);
  transition: border-color 0.35s, transform 0.35s var(--ease);
}
.partner:hover { border-color: rgba(45, 226, 166, 0.5); transform: translateY(-4px); }
.partner-en { font-family: var(--mono); font-size: 0.62rem; letter-spacing: 0.18em; color: var(--accent); }
.partner-title { margin-top: 16px; font-size: 1.3rem; }
.partner-desc { margin-top: 12px; color: var(--ink-dim); font-size: 0.92rem; }

.cooperate-contact {
  margin-top: 44px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  border: 1px solid rgba(45, 226, 166, 0.3);
  border-radius: 16px;
  padding: 28px 32px;
  background: rgba(45, 226, 166, 0.04);
}
.cc-label { font-family: var(--mono); font-size: 0.7rem; letter-spacing: 0.2em; color: var(--ink-dim); }
.cc-mail {
  margin-top: 6px;
  display: inline-block;
  font-family: var(--mono);
  font-size: 1.18rem;
  color: var(--accent);
  transition: opacity 0.3s;
}
.cc-mail:hover { opacity: 0.8; }

@media (max-width: 880px) {
  .partner-grid { grid-template-columns: 1fr; }
  .cooperate { padding: 0 0 110px; }
}
</style>

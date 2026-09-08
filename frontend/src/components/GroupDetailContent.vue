<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useScrollReveal } from '../composables/useGsapReveal'
import { countUp } from '../utils/motion'
import PageHeader from './PageHeader.vue'
import PlaceholderImage from './PlaceholderImage.vue'
import type { GroupInfo } from '../data/groups'

/**
 * 组别详情正文：路由页（/groups/:code）与全屏浮层（GroupOverlay）共用。
 * 自带滚动入场与计数动画，各自实例独立触发。
 * immediate=true（浮层内）：挂载即播放入场，不依赖窗口滚动（浮层有独立滚动容器）。
 */
const props = withDefaults(defineProps<{ group: GroupInfo; immediate?: boolean }>(), { immediate: false })

const root = ref<HTMLElement | null>(null)
/* PageHeader 自带入场动画：父级 reveal 跳过其子树，避免同一元素被两套 tween 争抢（表现为入场卡住/发黑） */
useScrollReveal(root, {
  selector: '[data-reveal]:not(.page-head *)',
  blur: 6,
  stagger: 0.08,
  immediate: props.immediate,
})

onMounted(() => {
  root.value?.querySelectorAll<HTMLElement>('[data-count]').forEach((node) => {
    const target = Number(node.dataset.count)
    countUp(node, target, 1.8, 'power2.out', 0.2)
  })
})
</script>

<template>
  <div ref="root">
    <PageHeader
      :eyebrow="'04 / 组别介绍 · ' + props.group.code"
      :title="props.group.name"
      :desc="'「' + props.group.quote + '」'"
    />

    <div class="cover" data-reveal>
      <PlaceholderImage :label="props.group.image + ' · 组别主视觉'" ratio="21 / 9" accent />
    </div>

    <div class="detail-grid">
      <div class="detail-main">
        <p v-for="(p, i) in props.group.intro" :key="i" class="intro-p" data-reveal>{{ p }}</p>

        <section class="block" data-reveal>
          <p class="block-label">工作内容</p>
          <ul class="task-list">
            <li v-for="t in props.group.tasks" :key="t">{{ t }}</li>
          </ul>
        </section>

        <section class="block" data-reveal>
          <p class="block-label">技术栈</p>
          <div class="stack-list">
            <span v-for="s in props.group.stack" :key="s" class="stack-tag">{{ s }}</span>
          </div>
        </section>
      </div>

      <aside class="detail-side" data-reveal>
        <div class="stats">
          <div v-for="s in props.group.stats" :key="s.label" class="stat">
            <p class="stat-num"><span :data-count="s.v">0</span><span class="stat-suffix">{{ s.suffix }}</span></p>
            <p class="stat-label">{{ s.label }}</p>
          </div>
        </div>
        <div class="need-card">
          <p class="need-title">招募要求</p>
          <p class="need-text">{{ props.group.need }}</p>
        </div>
      </aside>
    </div>

    <section class="gallery">
      <p class="block-label" data-reveal>组别图集 <span class="label-note">（占位素材）</span></p>
      <div class="gallery-grid">
        <div v-for="(l, i) in props.group.gallery" :key="l" class="gallery-item" data-reveal>
          <PlaceholderImage :label="l" :ratio="i % 3 === 1 ? '4 / 5' : '4 / 3'" />
        </div>
      </div>
    </section>

    <div class="cta-row" data-reveal>
      <p class="cta-text">对{{ props.group.name }}感兴趣？去投递你的简历。</p>
      <RouterLink to="/recruit" class="btn btn-primary" data-magnet>投递简历 <span aria-hidden="true">→</span></RouterLink>
    </div>
  </div>
</template>

<style scoped>
.cover { margin-top: 34px; }

.detail-grid {
  margin-top: 44px;
  display: grid;
  grid-template-columns: minmax(0, 7fr) minmax(0, 5fr);
  gap: 44px;
  align-items: start;
}
.intro-p { margin-top: 18px; color: var(--ink-dim); font-size: 1.02rem; line-height: 1.9; }
.intro-p:first-child { margin-top: 0; }

.block { margin-top: 44px; }
.block-label {
  display: flex;
  align-items: center;
  gap: 12px;
  font-family: var(--mono);
  font-size: 0.7rem;
  letter-spacing: 0.22em;
  color: var(--ink-dim);
}
.block-label::after {
  content: "";
  width: 26px;
  height: 1px;
  background: var(--accent);
}
.label-note { opacity: 0.6; }

.task-list { list-style: none; margin-top: 14px; display: flex; flex-wrap: wrap; gap: 10px; }
.task-list li {
  font-size: 0.9rem;
  color: var(--ink);
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 7px 15px;
  background: rgba(255, 255, 255, 0.02);
}
.stack-list { margin-top: 14px; display: flex; flex-wrap: wrap; gap: 8px; }
.stack-tag {
  font-family: var(--mono);
  font-size: 0.68rem;
  letter-spacing: 0.04em;
  padding: 5px 11px;
  border: 1px solid var(--line);
  border-radius: 6px;
  color: var(--ink-dim);
}

.detail-side { position: sticky; top: calc(var(--nav-h) + 26px); display: flex; flex-direction: column; gap: 18px; }
.stats {
  display: grid;
  gap: 22px;
  padding: 26px 22px;
  border: 1px solid var(--line);
  border-left: 3px solid var(--accent);
  border-radius: var(--radius);
  background: var(--surface);
}
.stat-num {
  font-family: var(--mono);
  font-size: 1.9rem;
  font-weight: 700;
  color: var(--ink);
  font-variant-numeric: tabular-nums;
}
.stat-suffix { color: var(--accent); font-size: 0.55em; }
.stat-label { margin-top: 6px; font-size: 0.8rem; color: var(--ink-dim); }

.need-card {
  padding: 22px 20px;
  border: 1px solid rgba(45, 226, 166, 0.35);
  border-radius: var(--radius);
  background: rgba(45, 226, 166, 0.05);
}
.need-title { font-family: var(--mono); font-size: 0.68rem; letter-spacing: 0.2em; color: var(--accent); }
.need-text { margin-top: 10px; font-size: 0.95rem; color: var(--ink); line-height: 1.75; }

.gallery { margin-top: 64px; }
.gallery-grid { margin-top: 16px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }

.cta-row {
  margin-top: 70px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  flex-wrap: wrap;
  border: 1px solid rgba(45, 226, 166, 0.3);
  border-radius: 18px;
  padding: 40px 32px;
  background: rgba(45, 226, 166, 0.04);
}
.cta-text { font-size: 1.15rem; }

@media (max-width: 880px) {
  .detail-grid { grid-template-columns: 1fr; gap: 36px; }
  .detail-side { position: static; }
  .gallery-grid { grid-template-columns: 1fr; }
}
</style>
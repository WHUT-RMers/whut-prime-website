<script setup lang="ts">
import { ref } from 'vue'
import PageHeader from '../components/PageHeader.vue'
import PlaceholderImage from '../components/PlaceholderImage.vue'
import { useScrollReveal } from '../composables/useGsapReveal'
import { groups, groupRoute, type GroupInfo } from '../data/groups'
import { groupOverlay } from '../composables/useGroupOverlay'

const root = ref<HTMLElement | null>(null)
useScrollReveal(root, { stagger: 0.08 })

const deckStyle = (g: GroupInfo) => ({ '--deck-hue': String(g.hue) })

/** 左键单击弹出全屏详情浮层；修饰键/中键放行系统默认（新标签打开路由详情页） */
function onGroupClick(g: GroupInfo, e: MouseEvent) {
  if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) return
  e.preventDefault()
  groupOverlay.open(g)
}
</script>

<template>
  <div class="page">
    <div class="container">
      <PageHeader
        eyebrow="04 / 组别介绍"
        title="四大组别与技术栈"
        desc="一辆车从图纸到赛场，需要四双手。无论你擅长结构、代码、算法还是运营，PRIME 都有你的位置。"
      />
    </div>

    <div ref="root" class="container">
      <a
        v-for="(g, i) in groups"
        :key="g.code"
        :href="groupRoute(g.code)"
        class="group"
        :style="deckStyle(g)"
        data-reveal
        @click="onGroupClick(g, $event)"
      >
        <div class="group-media">
          <PlaceholderImage :label="g.image" ratio="4 / 3" accent />
        </div>
        <div class="group-body">
          <div class="group-head">
            <span class="group-index">{{ String(i + 1).padStart(2, '0') }}</span>
            <span class="group-code">{{ g.code }}</span>
            <span class="group-en">{{ g.en }}</span>
          </div>
          <h2 class="group-name">{{ g.name }}</h2>
          <p class="group-desc">{{ g.d }}</p>

          <div class="group-section">
            <p class="group-label">工作内容</p>
            <ul class="task-list">
              <li v-for="t in g.tasks" :key="t">{{ t }}</li>
            </ul>
          </div>

          <div class="group-section">
            <p class="group-label">技术栈</p>
            <div class="stack-list">
              <span v-for="s in g.stack" :key="s" class="stack-tag">{{ s }}</span>
            </div>
          </div>

          <p class="group-need"><span class="need-flag">招募</span>{{ g.need }}</p>
          <p class="group-more">查看组别详情 <span class="group-more-arrow" aria-hidden="true">→</span></p>
        </div>
      </a>

      <div class="cta-row" data-reveal>
        <p class="cta-text">找到属于你的组别了吗？</p>
        <RouterLink to="/recruit" class="btn btn-primary">投递简历 <span aria-hidden="true">→</span></RouterLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page { padding-bottom: 150px; }

.group {
  margin-top: 64px;
  display: grid;
  grid-template-columns: minmax(0, 5fr) minmax(0, 7fr);
  gap: 40px;
  align-items: center;
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: 34px;
  background: linear-gradient(160deg, rgba(255, 255, 255, 0.03), transparent 60%);
  transition: border-color 0.3s, background 0.3s, transform 0.35s var(--ease-expo);
}
.group:hover {
  border-color: hsl(var(--deck-hue, 158), 60%, 58%);
  background: linear-gradient(160deg, rgba(255, 255, 255, 0.05), transparent 60%);
  transform: translateY(-2px);
}
.group-media { min-width: 0; }

.group-head { display: flex; align-items: center; gap: 14px; }
.group-index { font-family: var(--mono); font-size: 0.85rem; color: var(--accent); letter-spacing: 0.1em; }
.group-code {
  font-family: var(--mono);
  font-size: 0.7rem;
  letter-spacing: 0.14em;
  color: var(--accent);
  border: 1px solid rgba(45, 226, 166, 0.4);
  border-radius: 6px;
  padding: 3px 8px;
}
.group-en { font-family: var(--mono); font-size: 0.6rem; letter-spacing: 0.14em; color: #5b6673; }

.group-name { margin-top: 16px; font-size: 1.7rem; }
.group-desc { margin-top: 12px; color: var(--ink-dim); font-size: 0.98rem; }

.group-section { margin-top: 22px; }
.group-label {
  font-family: var(--mono);
  font-size: 0.68rem;
  letter-spacing: 0.2em;
  color: var(--ink-dim);
}
.task-list { list-style: none; margin-top: 12px; display: flex; flex-wrap: wrap; gap: 10px; }
.task-list li {
  font-size: 0.86rem;
  color: var(--ink);
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 6px 14px;
  background: rgba(255, 255, 255, 0.02);
}
.stack-list { margin-top: 12px; display: flex; flex-wrap: wrap; gap: 8px; }
.stack-tag {
  font-family: var(--mono);
  font-size: 0.68rem;
  letter-spacing: 0.04em;
  padding: 4px 10px;
  border: 1px solid var(--line);
  border-radius: 999px;
  color: var(--ink-dim);
}

.group-need {
  margin-top: 22px;
  padding-top: 18px;
  border-top: 1px dashed var(--line);
  font-size: 0.9rem;
  color: var(--ink-dim);
}
.need-flag {
  font-family: var(--mono);
  font-size: 0.66rem;
  letter-spacing: 0.1em;
  color: var(--accent-ink);
  background: var(--accent);
  border-radius: 5px;
  padding: 2px 8px;
  margin-right: 10px;
}

/* 整卡可点：底部给出跳转暗示 */
.group-more {
  margin-top: 22px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-family: var(--mono);
  font-size: 0.72rem;
  letter-spacing: 0.18em;
  color: var(--accent);
}
.group-more-arrow { transition: transform 0.35s var(--ease-expo); }
.group:hover .group-more-arrow { transform: translateX(5px); }

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
  .group { grid-template-columns: 1fr; padding: 24px; gap: 24px; }
  .group-media { max-width: 520px; }
}
</style>

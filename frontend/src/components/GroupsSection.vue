<script setup lang="ts">
import { ref } from 'vue'
import PlaceholderImage from './PlaceholderImage.vue'
import { useScrollReveal } from '../composables/useGsapReveal'
import { useMouseFx } from '../composables/useMouseFx'
import { groups, groupRoute, type GroupInfo } from '../data/groups'
import { groupOverlay } from '../composables/useGroupOverlay'

/**
 * 03 技术组别：四个组按 2×2 排列（≤860px 收成单列）。
 * 卡片结构参照 wute.club 的技术组别卡片——上图 + 组名 + 一句话，
 * 额外保留我们的组别代码、技术栈标签与招募提示。
 * 图片为占位：素材到位后把 <PlaceholderImage> 换成 <img src="/static/groups/xxx.jpg" /> 即可。
 */
const root = ref<HTMLElement | null>(null)
useScrollReveal(root, { blur: 4, stagger: 0.09 })
useMouseFx(root)

const deckStyle = (g: GroupInfo) => ({ '--deck-hue': String(g.hue) })

/** 左键单击弹出全屏详情浮层；修饰键/中键放行系统默认（新标签打开路由详情页） */
function onCardClick(g: GroupInfo, e: MouseEvent) {
  if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) return
  e.preventDefault()
  groupOverlay.open(g)
}
</script>

<template>
  <section id="groups" ref="root" class="groups">
    <div class="container">
      <header class="groups-head">
        <p class="eyebrow" data-reveal>03 / 技术组别</p>
        <h2 class="groups-title" data-reveal>四大组别与技术栈</h2>
        <p class="groups-lead" data-reveal>一个机器人从图纸到赛场，需要四双手。</p>
      </header>

      <div class="group-grid">
        <a
          v-for="(g, i) in groups"
          :key="g.code"
          :href="groupRoute(g.code)"
          class="group-card"
          :style="deckStyle(g)"
          data-reveal
          data-tilt
          data-spot
          @click="onCardClick(g, $event)"
        >
          <div class="card-media">
            <PlaceholderImage :label="g.image" ratio="16 / 9" />
            <span class="card-no" aria-hidden="true">{{ String(i + 1).padStart(2, '0') }}</span>
          </div>

          <div class="card-body">
            <div class="card-top">
              <span class="card-code">{{ g.code }}</span>
              <span class="card-en">{{ g.en }}</span>
              <span class="card-go">组别详情 <i aria-hidden="true">→</i></span>
            </div>
            <h3 class="card-name">{{ g.name }}</h3>
            <p class="card-desc">{{ g.d }}</p>
            <div class="card-stack">
              <span v-for="s in g.stack" :key="s" class="stack-tag">{{ s }}</span>
            </div>
            <p class="card-need"><span class="need-flag">招募</span>{{ g.need }}</p>
          </div>
        </a>
      </div>
    </div>
  </section>
</template>

<style scoped>
.groups { padding: 0 0 var(--section-space); }
.groups-title { margin-top: 22px; font-size: clamp(1.9rem, 4vw, 3.1rem); }
.groups-lead { margin-top: 14px; color: var(--ink-dim); }

/* ---------- 四组 2×2 ---------- */
.group-grid {
  margin-top: clamp(38px, 5vw, 54px);
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: clamp(16px, 2.2vw, 26px);
}
.group-card {
  position: relative;
  display: flex;
  flex-direction: column;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--surface);
  overflow: hidden;
  transform-style: preserve-3d;
  transition: border-color 0.3s, background 0.3s, transform 0.35s var(--ease-expo);
}
.group-card:hover {
  border-color: hsl(var(--deck-hue, 158), 70%, 60%);
  background: var(--surface-2);
  transform: translateY(-5px);
}

.card-media { position: relative; border-bottom: 1px solid var(--line); }
.card-no {
  position: absolute;
  right: 16px;
  bottom: -14px;
  font-family: var(--display);
  font-size: clamp(3.2rem, 5vw, 4.6rem);
  line-height: 1;
  color: transparent;
  -webkit-text-stroke: 1px hsla(var(--deck-hue, 158), 80%, 70%, 0.25);
  user-select: none;
  pointer-events: none;
}

.card-body { display: flex; flex-direction: column; flex: 1; padding: clamp(20px, 2.4vw, 28px); }
.card-top { display: flex; align-items: center; gap: 12px; }
.card-code {
  font-family: var(--mono);
  font-size: 0.72rem;
  letter-spacing: 0.16em;
  color: hsl(var(--deck-hue, 158), 80%, 66%);
  border: 1px solid hsla(var(--deck-hue, 158), 65%, 60%, 0.4);
  border-radius: 6px;
  padding: 3px 10px;
}
.card-en { font-family: var(--mono); font-size: 0.6rem; letter-spacing: 0.14em; color: var(--ink-faint); }
.card-go {
  margin-left: auto;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-family: var(--mono);
  font-size: 0.66rem;
  letter-spacing: 0.14em;
  color: var(--accent);
  opacity: 0.7;
  transition: opacity 0.3s, transform 0.35s var(--ease-expo);
}
.card-go i { font-style: normal; transition: transform 0.35s var(--ease-expo); }
.group-card:hover .card-go { opacity: 1; }
.group-card:hover .card-go i { transform: translateX(4px); }

.card-name { margin-top: 18px; font-size: clamp(1.35rem, 2.2vw, 1.75rem); }
.card-desc { margin-top: 10px; font-size: 0.92rem; color: var(--ink-dim); }
.card-stack { margin-top: auto; padding-top: 20px; display: flex; flex-wrap: wrap; gap: 8px; }
.stack-tag {
  font-family: var(--mono);
  font-size: 0.68rem;
  letter-spacing: 0.04em;
  padding: 4px 10px;
  border: 1px solid var(--line);
  border-radius: 6px;
  color: var(--ink-dim);
  transition: border-color 0.25s, color 0.25s;
}
.stack-tag:hover { border-color: hsl(var(--deck-hue, 158), 70%, 62%); color: var(--ink); }
.card-need { margin-top: 16px; font-size: 0.86rem; color: var(--ink-dim); }
.need-flag {
  font-family: var(--mono);
  font-size: 0.66rem;
  letter-spacing: 0.1em;
  color: var(--accent-ink);
  background: var(--accent);
  border-radius: 4px;
  padding: 2px 8px;
  margin-right: 10px;
}

@media (max-width: 860px) {
  .group-grid { grid-template-columns: minmax(0, 1fr); }
}
</style>

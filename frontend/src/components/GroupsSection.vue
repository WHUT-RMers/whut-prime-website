<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { useScrollReveal } from '../composables/useGsapReveal'
import { useMouseFx } from '../composables/useMouseFx'
import { prefersReducedMotion } from '../utils/motion'

const root = ref<HTMLElement | null>(null)
const stage = ref<HTMLElement | null>(null)
const track = ref<HTMLElement | null>(null)
const prog = ref<HTMLElement | null>(null)

useScrollReveal(root, { selector: '[data-reveal]', blur: 4, stagger: 0.09 })
useMouseFx(root)

const groups = [
  {
    code: 'MEC', name: '机械组', en: 'MECHANICAL', hue: 158,
    d: '机器人结构设计与加工装配：云台、底盘、发射机构的机械美学。',
    stack: ['SolidWorks', 'ANSYS', '碳纤维加工', '3D 打印'],
    need: '懂公差，也懂暴力美学',
  },
  {
    code: 'ELC', name: '电控组', en: 'EMBEDDED CONTROL', hue: 208,
    d: '嵌入式系统设计与机器人决策：让每一度转角都有依据。',
    stack: ['STM32', 'FreeRTOS', 'CAN 总线', 'PID', '射频前端'],
    need: '写过驱动，调过 PID',
  },
  {
    code: 'VIS', name: '视觉算法组', en: 'VISION & ALGORITHM', hue: 268,
    d: '机器视觉与自主导航：让机器人看见、判断、自主行动。',
    stack: ['C++', 'Python', 'OpenCV', '深度学习', 'SLAM / 自主导航'],
    need: '跑通过 Demo，更喜欢真枪实弹',
  },
  {
    code: 'COM', name: '商业运营组', en: 'COMMERCIAL & OPERATION', hue: 32,
    d: '赛事运营、商业赞助与媒体矩阵：让战队的战绩被看见。',
    stack: ['公众号 / 视频号', 'B 站 / 抖音', '平面设计', '项目管理'],
    need: '能写能剪，也能谈合作',
  },
]

const deckStyle = (g: (typeof groups)[number]) => ({ '--deck-hue': String(g.hue) })

let mm: gsap.MatchMedia | undefined

onMounted(() => {
  const el = root.value
  if (!el || prefersReducedMotion()) return

  mm = gsap.matchMedia()

  /* 桌面端：pin + scrub 横向穿行 */
  mm.add('(min-width: 1001px) and (prefers-reduced-motion: no-preference)', () => {
    const tr = track.value
    const st = stage.value
    const pb = prog.value
    if (!tr || !st) return

    const getDist = () => Math.max(0, tr.scrollWidth - window.innerWidth)

    gsap.to(tr, {
      x: () => -getDist(),
      ease: 'none',
      scrollTrigger: {
        trigger: st,
        start: 'top top',
        end: () => '+=' + getDist(),
        scrub: 1,
        pin: true,
        anticipatePin: 1,
        invalidateOnRefresh: true,
        onUpdate: (self) => {
          if (pb) gsap.set(pb, { scaleX: self.progress })
        },
      },
    })

    gsap.utils.toArray<HTMLElement>('.deck-num').forEach((num, i) => {
      gsap.fromTo(
        num,
        { xPercent: i % 2 ? 14 : -14 },
        {
          xPercent: i % 2 ? -14 : 14,
          ease: 'none',
          scrollTrigger: {
            trigger: num.closest('.group-deck'),
            start: 'left 115%',
            end: 'right -15%',
            scrub: 0.8,
          },
        },
      )
    })
  })

  mm.add('(max-width: 1000px)', () => undefined)
})

onBeforeUnmount(() => {
  mm?.revert()
  void ScrollTrigger
})
</script>

<template>
  <section id="groups" ref="root" class="groups">
    <div ref="stage" class="groups-stage">
      <header class="groups-head container">
        <p class="eyebrow" data-reveal>04 / 组别介绍</p>
        <h2 class="groups-title" data-reveal>四大组别与技术栈</h2>
        <p class="groups-lead" data-reveal>一辆车从图纸到赛场，需要四双手。</p>
        <p class="groups-hint" data-reveal aria-hidden="true">
          SCROLL <i class="hint-arrow">→</i> 横向穿行组别舱段
        </p>
      </header>

      <div ref="track" class="groups-track">
        <article
          v-for="(g, i) in groups"
          :key="g.code"
          class="group-deck"
          :style="deckStyle(g)"
          data-tilt
          data-spot
        >
          <span class="deck-num" aria-hidden="true">{{ String(i + 1).padStart(2, '0') }}</span>
          <div class="deck-top">
            <span class="deck-code">{{ g.code }}</span>
            <span class="deck-en">{{ g.en }}</span>
          </div>
          <h3 class="deck-name">{{ g.name }}</h3>
          <p class="deck-desc">{{ g.d }}</p>
          <div class="deck-stack">
            <span v-for="s in g.stack" :key="s" class="stack-tag">{{ s }}</span>
          </div>
          <p class="deck-need"><span class="need-flag">招募</span>{{ g.need }}</p>
        </article>

        <article class="group-end" data-tilt data-spot>
          <span class="end-num" aria-hidden="true">GO</span>
          <h3 class="end-title">找到你的组别</h3>
          <p class="end-desc">让热爱，变成赛季的注脚——四大组别开放投递。</p>
          <RouterLink to="/recruit" class="btn btn-primary" data-magnet>投递简历 <span aria-hidden="true">→</span></RouterLink>
        </article>
      </div>

      <div class="groups-progress container" aria-hidden="true">
        <div class="gp-track"><span ref="prog"></span></div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.groups-stage { position: relative; display: flex; flex-direction: column; overflow: hidden; }

.groups-head { padding-top: 110px; position: relative; z-index: 2; max-width: 760px; }
.groups-title { margin-top: 22px; font-size: clamp(1.9rem, 4vw, 3.1rem); }
.groups-lead { margin-top: 14px; color: var(--ink-dim); }
.groups-hint {
  margin-top: 22px;
  font-family: var(--mono);
  font-size: 0.66rem;
  letter-spacing: 0.28em;
  color: var(--accent);
  text-transform: uppercase;
  display: flex;
  align-items: center;
  gap: 10px;
}
.hint-arrow {
  font-style: normal;
  animation: flow-x 1.1s linear infinite;
  background: linear-gradient(90deg, var(--accent) 40%, transparent 40%) no-repeat;
  background-size: 9px 2px;
  background-position-y: center;
  width: 42px;
  height: 2px;
  display: inline-block;
  color: transparent;
}

/* ---------- 桌面：横向轨道 ---------- */
@media (min-width: 1001px) {
  .groups { padding-bottom: 0; }
  .groups-stage {
    height: calc(100vh - var(--nav-h));
    min-height: 640px;
    justify-content: center;
    gap: 34px;
  }
  .groups-head { padding-top: 0; }
  .groups-track {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 22px;
    padding: 0 max(24px, calc((100vw - var(--maxw)) / 2));
    width: max-content;
    will-change: transform;
  }
  .group-deck {
    position: relative;
    flex: 0 0 auto;
    width: min(500px, 44vw);
    height: min(420px, 52vh);
    padding: 34px 32px;
    border: 1px solid hsla(var(--deck-hue, 158), 55%, 62%, 0.35);
    border-radius: var(--radius);
    background: var(--surface);
    overflow: hidden;
    display: flex;
    flex-direction: column;
    transform-style: preserve-3d;
    transition: border-color 0.3s, background 0.3s;
  }
  .group-deck:hover { border-color: hsl(var(--deck-hue, 158), 75%, 62%); background: var(--surface-2); }
  .deck-num {
    position: absolute;
    right: 18px;
    top: -28px;
    font-family: var(--display);
    font-size: 9rem;
    line-height: 1;
    color: transparent;
    -webkit-text-stroke: 1px hsla(var(--deck-hue, 158), 80%, 70%, 0.22);
    user-select: none;
    pointer-events: none;
    will-change: transform;
  }
  .group-end {
    flex: 0 0 auto;
    width: min(460px, 40vw);
    height: min(420px, 52vh);
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: center;
    gap: 18px;
    padding: 40px;
    border: 1px solid var(--accent);
    border-radius: var(--radius);
    background: rgba(45, 226, 166, 0.06);
  }
  .group-end:hover { background: rgba(45, 226, 166, 0.12); }
  .end-num {
    font-family: var(--display);
    font-size: 4.6rem;
    line-height: 1;
    color: transparent;
    -webkit-text-stroke: 1px var(--accent);
  }
  .end-title { font-size: 1.9rem; }
  .end-desc { color: var(--ink-dim); max-width: 320px; }
  .groups-progress { padding-bottom: 44px; }
}

.deck-top { display: flex; align-items: center; gap: 14px; position: relative; }
.deck-code {
  font-family: var(--mono);
  font-size: 0.74rem;
  letter-spacing: 0.16em;
  color: hsl(var(--deck-hue, 158), 80%, 66%);
  border: 1px solid hsla(var(--deck-hue, 158), 65%, 60%, 0.4);
  border-radius: 6px;
  padding: 3px 10px;
}
.deck-en { font-family: var(--mono); font-size: 0.6rem; letter-spacing: 0.14em; color: var(--ink-faint); }
.deck-name { margin-top: 26px; font-size: 1.8rem; position: relative; }
.deck-desc { margin-top: 12px; font-size: 0.92rem; color: var(--ink-dim); position: relative; }
.deck-stack { margin-top: auto; padding-top: 18px; display: flex; flex-wrap: wrap; gap: 8px; position: relative; }
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
.deck-need { margin-top: 16px; font-size: 0.86rem; color: var(--ink-dim); position: relative; }
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

.groups-progress { position: relative; z-index: 2; }
.gp-track { height: 2px; background: var(--line); border-radius: 2px; overflow: hidden; }
.gp-track span {
  display: block;
  height: 100%;
  transform: scaleX(0);
  transform-origin: left;
  background: var(--accent);
}

/* ---------- 移动端：纵向堆叠 ---------- */
@media (max-width: 1000px) {
  .groups { padding-bottom: 0; }
  .groups-stage { padding: 90px 0 100px; gap: 26px; }
  .groups-track { display: grid; grid-template-columns: 1fr; gap: 14px; margin-top: 40px; }
  .group-deck {
    position: relative;
    padding: 26px 24px;
    border: 1px solid hsla(var(--deck-hue, 158), 55%, 62%, 0.35);
    border-radius: var(--radius);
    background: var(--surface);
    overflow: hidden;
  }
  .deck-num {
    position: absolute;
    right: 16px;
    top: -18px;
    font-family: var(--display);
    font-size: 5.6rem;
    color: transparent;
    -webkit-text-stroke: 1px hsla(var(--deck-hue, 158), 80%, 70%, 0.18);
    pointer-events: none;
  }
  .group-end {
    padding: 30px 24px;
    border: 1px solid var(--accent);
    border-radius: var(--radius);
    background: rgba(45, 226, 166, 0.06);
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 14px;
  }
  .end-title { font-size: 1.4rem; }
  .end-desc { color: var(--ink-dim); }
  .groups-progress { display: none; }
  .groups-hint { display: none; }
}
</style>

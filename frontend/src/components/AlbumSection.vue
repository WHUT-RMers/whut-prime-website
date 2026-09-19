<script setup lang="ts">
import { ref } from 'vue'
import PlaceholderImage from './PlaceholderImage.vue'
import { useScrollReveal } from '../composables/useGsapReveal'

/**
 * 04 战队相册（占位版）。
 * 实拍素材到位后，把每个 <PlaceholderImage> 换成 <img src="/static/album/xxx.jpg" /> 即可，
 * 槽位与栅格都不用动；需要增删照片就改 tiles 数组。
 */
const root = ref<HTMLElement | null>(null)
useScrollReveal(root, { stagger: 0.08, blur: 4 })

const tiles = [
  { label: '赛场实拍 · 对抗区', ratio: '16 / 9' },
  { label: '备赛调试 · 基地', ratio: '16 / 9' },
  { label: '全队合影', ratio: '4 / 3' },
  { label: '荣誉时刻', ratio: '4 / 3' },
  { label: '幕后花絮', ratio: '4 / 3' },
]
</script>

<template>
  <section id="album" ref="root" class="album">
    <div class="container">
      <p class="eyebrow" data-reveal>04 / 战队相册</p>
      <h2 class="album-title" data-reveal>战队影像</h2>
      <p class="album-lead" data-reveal>
        相册按「赛场 · 备赛 · 合影 · 荣誉」分类整理中，实拍素材到位后逐张替换下方占位。
      </p>

      <div class="album-grid">
        <div
          v-for="(t, i) in tiles"
          :key="t.label"
          class="album-cell"
          :class="'cell-' + (i + 1)"
          data-reveal
        >
          <PlaceholderImage :label="t.label" :ratio="t.ratio" />
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.album { padding: 0 0 var(--section-space); }
.album-title { margin-top: 22px; font-size: clamp(1.9rem, 4vw, 3.1rem); }
.album-lead {
  margin-top: 18px;
  max-width: 620px;
  color: var(--ink-dim);
  text-wrap: pretty;
}

.album-grid {
  margin-top: clamp(38px, 5vw, 54px);
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: clamp(14px, 2vw, 18px);
}
.album-cell { min-width: 0; }
/* 首行两张 16/9 大图，次行三张 4/3 小图 */
.cell-1,
.cell-2 { grid-column: span 3; }
.cell-3,
.cell-4,
.cell-5 { grid-column: span 2; }

@media (max-width: 900px) {
  .album-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .cell-1,
  .cell-2,
  .cell-3,
  .cell-4,
  .cell-5 { grid-column: auto; }
}
@media (max-width: 560px) {
  .album-grid { grid-template-columns: minmax(0, 1fr); }
}
</style>

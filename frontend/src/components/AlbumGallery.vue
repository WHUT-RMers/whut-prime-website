<script setup lang="ts">
import { ref } from 'vue'
import PlaceholderImage from './PlaceholderImage.vue'
import { useScrollReveal } from '../composables/useGsapReveal'

/**
 * 相册占位栅格：首页 04 战队相册与 /album 页面共用。
 * 实拍素材到位后，把每个 <PlaceholderImage> 换成 <img src="/static/album/xxx.jpg" /> 即可，
 * 槽位与栅格不用动；增删照片改 tiles 数组。
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
  <div ref="root" class="album-grid">
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
</template>

<style scoped>
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

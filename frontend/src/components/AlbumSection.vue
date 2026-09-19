<script setup lang="ts">
import { ref } from 'vue'
import AlbumGallery from './AlbumGallery.vue'
import { useScrollReveal } from '../composables/useGsapReveal'

/** 04 战队相册：只负责标题区入场，占位栅格的入场由 AlbumGallery 自己管 */
const root = ref<HTMLElement | null>(null)
useScrollReveal(root, { stagger: 0.08, blur: 4, selector: '.album-head [data-reveal]' })
</script>

<template>
  <section id="album" ref="root" class="album">
    <div class="container">
      <div class="album-head">
        <p class="eyebrow" data-reveal>04 / 战队相册</p>
        <h2 class="album-title" data-reveal>战队影像</h2>
        <p class="album-lead" data-reveal>
          相册按「赛场 · 备赛 · 合影 · 荣誉」分类整理中，实拍素材到位后逐张替换下方占位。
        </p>
      </div>
      <AlbumGallery />
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
</style>

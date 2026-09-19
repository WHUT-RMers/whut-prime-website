<script setup lang="ts">
import PageHeader from '../components/PageHeader.vue'
import AlbumGallery from '../components/AlbumGallery.vue'
</script>

<template>
  <div class="page">
    <div class="container">
      <PageHeader
        eyebrow="04 / 战队相册"
        title="战队影像"
        desc="赛场、备赛、合影与荣誉时刻。相册整理中，实拍素材到位后逐张替换下方占位。"
      />
      <AlbumGallery />
    </div>
  </div>
</template>

<style scoped>
.page { padding-bottom: var(--section-space); }
</style>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

type CoverImage = { id: number; caption: string; url: string }

const props = withDefaults(defineProps<{
  images: CoverImage[]
  title: string
  imageFocus?: string
  interval?: number
}>(), { imageFocus: 'center', interval: 5000 })

const active = ref(0)
let timer: number | undefined

function stop() {
  if (timer !== undefined) window.clearInterval(timer)
  timer = undefined
}

function start() {
  stop()
  if (props.images.length < 2 || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
  timer = window.setInterval(() => { active.value = (active.value + 1) % props.images.length }, props.interval)
}

watch(() => props.images, () => { active.value = 0; start() }, { deep: true })
onMounted(start)
onBeforeUnmount(stop)
</script>

<template>
  <div class="news-cover-carousel" @mouseenter="stop" @mouseleave="start">
    <img v-for="(image, index) in images" :key="image.id" :src="image.url" :alt="index === active ? (image.caption || title) : ''" :aria-hidden="index === active ? undefined : 'true'" :class="{ active: index === active }" :style="{ objectPosition: imageFocus }" />
    <span v-if="images.length > 1" class="counter" aria-hidden="true">{{ active + 1 }} / {{ images.length }}</span>
  </div>
</template>

<style scoped>
.news-cover-carousel{position:relative;width:100%;height:100%;overflow:hidden;background:var(--surface-2,#0d1018)}
.news-cover-carousel img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:0;transform:scale(1.015);transition:opacity .65s ease,transform 5s linear;will-change:opacity,transform}
.news-cover-carousel img.active{opacity:1;transform:scale(1.06)}
.counter{position:absolute;right:11px;bottom:10px;padding:3px 7px;border:1px solid rgba(255,255,255,.22);background:rgba(6,7,13,.72);color:var(--ink);font:600 .62rem var(--mono);letter-spacing:.08em;pointer-events:none}
@media (hover:hover) and (pointer:fine){.news-cover-carousel:hover img.active{transform:scale(1.11)}}
@media (prefers-reduced-motion:reduce){.news-cover-carousel img{transition:none;transform:none}.news-cover-carousel img.active{transform:none}}
</style>

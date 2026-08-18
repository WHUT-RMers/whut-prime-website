<script setup lang="ts">
/**
 * 图片占位组件：正式素材到位前先用它占位。
 * 替换方式：把 <PlaceholderImage label="..." /> 换成 <img src="/assets/xxx.jpg" /> 即可。
 */
withDefaults(
  defineProps<{
    label: string
    /** 宽高比，如 '4 / 3'、'16 / 9' */
    ratio?: string
    /** 是否强调（accent 调） */
    accent?: boolean
  }>(),
  { ratio: '4 / 3', accent: false },
)
</script>

<template>
  <div
    class="ph"
    :class="{ accent }"
    :style="{ aspectRatio: ratio }"
    role="img"
    :aria-label="'图片占位：' + label"
  >
    <svg class="ph-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true">
      <path d="M3 7a2 2 0 0 1 2-2h2l1.5-2h7L17 5h2a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7z" />
      <circle cx="12" cy="12.5" r="3.6" />
    </svg>
    <span class="ph-label">{{ label }}</span>
    <span class="ph-note">PHOTO PLACEHOLDER</span>
  </div>
</template>

<style scoped>
.ph {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  width: 100%;
  border: 1px dashed var(--line);
  border-radius: var(--radius);
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.025) 25%, transparent 25%) 0 0 / 22px 22px,
    linear-gradient(315deg, rgba(255, 255, 255, 0.025) 25%, transparent 25%) 0 0 / 22px 22px,
    var(--bg-soft);
  color: var(--ink-faint, #5b6673);
  overflow: hidden;
}
.ph.accent {
  background:
    linear-gradient(135deg, rgba(45, 226, 166, 0.06) 25%, transparent 25%) 0 0 / 22px 22px,
    linear-gradient(315deg, rgba(45, 226, 166, 0.06) 25%, transparent 25%) 0 0 / 22px 22px,
    var(--bg-soft);
}
.ph-icon { width: 34px; height: 34px; opacity: 0.55; }
.ph-label {
  font-family: var(--mono);
  font-size: 0.8rem;
  letter-spacing: 0.14em;
  color: var(--ink-dim);
}
.ph-note {
  font-family: var(--mono);
  font-size: 0.58rem;
  letter-spacing: 0.3em;
  opacity: 0.5;
}
</style>
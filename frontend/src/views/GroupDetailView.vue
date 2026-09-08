<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import GroupDetailContent from '../components/GroupDetailContent.vue'
import { useScrollReveal } from '../composables/useGsapReveal'
import { groupByCode } from '../data/groups'

/** 组别详情路由页：直接访问 /groups/mec 等链接时使用（入口交互走全屏浮层） */

const route = useRoute()
const root = ref<HTMLElement | null>(null)
useScrollReveal(root, { blur: 6, stagger: 0.08 })

const group = computed(() => groupByCode((route.params.code as string) ?? ''))
</script>

<template>
  <div class="page">
    <div class="container">
      <template v-if="group">
        <div ref="root">
          <p class="crumb" data-reveal>
            <RouterLink to="/groups" class="crumb-link">← 返回组别介绍</RouterLink>
          </p>
        </div>
        <GroupDetailContent :key="group.code" :group="group" />
      </template>

      <div v-else class="notfound">
        <p class="eyebrow">404 / 组别</p>
        <h1 class="nf-title">没有找到这个组别</h1>
        <p class="nf-desc">链接可能已失效，返回组别介绍看看其他组吧。</p>
        <RouterLink to="/groups" class="btn btn-ghost">返回组别介绍</RouterLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page { padding-bottom: 150px; }

.crumb { margin-top: 28px; }
.crumb-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-family: var(--mono);
  font-size: 0.72rem;
  letter-spacing: 0.18em;
  color: var(--ink-dim);
  transition: color 0.25s, transform 0.3s var(--ease-expo);
}
.crumb-link:hover { color: var(--accent); transform: translateX(-3px); }

.notfound { padding: 120px 0 60px; display: flex; flex-direction: column; align-items: flex-start; gap: 18px; }
.nf-title { font-size: 2rem; }
.nf-desc { color: var(--ink-dim); }
</style>
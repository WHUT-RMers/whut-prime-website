import { ref } from 'vue'
import type { GroupInfo } from '../data/groups'

/**
 * 组别详情浮层（全屏弹出页）的单一状态源。
 * 首页 04 板块与组别列表页的卡片点击都会 open 到这里，
 * GroupOverlay.vue 监听 group 渲染全屏浮层；关闭后底层页面滚动位置天然保留。
 */
const group = ref<GroupInfo | null>(null)

function open(g: GroupInfo) {
  group.value = g
}

function close() {
  group.value = null
}

export const groupOverlay = { group, open, close }
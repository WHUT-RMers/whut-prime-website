import { ref, type Ref } from 'vue'

export type Theme = 'dark' | 'light'

const STORAGE_KEY = 'whut-prime-theme'

/** 写入 <html data-theme>，供全站 CSS 变量切换 */
export function applyTheme(theme: Theme): void {
  document.documentElement.setAttribute('data-theme', theme)
}

/**
 * 顶栏主题开关：
 * - 默认深色（index.html 内联防闪烁脚本同样以 dark 兜底）
 * - 点击后写入 localStorage，之后固定为用户选择
 */
export function useTheme(): { theme: Ref<Theme>; toggle: () => void } {
  const theme = ref<Theme>(
    document.documentElement.getAttribute('data-theme') === 'light' ? 'light' : 'dark',
  )

  function toggle(): void {
    const next: Theme = theme.value === 'dark' ? 'light' : 'dark'
    theme.value = next
    applyTheme(next)
    try {
      localStorage.setItem(STORAGE_KEY, next)
    } catch {
      /* 隐私模式下忽略 */
    }
  }

  return { theme, toggle }
}

import { ref, type Ref } from 'vue'

export type Theme = 'dark' | 'light'

const STORAGE_KEY = 'whut-prime-theme'

export function systemTheme(): Theme {
  return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark'
}

export function storedTheme(): Theme | null {
  try {
    const value = localStorage.getItem(STORAGE_KEY)
    return value === 'dark' || value === 'light' ? value : null
  } catch {
    return null
  }
}

/** 写入 <html data-theme>，供全站 CSS 变量切换 */
export function applyTheme(theme: Theme): void {
  document.documentElement.setAttribute('data-theme', theme)
}

/**
 * 顶栏主题开关：
 * - 未手动设置过时跟随系统（prefers-color-scheme 变化自动切换）
 * - 点击后写入 localStorage，之后固定为用户选择
 */
export function useTheme(): { theme: Ref<Theme>; toggle: () => void } {
  const theme = ref<Theme>(
    (document.documentElement.getAttribute('data-theme') as Theme) || systemTheme(),
  )
  const media = window.matchMedia('(prefers-color-scheme: light)')
  const onMediaChange = () => {
    if (storedTheme()) return
    const next = media.matches ? 'light' : 'dark'
    theme.value = next
    applyTheme(next)
  }
  media.addEventListener('change', onMediaChange)

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

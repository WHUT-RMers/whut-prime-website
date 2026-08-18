/** 单字符 HTML 转义 */
function escapeHtml(ch: string): string {
  if (ch === '&') return '&amp;'
  if (ch === '<') return '&lt;'
  if (ch === '>') return '&gt;'
  return ch
}

/**
 * 将文本拆成逐个 <span class="char"> 的 HTML，用于 GSAP 逐字动画。
 * 空格原样保留，避免粘连。
 */
export function charsHtml(text: string): string {
  return text
    .split('')
    .map((ch) => (ch === ' ' ? ' ' : `<span class="char">${escapeHtml(ch)}</span>`))
    .join('')
}

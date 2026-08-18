import { onBeforeUnmount, onMounted, type Ref } from 'vue'
import { gsap } from 'gsap'
import { prefersReducedMotion } from '../utils/motion'

interface FxTargets {
  tilt: HTMLElement[]
  spot: HTMLElement[]
  mag: HTMLElement[]
}

interface Engine {
  rx: gsap.QuickToFunc
  ry: gsap.QuickToFunc
  tx: gsap.QuickToFunc
  ty: gsap.QuickToFunc
}

/**
 * 鼠标互动引擎（桌面精细指针设备）：
 * - [data-tilt]    卡片跟随光标 3D 倾斜（rotationX / rotationY，带透视）
 * - [data-spot]    光标聚光斑（写入 --mx / --my，配合 CSS ::before 显示）
 * - [data-magnet]  磁吸按钮（向光标方向位移 ~6px，离开回弹）
 * 触摸设备 / 减弱动态用户自动跳过。
 */
export function useMouseFx(rootRef: Ref<HTMLElement | null>): void {
  let targets: FxTargets = { tilt: [], spot: [], mag: [] }
  let engines = new Map<HTMLElement, Engine>()
  let magnetHover = new Set<HTMLElement>()
  const rafId = { id: 0 }

  const onMove = (e: PointerEvent) => {
    if (rafId.id) return
    rafId.id = requestAnimationFrame(() => {
      rafId.id = 0
      for (const el of targets.tilt) {
        const r = el.getBoundingClientRect()
        const en = engines.get(el)
        if (!en) continue
        const inside =
          e.clientX >= r.left && e.clientX <= r.right &&
          e.clientY >= r.top && e.clientY <= r.bottom
        if (!inside) {
          en.rx(0)
          en.ry(0)
          continue
        }
        const px = (e.clientX - r.left) / r.width - 0.5
        const py = (e.clientY - r.top) / r.height - 0.5
        en.rx(py * -7)   // 俯仰
        en.ry(px * 9)    // 偏航（左右更灵敏）
      }
      for (const el of targets.spot) {
        const r = el.getBoundingClientRect()
        el.style.setProperty('--mx', `${Math.round(e.clientX - r.left)}px`)
        el.style.setProperty('--my', `${Math.round(e.clientY - r.top)}px`)
      }
      for (const el of targets.mag) {
        if (!magnetHover.has(el)) continue
        const r = el.getBoundingClientRect()
        const dx = e.clientX - (r.left + r.width / 2)
        const dy = e.clientY - (r.top + r.height / 2)
        const dist = Math.hypot(dx, dy)
        const pull = Math.min(1, 40 / Math.max(dist, 1))
        const en = engines.get(el)
        if (!en) continue
        en.tx(dx * 0.16 * pull)
        en.ty(dy * 0.16 * pull)
      }
    })
  }

  const onLeavePage = () => {
    for (const el of targets.tilt) {
      const en = engines.get(el)
      if (en) {
        en.rx(0)
        en.ry(0)
      }
    }
    for (const el of targets.mag) {
      const en = engines.get(el)
      if (en) {
        en.tx(0)
        en.ty(0)
      }
      magnetHover.delete(el)
    }
  }

  const onEnter = (e: PointerEvent) => {
    const el = (e.target as HTMLElement).closest?.('[data-magnet]') as HTMLElement | null
    if (el) magnetHover.add(el)
  }
  const onLeave = (e: PointerEvent) => {
    const el = (e.target as HTMLElement).closest?.('[data-magnet]') as HTMLElement | null
    if (el) {
      magnetHover.delete(el)
      const en = engines.get(el)
      if (en) {
        en.tx(0)
        en.ty(0)
      }
    }
  }



  onMounted(() => {
    const root = rootRef.value
    if (!root) return
    if (prefersReducedMotion()) return
    if (!window.matchMedia('(pointer: fine)').matches) return

    targets = {
      tilt: Array.from(root.querySelectorAll<HTMLElement>('[data-tilt]')),
      spot: Array.from(root.querySelectorAll<HTMLElement>('[data-spot]')),
      mag: Array.from(root.querySelectorAll<HTMLElement>('[data-magnet]')),
    }
    if (!targets.tilt.length && !targets.spot.length && !targets.mag.length) return

    for (const el of targets.tilt) {
      gsap.set(el, { transformPerspective: 900 })
      engines.set(el, {
        rx: gsap.quickTo(el, 'rotationX', { duration: 0.55, ease: 'power3.out' }),
        ry: gsap.quickTo(el, 'rotationY', { duration: 0.55, ease: 'power3.out' }),
        tx: gsap.quickTo(el, 'x', { duration: 0.45, ease: 'power3.out' }),
        ty: gsap.quickTo(el, 'y', { duration: 0.45, ease: 'power3.out' }),
      })
    }
    for (const el of targets.mag) {
      if (!engines.has(el)) {
        engines.set(el, {
          rx: gsap.quickTo(el, 'rotationX', { duration: 0.55, ease: 'power3.out' }),
          ry: gsap.quickTo(el, 'rotationY', { duration: 0.55, ease: 'power3.out' }),
          tx: gsap.quickTo(el, 'x', { duration: 0.45, ease: 'power3.out' }),
          ty: gsap.quickTo(el, 'y', { duration: 0.45, ease: 'power3.out' }),
        })
      }
    }

    root.addEventListener('pointermove', onMove, { passive: true })
    root.addEventListener('pointerenter', onEnter, { passive: true })
    root.addEventListener('pointerleave', onLeave, { passive: true })
    document.addEventListener('mouseleave', onLeavePage)
  })

  onBeforeUnmount(() => {
    const root = rootRef.value
    if (root) {
      root.removeEventListener('pointermove', onMove)
      root.removeEventListener('pointerenter', onEnter)
      root.removeEventListener('pointerleave', onLeave)
    }
    document.removeEventListener('mouseleave', onLeavePage)
    if (rafId.id) cancelAnimationFrame(rafId.id)
  })
}
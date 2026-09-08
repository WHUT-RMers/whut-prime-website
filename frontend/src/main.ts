import { createApp } from 'vue'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { ScrollToPlugin } from 'gsap/ScrollToPlugin'
import App from './App.vue'
import router from './router'
import './style.css'

gsap.registerPlugin(ScrollTrigger, ScrollToPlugin)

// 移动端 resize（如 iOS 地址栏折叠）不触发全量 refresh，避免布局抖动
ScrollTrigger.config({ ignoreMobileResize: true })

const app = createApp(App)
app.use(router)
app.mount('#app')

// 字体/资源加载后刷新 ScrollTrigger，确保 pin 与 scrub 距离精确
if (document.fonts?.ready) {
  document.fonts.ready.then(() => ScrollTrigger.refresh())
}
window.addEventListener('load', () => ScrollTrigger.refresh())

import { createApp } from 'vue'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import App from './App.vue'
import router from './router'
import './style.css'

gsap.registerPlugin(ScrollTrigger)

const app = createApp(App)
app.use(router)
app.mount('#app')

// 字体/资源加载后刷新 ScrollTrigger，确保 pin 与 scrub 距离精确
if (document.fonts?.ready) {
  document.fonts.ready.then(() => ScrollTrigger.refresh())
}
window.addEventListener('load', () => ScrollTrigger.refresh())

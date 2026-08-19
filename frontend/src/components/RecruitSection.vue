<script setup lang="ts">
import { ref } from 'vue'
import { useScrollReveal } from '../composables/useGsapReveal'

const root = ref<HTMLElement | null>(null)
useScrollReveal(root, { blur: 8, stagger: 0.07 })

</script>

<template>
  <section id="recruit" ref="root" class="recruit">
    <div class="container recruit-inner">
      <div class="recruit-intro" data-reveal>
        <p class="eyebrow">05 / 简历投递</p>
        <h2 class="recruit-title">加入 PRIME</h2>
        <p class="recruit-lead">
          每年九月初招新开启，春夏赛季开放补录。零基础没关系，
          我们只要求你肯学、能熬、爱折腾。
        </p>
        <ul class="recruit-list">
          <li><span class="li-k">基地</span> 马房山校区东院 · 自动化学院求实楼东附楼 102 室</li>
          <li><span class="li-k">通道</span>官网在线投递，提交后可由招新负责人统一审核</li>
          <li><span class="li-k">流程</span> 简历筛选 → 组内面试 → 试用期一个月</li>
        </ul>
      </div>

      <RouterLink to="/recruit" class="recruit-form" data-reveal>
        <p class="eyebrow">ONLINE / APPLY</p>
        <h3>在线投递通道</h3>
        <p class="form-lead">填写完整报名信息、上传 PDF 简历，并在提交前确认个人信息使用说明。</p>
        <span class="btn btn-primary submit-btn">前往投递 →</span>
      </RouterLink>
    </div>
  </section>
</template>

<style scoped>
.recruit { padding: 0 0 150px; }
.recruit-inner {
  display: grid;
  grid-template-columns: minmax(0, 5fr) minmax(0, 7fr);
  gap: 64px;
  align-items: start;
}
.recruit-title {
  margin-top: 22px;
  font-size: clamp(1.9rem, 4vw, 3.1rem);
}
.recruit-lead { margin-top: 18px; color: var(--ink-dim); max-width: 420px; }

.recruit-list { list-style: none; margin-top: 34px; display: flex; flex-direction: column; gap: 16px; }
.recruit-list li { font-size: 0.95rem; color: var(--ink-dim); transition: color 0.3s, transform 0.4s var(--ease-expo); }
.recruit-list li:hover { color: var(--ink); transform: translateX(6px); }
.li-k {
  font-family: var(--mono);
  font-size: 0.72rem;
  letter-spacing: 0.1em;
  color: var(--accent);
  border: 1px solid rgba(45, 226, 166, 0.35);
  border-radius: 6px;
  padding: 2px 9px;
  margin-right: 12px;
  background: rgba(45, 226, 166, 0.05);
}

.recruit-form {
  position: relative;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--surface);
  padding: 36px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
/* HUD 四角刻度 */
.recruit-form::before {
  content: "";
  position: absolute;
  inset: 10px;
  pointer-events: none;
  border-radius: 14px;
  background:
    linear-gradient(var(--accent), var(--accent)) left top / 18px 2px no-repeat,
    linear-gradient(var(--accent), var(--accent)) left top / 2px 18px no-repeat,
    linear-gradient(var(--accent), var(--accent)) right top / 18px 2px no-repeat,
    linear-gradient(var(--accent), var(--accent)) right top / 2px 18px no-repeat,
    linear-gradient(var(--accent), var(--accent)) left bottom / 18px 2px no-repeat,
    linear-gradient(var(--accent), var(--accent)) left bottom / 2px 18px no-repeat,
    linear-gradient(var(--accent), var(--accent)) right bottom / 18px 2px no-repeat,
    linear-gradient(var(--accent), var(--accent)) right bottom / 2px 18px no-repeat;
  opacity: 0.6;
}
.recruit-form h3 { margin-top: 22px; font-size: 1.6rem; }
.form-lead { margin-top: 14px; color: var(--ink-dim); max-width: 460px; }
.submit-btn { align-self: flex-start; margin-top: 4px; }
.submit-tip { font-size: 0.82rem; color: var(--accent); }

@media (max-width: 880px) {
  .recruit-inner { grid-template-columns: 1fr; gap: 48px; }
  .recruit { padding: 0 0 110px; }
}
</style>

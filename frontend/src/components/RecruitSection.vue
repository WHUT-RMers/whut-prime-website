<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useScrollReveal } from '../composables/useGsapReveal'

const root = ref<HTMLElement | null>(null)
useScrollReveal(root)

const form = reactive({
  name: '',
  contact: '',
  group: '',
  intro: '',
})

const submitted = ref(false)

function onSubmit() {
  // demo 版：仅做前端提示，后端接入后改为真实提交
  submitted.value = true
}

const groups = ['机械组', '电控组', '算法组', '运营组', '还没想好']
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
          <li><span class="li-k">基地</span> 南湖校区 · 大学生创业园</li>
          <li><span class="li-k">通道</span> 邮箱简历 + 问卷表二选一</li>
          <li><span class="li-k">流程</span> 简历筛选 → 组内面试 → 试用期一个月</li>
        </ul>
      </div>

      <form class="recruit-form" data-reveal @submit.prevent="onSubmit">
        <div class="field">
          <label for="r-name">姓名</label>
          <input id="r-name" v-model="form.name" type="text" placeholder="你的名字" required />
        </div>
        <div class="field">
          <label for="r-contact">联系方式</label>
          <input id="r-contact" v-model="form.contact" type="text" placeholder="邮箱或微信号" required />
        </div>
        <div class="field">
          <label for="r-group">意向组别</label>
          <select id="r-group" v-model="form.group" required>
            <option value="" disabled selected>请选择组别</option>
            <option v-for="g in groups" :key="g" :value="g">{{ g }}</option>
          </select>
        </div>
        <div class="field">
          <label for="r-intro">一句话介绍自己</label>
          <textarea id="r-intro" v-model="form.intro" rows="3" placeholder="做过什么项目 / 为什么想加入"></textarea>
        </div>
        <div class="field">
          <label>附件简历</label>
          <div class="file-note">demo 版暂未接入文件上传，请将简历发送至上方简历投递邮箱。</div>
        </div>

        <button class="btn btn-primary submit-btn" type="submit">
          {{ submitted ? '已收到（demo）' : '提交简历' }}
        </button>
        <p v-if="submitted" class="submit-tip" role="status">
          demo 版本仅做前端演示，简历不会真的提交；后端接入后这里会变为真实投递通道。
        </p>
      </form>
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
.recruit-list li { font-size: 0.95rem; color: var(--ink-dim); }
.li-k {
  font-family: var(--mono);
  font-size: 0.72rem;
  letter-spacing: 0.1em;
  color: var(--accent);
  border: 1px solid rgba(45, 226, 166, 0.35);
  border-radius: 6px;
  padding: 2px 9px;
  margin-right: 12px;
}

.recruit-form {
  border: 1px solid var(--line);
  border-radius: 16px;
  background: var(--bg-soft);
  padding: 34px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.field { display: flex; flex-direction: column; gap: 9px; }
.field label { font-size: 0.86rem; color: var(--ink-dim); }
.field input,
.field select,
.field textarea {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--line);
  border-radius: 10px;
  color: var(--ink);
  font-family: inherit;
  font-size: 0.94rem;
  padding: 12px 14px;
  transition: border-color 0.3s, background 0.3s;
}
.field input:focus,
.field select:focus,
.field textarea:focus {
  outline: none;
  border-color: var(--accent);
  background: rgba(45, 226, 166, 0.04);
}
.field input::placeholder,
.field textarea::placeholder { color: var(--ink-faint, #5b6673); }
.field select { appearance: none; cursor: pointer; }
.field select option { background: var(--bg-soft); color: var(--ink); }
.file-note {
  font-size: 0.82rem;
  color: var(--ink-dim);
  border: 1px dashed var(--line);
  border-radius: 10px;
  padding: 12px 14px;
}
.submit-btn { align-self: flex-start; margin-top: 4px; }
.submit-tip { font-size: 0.82rem; color: var(--accent); }

@media (max-width: 880px) {
  .recruit-inner { grid-template-columns: 1fr; gap: 48px; }
  .recruit { padding: 0 0 110px; }
}
</style>

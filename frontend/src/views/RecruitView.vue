<script setup lang="ts">
import { reactive, ref } from 'vue'
import PageHeader from '../components/PageHeader.vue'
import PlaceholderImage from '../components/PlaceholderImage.vue'
import { useScrollReveal } from '../composables/useGsapReveal'

const root = ref<HTMLElement | null>(null)
useScrollReveal(root, { stagger: 0.08 })

const steps = [
  { no: '01', t: '投递简历', d: '填写下方表单，或将简历发送至战队邮箱。', k: '邮箱 / 表单' },
  { no: '02', t: '简历筛选', d: '各组负责人根据方向与经历进行初筛。', k: '大约一周' },
  { no: '03', t: '组内面试', d: '与组长聊一聊你的项目、思路与热情。', k: '线上 / 线下' },
  { no: '04', t: '试用期', d: '一个月实战任务考察，双向选择。', k: '一个月' },
]

const form = reactive({ name: '', contact: '', group: '', intro: '' })
const submitted = ref(false)

function onSubmit() {
  submitted.value = true
}

const groups = ['机械组', '电控组', '视觉算法组', '商业运营组', '还没想好']

const faqs = [
  { q: '零基础可以加入吗？', a: '可以。机械、电控、视觉算法均开设新人任务与培训课程，我们更看重学习意愿与投入度。' },
  { q: '招新有时间限制吗？', a: '每年九月初正式开启大规模招新，春夏赛季面向全校开放补录，具体以战队公告为准。' },
  { q: '面试会问什么？', a: '主要围绕你的项目经历、解决问题的思路与学习计划，不要求面面俱到，诚实比完美更重要。' },
  { q: '可以同时报名多个组别吗？', a: '建议选择一个最想深入的组别；面试通过后若有交叉兴趣，也可以参与其他组别的技术活动。' },
]
</script>

<template>
  <div class="page">
    <div class="container">
      <PageHeader
        eyebrow="05 / 投递简历"
        title="加入 PRIME"
        desc="每年九月初招新开启，春夏赛季开放补录。零基础没关系，我们只要求你肯学、能熬、爱折腾。"
      />

      <div class="poster" data-reveal>
        <PlaceholderImage label="2027 赛季招新海报" ratio="21 / 9" accent />
      </div>

      <!-- 流程步骤 -->
      <div ref="root" class="steps">
        <div v-for="s in steps" :key="s.no" class="step" data-reveal>
          <span class="step-no">{{ s.no }}</span>
          <h3 class="step-title">{{ s.t }}</h3>
          <p class="step-desc">{{ s.d }}</p>
          <span class="step-key">{{ s.k }}</span>
        </div>
      </div>

      <!-- 表单与 FAQ -->
      <div class="lower">
        <form class="form-card" data-reveal @submit.prevent="onSubmit">
          <h3 class="card-title">在线投递</h3>
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
            <div class="file-note">demo 版暂未接入文件上传，请将简历发送至战队邮箱：whut_prime@foxmail.com</div>
          </div>
          <button class="btn btn-primary submit-btn" type="submit">
            {{ submitted ? '已收到（demo）' : '提交简历' }}
          </button>
          <p v-if="submitted" class="submit-tip" role="status">
            demo 版本仅做前端演示，简历不会真的提交；后端接入后这里会变为真实投递通道。
          </p>
        </form>

        <div class="faq-card" data-reveal>
          <h3 class="card-title">常见问题</h3>
          <div v-for="f in faqs" :key="f.q" class="faq-item">
            <p class="faq-q">{{ f.q }}</p>
            <p class="faq-a">{{ f.a }}</p>
          </div>
          <div class="faq-contact">
            <p class="fc-label">仍有疑问？</p>
            <a class="fc-mail" href="mailto:whut_prime@foxmail.com">whut_prime@foxmail.com</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page { padding-bottom: 150px; }

.poster { margin-top: 56px; }

.steps {
  margin-top: 64px;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}
.step {
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 24px 20px;
  background: linear-gradient(160deg, rgba(255, 255, 255, 0.03), transparent 60%);
}
.step-no { font-family: var(--mono); font-size: 0.8rem; color: var(--accent); letter-spacing: 0.1em; }
.step-title { margin-top: 12px; font-size: 1.15rem; }
.step-desc { margin-top: 10px; font-size: 0.86rem; color: var(--ink-dim); }
.step-key {
  display: inline-block;
  margin-top: 14px;
  font-family: var(--mono);
  font-size: 0.64rem;
  letter-spacing: 0.1em;
  color: var(--ink-dim);
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 3px 10px;
}

.lower {
  margin-top: 48px;
  display: grid;
  grid-template-columns: minmax(0, 7fr) minmax(0, 5fr);
  gap: 18px;
  align-items: start;
}
.form-card,
.faq-card {
  border: 1px solid var(--line);
  border-radius: 18px;
  background: var(--bg-soft);
  padding: 32px;
}
.card-title { font-size: 1.3rem; }

.form-card { display: flex; flex-direction: column; gap: 18px; }
.field { display: flex; flex-direction: column; gap: 8px; }
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
.field textarea::placeholder { color: #5b6673; }
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

.faq-card { display: flex; flex-direction: column; gap: 20px; }
.faq-item { padding-bottom: 16px; border-bottom: 1px solid var(--line); }
.faq-q { font-size: 0.98rem; font-weight: 600; }
.faq-a { margin-top: 8px; font-size: 0.88rem; color: var(--ink-dim); line-height: 1.7; }
.fc-label { font-family: var(--mono); font-size: 0.68rem; letter-spacing: 0.18em; color: var(--ink-dim); }
.fc-mail { margin-top: 8px; display: inline-block; font-family: var(--mono); font-size: 0.98rem; color: var(--accent); }

@media (max-width: 1000px) {
  .steps { grid-template-columns: repeat(2, 1fr); }
  .lower { grid-template-columns: 1fr; }
}
@media (max-width: 560px) {
  .steps { grid-template-columns: 1fr; }
}
</style>

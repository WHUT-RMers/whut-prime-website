<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import PageHeader from '../components/PageHeader.vue'
import { api } from '../api'

const open = ref(false)
const sending = ref(false)
const success = ref('')
const error = ref('')
const resume = ref<File | null>(null)
const form = reactive({
  name: '', qq: '', wechat: '', email: '', phone: '', college: '', major_class: '',
  groups: [] as string[], introduction: '', experience: '', availability: '', consent: false,
})
const groups = [['mechanical', '机械组'], ['electrical', '电控组'], ['algorithm', '算法组'], ['operations', '运营组']]

onMounted(async () => {
  try { open.value = (await api.recruitmentStatus()).is_open }
  catch { error.value = '暂时无法获取报名状态，请稍后重试。' }
})

function selectFile(event: Event) { resume.value = (event.target as HTMLInputElement).files?.[0] || null }

async function submit() {
  error.value = ''; success.value = ''
  if (!open.value) { error.value = '当前不在报名时间，暂不接收报名信息。'; return }
  if (!resume.value) { error.value = '请上传 PDF 简历。'; return }
  if (resume.value.type !== 'application/pdf' || resume.value.size > 10 * 1024 * 1024) { error.value = '请上传 10 MB 以内的 PDF 简历。'; return }
  sending.value = true
  const data = new FormData()
  Object.entries(form).forEach(([key, value]) => data.append(key, Array.isArray(value) ? JSON.stringify(value) : String(value)))
  data.set('intended_groups', JSON.stringify(form.groups)); data.append('resume', resume.value)
  try { const result = await api.apply(data); success.value = `投递成功，你的报名编号是 ${result.application_no}。请留意后续通知。` }
  catch (reason: any) { error.value = reason?.error || '提交失败，请检查填写内容后重试。' }
  finally { sending.value = false }
}
</script>

<template>
  <div class="page"><div class="container">
    <PageHeader eyebrow="05 / 投递简历" title="加入 PRIME" desc="每年九月初招新开启，春夏赛季开放补录。零基础没关系，我们只要你肯学、能熬、爱折腾。" />
    <div class="recruit-poster" aria-label="招新海报占位区域"><span class="poster-dot"></span><span class="poster-icon">▣</span><p>2027 赛季招新海报</p><small>PHOTO PLACEHOLDER</small></div>
    <div class="steps">
      <div><b>01</b><h3>投递简历</h3><p>填写下方表单，上传 PDF 简历。</p></div><div><b>02</b><h3>简历筛选</h3><p>各组负责人根据方向与经历初筛。</p></div><div><b>03</b><h3>组内面试</h3><p>聊一聊项目、思路与热情。</p></div><div><b>04</b><h3>试用期</h3><p>在实战任务中双向选择。</p></div>
    </div>
    <div class="apply-layout"><section class="form-card"><form @submit.prevent="submit">
      <div class="form-heading"><h2>在线投递</h2><p>提交前请确认信息真实；简历仅用于本次战队招新审核。</p></div>
      <div class="two"><label>姓名<input v-model="form.name" required maxlength="32" placeholder="你的姓名" /></label><label>学院<input v-model="form.college" required maxlength="80" placeholder="例如：自动化学院" /></label><label>专业与班级<input v-model="form.major_class" required maxlength="120" placeholder="例如：机械设计制造及其自动化 2301 班" /></label><label>每周可投入时间<input v-model="form.availability" required maxlength="80" placeholder="例如：每周 12 小时" /></label></div>
      <fieldset><legend>联系方式（以下四项均为必填）</legend><div class="two"><label>QQ<input v-model="form.qq" required maxlength="20" inputmode="numeric" placeholder="QQ 号码" /></label><label>微信<input v-model="form.wechat" required maxlength="80" placeholder="微信号" /></label><label>邮箱<input v-model="form.email" required type="email" placeholder="name@example.com" /></label><label>手机号码<input v-model="form.phone" required type="tel" maxlength="32" placeholder="常用手机号" /></label></div></fieldset>
      <fieldset><legend>意向组别（可多选）</legend><label v-for="group in groups" :key="group[0]" class="check"><input v-model="form.groups" type="checkbox" :value="group[0]" />{{ group[1] }}</label></fieldset>
      <label>自我介绍<textarea v-model="form.introduction" required rows="4" placeholder="为什么想加入 PRIME？你最想投入哪个方向？" /></label><label>项目或竞赛经历（选填）<textarea v-model="form.experience" rows="3" placeholder="可填写项目、竞赛、作品链接或相关经历。" /></label><label>PDF 简历（最大 10 MB）<input type="file" accept="application/pdf,.pdf" required @change="selectFile" /></label><label class="check consent"><input v-model="form.consent" type="checkbox" required />我同意战队仅为本次招新收集、使用以上个人信息。</label><button class="btn btn-primary" :disabled="sending">{{ sending ? '正在提交…' : '提交简历' }}</button><p v-if="error" class="error" role="alert">{{ error }}</p><p v-if="success" class="success">{{ success }}</p>
    </form></section>
    <aside class="faq-card">
      <h2>常见问题</h2>
      <article><h3>零基础可以加入吗？</h3><p>可以。机械、电控、视觉算法均开设新人任务与培训课程，我们更看重学习意愿与投入度。</p></article>
      <article><h3>招新有时间限制吗？</h3><p>每年九月初正式开启大规模招新，春夏赛季面向全校开放补录，具体以战队公告为准。</p></article>
      <article><h3>面试会问什么？</h3><p>主要围绕你的项目经历、解决问题的思路与学习计划，不要求面面俱到，诚实比完美更重要。</p></article>
      <article><h3>可以同时报名多个组别吗？</h3><p>可以。建议选择一个最想深入的组别；面试通过后若有交叉兴趣，也可以参与其他组别的技术活动。</p></article>
      <div class="faq-contact"><span>仍有疑问？</span><a href="mailto:whut_prime@foxmail.com">whut_prime@foxmail.com</a></div>
    </aside></div>
  </div></div>
</template>

<style scoped>
.page{padding-bottom:150px}.recruit-poster{height:min(42vw,520px);min-height:270px;margin-top:54px;border:1px solid var(--line);border-radius:14px;display:flex;flex-direction:column;align-items:center;justify-content:center;background:repeating-linear-gradient(135deg,#0b151a 0 18px,#081014 18px 36px);color:var(--ink-dim);position:relative;overflow:hidden}.recruit-poster::after{content:'';position:absolute;inset:0;background:radial-gradient(circle at 50% 50%,rgba(45,226,166,.09),transparent 36%)}.poster-dot{width:48px;height:48px;border:1px solid var(--ink-dim);border-radius:50%;position:relative;z-index:1}.poster-dot::after{content:'';position:absolute;inset:20px;border-radius:50%;background:var(--accent)}.poster-icon,.recruit-poster p,.recruit-poster small{z-index:1}.poster-icon{font-size:2rem;margin-top:12px;color:#526070}.recruit-poster p{margin-top:10px;letter-spacing:.12em}.recruit-poster small{margin-top:10px;font-family:var(--mono);letter-spacing:.2em;color:#526070}.steps{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-top:48px}.steps>div,.form-card,.faq-card{border:1px solid var(--line);background:var(--surface)}.steps>div{padding:24px;min-height:180px}.steps b{font:700 .75rem var(--mono);color:var(--accent)}.steps h3{margin-top:24px;font-size:1.25rem}.steps p,.form-heading p{margin-top:10px;color:var(--ink-dim);line-height:1.65}.apply-layout{display:grid;grid-template-columns:minmax(0,1.4fr) minmax(300px,.9fr);gap:26px;margin-top:56px;align-items:start}.form-card{padding:40px}.form-card form{display:flex;flex-direction:column;gap:22px}.form-heading h2,.faq-card h2{font-size:1.8rem}.two{display:grid;grid-template-columns:1fr 1fr;gap:16px}label{display:flex;flex-direction:column;gap:8px;color:var(--ink-dim);font-size:.9rem}input,textarea{box-sizing:border-box;width:100%;background:#090b10;color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:12px 14px;font:inherit}input:focus,textarea:focus{outline:none;border-color:var(--accent)}fieldset{border:1px solid var(--line);border-radius:8px;padding:20px;display:flex;gap:18px;flex-wrap:wrap}legend{padding:0 5px;color:var(--ink);font-weight:700}.check{display:flex;flex-direction:row;align-items:center;gap:8px;color:var(--ink)}.check input{width:auto;accent-color:var(--accent)}.consent{margin-top:2px}.error{color:var(--accent-warm)}.success{color:var(--accent)}button:disabled{opacity:.6;cursor:wait}.faq-card{position:sticky;top:104px;padding:34px}.faq-card article{padding:22px 0;border-bottom:1px solid var(--line)}.faq-card article h3{font-size:1.1rem}.faq-card article p{margin-top:10px;color:var(--ink-dim);line-height:1.7}.faq-contact{padding-top:24px;display:flex;flex-direction:column;gap:12px;color:var(--ink-dim)}.faq-contact a{color:var(--accent);font-size:1.05rem}@media(max-width:900px){.apply-layout{grid-template-columns:1fr}.faq-card{position:static;max-width:760px}.steps,.two{grid-template-columns:1fr 1fr}}@media(max-width:700px){.form-card{padding:24px}.recruit-poster{margin-top:36px}}@media(max-width:450px){.steps,.two{grid-template-columns:1fr}.page{padding-bottom:90px}.form-card{padding:18px}.steps>div{min-height:auto}.recruit-poster{min-height:220px}}
</style>

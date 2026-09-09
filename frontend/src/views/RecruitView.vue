<script setup lang="ts">
import { onMounted, onUnmounted, reactive, ref } from 'vue'
import PageHeader from '../components/PageHeader.vue'
import { api, type RecruitmentApplicationSummary } from '../api'

const open = ref(false)
const sending = ref(false)
const sendingCode = ref(false)
const emailVerificationRequired = ref(false)
const emailVerified = ref(false)
const emailHint = ref('')
const emailError = ref(false)
const resendSeconds = ref(0)
const pollingEmail = ref(false)
let resendTimer: ReturnType<typeof window.setInterval> | undefined
let verifyPoll: ReturnType<typeof window.setInterval> | undefined
let pollTicks = 0
const existingApplication = ref<RecruitmentApplicationSummary | null>(null)
const editingExisting = ref(false)
const success = ref('')
const error = ref('')
const attachments = ref<File[]>([])
const form = reactive({
  name: '', qq: '', wechat: '', email: '', phone: '', college: '', major_class: '',
  primary_choice: '', accepts_adjustment: false, second_choice: '', introduction: '', experience: '', availability: '', consent: false,
})
const groups = [['mechanical', '机械组'], ['electrical', '电控组'], ['algorithm', '算法组'], ['operations', '运营组']]

onMounted(async () => {
  try {
    const status = await api.recruitmentStatus()
    open.value = status.is_open
    emailVerificationRequired.value = status.email_verification_required
  }
  catch { error.value = '暂时无法获取报名状态，请稍后重试。' }
})

function selectFiles(event: Event) {
  const input = event.target as HTMLInputElement
  const selected = Array.from(input.files || [])
  const known = new Set(attachments.value.map((file) => `${file.name}-${file.size}-${file.lastModified}`))
  attachments.value.push(...selected.filter((file) => !known.has(`${file.name}-${file.size}-${file.lastModified}`)))
  // 保留最近一次选择的文件名，避免原生控件显示“未选择任何文件”；
  // 完整材料清单以下方列表为准，后续选择会继续追加。
}

function removeAttachment(index: number) { attachments.value.splice(index, 1) }

function formReadyForVerification() {
  const required = ['name', 'qq', 'wechat', 'email', 'phone', 'college', 'major_class', 'primary_choice', 'introduction', 'availability'] as const
  if (required.some((key) => !form[key]?.trim())) { error.value = '请先完整填写报名信息，再发送邮箱验证链接。'; return false }
  if (!editingExisting.value && !attachments.value.length) { error.value = '请至少上传一份报名材料。'; return false }
  if (!form.consent) { error.value = '请先同意个人信息使用说明。'; return false }
  if (form.accepts_adjustment && form.second_choice === form.primary_choice) { error.value = '第二志愿不能与第一志愿相同。'; return false }
  return true
}

function startResendCountdown(seconds = 60) {
  if (resendTimer) window.clearInterval(resendTimer)
  resendSeconds.value = seconds
  resendTimer = window.setInterval(() => {
    resendSeconds.value -= 1
    if (resendSeconds.value <= 0 && resendTimer) {
      window.clearInterval(resendTimer)
      resendTimer = undefined
    }
  }, 1000)
}

onUnmounted(() => {
  if (resendTimer) window.clearInterval(resendTimer)
  stopVerifyPoll()
})

/**
 * 邮件魔法链接流程：发送后轮询后端记录，链接被点击即自动识别为已验证，
 * 无需用户回到本站手动回填验证码。
 */
function stopVerifyPoll() {
  if (verifyPoll) { window.clearInterval(verifyPoll); verifyPoll = undefined }
  pollingEmail.value = false
}

async function checkEmailVerified() {
  pollTicks += 1
  if (pollTicks > 300) { stopVerifyPoll(); emailError.value = true; emailHint.value = '验证链接已过期，请重新发送。'; return }
  try {
    const status = await api.emailVerifyStatus(form.email)
    if (status.verified) {
      emailVerified.value = true
      emailHint.value = ''
      stopVerifyPoll()
      const result = await api.recruitmentApplicationStatus(form.email)
      existingApplication.value = result.application
      editingExisting.value = false
    }
  } catch { /* 轮询瞬时失败忽略，下一轮继续 */ }
}

function startVerifyPoll() {
  stopVerifyPoll()
  pollTicks = 0
  pollingEmail.value = true
  verifyPoll = window.setInterval(checkEmailVerified, 2000)
}

async function sendEmailCode() {
  error.value = ''; emailHint.value = ''; emailError.value = false; emailVerified.value = false
  if (!formReadyForVerification()) return
  sendingCode.value = true
  try {
    emailHint.value = (await api.sendRecruitmentEmailCode(form.email)).message
    startResendCountdown()
    startVerifyPoll()
  }
  catch (reason: any) {
    emailError.value = true
    emailHint.value = reason?.error || '验证链接发送失败，请稍后再试。'
    if (reason?.cooldown_seconds) startResendCountdown(reason.cooldown_seconds)
  }
  finally { sendingCode.value = false }
}

function startEditingExisting() {
  if (!existingApplication.value?.can_edit) return
  Object.assign(form, existingApplication.value.form)
  attachments.value = []
  editingExisting.value = true
  success.value = ''
  error.value = ''
}

async function submit() {
  error.value = ''; success.value = ''
  if (!open.value) { error.value = '当前不在报名时间，暂不接收报名信息。'; return }
  if (emailVerificationRequired.value && !emailVerified.value) { error.value = '请先完成邮箱验证。'; return }
  if (existingApplication.value && !editingExisting.value) { error.value = '该邮箱已有报名记录，请点击“修改报名信息”后再提交。'; return }
  if (!form.primary_choice) { error.value = '请选择第一志愿。'; return }
  if (form.accepts_adjustment && form.second_choice === form.primary_choice) { error.value = '第二志愿不能与第一志愿相同。'; return }
  if ((!existingApplication.value || !editingExisting.value) && !attachments.value.length) { error.value = '请至少上传一份报名材料。'; return }
  sending.value = true
  const data = new FormData()
  Object.entries(form).forEach(([key, value]) => data.append(key, Array.isArray(value) ? JSON.stringify(value) : String(value)))
  attachments.value.forEach((file) => data.append('attachments', file))
  try {
    if (existingApplication.value && editingExisting.value) {
      const result = await api.updateRecruitment(existingApplication.value.id, data)
      success.value = `${result.message} 报名编号：${result.application_no}。`
      editingExisting.value = false
      existingApplication.value = null
      emailVerified.value = false
    } else {
      const result = await api.apply(data)
      success.value = `投递成功，你的报名编号是 ${result.application_no}。请留意后续通知。`
    }
  }
  catch (reason: any) { error.value = reason?.error || '提交失败，请检查填写内容后重试。' }
  finally { sending.value = false }
}
</script>

<template>
  <div class="page"><div class="container">
    <PageHeader eyebrow="05 / 投递简历" title="加入 PRIME" desc="每年九月初招新开启，春夏赛季开放补录。零基础没关系，我们只要你肯学、能熬、爱折腾。" />
    <div class="recruit-poster" aria-label="招新海报占位区域"><span class="poster-dot"></span><span class="poster-icon">▣</span><p>2027 赛季招新海报</p><small>PHOTO PLACEHOLDER</small></div>
    <div class="steps">
      <div><b>01</b><h3>提交材料</h3><p>填写表单并上传至少一份报名材料。</p></div><div><b>02</b><h3>简历筛选</h3><p>各组负责人根据方向与经历初筛。</p></div><div><b>03</b><h3>组内面试</h3><p>聊一聊项目、思路与热情。</p></div><div><b>04</b><h3>试用期</h3><p>在实战任务中双向选择。</p></div>
    </div>
    <div class="apply-layout"><section class="form-card"><form @submit.prevent="submit">
      <div class="form-heading"><h2>在线投递</h2><p>提交前请确认信息真实；简历仅用于本次战队招新审核。</p></div>
      <div class="two"><label>姓名<input v-model="form.name" required maxlength="32" placeholder="你的姓名" /></label><label>学院<input v-model="form.college" required maxlength="80" placeholder="例如：自动化学院" /></label><label>专业与班级<input v-model="form.major_class" required maxlength="120" placeholder="例如：机械设计制造及其自动化 2301 班" /></label><label>每周可投入时间<input v-model="form.availability" required maxlength="80" placeholder="例如：每周 12 小时" /></label></div>
      <fieldset><legend>联系方式（以下四项均为必填）</legend><div class="two"><label>QQ<input v-model="form.qq" required maxlength="20" inputmode="numeric" placeholder="QQ 号码" /></label><label>微信<input v-model="form.wechat" required maxlength="80" placeholder="微信号" /></label><div class="email-cell"><label>邮箱<input v-model="form.email" required type="email" placeholder="name@example.com" @input="emailVerified = false; existingApplication = null; editingExisting = false; stopVerifyPoll()" /></label><button v-if="emailVerificationRequired" class="vp-btn" type="button" :disabled="sendingCode || resendSeconds > 0 || emailVerified" @click="sendEmailCode"><span v-if="emailVerified">✓ 邮箱已验证</span><span v-else-if="sendingCode">发送中…</span><span v-else-if="resendSeconds > 0">{{ resendSeconds }}s 后可重发</span><span v-else>发送邮箱验证链接</span></button><p class="vp-hint" :class="{ ok: emailVerified, err: emailError }"><template v-if="emailVerified">验证通过，可以提交报名了。</template><template v-else-if="pollingEmail">链接已发送至邮箱，点击邮件中的链接即可自动验证。</template><template v-else>{{ emailHint || '验证链接 10 分钟有效；点击后无需返回本站。' }}</template></p></div><label>手机号码<input v-model="form.phone" required type="tel" maxlength="32" placeholder="常用手机号" /></label></div></fieldset>
      <section v-if="existingApplication && !editingExisting" class="existing-application" aria-live="polite"><span>已完成身份验证</span><h3>你已经提交过报名</h3><dl><div><dt>报名编号</dt><dd>{{ existingApplication.application_no }}</dd></div><div><dt>第一志愿</dt><dd>{{ groups.find((group) => group[0] === existingApplication?.primary_choice)?.[1] }}</dd></div><div><dt>当前状态</dt><dd>{{ existingApplication.status }}</dd></div><div><dt>最后提交</dt><dd>{{ existingApplication.created_at }}</dd></div></dl><p v-if="existingApplication.can_edit">当前仍未审核，可在线修改 {{ 2 - existingApplication.modification_count }} 次；每次修改都会覆盖此前填写内容，并刷新最后提交时间。</p><p v-else>报名已进入处理流程，或修改次数已用完；如有问题请联系管理员。</p><button v-if="existingApplication.can_edit" type="button" class="btn btn-primary" @click="startEditingExisting">修改报名信息（剩余 {{ 2 - existingApplication.modification_count }} 次）</button></section>
      <template v-if="!existingApplication || editingExisting">
      <fieldset><legend>志愿与调剂</legend><p class="field-tip">第一志愿为唯一的优先投递方向。若选择服从调剂，可指定一个不同的第二志愿，或接受战队统筹安排。</p><label>第一志愿<select v-model="form.primary_choice" required><option value="" disabled>请选择最想加入的组别</option><option v-for="group in groups" :key="group[0]" :value="group[0]">{{ group[1] }}</option></select></label><label class="check"><input v-model="form.accepts_adjustment" type="checkbox" />我愿意服从组别调剂</label><label v-if="form.accepts_adjustment">第二志愿 / 调剂意向<select v-model="form.second_choice"><option value="">接受战队统筹安排</option><option v-for="group in groups.filter((group) => group[0] !== form.primary_choice)" :key="group[0]" :value="group[0]">{{ group[1] }}</option></select></label></fieldset>
      <label>自我介绍<textarea v-model="form.introduction" required rows="4" placeholder="为什么想加入 PRIME？你最想投入哪个方向？" /></label><label>项目或竞赛经历（选填）<textarea v-model="form.experience" rows="3" placeholder="可填写项目、竞赛、作品链接或相关经历。" /></label><section class="attachment-field"><span>报名材料（可多选，可分多次添加）</span><label class="file-picker"><input type="file" multiple accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.jpg,.jpeg,.png,.gif,.webp,.bmp,.txt,.md,.csv,.json,.mp4,.mov,.webm,.mp3,.wav,.m4a,.zip,.rar,.7z" @change="selectFiles" /><strong>＋ 选择文件并添加</strong></label><small>{{ editingExisting ? '原有附件会保留；可继续分批追加新材料。' : '至少上传一份材料；支持常见文档、表格、演示、图片、音视频、文本和压缩包。单个附件不超过 15 MB。' }}</small></section><ul v-if="attachments.length" class="file-list"><li v-for="(file, index) in attachments" :key="`${file.name}-${file.lastModified}`"><span>{{ file.name }}</span><button type="button" @click="removeAttachment(index)">移除</button></li></ul><label class="check consent"><input v-model="form.consent" type="checkbox" required />我同意战队仅为本次招新收集、使用以上个人信息。</label><button class="btn btn-primary" :disabled="sending">{{ sending ? '正在提交…' : editingExisting ? `确认修改（剩余 ${2 - (existingApplication?.modification_count || 0)} 次）` : '提交简历' }}</button><p v-if="error" class="error" role="alert">{{ error }}</p><p v-if="success" class="success">{{ success }}</p>
      </template>
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
.page{padding-bottom:var(--section-space)}.recruit-poster{height:300px;margin-top:40px;border:1px solid var(--line);border-radius:var(--radius);display:grid;place-items:center;align-content:center;background:repeating-linear-gradient(135deg,#0b151a 0 18px,#081014 18px 36px);color:var(--ink-dim)}.poster-icon{font-size:2rem;color:var(--accent)}.recruit-poster p{margin-top:10px}.recruit-poster small{margin-top:8px;font:12px var(--mono);letter-spacing:.16em}.steps{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-top:42px}.steps>div,.form-card,.faq-card{border:1px solid var(--line);border-radius:var(--radius);background:var(--surface)}.steps>div{padding:24px}.steps b{color:var(--accent);font:700 .75rem var(--mono)}.steps h3{margin-top:18px}.steps p,.form-heading p{margin-top:9px;color:var(--ink-dim);line-height:1.65}.apply-layout{display:grid;grid-template-columns:minmax(0,1.4fr) minmax(300px,.9fr);gap:28px;margin-top:52px;align-items:start}.form-card,.faq-card{padding:34px}.form-card form{display:flex;flex-direction:column;gap:22px}.two{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}label{display:flex;flex-direction:column;gap:8px;color:var(--ink-dim);font-size:.9rem}input,textarea,.form-card select{box-sizing:border-box;width:100%;min-height:50px;background:#090b10;color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:12px 14px;font:inherit}textarea{resize:vertical;line-height:1.7}input:focus,textarea:focus,.form-card select:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 3px rgba(45,226,166,.08)}input[type=file]{height:auto;padding:10px}fieldset{min-width:0;border:1px solid var(--line);border-radius:8px;padding:20px;display:flex;flex-direction:column;gap:14px}legend{padding:0 5px;color:var(--ink);font-weight:700}.field-tip,.file-list,.form-card small{margin:0;color:var(--ink-dim);font-size:.82rem;line-height:1.65}.file-list{color:var(--accent)}.check{min-height:30px;display:flex;flex-direction:row;align-items:center;gap:10px;color:var(--ink);cursor:pointer}.check input{flex:0 0 auto;width:18px;height:18px;min-height:0;accent-color:var(--accent)}.error{color:var(--accent-warm)}.success{color:var(--accent)}.faq-card{position:sticky;top:calc(var(--nav-h) + 24px)}.faq-card article{padding:20px 0;border-bottom:1px solid var(--line)}.faq-card article p{margin-top:9px;color:var(--ink-dim);line-height:1.7}.faq-contact{padding-top:22px;display:flex;flex-direction:column;gap:10px;color:var(--ink-dim)}.faq-contact a{color:var(--accent)}@media(max-width:980px){.apply-layout{grid-template-columns:1fr}.faq-card{position:static}.steps{grid-template-columns:1fr 1fr}}@media(max-width:620px){.two,.steps{grid-template-columns:1fr}.form-card,.faq-card{padding:22px}.recruit-poster{height:230px}}
</style>
<style scoped>
.email-cell{ display:flex; flex-direction:column; gap:8px; }
.vp-btn{
  box-sizing:border-box;
  min-height:50px; padding:0 18px;
  background:#090b10; color:var(--ink);
  border:1px solid var(--line); border-radius:8px;
  font:inherit; font-size:.9rem;
  cursor:pointer; transition:border-color .25s,color .25s;
}
.vp-btn:hover:not(:disabled){ border-color:var(--accent); color:var(--accent); }
.vp-btn:disabled{ opacity:.5; cursor:not-allowed; }
.vp-hint{ margin:0; font-size:.78rem; color:var(--ink-dim); line-height:1.55; }
.vp-hint.ok{ color:var(--accent); }
.vp-hint.err{ color:var(--accent-warm); }
.attachment-field{display:grid;gap:9px;color:var(--ink-dim);font-size:.9rem}.file-picker{position:relative;display:flex;align-items:center;justify-content:center;min-height:54px;border:1px dashed rgba(45,226,166,.45);border-radius:8px;background:rgba(45,226,166,.035);color:var(--accent);cursor:pointer;transition:.18s ease}.file-picker:hover{border-color:var(--accent);background:rgba(45,226,166,.08)}.file-picker input{position:absolute;inset:0;width:100%;min-height:0;opacity:0;cursor:pointer}.file-picker strong{font-size:.9rem}
.file-list{display:grid;gap:7px;padding:0;list-style:none}.file-list li{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:8px 10px;border:1px solid rgba(45,226,166,.18);border-radius:6px;background:rgba(45,226,166,.035)}.file-list span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.file-list button{border:0;background:transparent;color:var(--accent-warm);font:inherit;font-size:.78rem;cursor:pointer}
.existing-application{position:relative;overflow:hidden;padding:25px;border:1px solid rgba(45,226,166,.35);border-radius:10px;background:linear-gradient(135deg,rgba(45,226,166,.09),rgba(77,163,255,.045))}.existing-application:after{position:absolute;right:-35px;top:-52px;width:140px;height:140px;border:1px solid rgba(45,226,166,.34);border-radius:50%;content:""}.existing-application>span{color:var(--accent);font:700 .72rem var(--mono);letter-spacing:.12em}.existing-application h3{margin:9px 0 18px;font-size:1.35rem}.existing-application dl{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1px;margin:0;border:1px solid var(--line);background:var(--line)}.existing-application dl div{padding:12px 14px;background:#0a0d12}.existing-application dt{margin-bottom:4px;color:var(--ink-dim);font-size:.75rem}.existing-application dd{margin:0;color:var(--ink);font-weight:700}.existing-application p{margin:16px 0;color:var(--ink-dim);font-size:.84rem;line-height:1.7}.existing-application .btn{position:relative;z-index:1}
@media(max-width:620px){.existing-application dl{grid-template-columns:1fr}}
</style>

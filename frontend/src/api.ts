export interface NewsItem {
  slug: string
  title: string
  summary: string
  category: string
  cover_url: string
  cover_images: { id: number; caption: string; url: string }[]
  image_focus: string
  published_at: string | null
  is_pinned: boolean
  external_url: string
  view_count: number
}

export interface NewsDetail extends NewsItem {
  body: string
  previous: NewsItem | null
  next: NewsItem | null
}

const csrf = () => document.cookie.split('; ').find((item) => item.startsWith('csrftoken='))?.split('=')[1] || ''

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api/${path}`, { ...init, headers: { ...(init?.headers || {}), ...(init?.method === 'POST' ? { 'X-CSRFToken': csrf() } : {}) } })
  const data = await response.json().catch(() => ({}))
  if (!response.ok) throw data
  return data as T
}

export const api = {
  news: (params = '') => request<{ items: NewsItem[]; categories: string[] }>(`news/${params}`),
  article: (slug: string) => request<NewsDetail>(`news/${slug}/`),
  countView: (slug: string) => request<{ view_count: number }>(`news/${slug}/view/`, { method: 'POST' }),
  recruitmentStatus: () => request<{ is_open: boolean; notice: string; email_verification_required: boolean }>('recruitment/status/'),
  sendRecruitmentEmailCode: (email: string) => {
    const payload = new FormData(); payload.append('email', email)
    return request<{ message: string }>('recruitment/email-code/', { method: 'POST', body: payload })
  },
  emailVerifyStatus: (email: string) => {
    const payload = new FormData(); payload.append('email', email)
    return request<{ verified: boolean }>('recruitment/email-status/', { method: 'POST', body: payload })
  },
  recruitmentApplicationStatus: (email: string) => {
    const payload = new FormData(); payload.append('email', email)
    return request<{ exists: boolean; application: RecruitmentApplicationSummary | null }>('recruitment/application-status/', { method: 'POST', body: payload })
  },
  apply: (payload: FormData) => request<{ application_no: string }>('recruitment/applications/', { method: 'POST', body: payload }),
  updateRecruitment: (id: number, payload: FormData) => request<{ application_no: string; message: string }>(`recruitment/applications/${id}/update/`, { method: 'POST', body: payload }),
}

export interface RecruitmentApplicationSummary {
  id: number
  application_no: string
  primary_choice: string
  status: string
  created_at: string
  can_edit: boolean
  modification_count: number
  form: {
    name: string; qq: string; wechat: string; email: string; phone: string; college: string; major_class: string
    primary_choice: string; accepts_adjustment: boolean; second_choice: string; introduction: string; experience: string; availability: string; consent: boolean
  }
  attachments: string[]
}

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
  recruitmentStatus: () => request<{ is_open: boolean; notice: string }>('recruitment/status/'),
  apply: (payload: FormData) => request<{ application_no: string }>('recruitment/applications/', { method: 'POST', body: payload }),
}

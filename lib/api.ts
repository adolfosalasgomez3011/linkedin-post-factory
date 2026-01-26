const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface GeneratePostRequest {
  pillar: string
  format_type: string
  topic?: string
  provider?: string
}

export interface PostResponse {
  id: string
  pillar: string
  format: string
  topic: string
  text: string
  hashtags: string[]
  voice_score: number
  length: number
  created_at: string
  status: string
}

export const api = {
  async generatePost(data: GeneratePostRequest): Promise<PostResponse> {
    const res = await fetch(`${API_URL}/posts/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    if (!res.ok) throw new Error('Failed to generate post')
    return res.json()
  },

  async batchGenerate(count: number, pillar?: string): Promise<{ message: string; count: number }> {
    const res = await fetch(`${API_URL}/posts/batch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ count, pillar }),
    })
    if (!res.ok) throw new Error('Failed to batch generate')
    return res.json()
  },

  async checkVoice(text: string): Promise<{ score: number; grade: string; issues: string[] }> {
    const res = await fetch(`${API_URL}/posts/check-voice`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    })
    if (!res.ok) throw new Error('Failed to check voice')
    return res.json()
  },

  async getStats(): Promise<any> {
    const res = await fetch(`${API_URL}/stats`)
    if (!res.ok) throw new Error('Failed to get stats')
    return res.json()
  },

  async getDashboard(): Promise<any> {
    const res = await fetch(`${API_URL}/dashboard`)
    if (!res.ok) throw new Error('Failed to get dashboard')
    return res.json()
  },

  async getTrendingNews(category: string = 'technology', count: number = 10): Promise<any> {
    const res = await fetch(`${API_URL}/news/trending?category=${category}&count=${count}`)
    if (!res.ok) throw new Error('Failed to fetch trending news')
    return res.json()
  },
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface GeneratePostRequest {
  pillar: string
  post_type: string
  format_type: string
  topic?: string
  provider?: string
  news_article?: {
    title: string
    description: string
    url: string
    image_url?: string
    source: string
    published_at: string
    author?: string
  }
}

export interface PostResponse {
  id: string
  pillar: string
  format: string
  topic: string
  content: string  // API returns 'content', not 'text'
  text: string     // Keep for backward compatibility
  hashtags: string[]
  voice_score: number
  length: number
  created_at: string
  status: string
  carousel_url?: string  // PDF data URI for carousel posts
}

export const api = {
  async generatePost(data: GeneratePostRequest): Promise<PostResponse> {
    const res = await fetch(`${API_URL}/posts/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    if (!res.ok) {
      const errorText = await res.text()
      try {
        const errorJson = JSON.parse(errorText)
        throw new Error(errorJson.detail || 'Failed to generate post')
      } catch (e) {
        throw new Error(`Failed to generate post: ${errorText}`)
      }
    }
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
}

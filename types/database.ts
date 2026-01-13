export type Database = {
  public: {
    Tables: {
      posts: {
        Row: {
          id: string
          pillar: string
          format: string
          topic: string | null
          text: string
          hashtags: string | null
          created_at: string
          status: 'raw' | 'review' | 'approved' | 'scheduled' | 'posted'
          voice_score: number | null
          length: number | null
          media_urls: string[] | null
          media_type: 'code' | 'chart' | 'ai-image' | 'infographic' | 'carousel' | 'demo' | null
          demo_url: string | null
        }
        Insert: {
          id?: string
          pillar: string
          format: string
          topic?: string | null
          text: string
          hashtags?: string | null
          created_at?: string
          status?: 'raw' | 'review' | 'approved' | 'scheduled' | 'posted'
          voice_score?: number | null
          length?: number | null
          media_urls?: string[] | null
          media_type?: 'code' | 'chart' | 'ai-image' | 'infographic' | 'carousel' | 'demo' | null
          demo_url?: string | null
        }
        Update: {
          id?: string
          pillar?: string
          format?: string
          topic?: string | null
          text?: string
          hashtags?: string | null
          created_at?: string
          status?: 'raw' | 'review' | 'approved' | 'scheduled' | 'posted'
          voice_score?: number | null
          length?: number | null
          media_urls?: string[] | null
          media_type?: 'code' | 'chart' | 'ai-image' | 'infographic' | 'carousel' | 'demo' | null
          demo_url?: string | null
        }
      }
      engagement: {
        Row: {
          id: number
          post_id: string
          views: number
          likes: number
          comments: number
          shares: number
          engagement_rate: number | null
          updated_at: string
        }
      }
    }
  }
}

export type Post = Database['public']['Tables']['posts']['Row']
export type PostInsert = Database['public']['Tables']['posts']['Insert']
export type PostUpdate = Database['public']['Tables']['posts']['Update']
export type PostStatus = Post['status']

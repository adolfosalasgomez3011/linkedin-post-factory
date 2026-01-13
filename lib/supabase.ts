import { createClient } from '@supabase/supabase-js'
import type { Database, Post, PostInsert, PostUpdate, PostStatus } from '@/types/database'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient<Database>(supabaseUrl, supabaseKey)

// Post CRUD operations
export const postService = {
  // Get all posts
  async getPosts() {
    const { data, error } = await supabase
      .from('posts')
      .select('*')
      .order('created_at', { ascending: false })
    
    if (error) throw error
    return data
  },

  // Get posts by status
  async getPostsByStatus(status: PostStatus) {
    const { data, error } = await supabase
      .from('posts')
      .select('*')
      .eq('status', status)
      .order('created_at', { ascending: false })
    
    if (error) throw error
    return data
  },

  // Get posts by pillar
  async getPostsByPillar(pillar: string) {
    const { data, error } = await supabase
      .from('posts')
      .select('*')
      .eq('pillar', pillar)
      .order('created_at', { ascending: false })
    
    if (error) throw error
    return data
  },

  // Get single post
  async getPost(id: string) {
    const { data, error } = await supabase
      .from('posts')
      .select('*')
      .eq('id', id)
      .single()
    
    if (error) throw error
    return data
  },

  // Create post
  async createPost(post: PostInsert) {
    const { data, error } = await supabase
      .from('posts')
      .insert(post as any)
      .select()
      .single()
    
    if (error) throw error
    return data
  },

  // Update post
  async updatePost(id: string, updates: PostUpdate) {
    const { data, error } = await (supabase
      .from('posts') as any)
      .update(updates)
      .eq('id', id)
      .select()
      .single()
    
    if (error) throw error
    return data
  },

  // Update post status
  async updatePostStatus(id: string, status: PostStatus) {
    const { data, error } = await (supabase
      .from('posts') as any)
      .update({ status })
      .eq('id', id)
      .select()
      .single()
    
    if (error) throw error
    return data
  },

  // Delete post
  async deletePost(id: string) {
    const { error } = await supabase
      .from('posts')
      .delete()
      .eq('id', id)
    
    if (error) throw error
  },

  // Search posts
  async searchPosts(query: string) {
    const { data, error } = await supabase
      .from('posts')
      .select('*')
      .or(`text.ilike.%${query}%,topic.ilike.%${query}%,pillar.ilike.%${query}%`)
      .order('created_at', { ascending: false })
    
    if (error) throw error
    return data
  },

  // Get stats
  async getStats() {
    const { data: posts, error } = await supabase
      .from('posts')
      .select('status, voice_score')

    if (error) throw error

    const total = posts?.length || 0
    const byStatus = (posts || []).reduce((acc, post) => {
      acc[(post as any).status] = (acc[(post as any).status] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    const avgVoiceScore = (posts || [])
      .filter(p => (p as any).voice_score !== null)
      .reduce((acc, p) => acc + ((p as any).voice_score || 0), 0) / (posts || []).filter(p => (p as any).voice_score !== null).length || 0

    return {
      total,
      byStatus,
      avgVoiceScore
    }
  }
}

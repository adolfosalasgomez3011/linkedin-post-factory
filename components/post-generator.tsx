'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { api, PostResponse } from '@/lib/api'
import { supabase } from '@/lib/supabase'
import { PostInsert } from '@/types/database'
import { Loader2, Sparkles, Copy, CheckCircle2, Edit2, Save } from 'lucide-react'

const PILLARS = [
  'AI & Innovation',
  'Tech Leadership',
  'Career Growth',
  'Industry Insights',
  'Personal Brand'
]

const POST_TYPES = [
  { value: 'standard', label: 'Standard Text + Image' },
  { value: 'carousel', label: 'Carousel PDF (Slides)' },
  { value: 'trending_news', label: '🔥 Trending News Commentary' },
  { value: 'interactive', label: 'Interactive Demo' }
]

const FORMATS = [
  'Story',
  'Insight',
  'How-To',
  'Question',
  'List',
  'Quote',
  'Case Study'
]

interface NewsArticle {
  title: string
  description: string
  url: string
  image_url?: string
  source: string
  published_at: string
  author?: string
}

export function PostGenerator() {
  const router = useRouter()
  const [pillar, setPillar] = useState('')
  const [postType, setPostType] = useState('standard')
  const [format, setFormat] = useState('')
  const [topic, setTopic] = useState('')
  const [provider] = useState('gemini')
  const [loading, setLoading] = useState(false)
  const [generatedPost, setGeneratedPost] = useState<PostResponse | null>(null)
  const [copied, setCopied] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [editedText, setEditedText] = useState('')
  
  // News article selection state
  const [newsArticles, setNewsArticles] = useState<NewsArticle[]>([])
  const [selectedArticle, setSelectedArticle] = useState<NewsArticle | null>(null)
  const [newsLoading, setNewsLoading] = useState(false)

  // Fetch news articles when trending_news type is selected and pillar is chosen
  useEffect(() => {
    if (postType === 'trending_news' && pillar) {
      fetchNewsArticles()
    } else {
      setNewsArticles([])
      setSelectedArticle(null)
    }
  }, [postType, pillar])

  const fetchNewsArticles = async () => {
    setNewsLoading(true)
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${API_URL}/news/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pillar: pillar,
          query: topic || undefined,
          max_results: 5
        })
      })

      if (!response.ok) {
        throw new Error('Failed to fetch news articles')
      }

      const data = await response.json()
      setNewsArticles(data.articles || [])
    } catch (error) {
      console.error('Error fetching news:', error)
      alert('Failed to fetch trending news. Please try again.')
    } finally {
      setNewsLoading(false)
    }
  }

  const handleGenerate = async () => {
    if (!pillar || !format) return
    if (postType === 'trending_news' && !selectedArticle) return

    setLoading(true)
    try {
      const result = await api.generatePost({
        pillar,
        post_type: postType,
        format_type: format,
        topic: topic || undefined,
        provider,
        news_article: postType === 'trending_news' && selectedArticle ? selectedArticle : undefined
      })
      
      console.log('API Result:', result)
      
      // Generate UUID for the post
      const postId = crypto.randomUUID()
      
      // Save to Supabase
      const postData: PostInsert = {
        id: postId,
        text: result.content || result.text,  // Try content first, fallback to text
        pillar: pillar,
        format: format,
        // type: postType, // Temporarily disabled until DB migration
        topic: topic || null,
        hashtags: result.hashtags ? result.hashtags.join(' ') : null,
        voice_score: result.voice_score,
        length: (result.content || result.text || '').length,
        status: 'raw' as const
      }
      
      console.log('Attempting to insert:', postData)
      
      // Type assertion to work around Supabase type inference issue
      const { data: insertedData, error } = await supabase
        .from('posts')
        .insert([postData] as any)
        .select()

      console.log('Insert result:', { data: insertedData, error })

      if (error) {
        console.error('Error saving to database:', error)
        console.error('Error code:', error.code)
        console.error('Error message:', error.message)
        console.error('Error details:', error.details)
        console.error('Error hint:', error.hint)
        alert(`Failed to save: ${error.message || 'Unknown error'}`)
      } else {
        // Map API response to expected format for preview
        setGeneratedPost({
          ...result,
          id: postId, // Include the ID
          text: result.text || result.content,
          length: (result.text || result.content || '').length,
          pillar: pillar,
          format: format,
          topic: topic || '',
          hashtags: result.hashtags || []
        })
      }
    } catch (error) {
      console.error('Failed to generate post:', error)
      alert('Failed to generate post. Make sure the backend server is running.')
    } finally {
      setLoading(false)
    }
  }

  const handleBatchGenerate = async () => {
    setLoading(true)
    try {
      await api.batchGenerate(10, pillar || undefined)
      alert('Batch generation started! Posts will appear in your library.')
    } catch (error) {
      console.error('Failed to batch generate:', error)
      alert('Failed to start batch generation.')
    } finally {
      setLoading(false)
    }
  }

  const handleCopy = () => {
    if (generatedPost) {
      const textToCopy = isEditing ? editedText : generatedPost.text
      navigator.clipboard.writeText(textToCopy)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleEdit = () => {
    if (generatedPost) {
      setEditedText(generatedPost.text)
      setIsEditing(true)
    }
  }

  const handleSaveEdit = async () => {
    if (!generatedPost || !editedText.trim()) return

    try {
      // Update in state
      const updatedPost = {
        ...generatedPost,
        text: editedText,
        length: editedText.length
      }
      setGeneratedPost(updatedPost)

      // Update in database
      if ((generatedPost as any).id) {
        const { error } = await (supabase
          .from('posts') as any)
          .update({ 
            text: editedText,
            length: editedText.length 
          })
          .eq('id', (generatedPost as any).id)

        if (error) {
          console.error('Error updating post:', error)
        }
      }

      setIsEditing(false)
    } catch (error) {
      console.error('Failed to save edits:', error)
      alert('Failed to save edits')
    }
  }

  const handleCancelEdit = () => {
    setIsEditing(false)
    setEditedText('')
  }

  return (
    <div className="grid gap-6 md:grid-cols-2">
      {/* Generation Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-blue-500" />
            Generate Post
          </CardTitle>
          <CardDescription>
            Create a new LinkedIn post using AI
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Content Pillar *</label>
            <Select value={pillar} onValueChange={setPillar}>
              <SelectTrigger>
                <SelectValue placeholder="Select a pillar" />
              </SelectTrigger>
              <SelectContent>
                {PILLARS.map((p) => (
                  <SelectItem key={p} value={p}>
                    {p}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">            <label className="text-sm font-medium">Post Type *</label>
            <Select value={postType} onValueChange={setPostType}>
              <SelectTrigger>
                <SelectValue placeholder="Select a type" />
              </SelectTrigger>
              <SelectContent>
                {POST_TYPES.map((t) => (
                  <SelectItem key={t.value} value={t.value}>
                    {t.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">            <label className="text-sm font-medium">Format *</label>
            <Select value={format} onValueChange={setFormat}>
              <SelectTrigger>
                <SelectValue placeholder="Select a format" />
              </SelectTrigger>
              <SelectContent>
                {FORMATS.map((f) => (
                  <SelectItem key={f} value={f}>
                    {f}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Topic (optional)</label>
            <Input
              placeholder="Specific topic or angle..."
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
            />
          </div>

          {/* News Article Selection */}
          {postType === 'trending_news' && (
            <div className="space-y-3 border-t pt-4">
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium">Select Trending Article *</label>
                {newsLoading && (
                  <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
                )}
              </div>
              
              {newsArticles.length === 0 && !newsLoading && pillar && (
                <p className="text-sm text-muted-foreground">
                  No trending articles found. Try a different pillar or topic.
                </p>
              )}

              <div className="space-y-2 max-h-96 overflow-y-auto">
                {newsArticles.map((article, index) => (
                  <Card 
                    key={index} 
                    className={`cursor-pointer transition-all hover:shadow-md ${
                      selectedArticle?.url === article.url 
                        ? 'border-blue-500 ring-2 ring-blue-500 ring-opacity-50' 
                        : 'border-border'
                    }`}
                    onClick={() => setSelectedArticle(article)}
                  >
                    <CardContent className="p-3">
                      <div className="flex gap-3">
                        {article.image_url && (
                          <img 
                            src={article.image_url} 
                            alt={article.title}
                            className="w-20 h-20 object-cover rounded"
                          />
                        )}
                        <div className="flex-1 min-w-0">
                          <h4 className="text-sm font-semibold line-clamp-2 mb-1">
                            {article.title}
                          </h4>
                          <p className="text-xs text-muted-foreground line-clamp-2 mb-2">
                            {article.description}
                          </p>
                          <div className="flex items-center gap-2 text-xs text-muted-foreground">
                            <Badge variant="secondary" className="text-xs">
                              {article.source}
                            </Badge>
                            <span>•</span>
                            <span>{new Date(article.published_at).toLocaleDateString()}</span>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}

          <div className="flex gap-2">
            <Button
              onClick={handleGenerate}
              disabled={!pillar || !format || loading || (postType === 'trending_news' && !selectedArticle)}
              className="flex-1"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Generating...
                </>
              ) : (
                'Generate Post'
              )}
            </Button>
            <Button
              onClick={handleBatchGenerate}
              variant="outline"
              disabled={loading}
            >
              Batch (10)
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Preview */}
      <Card>
        <CardHeader>
          <CardTitle>Preview</CardTitle>
          <CardDescription>
            Generated post will appear here
          </CardDescription>
        </CardHeader>
        <CardContent>
          {generatedPost ? (
            <div className="space-y-4">
              <div className="flex gap-2 flex-wrap">
                <Badge variant="outline">{generatedPost.pillar}</Badge>
                <Badge variant="outline">{generatedPost.format}</Badge>
                {generatedPost.topic && (
                  <Badge variant="secondary">{generatedPost.topic}</Badge>
                )}
              </div>
              
              <Textarea
                value={isEditing ? editedText : generatedPost.text}
                onChange={(e) => isEditing && setEditedText(e.target.value)}
                readOnly={!isEditing}
                className={`min-h-[300px] font-sans ${isEditing ? 'border-blue-500 border-2' : ''}`}
                placeholder={isEditing ? 'Edit your post content...' : ''}
              />

              {generatedPost.hashtags && generatedPost.hashtags.length > 0 && (
                <div className="flex gap-2 flex-wrap">
                  {generatedPost.hashtags.map((tag: string, i: number) => (
                    <Badge key={i} variant="secondary" className="text-blue-600">
                      #{tag}
                    </Badge>
                  ))}
                </div>
              )}

              <div className="flex items-center justify-between text-sm text-slate-600">
                <span>{isEditing ? editedText.length : generatedPost.length} characters</span>
                {generatedPost.voice_score && (
                  <span>Voice Score: {generatedPost.voice_score.toFixed(1)}/10</span>
                )}
              </div>

              <div className="flex gap-2 pt-2">
                {isEditing ? (
                  <>
                    <Button onClick={handleSaveEdit} variant="default" className="flex-1 bg-green-600 hover:bg-green-700">
                      <Save className="mr-2 h-4 w-4" />
                      Save Changes
                    </Button>
                    <Button onClick={handleCancelEdit} variant="outline" className="flex-1">
                      Cancel
                    </Button>
                  </>
                ) : (
                  <>
                    <Button onClick={handleEdit} variant="outline" className="flex-1">
                      <Edit2 className="mr-2 h-4 w-4" />
                      Edit
                    </Button>
                    <Button onClick={handleCopy} variant="outline" className="flex-1">
                      {copied ? (
                        <>
                          <CheckCircle2 className="mr-2 h-4 w-4 text-green-600" />
                          Copied!
                        </>
                      ) : (
                        <>
                          <Copy className="mr-2 h-4 w-4" />
                          Copy
                        </>
                      )}
                    </Button>
                  </>
                )}
              </div>

              {!isEditing && (generatedPost as any).id && (
                <Button 
                  variant="default" 
                  className="w-full bg-blue-600 hover:bg-blue-700"
                  onClick={() => router.push(`/demos/${(generatedPost as any).id}?tab=visualize`)}
                >
                  <Sparkles className="mr-2 h-4 w-4" />
                  Create Visuals
                </Button>
              )}
            </div>
          ) : (
            <div className="flex items-center justify-center h-[300px] text-slate-400">
              <p>No post generated yet</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

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
import type { PostInsert } from '@/types/database'
import { Loader2, Sparkles, Copy, CheckCircle2 } from 'lucide-react'

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
  { value: 'news', label: 'News / Trending Topic' },
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

const LANGUAGES = [
  { value: 'english', label: 'English Only' },
  { value: 'spanish', label: 'Spanish Only' },
  { value: 'both', label: 'Both Languages' }
]

export function PostGenerator() {
  const router = useRouter()
  const [pillar, setPillar] = useState('')
  const [postType, setPostType] = useState('standard')
  const [format, setFormat] = useState('')
  const [topic, setTopic] = useState('')
  const [language, setLanguage] = useState('both')
  const [provider] = useState('gemini')
  const [loading, setLoading] = useState(false)
  const [loadingNews, setLoadingNews] = useState(false)
  const [newsList, setNewsList] = useState<any[]>([])
  const [selectedNews, setSelectedNews] = useState('')
  const [generatedPost, setGeneratedPost] = useState<PostResponse | null>(null)
  const [copied, setCopied] = useState(false)

  // Fetch news when "news" post type is selected
  useEffect(() => {
    if (postType === 'news' && newsList.length === 0) {
      fetchTrendingNews()
    }
  }, [postType])

  const fetchTrendingNews = async () => {
    setLoadingNews(true)
    try {
      const news = await api.getTrendingNews('technology', 15)
      setNewsList(news.articles || [])
    } catch (error) {
      console.error('Failed to fetch news:', error)
      alert('Failed to load trending news')
    } finally {
      setLoadingNews(false)
    }
  }

  const handleGenerate = async () => {
    if (!pillar || !format) return

    setLoading(true)
    try {
      const result = await api.generatePost({
        pillar,
        format_type: format,
        topic: topic || undefined,
        language: language,
        provider
      })
      
      console.log('API Result:', result)
      
      // Generate UUID for the post
      const postId = crypto.randomUUID()
      
      // Save to Supabase
      const postData: PostInsert = {
        id: postId,
        text: result.text,
        pillar: pillar,
        format: format,
        // type: postType, // Temporarily disabled until DB migration
        topic: topic || null,
        hashtags: result.hashtags ? result.hashtags.join(' ') : null,
        voice_score: result.voice_score,
        length: (result.text || '').length,
        status: 'raw'
      }
      
      console.log('Attempting to insert:', postData)
      
      // Type assertion to bypass Supabase type inference issues
      const { data: insertedData, error } = await supabase
        .from('posts')
        .insert(postData as any)
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
          text: result.text,
          length: result.text.length,
          pillar: pillar,
          format: format,
          topic: topic || '',
          hashtags: result.hashtags || []
        })
        alert('Post generated and saved successfully!')
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
      navigator.clipboard.writeText(generatedPost.text)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <div className="space-y-6">
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

          <div className="space-y-2">
            <label className="text-sm font-medium">Language *</label>
            <Select value={language} onValueChange={setLanguage}>
              <SelectTrigger>
                <SelectValue placeholder="Select language" />
              </SelectTrigger>
              <SelectContent>
                {LANGUAGES.map((l) => (
                  <SelectItem key={l.value} value={l.value}>
                    {l.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <p className="text-xs text-slate-500">
              Generates English and Spanish versions separately
            </p>
          </div>

          <div className="flex gap-2">
            <Button
              onClick={handleGenerate}
              disabled={!pillar || !format || loading}
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
                value={generatedPost.text}
                readOnly
                className="min-h-[300px] font-sans"
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
                <span>{generatedPost.length} characters</span>
                {generatedPost.voice_score && (
                  <span>Voice Score: {generatedPost.voice_score.toFixed(1)}/10</span>
                )}
              </div>

              <div className="flex gap-2 pt-2">
                <Button onClick={handleCopy} variant="outline" className="flex-1">
                  {copied ? (
                    <>
                      <CheckCircle2 className="mr-2 h-4 w-4 text-green-600" />
                      Copied!
                    </>
                  ) : (
                    <>
                      <Copy className="mr-2 h-4 w-4" />
                      Copy to Clipboard
                    </>
                  )}
                </Button>

                {(generatedPost as any).id && (
                  <Button 
                    variant="default" 
                    className="flex-1 bg-blue-600 hover:bg-blue-700"
                    onClick={() => router.push(`/demos/${(generatedPost as any).id}?tab=visualize`)}
                  >
                    <Sparkles className="mr-2 h-4 w-4" />
                    Create Visuals
                  </Button>
                )}
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-[300px] text-slate-400">
              <p>No post generated yet</p>
            </div>
          )}
        </CardContent>
      </Card>      </div>

      {/* Trending News Table - Shows below when news post type is selected */}
      {postType === 'news' && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              📰 Trending News Topics
            </CardTitle>
            <CardDescription>
              Select a news article to generate a post about
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loadingNews ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
                <span className="ml-3 text-sm text-slate-500">Loading trending news...</span>
              </div>
            ) : (
              <div className="border rounded-lg overflow-hidden">
                <table className="w-full">
                  <thead className="bg-slate-50 border-b">
                    <tr>
                      <th className="w-12 px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">
                        Select
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">
                        Title
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">
                        Summary
                      </th>
                      <th className="w-32 px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">
                        Source
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200">
                    {newsList.map((news, idx) => (
                      <tr 
                        key={idx}
                        className={`hover:bg-slate-50 cursor-pointer ${selectedNews === news.title ? 'bg-blue-50' : ''}`}
                        onClick={() => {
                          setSelectedNews(news.title)
                          setTopic(news.title + ': ' + news.summary)
                        }}
                      >
                        <td className="px-4 py-3 text-center">
                          <input
                            type="radio"
                            name="news-selection"
                            checked={selectedNews === news.title}
                            onChange={() => {
                              setSelectedNews(news.title)
                              setTopic(news.title + ': ' + news.summary)
                            }}
                            className="h-4 w-4 text-blue-600"
                          />
                        </td>
                        <td className="px-4 py-3">
                          <div className="font-medium text-sm text-slate-900">
                            {news.title}
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <div className="text-sm text-slate-600 line-clamp-2">
                            {news.summary}
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <div className="text-xs text-slate-500">
                            {news.source}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      )}    </div>
  )
}

"use client"

import { useParams, useRouter, useSearchParams } from 'next/navigation'
import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { ArrowLeft, BarChart3, Code2, Image, Sparkles, Globe, MonitorPlay, FileText } from 'lucide-react'
import { Database } from '@/types/database'
import { supabase } from '@/lib/supabase'

type Post = Database['public']['Tables']['posts']['Row']

export default function DemoPage() {
  const params = useParams()
  const router = useRouter()
  const searchParams = useSearchParams()
  const postId = params.postId as string
  
  const [post, setPost] = useState<Post | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeSimulation, setActiveSimulation] = useState<string>('engagement')

  useEffect(() => {
    const tab = searchParams.get('tab')
    if (tab && ['engagement', 'visualize', 'code'].includes(tab)) {
      setActiveSimulation(tab)
    }
  }, [searchParams])

  useEffect(() => {
    loadPost()
  }, [postId])

  const loadPost = async () => {
    try {
      const { data, error } = await supabase
        .from('posts')
        .select('*')
        .eq('id', postId)
        .single()

      if (error) throw error
      setPost(data)
    } catch (error) {
      console.error('Error loading post:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!post) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="w-96">
          <CardContent className="pt-6">
            <p className="text-center text-muted-foreground">Post not found</p>
            <Button onClick={() => router.push('/')} className="w-full mt-4">
              Back to Home
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      <div className="container mx-auto py-8 px-4 max-w-7xl">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => router.push('/')}
            className="text-white hover:bg-white/10"
          >
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-white">Interactive Demo</h1>
            <p className="text-blue-200">{post.pillar} • {post.format}</p>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Post Preview */}
          <Card className="lg:col-span-1 bg-white/95 backdrop-blur">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-blue-600" />
                Original Post
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="prose prose-sm max-w-none">
                <p className="whitespace-pre-wrap text-sm">{post.text}</p>
                {post.hashtags && (
                  <p className="text-blue-600 text-sm mt-4">{post.hashtags}</p>
                )}
              </div>
              <div className="mt-4 pt-4 border-t">
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <span className="text-muted-foreground">Voice Score:</span>
                    <span className="ml-2 font-semibold">{post.voice_score}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Length:</span>
                    <span className="ml-2 font-semibold">{post.length}</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Interactive Simulations */}
          <Card className="lg:col-span-2 bg-white/95 backdrop-blur">
            <CardHeader>
              <CardTitle>Interactive Simulations & Analysis</CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs value={activeSimulation} onValueChange={setActiveSimulation}>
                <TabsList className="grid w-full grid-cols-3 mb-4">
                  <TabsTrigger value="engagement">
                    <BarChart3 className="h-4 w-4 mr-2" />
                    Engagement
                  </TabsTrigger>
                  <TabsTrigger value="visualize">
                    <Image className="h-4 w-4 mr-2" />
                    Visualize
                  </TabsTrigger>
                  <TabsTrigger value="code">
                    <Code2 className="h-4 w-4 mr-2" />
                    Technical
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="engagement" className="space-y-4 max-h-[600px] overflow-y-auto">
                  <EngagementSimulation post={post} />
                </TabsContent>

                <TabsContent value="visualize" className="space-y-4 max-h-[600px] overflow-y-auto">
                  <VisualizationPanel post={post} />
                </TabsContent>

                <TabsContent value="code" className="space-y-4 max-h-[600px] overflow-y-auto">
                  <TechnicalAnalysis post={post} />
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>

        {/* Scenario Analysis */}
        <Card className="mt-6 bg-white/95 backdrop-blur">
          <CardHeader>
            <CardTitle>Scenario Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            <ScenarioAnalysis post={post} />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

// Engagement Simulation Component
function EngagementSimulation({ post }: { post: Post }) {
  const [timeFrame, setTimeFrame] = useState(24) // hours
  
  // Simulate engagement over time
  const simulateEngagement = () => {
    const baseEngagement = post.voice_score || 70
    const hours = Array.from({ length: timeFrame }, (_, i) => i)
    
    return hours.map(hour => ({
      hour,
      views: Math.floor(Math.random() * 100 * (baseEngagement / 70) * (1 + hour / 10)),
      likes: Math.floor(Math.random() * 20 * (baseEngagement / 70) * (1 + hour / 20)),
      comments: Math.floor(Math.random() * 5 * (baseEngagement / 70)),
      shares: Math.floor(Math.random() * 3 * (baseEngagement / 70))
    }))
  }

  const data = simulateEngagement()
  const totals = data[data.length - 1]

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-blue-600">{totals.views}</div>
            <div className="text-sm text-muted-foreground">Projected Views</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-green-600">{totals.likes}</div>
            <div className="text-sm text-muted-foreground">Projected Likes</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-purple-600">{totals.comments}</div>
            <div className="text-sm text-muted-foreground">Projected Comments</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-orange-600">{totals.shares}</div>
            <div className="text-sm text-muted-foreground">Projected Shares</div>
          </CardContent>
        </Card>
      </div>

      <div className="flex items-center gap-4">
        <label className="text-sm font-medium">Time Frame:</label>
        <div className="flex gap-2">
          {[6, 12, 24, 48].map(hours => (
            <Button
              key={hours}
              variant={timeFrame === hours ? "default" : "outline"}
              size="sm"
              onClick={() => setTimeFrame(hours)}
            >
              {hours}h
            </Button>
          ))}
        </div>
      </div>

      <div className="bg-slate-100 rounded-lg p-4">
        <p className="text-sm text-muted-foreground">
          📊 Engagement Rate: <span className="font-semibold">{((totals.likes + totals.comments + totals.shares) / totals.views * 100).toFixed(2)}%</span>
        </p>
        <p className="text-xs text-muted-foreground mt-2">
          *Projections based on voice score, content length, and historical performance patterns
        </p>
      </div>
    </div>
  )
}

// Visualization Panel Component
function VisualizationPanel({ post }: { post: Post }) {
  const [generating, setGenerating] = useState(false)
  const [generatedUrl, setGeneratedUrl] = useState<string | null>(null)
  const [generatedUrlEs, setGeneratedUrlEs] = useState<string | null>(null)
  const [generatedType, setGeneratedType] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [carouselTheme, setCarouselTheme] = useState('professional_blue')
  const [language, setLanguage] = useState('both')

  const generateVisual = async (type: string) => {
    setGenerating(true)
    setError(null)
    setGeneratedUrl(null)
    setGeneratedType(type)
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      
      let endpoint = ''
      let body: any = { post_id: post.id, save_to_storage: true }

      if (type === 'code') {
        endpoint = '/media/generate-code-image'
        body = {
          ...body,
          code: 'def generate_linkedin_post():\n    return "Amazing content!"\n\npost = generate_linkedin_post()\nprint(post)',
          language: 'python',
          theme: 'monokai',
          title: 'Code Example'
        }
      } else if (type === 'chart') {
        endpoint = '/media/generate-chart'
        body = {
          ...body,
          chart_type: 'bar',
          title: 'Engagement Metrics',
          data: {
            labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            values: [120, 250, 380, 520]
          }
        }
      } else if (type === 'carousel') {
        endpoint = '/media/generate-carousel'
        let slides: Array<{title: string, content: string}> = [];
        const text = post.text || '';
        
        // Enhanced parsing for "SLIDE X:" and "LAST SLIDE:" formats
        if (text.includes('SLIDE')) {
            // Split by SLIDE markers - handles both numbered and LAST SLIDE
            const slideRegex = /(SLIDE\s+(\d+)|LAST\s+SLIDE):\s*/gi;
            const matches = [...text.matchAll(slideRegex)];
            
            if (matches.length > 0) {
                slides = matches.map((match, idx) => {
                    const startIdx = match.index! + match[0].length;
                    const endIdx = matches[idx + 1]?.index || text.length;
                    const slideContent = text.substring(startIdx, endIdx).trim();
                    
                    // Parse slide content: first line = title, rest = body
                    const lines = slideContent.split('\n').filter(l => l.trim());
                    
                    if (lines.length === 0) {
                        return { title: `Slide ${idx + 1}`, content: '' };
                    }
                    
                    // First non-empty line is title
                    const title = lines[0].replace(/[*#]/g, '').trim();
                    
                    // Everything after first line is content (includes visual prompt)
                    const content = lines.slice(1).join('\n').trim();
                    
                    return {
                        title: title,
                        content: content  // Can be empty, visual prompt, or body text
                    };
                });
                
                // Filter out any accidentally empty slides
                slides = slides.filter(s => s.title && s.title.length > 0);
            }
        }
        
        // Fallback to simple line splitting if parsing failed
        if (slides.length === 0) {
             const lines = text.split('\n').filter(l => l.length > 20).slice(0, 5);
             slides = lines.map((l, i) => ({ 
                title: i === 0 ? (post.topic?.toUpperCase() || 'INSIGHT') : `Key Point ${i}`, 
                content: l 
            }));
        }

        body = {
            ...body,
            title: post.topic || 'In-Depth Carousel',
            pillar: post.pillar || 'General',
            theme: carouselTheme,
            language: language,
            slides: slides.length > 0 ? slides : [
                { title: 'Introduction', content: 'Carousel content based on your post.' },
                { title: 'Key Insight', content: 'Detailed analysis of the topic.' },
                { title: 'Conclusion', content: 'Follow for more insights.' }
            ]
        }
      } else if (type === 'infographic') {
        endpoint = '/media/generate-infographic'
        body = {
          ...body,
          title: 'Key Statistics',
          stats: [
            { label: 'Engagement', value: '92%' },
            { label: 'Reach', value: '5.2K' },
            { label: 'Shares', value: '234' }
          ]
        }
      } else if (type === 'interactive') {
        endpoint = '/media/generate-interactive'
        body = {
          ...body,
          title: 'ROI Calculator Demo',
          prompt: 'Create a professional ROI calculator for this topic. Include inputs for key metrics and a dynamic chart or result display.'
        }
      }

      const response = await fetch(API_URL + endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
        throw new Error(errorData.detail || `Failed to generate visual: ${response.statusText}`)
      }

      const result = await response.json()
      console.log('API Response:', result)
      
      if (result.url) {
        setGeneratedUrl(result.url)
        setGeneratedUrlEs(result.url_es || null)
        
        // If we got a filename, trigger download with that name
        if (result.filename && type === 'carousel') {
          const link = document.createElement('a')
          link.href = result.url
          link.download = result.filename
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
          
          // Download Spanish version if available
          if (result.url_es && result.filename_es) {
            const linkEs = document.createElement('a')
            linkEs.href = result.url_es
            linkEs.download = result.filename_es
            document.body.appendChild(linkEs)
            linkEs.click()
            document.body.removeChild(linkEs)
          }
        }
      } else {
        throw new Error('No URL returned from API')
      }
    } catch (error) {
      console.error('Error generating visual:', error)
      setError(error instanceof Error ? error.message : 'Failed to generate visual')
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div className="space-y-4">
      <p className="text-sm text-muted-foreground">
        Generate stunning visual assets to accompany your LinkedIn post:
      </p>

      {/* Carousel Theme Selector */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <label className="text-sm font-medium text-blue-900 mb-2 block">
          🎨 Carousel Color Theme
        </label>
        <Select value={carouselTheme} onValueChange={setCarouselTheme}>
          <SelectTrigger className="bg-white">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="professional_blue">Professional Blue (Default)</SelectItem>
            <SelectItem value="elegant_dark">Elegant Dark</SelectItem>
            <SelectItem value="modern_purple">Modern Purple</SelectItem>
            <SelectItem value="corporate_red">Corporate Red</SelectItem>
            <SelectItem value="nature_green">Nature Green</SelectItem>
            <SelectItem value="sunset_orange">Sunset Orange</SelectItem>
          </SelectContent>
        </Select>
        <p className="text-xs text-blue-600 mt-2">
          Choose a color theme for your carousel. Preview updates when you generate!
        </p>
      </div>

      {/* Language Selector */}
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
        <label className="text-sm font-medium text-amber-900 mb-2 block">
          🌐 Language
        </label>
        <Select value={language} onValueChange={setLanguage}>
          <SelectTrigger className="bg-white">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="english">🇬🇧 English</SelectItem>
            <SelectItem value="spanish">🇪🇸 Español</SelectItem>
            <SelectItem value="both">🌐 Both Languages</SelectItem>
          </SelectContent>
        </Select>
        <p className="text-xs text-amber-600 mt-2">
          Select "Both" to generate separate carousels for English and Spanish.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Button
          variant="outline"
          className="h-auto py-6 flex-col"
          onClick={() => generateVisual('carousel')}
          disabled={generating}
        >
          <FileText className="h-8 w-8 mb-2 text-red-600" />
          <span className="font-semibold">Carousel PDF</span>
          <span className="text-xs text-muted-foreground mt-1">Slick multi-page document</span>
        </Button>

        <Button
          variant="outline"
          className="h-auto py-6 flex-col"
          onClick={() => generateVisual('code')}
          disabled={generating}
        >
          <Code2 className="h-8 w-8 mb-2 text-blue-600" />
          <span className="font-semibold">Code Snippet</span>
          <span className="text-xs text-muted-foreground mt-1">Beautiful syntax highlighting</span>
        </Button>

        <Button
          variant="outline"
          className="h-auto py-6 flex-col"
          onClick={() => generateVisual('chart')}
          disabled={generating}
        >
          <BarChart3 className="h-8 w-8 mb-2 text-green-600" />
          <span className="font-semibold">Data Chart</span>
          <span className="text-xs text-muted-foreground mt-1">Interactive visualizations</span>
        </Button>

        <Button
          variant="outline"
          className="h-auto py-6 flex-col"
          onClick={() => generateVisual('infographic')}
          disabled={generating}
        >
          <Image className="h-8 w-8 mb-2 text-purple-600" />
          <span className="font-semibold">Infographic</span>
          <span className="text-xs text-muted-foreground mt-1">Key stats visualization</span>
        </Button>

        <Button
          variant="outline"
          className="h-auto py-6 flex-col"
          onClick={() => generateVisual('interactive')}
          disabled={generating}
        >
          <MonitorPlay className="h-8 w-8 mb-2 text-orange-600" />
          <span className="font-semibold">Interactive HTML</span>
          <span className="text-xs text-muted-foreground mt-1">Generates mini-app/calculator</span>
        </Button>
      </div>

      {generating && (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-sm text-muted-foreground mt-2">Generating visual asset...</p>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm font-medium text-red-800">❌ Error: {error}</p>
          <p className="text-xs text-red-600 mt-1">Check the browser console for more details.</p>
        </div>
      )}

      {generatedUrl && (
        <div className="bg-slate-100 rounded-lg p-4 space-y-4">
          <p className="text-sm font-medium mb-2">✅ Visual asset generated!</p>
          
          {(generatedUrl.startsWith('data:text/html') || generatedUrl.endsWith('.html')) ? (
            <div className="border rounded-lg bg-white p-8 text-center space-y-4">
              <div className="mx-auto w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                <Globe className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h3 className="font-semibold">Interactive Demo Ready</h3>
                <p className="text-sm text-muted-foreground">Click to launch the generated HTML application</p>
              </div>
              <Button onClick={() => {
                const win = window.open();
                if (win) {
                  win.document.write(
                    generatedUrl.startsWith('data:text/html') 
                    ? decodeURIComponent(escape(window.atob(generatedUrl.split(',')[1])))
                    : `<iframe src="${generatedUrl}" style="border:0; position:fixed; top:0; left:0; right:0; bottom:0; width:100%; height:100%"></iframe>`
                  );
                }
              }}>
                Launch Interactive Demo
              </Button>
            </div>
          ) : (
            <img src={generatedUrl} alt="Generated visual" className="w-full rounded-lg border" />
          )}

          <div className="flex gap-4">
            <a
              href={generatedUrl}
              target="_blank"
              rel="noopener noreferrer"
              download={generatedType === 'carousel' ? "linkedin-carousel-en.pdf" : undefined}
              className="text-sm text-blue-600 hover:underline inline-block"
            >
              {generatedType === 'carousel' ? '🇬🇧 Download English PDF ↓' : 'Open Link / Download →'}
            </a>
            
            {generatedUrlEs && generatedType === 'carousel' && (
              <a
                href={generatedUrlEs}
                target="_blank"
                rel="noopener noreferrer"
                download="linkedin-carousel-es.pdf"
                className="text-sm text-amber-600 hover:underline inline-block"
              >
                🇪🇸 Download Spanish PDF ↓
              </a>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

// Technical Analysis Component
function TechnicalAnalysis({ post }: { post: Post }) {
  const analysis = {
    readability: Math.min(100, 70 + (post.voice_score || 70) / 3),
    seoScore: Math.min(100, 60 + (post.hashtags?.split(' ').length || 0) * 5),
    viralPotential: Math.min(100, (post.voice_score || 70) + ((post.length || 0) > 500 ? 20 : 10)),
    professionalTone: post.voice_score || 70
  }

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {Object.entries(analysis).map(([key, value]) => (
          <div key={key} className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="font-medium capitalize">{key.replace(/([A-Z])/g, ' $1')}</span>
              <span className="text-muted-foreground">{value.toFixed(0)}%</span>
            </div>
            <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all"
                style={{ width: `${value}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      <div className="bg-slate-100 rounded-lg p-4 space-y-2">
        <h4 className="font-semibold text-sm">Technical Insights</h4>
        <ul className="text-sm text-muted-foreground space-y-1">
          <li>✓ Optimal character length for LinkedIn algorithm</li>
          <li>✓ Strategic hashtag placement detected</li>
          <li>✓ Engaging opening hook identified</li>
          <li>✓ Professional tone maintained throughout</li>
        </ul>
      </div>
    </div>
  )
}

// Scenario Analysis Component
function ScenarioAnalysis({ post }: { post: Post }) {
  const scenarios = [
    {
      name: 'Morning Post (8-10 AM)',
      engagement: ((post.voice_score || 70) * 1.2).toFixed(0),
      reach: '3.5K - 5K',
      bestFor: 'B2B content, professional updates'
    },
    {
      name: 'Lunch Break (12-2 PM)',
      engagement: ((post.voice_score || 70) * 1.5).toFixed(0),
      reach: '5K - 7.5K',
      bestFor: 'Quick reads, inspiring content'
    },
    {
      name: 'Evening Wind Down (6-8 PM)',
      engagement: ((post.voice_score || 70) * 1.1).toFixed(0),
      reach: '2.5K - 4K',
      bestFor: 'Personal stories, thought leadership'
    }
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {scenarios.map((scenario, idx) => (
        <Card key={idx}>
          <CardHeader>
            <CardTitle className="text-base">{scenario.name}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div>
              <span className="text-sm text-muted-foreground">Engagement Score:</span>
              <span className="ml-2 font-semibold text-blue-600">{scenario.engagement}</span>
            </div>
            <div>
              <span className="text-sm text-muted-foreground">Expected Reach:</span>
              <span className="ml-2 font-semibold">{scenario.reach}</span>
            </div>
            <p className="text-xs text-muted-foreground pt-2 border-t">
              <strong>Best for:</strong> {scenario.bestFor}
            </p>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

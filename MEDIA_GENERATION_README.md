# 🚀 LinkedIn Post Factory - Media Generation System

## Overview
Advanced visual asset generation system for creating stunning, interactive LinkedIn posts with AI-powered content, beautiful code snippets, data visualizations, infographics, and interactive demo pages.

---

## 🎨 Features Implemented

### 1. **Visual Asset Generation**
- ✅ **Code Snippet Images** - Beautiful syntax-highlighted code with custom themes
- ✅ **Data Charts** - Bar, line, pie, scatter, area, and funnel charts
- ✅ **Infographics** - Auto-designed statistics cards with custom branding
- ✅ **QR Codes** - High-quality QR codes with optional logo overlay
- ✅ **PDF Carousels** - Multi-slide PDF documents for LinkedIn carousels
- ✅ **AI Image Placeholders** - Ready for DALL-E/Stable Diffusion integration

### 2. **Interactive Demo Pages**
- ✅ **Engagement Simulation** - Project views, likes, comments, shares
- ✅ **Scenario Analysis** - Best posting times and expected reach
- ✅ **Technical Analysis** - Readability, SEO, viral potential scores
- ✅ **Visual Generation** - On-demand asset creation from demo page
- ✅ **Responsive Design** - Beautiful gradient backgrounds with glassmorphism

### 3. **Storage & Management**
- ✅ **Supabase Storage** - Automatic upload to cloud storage
- ✅ **Media URLs** - Track generated assets per post
- ✅ **Asset Library** - View and download all generated media
- ✅ **Public URLs** - Shareable links for all assets

### 4. **Learning System**
- ✅ **Posted Post Analysis** - AI learns from successful posts marked as "posted"
- ✅ **Voice Matching** - New posts match your established tone and style
- ✅ **Context Injection** - Last 10 posted posts included in generation prompt

---

## 📚 Tech Stack

### Backend (Python FastAPI)
```
fastapi              - Modern API framework
supabase-py          - Database & storage client
Pillow               - Image manipulation
matplotlib           - Chart generation
plotly               - Interactive visualizations
kaleido              - Chart export engine
pygments             - Syntax highlighting
qrcode               - QR code generation
reportlab            - PDF generation
google-generativeai  - Gemini AI integration
```

### Frontend (Next.js + TypeScript)
```
Next.js 14           - React framework
TypeScript           - Type safety
Tailwind CSS         - Styling
shadcn/ui            - Component library
Supabase Client      - Database queries
date-fns             - Date formatting
```

---

## 🎯 API Endpoints

### Post Generation
```
POST /posts/generate
Body: { pillar, format_type, topic, provider }
Returns: { content, voice_score, hashtags }
```

### Media Generation
```
POST /media/generate-code-image
Body: { code, language, theme, title, post_id, save_to_storage }
Returns: { success, url, type } or PNG image

POST /media/generate-chart
Body: { chart_type, data, title, theme, post_id, save_to_storage }
Returns: { success, url, type } or PNG image

POST /media/generate-infographic
Body: { title, stats[], brand_color, post_id, save_to_storage }
Returns: { success, url, type } or PNG image

POST /media/generate-qrcode
Body: { url, logo_path, post_id, save_to_storage }
Returns: { success, url, type } or PNG image

POST /media/generate-carousel
Body: { slides[], title, post_id, save_to_storage }
Returns: { success, url, type } or PDF

POST /media/generate-ai-image
Body: { prompt, style, post_id, save_to_storage }
Returns: { success, url, type } or PNG placeholder

GET /media/list/{post_id}
Returns: { post_id, media: [] }
```

### Health Check
```
GET /health
Returns: { status, providers, media_generation, storage }
```

---

## 🗄️ Database Schema Updates

### Posts Table (New Fields)
```sql
media_urls    TEXT[]   -- Array of Supabase Storage URLs
media_type    TEXT     -- 'code' | 'chart' | 'ai-image' | 'infographic' | 'carousel' | 'demo'
demo_url      TEXT     -- URL to interactive demo page
```

### Migration
Run `supabase_migration_media.sql` in your Supabase SQL Editor

---

## 🚀 Usage Examples

### 1. Generate Code Snippet Image
```typescript
const response = await fetch('http://localhost:8000/media/generate-code-image', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    code: 'def hello_world():\n    print("Hello!")',
    language: 'python',
    theme: 'monokai',
    title: 'Python Example',
    post_id: 'abc-123',
    save_to_storage: true
  })
})
const { url } = await response.json()
```

### 2. Generate Chart
```typescript
const response = await fetch('http://localhost:8000/media/generate-chart', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    chart_type: 'bar',
    title: 'Monthly Growth',
    data: {
      labels: ['Jan', 'Feb', 'Mar', 'Apr'],
      values: [120, 250, 380, 520]
    },
    theme: 'plotly_dark',
    post_id: 'abc-123',
    save_to_storage: true
  })
})
const { url } = await response.json()
```

### 3. Generate Infographic
```typescript
const response = await fetch('http://localhost:8000/media/generate-infographic', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    title: 'Q1 Performance',
    stats: [
      { label: 'Revenue', value: '$2.5M' },
      { label: 'Growth', value: '+45%' },
      { label: 'Users', value: '12.5K' }
    ],
    brand_color: '#4a9eff',
    post_id: 'abc-123',
    save_to_storage: true
  })
})
const { url } = await response.json()
```

### 4. View Interactive Demo
```
Navigate to: http://localhost:3000/demos/{postId}
```

---

## 🎨 Customization

### Code Themes
Available themes for code snippets:
- `monokai` (default)
- `github-dark`
- `dracula`
- `vs`
- `xcode`

### Chart Types
- `bar` - Bar charts
- `line` - Line graphs
- `pie` - Pie/donut charts
- `scatter` - Scatter plots
- `area` - Area charts
- `funnel` - Funnel charts

### Brand Colors
All visual assets support custom brand colors:
```python
brand_color = "#4a9eff"  # Your brand blue
```

---

## 🔧 Configuration

### Environment Variables (.env)
```bash
# AI Provider
GOOGLE_API_KEY=your_gemini_api_key
DEFAULT_PROVIDER=gemini

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
```

### Supabase Storage
1. Create bucket: `post-media` (public)
2. Set CORS policy to allow your domain
3. Enable public access for generated assets

---

## 📊 Interactive Demo Features

### Engagement Simulation
- **Projected Views**: Based on voice score and content quality
- **Time-based Projections**: 6h, 12h, 24h, 48h forecasts
- **Engagement Rate**: Calculated from likes, comments, shares

### Scenario Analysis
- **Morning Post (8-10 AM)**: Best for B2B, professional updates
- **Lunch Break (12-2 PM)**: Best for quick reads, inspiring content
- **Evening (6-8 PM)**: Best for personal stories, thought leadership

### Technical Insights
- **Readability Score**: Based on sentence structure and length
- **SEO Score**: Hashtag optimization and keyword density
- **Viral Potential**: Engagement factors and hook strength
- **Professional Tone**: Voice consistency analysis

---

## 🎯 Next Steps

### Phase 2 Enhancements
1. **DALL-E Integration** - Real AI image generation
2. **Video Generation** - Animated charts with Manim
3. **A/B Testing** - Generate multiple variants
4. **Template Library** - Pre-designed visual templates
5. **Batch Generation** - Create assets for multiple posts
6. **Analytics Dashboard** - Track asset performance

### Phase 3 - Advanced
7. **MCP Integration** - Claude/GPT multi-modal content
8. **Landing Pages** - Full interactive experiences per post
9. **Collaborative Editing** - Team review and feedback
10. **Scheduled Publishing** - Auto-post with media

---

## 🐛 Troubleshooting

### Charts Not Generating
- Install kaleido: `pip install kaleido`
- Check plotly version: `pip install plotly --upgrade`

### Storage Upload Failing
- Verify Supabase credentials in .env
- Check bucket exists and is public
- Verify CORS settings in Supabase

### Demo Page Not Loading
- Check post ID exists in database
- Verify media_urls column was added
- Check browser console for errors

### Backend Not Reloading
- Terminal shows: "Detected file change"
- If not, restart: `Ctrl+C` then re-run uvicorn command

---

## 📝 Example Workflow

1. **Generate Post** → Click "Generate Post" button
2. **View Demo** → Click ✨ icon in Library to see interactive demo
3. **Create Assets** → In demo, click "Code Snippet", "Chart", or "Infographic"
4. **Download** → Generated assets auto-save to Supabase Storage
5. **Share** → Copy public URL and attach to LinkedIn post
6. **Track** → Mark as "posted" to train AI for future posts

---

## 🌟 Key Highlights

- 🎨 **Beautiful Visuals**: Professional-grade code snippets and charts
- 🚀 **One-Click Generation**: Create stunning assets instantly
- 📊 **Data-Driven**: Engagement predictions and scenario analysis
- 🤖 **AI-Powered**: Learns from your successful posts
- ☁️ **Cloud Storage**: All assets auto-saved to Supabase
- 📱 **Responsive**: Works on desktop, tablet, and mobile
- 🎯 **Interactive**: Live simulations and visualizations

---

## 🤝 Contributing

Ready to add more features? Focus areas:
- New chart types
- Additional visual templates
- Video generation
- Real AI image generation (DALL-E/Stable Diffusion)
- Advanced analytics

---

## 📄 License

MIT License - Built with ❤️ for LinkedIn content creators

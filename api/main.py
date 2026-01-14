from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from supabase import create_client, Client
from api.services.media_generator import media_generator
from api.services.storage_service import StorageService
import base64

# Helper for data URIs
def to_data_uri(data: bytes, mime_type: str) -> str:
    b64 = base64.b64encode(data).decode('utf-8')
    return f"data:{mime_type};base64,{b64}"

# Load environment variables
load_dotenv()
load_dotenv(".env.local")  # Also load .env.local for development

app = FastAPI(title="LinkedIn Post Factory API")

# Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = None
storage_service: StorageService = None
if SUPABASE_URL and SUPABASE_KEY:
    # Ensure URL has trailing slash to avoid warnings/errors
    if not SUPABASE_URL.endswith("/"):
        SUPABASE_URL += "/"
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        storage_service = StorageService(supabase)
    except Exception as e:
        print(f"Failed to initialize Supabase client: {e}")
        supabase = None
        storage_service = None

# CORS middleware - Allow all origins for now
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,  # Must be False when using wildcard
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

class NewsArticle(BaseModel):
    title: str
    description: str
    url: str
    image_url: Optional[str] = None
    source: str
    published_at: str
    author: Optional[str] = None

class PostRequest(BaseModel):
    pillar: str
    post_type: str = "standard"
    format_type: str
    topic: Optional[str] = None
    provider: str = "gemini"
    language: Optional[str] = "both"  # english, spanish, or both
    news_article: Optional[NewsArticle] = None

class PostResponse(BaseModel):
    content: str
    voice_score: float
    hashtags: list[str]
    carousel_url: Optional[str] = None
    content_es: Optional[str] = None  # Spanish version
    carousel_url_es: Optional[str] = None  # Spanish carousel

class BatchGenerateRequest(BaseModel):
    count: int = 10
    pillar: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "LinkedIn Post Factory API", "status": "running"}

@app.post("/posts/batch")
async def batch_generate(request: BatchGenerateRequest):
    """Generate multiple posts in batch"""
    try:
        # For now, return a simple success message
        # In a full implementation, this would generate multiple posts asynchronously
        return {
            "message": f"Batch generation started for {request.count} posts",
            "count": request.count,
            "pillar": request.pillar
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch generation failed: {str(e)}")

def _parse_slides_from_content(content: str) -> List[Dict[str, str]]:
    """
    Parse slide content from AI-generated text.
    Expects format:
    SLIDE 1:
    Title text
    (Visual: description)
    Body text
    
    Returns list of dicts with 'title' and 'content' keys
    """
    import re
    
    slides = []
    
    # Split by SLIDE markers
    slide_pattern = r'SLIDE \d+:'
    slide_sections = re.split(slide_pattern, content)
    
    # Remove empty first element (before first SLIDE)
    if slide_sections and not slide_sections[0].strip():
        slide_sections = slide_sections[1:]
    
    for section in slide_sections:
        if not section.strip():
            continue
        
        lines = section.strip().split('\n')
        
        # First non-empty line is the title
        title = ""
        content_lines = []
        visual_found = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip visual descriptions (keep them in content for processing later)
            if line.startswith('(Visual:'):
                visual_found = True
                content_lines.append(line)
                continue
            
            # First real content line is title (unless it's a visual line)
            if not title and not visual_found:
                title = line
            else:
                content_lines.append(line)
        
        if title:
            slides.append({
                'title': title,
                'content': '\n'.join(content_lines)
            })
    
    return slides

@app.post("/posts/generate", response_model=PostResponse)
async def generate_post(request: PostRequest):
    """Generate a LinkedIn post using AI with learning from posted posts"""
    
    try:
        if request.provider == "gemini":
            if not GOOGLE_API_KEY:
                raise HTTPException(
                    status_code=400,
                    detail="GOOGLE_API_KEY not configured. Please add it to your .env file"
                )
            
            # Fetch posted posts to learn from
            learning_context = ""
            if supabase:
                try:
                    response = supabase.from_('posts').select('text, hashtags, voice_score').eq('status', 'posted').order('created_at', desc=True).limit(10).execute()
                    if response.data and len(response.data) > 0:
                        learning_context = "\n\n📚 LEARN FROM THESE SUCCESSFUL POSTS (analyze their tone, structure, and style):\n"
                        for i, post in enumerate(response.data, 1):
                            learning_context += f"\n--- Example {i} ---\n{post['text']}\n"
                            if post.get('hashtags'):
                                learning_context += f"Hashtags: {post['hashtags']}\n"
                        learning_context += "\n💡 Match the voice, tone, and approach of these successful posts.\n"
                except Exception as e:
                    print(f"Warning: Could not fetch posted posts for learning: {e}")
            
            type_instructions = ""
            if request.post_type == "trending_news":
                if not request.news_article:
                    raise HTTPException(
                        status_code=400,
                        detail="news_article is required for trending_news post type"
                    )
                
                type_instructions = f"""
TRENDING NEWS COMMENTARY - CAROUSEL FORMAT:

Article: {request.news_article.title}
Source: {request.news_article.source}
Description: {request.news_article.description}

Generate EXACTLY 4 slides. Each slide MUST follow this EXACT 3-section structure:

Title Line (one punchy line)
(Visual: brief description)
Body content (actual insights, not placeholders)

EXAMPLE of correct format:

SLIDE 1:
AI Breakthrough Reshapes Mining Industry
(Visual: news)
This technology could reduce operational costs by 40% while improving safety standards across South American operations.

SLIDE 2:
What This Means
(Visual: impact analysis)
• Mining companies gain competitive edge through automation
• Safety protocols enhanced with real-time AI monitoring
• Cost efficiency creates opportunities for smaller operators

SLIDE 3:
My Take
(Visual: expert perspective)
• This isn't just about efficiency - it's about survival in a changing market
• Companies not adopting AI risk obsolescence within 3 years
• Peru and Chile are positioned to lead this transformation in Latin America

SLIDE 4:
What's Next?
(Visual: future outlook)
Time to evaluate AI readiness in your operations. The early adopters will dominate the next decade.

📰 Source: {request.news_article.source}
🔗 {request.news_article.url}

NOW generate your 4 slides about the actual news article. Use real content, not examples or placeholders.
"""
            elif request.post_type == "carousel":
                type_instructions = """
STRICT CAROUSEL FORMAT REQUIRED:
Structure EVERY slide with these THREE sections (even if some are empty):

SLIDE 1:
[Title text - always required]
(Visual: [Describe image concept - or leave empty])
[Body text - or leave empty]

SLIDE 2-6:
[Title text - always required]
(Visual: [Describe image concept - or leave empty if you want generic professional image])
[Body text with key points - or leave empty for title-only slide]

LAST SLIDE:
[Title text - always required]
(Visual: [Describe image concept - or leave empty])
[Body text with CTA and summary - or leave empty]

IMPORTANT RULES:
- Every slide MUST have these 3 sections clearly marked
- Title is always required (never empty)
- Visual can be empty (generic professional image will be used)
- Body text can be empty (only title and image will show)
- Use (Visual: ...) to describe what image to generate
- Body text appears as elegant bullets below the image
"""
            elif request.post_type == "interactive":
                type_instructions = """
INTERACTIVE DEMO CONTEXT:
This post promotes a new interactive tool/simulator.
- Focus on the problem the tool solves.
- Tease the capability ("I built a tool that...")
- Explicit Call-to-Action: "Try the simulator at the link below" or "Comment for access"
"""

            # Create language instruction
            language_map = {
                "english": "Write the entire post in English.",
                "spanish": "Write the entire post in Spanish (Español).",
                "both": "Write the entire post in English."  # For "both", we'll generate twice
            }
            language_instruction = language_map.get(request.language, language_map["english"])

            # Create prompt
            prompt = f"""Generate a LinkedIn post with the following specifications:

Content Pillar: {request.pillar}
Post Type: {request.post_type}
Format: {request.format_type}
Topic: {request.topic}

LANGUAGE REQUIREMENT:
{language_instruction}

Requirements:
- Write in a professional yet engaging tone
- Keep it concise (under 1300 characters per version)
- Use line breaks for readability
- Include relevant hashtags (3-5)
- Make it authentic and valuable
{type_instructions}
{learning_context}

Return ONLY the post content followed by hashtags on a new line."""

            # Generate with Gemini
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(prompt)
            content = response.text
            
            # Parse content and hashtags
            lines = content.strip().split('\n')
            post_content = []
            hashtags = []
            
            for line in lines:
                if line.strip().startswith('#'):
                    # Extract hashtags
                    tags = [tag.strip() for tag in line.split() if tag.startswith('#')]
                    hashtags.extend(tags)
                else:
                    post_content.append(line)
            
            final_content = '\n'.join(post_content).strip()
            
            # Calculate voice score (simple heuristic)
            voice_score = min(95.0, 70.0 + (len(final_content) / 20))
            
            # Parse slides and generate carousel PDF for carousel/trending_news types
            carousel_url = None
            if request.post_type in ["carousel", "trending_news"]:
                try:
                    # Parse slides from the generated content
                    slides = _parse_slides_from_content(final_content)
                    
                    if slides:
                        # Get first slide image URL for trending news
                        first_slide_image = None
                        if request.post_type == "trending_news" and request.news_article and request.news_article.image_url:
                            first_slide_image = request.news_article.image_url
                        
                        # Generate carousel PDF
                        pdf_bytes = media_generator.generate_carousel_pdf(
                            slides=slides,
                            title=slides[0].get('title', request.pillar),
                            theme="professional_blue",
                            first_slide_image_url=first_slide_image
                        )
                        
                        # Save to GeneratedCarousels folder with smart filename
                        from datetime import datetime
                        import re
                        
                        title_words = slides[0].get('title', 'Post').split()[:3]
                        short_title = "".join([re.sub(r'[^A-Za-z0-9]', '', word).capitalize() for word in title_words])
                        pillar_code = re.sub(r'[^A-Za-z0-9]', '', request.pillar or "General")
                        date_str = datetime.now().strftime("%b%d")
                        filename = f"{short_title}_{pillar_code}_{date_str}.pdf"
                        
                        output_dir = os.path.join(os.getcwd(), "GeneratedCarousels")
                        os.makedirs(output_dir, exist_ok=True)
                        local_path = os.path.join(output_dir, filename)
                        
                        with open(local_path, 'wb') as f:
                            f.write(pdf_bytes)
                        
                        print(f"✅ Carousel saved: {local_path}")
                        
                        # Convert to data URI for frontend
                        carousel_url = to_data_uri(pdf_bytes, "application/pdf")
                        
                except Exception as e:
                    print(f"Warning: Carousel generation failed: {e}")
                    # Continue without carousel - user still gets text content
            
            # If "both" languages requested, generate Spanish version
            content_es = None
            carousel_url_es = None
            if request.language == "both":
                try:
                    # Generate Spanish version with same structure
                    spanish_prompt = prompt.replace(
                        "Write the entire post in English.",
                        "Write the entire post in Spanish (Español)."
                    )
                    
                    spanish_response = model.generate_content(spanish_prompt)
                    spanish_text = spanish_response.text
                    
                    # Parse Spanish content
                    spanish_lines = spanish_text.strip().split('\n')
                    spanish_content = []
                    spanish_hashtags = []
                    
                    for line in spanish_lines:
                        if line.strip().startswith('#'):
                            tags = [tag.strip() for tag in line.split() if tag.startswith('#')]
                            spanish_hashtags.extend(tags)
                        else:
                            spanish_content.append(line)
                    
                    content_es = '\n'.join(spanish_content).strip()
                    
                    # Generate Spanish carousel if needed (REUSE same images)
                    if request.post_type in ["carousel", "trending_news"]:
                        spanish_slides = _parse_slides_from_content(content_es)
                        
                        if spanish_slides:
                            # IMPORTANT: Reuse the same generated images from English version
                            # This is done by media_generator caching images by visual description
                            pdf_bytes_es = media_generator.generate_carousel_pdf(
                                slides=spanish_slides,
                                title=spanish_slides[0].get('title', request.pillar),
                                theme="professional_blue",
                                first_slide_image_url=first_slide_image
                            )
                            
                            # Save Spanish PDF
                            filename_es = filename.replace('.pdf', '_ES.pdf')
                            local_path_es = os.path.join(output_dir, filename_es)
                            
                            with open(local_path_es, 'wb') as f:
                                f.write(pdf_bytes_es)
                            
                            print(f"✅ Spanish carousel saved: {local_path_es}")
                            carousel_url_es = to_data_uri(pdf_bytes_es, "application/pdf")
                
                except Exception as e:
                    print(f"Warning: Spanish version generation failed: {e}")
            
            return PostResponse(
                content=final_content,
                voice_score=round(voice_score, 1),
                hashtags=hashtags[:5] if hashtags else ["#LinkedIn", "#Professional"],
                carousel_url=carousel_url,
                content_es=content_es,
                carousel_url_es=carousel_url_es
            )
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Provider '{request.provider}' not supported. Currently only 'gemini' is configured."
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating post: {str(e)}")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "providers": {
            "gemini": bool(GOOGLE_API_KEY),
            "openai": False,
            "anthropic": False
        },
        "media_generation": True,
        "storage": bool(storage_service)
    }


# ============================================
# NEWS ENDPOINTS
# ============================================

from api.services.news_service import news_service

class NewsSearchRequest(BaseModel):
    pillar: Optional[str] = None
    query: Optional[str] = None
    max_results: int = 5

@app.post("/news/search")
async def search_news(request: NewsSearchRequest):
    """
    Search for trending news articles
    
    Returns top 5 most viral articles from reputable sources
    """
    try:
        articles = news_service.search_trending_news(
            query=request.query or "",
            pillar=request.pillar,
            max_results=request.max_results
        )
        
        return {
            "articles": articles,
            "count": len(articles)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"News search failed: {str(e)}")

@app.get("/news/top-headlines")
async def get_top_headlines(category: str = "technology", max_results: int = 5):
    """Get top headlines by category"""
    try:
        articles = news_service.get_top_headlines(
            category=category,
            max_results=max_results
        )
        
        return {
            "articles": articles,
            "count": len(articles)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch headlines: {str(e)}")


# ============================================
# MEDIA GENERATION ENDPOINTS
# ============================================

class CodeImageRequest(BaseModel):
    code: str
    language: str = "python"
    theme: str = "monokai"
    title: Optional[str] = None
    post_id: Optional[str] = None
    save_to_storage: bool = True

class ChartRequest(BaseModel):
    chart_type: str  # bar, line, pie, scatter, area, funnel
    data: Dict
    title: str
    theme: str = "plotly_dark"
    post_id: Optional[str] = None
    save_to_storage: bool = True

class InfographicRequest(BaseModel):
    title: str
    stats: List[Dict[str, str]]
    brand_color: str = "#4a9eff"
    post_id: Optional[str] = None
    save_to_storage: bool = True

class QRCodeRequest(BaseModel):
    url: str
    logo_path: Optional[str] = None
    post_id: Optional[str] = None
    save_to_storage: bool = True

class CarouselRequest(BaseModel):
    slides: List[Dict[str, str]]
    title: str
    pillar: Optional[str] = "General"  # Content pillar for naming (Leadership, Tech, Growth, etc.)
    theme: Optional[str] = "professional_blue"  # Color theme (professional_blue, elegant_dark, modern_purple, etc.)
    language: Optional[str] = "both"  # Language: english, spanish, or both
    post_id: Optional[str] = None
    save_to_storage: bool = True
    first_slide_image_url: Optional[str] = None  # External image URL for first slide (e.g., news article image)

class AIImageRequest(BaseModel):
    prompt: str
    style: str = "professional"
    post_id: Optional[str] = None
    save_to_storage: bool = True

class InteractiveRequest(BaseModel):
    prompt: str
    title: str
    post_id: Optional[str] = None
    save_to_storage: bool = True

@app.post("/media/generate-interactive")
async def generate_interactive(request: InteractiveRequest):
    """Generate interactive HTML demo"""
    try:
        html_bytes = await media_generator.generate_interactive_html(
            prompt=request.prompt,
            title=request.title
        )
        
        url = None
        if request.save_to_storage and storage_service and request.post_id:
            try:
                url = storage_service.upload_media(
                    html_bytes,
                    request.post_id,
                    "interactive",
                    "html"
                )
            except Exception as e:
                print(f"Storage upload failed: {e}")
        
        if not url:
            url = to_data_uri(html_bytes, "text/html")

        return {"success": True, "url": url, "type": "interactive"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating interactive demo: {str(e)}")

@app.post("/media/generate-code-image")
async def generate_code_image(request: CodeImageRequest):
    """Generate beautiful code snippet image"""
    try:
        img_bytes = media_generator.generate_code_image(
            code=request.code,
            language=request.language,
            theme=request.theme,
            title=request.title
        )
        
        url = None
        if request.save_to_storage and storage_service and request.post_id:
            try:
                url = storage_service.upload_media(
                    img_bytes,
                    request.post_id,
                    "code",
                    "png"
                )
            except Exception as e:
                print(f"Storage upload failed: {e}")
        
        if not url:
            url = to_data_uri(img_bytes, "image/png")

        return {"success": True, "url": url, "type": "code"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating code image: {str(e)}")


@app.post("/media/generate-chart")
async def generate_chart(request: ChartRequest):
    """Generate interactive-style chart"""
    try:
        img_bytes = media_generator.generate_chart(
            chart_type=request.chart_type,
            data=request.data,
            title=request.title,
            theme=request.theme
        )
        
        url = None
        if request.save_to_storage and storage_service and request.post_id:
            try:
                url = storage_service.upload_media(
                    img_bytes,
                    request.post_id,
                    "chart",
                    "png"
                )
            except Exception as e:
                print(f"Storage upload failed: {e}")
        
        if not url:
            url = to_data_uri(img_bytes, "image/png")

        return {"success": True, "url": url, "type": "chart"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating chart: {str(e)}")


@app.post("/media/generate-infographic")
async def generate_infographic(request: InfographicRequest):
    """Generate infographic with statistics"""
    try:
        img_bytes = media_generator.generate_infographic(
            title=request.title,
            stats=request.stats,
            brand_color=request.brand_color
        )
        
        url = None
        if request.save_to_storage and storage_service and request.post_id:
            try:
                url = storage_service.upload_media(
                    img_bytes,
                    request.post_id,
                    "infographic",
                    "png"
                )
            except Exception as e:
                print(f"Storage upload failed: {e}")
        
        if not url:
            url = to_data_uri(img_bytes, "image/png")

        return {"success": True, "url": url, "type": "infographic"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating infographic: {str(e)}")


@app.post("/media/generate-qrcode")
async def generate_qrcode(request: QRCodeRequest):
    """Generate QR code"""
    try:
        img_bytes = media_generator.generate_qr_code(
            url=request.url,
            logo_path=request.logo_path
        )
        
        url = None
        if request.save_to_storage and storage_service and request.post_id:
            try:
                url = storage_service.upload_media(
                    img_bytes,
                    request.post_id,
                    "qrcode",
                    "png"
                )
            except Exception as e:
                print(f"Storage upload failed: {e}")
        
        if not url:
            url = to_data_uri(img_bytes, "image/png")

        return {"success": True, "url": url, "type": "qrcode"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating QR code: {str(e)}")


@app.post("/media/generate-carousel")
async def generate_carousel(request: CarouselRequest):
    """Generate PDF carousel (English, Spanish, or both)"""
    try:
        # Initialize Gemini model for translations
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Determine which languages to generate
        should_generate_english = request.language in ["english", "both"]
        should_generate_spanish = request.language in ["spanish", "both"]
        
        # English generation
        url = None
        filename = None
        local_path = None
        
        if should_generate_english:
            pdf_bytes = media_generator.generate_carousel_pdf(
                slides=request.slides,
                title=request.title,
                theme=request.theme or "professional_blue",
                first_slide_image_url=request.first_slide_image_url
            )
            
            # Create smart filename
            from datetime import datetime
            import re
            
            title_words = request.title.split()[:3]
            short_title = "".join([re.sub(r'[^A-Za-z0-9]', '', word).capitalize() for word in title_words])
            pillar_code = re.sub(r'[^A-Za-z0-9]', '', request.pillar or "General")
            date_str = datetime.now().strftime("%b%d")
            
            filename = f"{short_title}_{pillar_code}_{date_str}_EN.pdf"
            
            # Save locally
            output_dir = os.path.join(os.getcwd(), "GeneratedCarousels")
            os.makedirs(output_dir, exist_ok=True)
            
            local_path = os.path.join(output_dir, filename)
            with open(local_path, 'wb') as f:
                f.write(pdf_bytes)
            
            print(f"✅ English carousel saved: {local_path}")
            
            if request.save_to_storage and storage_service and request.post_id:
                try:
                    url = storage_service.upload_media(pdf_bytes, request.post_id, "carousel", "pdf")
                except Exception as e:
                    print(f"Storage upload failed: {e}")
            
            if not url:
                url = to_data_uri(pdf_bytes, "application/pdf")
        
        # Spanish generation
        url_es = None
        filename_es = None
        local_path_es = None
        
        if should_generate_spanish:
            # Translate slides to Spanish using Gemini
            try:
                translation_prompt = f"""Translate these carousel slides to Spanish (Español). 
Maintain the same structure and formatting. Keep technical terms appropriate for a professional Spanish-speaking audience.

Slides to translate:
{json.dumps(request.slides, indent=2)}

Return ONLY a JSON array of the translated slides in the exact same format."""
                
                print(f"🔄 Translating slides to Spanish...")
                translation_response = model.generate_content(translation_prompt)
                spanish_slides_text = translation_response.text.strip()
                
                print(f"📝 Translation response: {spanish_slides_text[:200]}...")
                
                # Clean markdown code blocks if present
                if spanish_slides_text.startswith('```'):
                    spanish_slides_text = spanish_slides_text.split('```')[1]
                    if spanish_slides_text.startswith('json'):
                        spanish_slides_text = spanish_slides_text[4:]
                    spanish_slides_text = spanish_slides_text.strip()
                
                spanish_slides = json.loads(spanish_slides_text)
                print(f"✅ Parsed {len(spanish_slides)} Spanish slides")
                
                # Generate Spanish PDF (reuses cached images via visual descriptions)
                print(f"🎨 Generating Spanish PDF...")
                pdf_bytes_es = media_generator.generate_carousel_pdf(
                    slides=spanish_slides,
                    title=spanish_slides[0].get('title', request.title) if spanish_slides else request.title,
                    theme=request.theme or "professional_blue",
                    first_slide_image_url=request.first_slide_image_url
                )
                
                # Create filename
                from datetime import datetime
                import re
                
                title_words = request.title.split()[:3]
                short_title = "".join([re.sub(r'[^A-Za-z0-9]', '', word).capitalize() for word in title_words])
                pillar_code = re.sub(r'[^A-Za-z0-9]', '', request.pillar or "General")
                date_str = datetime.now().strftime("%b%d")
                
                filename_es = f"{short_title}_{pillar_code}_{date_str}_ES.pdf"
                
                # Save locally
                output_dir = os.path.join(os.getcwd(), "GeneratedCarousels")
                local_path_es = os.path.join(output_dir, filename_es)
                
                with open(local_path_es, 'wb') as f:
                    f.write(pdf_bytes_es)
                
                print(f"✅ Spanish carousel saved: {local_path_es}")
                
                if request.save_to_storage and storage_service and request.post_id:
                    try:
                        url_es = storage_service.upload_media(pdf_bytes_es, request.post_id, "carousel", "pdf")
                    except Exception as e:
                        print(f"Storage upload failed: {e}")
                
                if not url_es:
                    url_es = to_data_uri(pdf_bytes_es, "application/pdf")
                    print(f"✅ Spanish data URI generated (length: {len(url_es)})")
                    
            except Exception as e:
                print(f"❌ ERROR: Spanish carousel generation failed: {str(e)}")
                import traceback
                traceback.print_exc()
                # Don't fail the whole request, just skip Spanish version
        
        # If Spanish-only was requested, move Spanish to main response
        if request.language == "spanish":
            url = url_es
            filename = filename_es
            local_path = local_path_es
        
        return {
            "success": True,
            "url": url,
            "filename": filename,
            "local_path": local_path,
            "url_es": url_es if request.language == "both" else None,
            "filename_es": filename_es if request.language == "both" else None,
            "local_path_es": local_path_es if request.language == "both" else None,
            "type": "carousel"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating carousel: {str(e)}")


@app.post("/media/generate-ai-image")
async def generate_ai_image(request: AIImageRequest):
    """Generate AI-powered image (placeholder)"""
    try:
        img_bytes = await media_generator.generate_ai_image(
            prompt=request.prompt,
            style=request.style
        )
        
        url = None
        if request.save_to_storage and storage_service and request.post_id:
            try:
                url = storage_service.upload_media(
                    img_bytes,
                    request.post_id,
                    "ai-image",
                    "png"
                )
            except Exception as e:
                print(f"Storage upload failed: {e}")
        
        if not url:
            url = to_data_uri(img_bytes, "image/png")

        return {"success": True, "url": url, "type": "ai-image"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating AI image: {str(e)}")


@app.get("/media/list/{post_id}")
async def list_post_media(post_id: str):
    """List all media assets for a post"""
    try:
        if not storage_service:
            return {"media": []}
        
        files = storage_service.list_post_media(post_id)
        return {"post_id": post_id, "media": files}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing media: {str(e)}")

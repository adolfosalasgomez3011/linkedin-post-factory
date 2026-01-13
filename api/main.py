from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://192.168.68.84:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

class PostRequest(BaseModel):
    pillar: str
    post_type: str = "standard"
    format_type: str
    topic: Optional[str] = None
    provider: str = "gemini"

class PostResponse(BaseModel):
    content: str
    voice_score: float
    hashtags: list[str]

@app.get("/")
async def root():
    return {"message": "LinkedIn Post Factory API", "status": "running"}

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
            if request.post_type == "carousel":
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

            # Create prompt
            prompt = f"""Generate a LinkedIn post with the following specifications:

Content Pillar: {request.pillar}
Post Type: {request.post_type}
Format: {request.format_type}
Topic: {request.topic}

Requirements:
- Write in a professional yet engaging tone
- Keep it concise (under 1300 characters)
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
            
            return PostResponse(
                content=final_content,
                voice_score=round(voice_score, 1),
                hashtags=hashtags[:5] if hashtags else ["#LinkedIn", "#Professional"]
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
    post_id: Optional[str] = None
    save_to_storage: bool = True

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
    """Generate PDF carousel"""
    try:
        pdf_bytes = media_generator.generate_carousel_pdf(
            slides=request.slides,
            title=request.title,
            theme=request.theme or "professional_blue"
        )
        
        # Create smart filename: ShortTitle_Pillar_DateShort
        from datetime import datetime
        import re
        
        # Clean title - take first 3-4 words, remove special chars
        title_words = request.title.split()[:3]
        short_title = "".join([re.sub(r'[^A-Za-z0-9]', '', word).capitalize() for word in title_words])
        
        # Pillar code
        pillar_code = re.sub(r'[^A-Za-z0-9]', '', request.pillar or "General")
        
        # Date: Jan13 format
        date_str = datetime.now().strftime("%b%d")
        
        # Final filename
        filename = f"{short_title}_{pillar_code}_{date_str}.pdf"
        
        # Save locally to GeneratedCarousels folder
        output_dir = os.path.join(os.getcwd(), "GeneratedCarousels")
        os.makedirs(output_dir, exist_ok=True)
        
        local_path = os.path.join(output_dir, filename)
        with open(local_path, 'wb') as f:
            f.write(pdf_bytes)
        
        print(f"✅ Carousel saved: {local_path}")
        
        url = None
        if request.save_to_storage and storage_service and request.post_id:
            try:
                url = storage_service.upload_media(
                    pdf_bytes,
                    request.post_id,
                    "carousel",
                    "pdf"
                )
            except Exception as e:
                print(f"Storage upload failed: {e}")

        if not url:
            url = to_data_uri(pdf_bytes, "application/pdf")
            
        return {
            "success": True, 
            "url": url,
            "filename": filename, 
            "type": "carousel",
            "filename": filename,
            "local_path": local_path
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

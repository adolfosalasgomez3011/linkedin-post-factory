"""
Media Asset Generation Service
Generates stunning visual assets for LinkedIn posts
"""
import io
import base64
import time
from typing import Dict, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import ImageFormatter
from pygments.styles import get_style_by_name
import qrcode
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import google.generativeai as genai
import os
import requests
import tempfile
import re
import subprocess
import json


class MediaGenerator:
    """Generate beautiful visual assets for LinkedIn posts"""
    
    # Color themes for carousel PDFs
    COLOR_THEMES = {
        'professional_blue': {
            'bg': '#0F172A',
            'accent': '#3B82F6',
            'text': '#F8FAFC',
            'dim': '#94A3B8'
        },
        'elegant_dark': {
            'bg': '#1A1A1A',
            'accent': '#00D4AA',
            'text': '#FFFFFF',
            'dim': '#888888'
        },
        'modern_purple': {
            'bg': '#1E1B4B',
            'accent': '#A78BFA',
            'text': '#F3F4F6',
            'dim': '#9CA3AF'
        },
        'corporate_red': {
            'bg': '#1F1B1B',
            'accent': '#EF4444',
            'text': '#FAFAFA',
            'dim': '#A1A1AA'
        },
        'nature_green': {
            'bg': '#0A2E1C',
            'accent': '#10B981',
            'text': '#F0FDF4',
            'dim': '#86EFAC'
        },
        'sunset_orange': {
            'bg': '#1C1917',
            'accent': '#F97316',
            'text': '#FAFAF9',
            'dim': '#A8A29E'
        }
    }
    
    def __init__(self):
        self.base_width = 1200
        self.base_height = 630  # LinkedIn optimal image size
        
    def generate_code_image(
        self,
        code: str,
        language: str = "python",
        theme: str = "monokai",
        title: Optional[str] = None
    ) -> bytes:
        """
        Generate beautiful code snippet image
        
        Args:
            code: Source code to visualize
            language: Programming language (python, javascript, java, etc.)
            theme: Pygments theme (monokai, github-dark, dracula, etc.)
            title: Optional title above code
            
        Returns:
            PNG image bytes
        """
        try:
            lexer = get_lexer_by_name(language, stripall=True)
        except:
            lexer = guess_lexer(code)
        
        # Generate code image with syntax highlighting
        formatter = ImageFormatter(
            style=theme,
            line_numbers=True,
            font_size=16,
            line_pad=6
        )
        
        code_img_data = highlight(code, lexer, formatter)
        code_img = Image.open(io.BytesIO(code_img_data))
        
        # Create canvas with padding and title
        padding = 60
        title_height = 80 if title else 0
        canvas_width = self.base_width
        canvas_height = code_img.height + (padding * 2) + title_height
        
        # Create gradient background
        canvas_img = Image.new('RGB', (canvas_width, canvas_height), '#1e1e1e')
        draw = ImageDraw.Draw(canvas_img)
        
        # Add gradient effect
        for y in range(canvas_height):
            color_val = int(30 + (y / canvas_height) * 20)
            draw.line([(0, y), (canvas_width, y)], fill=(color_val, color_val, color_val))
        
        # Add title if provided
        if title:
            try:
                font = ImageFont.truetype("arial.ttf", 32)
            except:
                font = ImageFont.load_default()
            
            draw.text(
                (padding, padding // 2),
                title,
                fill='#ffffff',
                font=font
            )
        
        # Paste code image
        code_x = (canvas_width - code_img.width) // 2
        code_y = padding + title_height
        canvas_img.paste(code_img, (code_x, code_y))
        
        # Add subtle border
        draw.rectangle(
            [(5, 5), (canvas_width - 5, canvas_height - 5)],
            outline='#4a9eff',
            width=3
        )
        
        # Convert to bytes
        output = io.BytesIO()
        canvas_img.save(output, format='PNG', quality=95)
        return output.getvalue()
    
    def generate_chart(
        self,
        chart_type: str,
        data: Dict,
        title: str,
        theme: str = "plotly_dark"
    ) -> bytes:
        """
        Generate interactive-style chart image
        
        Args:
            chart_type: bar, line, pie, scatter, area, funnel
            data: Chart data {'labels': [...], 'values': [...], 'x': [...], 'y': [...]}
            title: Chart title
            theme: Plotly theme
            
        Returns:
            PNG image bytes
        """
        fig = None
        
        if chart_type == "bar":
            fig = go.Figure(data=[
                go.Bar(
                    x=data.get('labels', []),
                    y=data.get('values', []),
                    marker_color='#4a9eff',
                    text=data.get('values', []),
                    textposition='auto',
                )
            ])
        
        elif chart_type == "line":
            fig = go.Figure(data=[
                go.Scatter(
                    x=data.get('x', []),
                    y=data.get('y', []),
                    mode='lines+markers',
                    line=dict(color='#4a9eff', width=3),
                    marker=dict(size=10)
                )
            ])
        
        elif chart_type == "pie":
            fig = go.Figure(data=[
                go.Pie(
                    labels=data.get('labels', []),
                    values=data.get('values', []),
                    hole=0.3,
                    marker=dict(colors=px.colors.qualitative.Vivid)
                )
            ])
        
        elif chart_type == "scatter":
            fig = go.Figure(data=[
                go.Scatter(
                    x=data.get('x', []),
                    y=data.get('y', []),
                    mode='markers',
                    marker=dict(
                        size=data.get('sizes', 12),
                        color=data.get('colors', '#4a9eff'),
                        opacity=0.8
                    )
                )
            ])
        
        elif chart_type == "area":
            fig = go.Figure(data=[
                go.Scatter(
                    x=data.get('x', []),
                    y=data.get('y', []),
                    fill='tozeroy',
                    fillcolor='rgba(74, 158, 255, 0.3)',
                    line=dict(color='#4a9eff', width=2)
                )
            ])
        
        elif chart_type == "funnel":
            fig = go.Figure(data=[
                go.Funnel(
                    y=data.get('labels', []),
                    x=data.get('values', []),
                    textposition="inside",
                    textinfo="value+percent initial",
                    marker=dict(color=px.colors.sequential.Blues_r)
                )
            ])
        
        if fig:
            fig.update_layout(
                title=dict(text=title, font=dict(size=24)),
                template=theme,
                width=self.base_width,
                height=self.base_height,
                showlegend=True,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(30,30,30,1)'
            )
            
            # Convert to image bytes
            img_bytes = fig.to_image(format="png", engine="kaleido")
            return img_bytes
        
        raise ValueError(f"Unsupported chart type: {chart_type}")
    
    def generate_infographic(
        self,
        title: str,
        stats: List[Dict[str, str]],
        brand_color: str = "#4a9eff"
    ) -> bytes:
        """
        Generate infographic with key statistics
        
        Args:
            title: Main title
            stats: List of {'label': 'X', 'value': 'Y'} dicts
            brand_color: Primary color hex
            
        Returns:
            PNG image bytes
        """
        img = Image.new('RGB', (self.base_width, self.base_height), '#1e1e1e')
        draw = ImageDraw.Draw(img)
        
        # Gradient background
        for y in range(self.base_height):
            factor = y / self.base_height
            r = int(30 + factor * 20)
            g = int(30 + factor * 20)
            b = int(50 + factor * 30)
            draw.line([(0, y), (self.base_width, y)], fill=(r, g, b))
        
        try:
            title_font = ImageFont.truetype("arialbd.ttf", 48)
            label_font = ImageFont.truetype("arial.ttf", 28)
            value_font = ImageFont.truetype("arialbd.ttf", 42)
        except:
            title_font = ImageFont.load_default()
            label_font = ImageFont.load_default()
            value_font = ImageFont.load_default()
        
        # Draw title
        draw.text((60, 50), title, fill='#ffffff', font=title_font)
        
        # Draw stats in grid
        stats_per_row = 3
        stat_width = (self.base_width - 120) // stats_per_row
        stat_height = 200
        start_y = 180
        
        for idx, stat in enumerate(stats[:6]):  # Max 6 stats
            row = idx // stats_per_row
            col = idx % stats_per_row
            
            x = 60 + (col * stat_width)
            y = start_y + (row * stat_height)
            
            # Draw stat box
            box_coords = [x, y, x + stat_width - 40, y + stat_height - 40]
            draw.rounded_rectangle(
                box_coords,
                radius=15,
                fill='#2a2a2a',
                outline=brand_color,
                width=3
            )
            
            # Draw value (large)
            value = stat.get('value', '')
            label = stat.get('label', '')
            
            value_bbox = draw.textbbox((0, 0), value, font=value_font)
            value_width = value_bbox[2] - value_bbox[0]
            value_x = x + (stat_width - 40 - value_width) // 2
            draw.text((value_x, y + 40), value, fill=brand_color, font=value_font)
            
            # Draw label (small)
            label_bbox = draw.textbbox((0, 0), label, font=label_font)
            label_width = label_bbox[2] - label_bbox[0]
            label_x = x + (stat_width - 40 - label_width) // 2
            draw.text((label_x, y + 110), label, fill='#cccccc', font=label_font)
        
        # Convert to bytes
        output = io.BytesIO()
        img.save(output, format='PNG', quality=95)
        return output.getvalue()
    
    def generate_qr_code(
        self,
        url: str,
        logo_path: Optional[str] = None
    ) -> bytes:
        """
        Generate QR code with optional logo
        
        Args:
            url: Target URL
            logo_path: Optional path to logo image
            
        Returns:
            PNG image bytes
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="#000000", back_color="#ffffff")
        img = img.convert('RGB')
        
        # Add logo if provided
        if logo_path and os.path.exists(logo_path):
            logo = Image.open(logo_path)
            logo_size = img.size[0] // 4
            logo = logo.resize((logo_size, logo_size))
            
            logo_pos = ((img.size[0] - logo_size) // 2, (img.size[1] - logo_size) // 2)
            img.paste(logo, logo_pos)
        
        # Convert to bytes
        output = io.BytesIO()
        img.save(output, format='PNG')
        return output.getvalue()
    
    def _generate_svg_visual(self, title: str):
        """
        Generate an abstract tech illustration using ReportLab primitives directly from AI JSON data.
        Bypasses SVG parsing for maximum reliability.
        """
        try:
            # 1. Configuration Check
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                print("DEBUG: GOOGLE_API_KEY missing, using fallback visual.")
                return self._create_fallback_visual(title)
            
            genai.configure(api_key=api_key)

            # 2. AI Generation - Requesting JSON Data
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"""
            You are a data visualization engine.
            Task: Create an abstract geometric composition for '{title}'.
            
            OUTPUT RULES:
            1. Return ONLY valid JSON.
            2. Structure: A list of objects.
            3. Property "type" must be one of: "rect", "circle", "line".
            4. Coordinate space: 500x300.
            5. Colors: Use Hex strings (#3B82F6, #10B981, #F472B6, #E2E8F0).
            
            Required properties per type:
            - rect: x, y, width, height, color, opacity (0.0-1.0)
            - circle: cx, cy, r, color, opacity
            - line: x1, y1, x2, y2, color, width (stroke width)
            
            Example output:
            [
              {{"type": "rect", "x": 50, "y": 50, "width": 100, "height": 100, "color": "#3B82F6", "opacity": 0.8}},
              {{"type": "circle", "cx": 200, "cy": 150, "r": 40, "color": "#10B981", "opacity": 1.0}}
            ]
            """
            
            print(f"DEBUG: Generating Visual Data for '{title}'...")
            response = model.generate_content(prompt)
            raw_text = response.text.strip()
            
            # Clean JSON
            json_text = raw_text.replace("```json", "").replace("```", "").strip()
            
            import json
            shapes_data = json.loads(json_text)
            
            # 3. Construct ReportLab Drawing
            from reportlab.graphics.shapes import Drawing, Rect, Circle, Line
            from reportlab.lib import colors as rl_colors
            
            drawing = Drawing(500, 300)
            
            for shape in shapes_data:
                try:
                    s_type = shape.get("type")
                    color_hex = shape.get("color", "#CCCCCC")
                    c = colors.HexColor(color_hex)
                    # Apply opacity if present (ReportLab Color supports alpha in recent versions, or use fillOpacity)
                    # Note: ReportLab alpha support varies, strictly it's best to keep solid or handle carefully.
                    # We will just use the color.
                    
                    if s_type == "rect":
                        r = Rect(shape['x'], shape['y'], shape['width'], shape['height'])
                        r.fillColor = c
                        r.strokeColor = None
                        drawing.add(r)
                    
                    elif s_type == "circle":
                        # Note: ReportLab Circle takes (cx, cy, r)
                        circ = Circle(shape['cx'], shape['cy'], shape['r'])
                        circ.fillColor = c
                        circ.strokeColor = None
                        drawing.add(circ)
                        
                    elif s_type == "line":
                        l = Line(shape['x1'], shape['y1'], shape['x2'], shape['y2'])
                        l.strokeColor = c
                        l.strokeWidth = shape.get('width', 2)
                        drawing.add(l)
                        
                except Exception as e:
                    print(f"DEBUG: Skipping invalid shape {shape}: {e}")
                    continue
            
            # --- NEW: Save artifact for verification ---
            try:
                from reportlab.graphics import renderPM
                output_dir = os.path.join(os.getcwd(), "GeminiImages")
                os.makedirs(output_dir, exist_ok=True)
                
                # Sanitize filename
                safe_title = "".join([c for c in title if c.isalnum() or c in (' ','-','_')]).strip()
                filename = f"gemini_gen_{safe_title[:30]}_{int(time.time())}.png"
                filepath = os.path.join(output_dir, filename)
                
                renderPM.drawToFile(drawing, filepath, fmt="PNG")
                print(f"DEBUG: Saved generated image to {filepath}")
            except Exception as save_err:
                print(f"DEBUG: Could not save PNG artifact: {save_err}")
                import traceback
                traceback.print_exc()
            # -------------------------------------------

            print(f"DEBUG: Successfully created JSON-based drawing for '{title}'")
            return drawing

        except Exception as e:
            print(f"DEBUG: AI generation failed ({e}), using fallback.")
            # import traceback
            # traceback.print_exc()
            return self._create_fallback_visual(title)

    def _create_fallback_visual(self, title: str):
        """Create a procedural geometric pattern (fallback)"""
        from reportlab.graphics.shapes import Drawing, Circle, Rect
        from reportlab.lib import colors
        import random
        
        d = Drawing(500, 300)
        # Random geometric elements
        for _ in range(8):
            x = random.randint(50, 450)
            y = random.randint(50, 250)
            size = random.randint(20, 80)
            color = random.choice(['#3B82F6', '#10B981', '#F472B6', '#64748B'])
            opacity = 0.3
            
            # Mix of circles and rects
            if random.random() > 0.5:
                # Note: ReportLab shapes don't support hex strings directly in fillOpacity, 
                # but we can use HexColor
                c = Circle(x, y, size/2, fillColor=colors.HexColor(color), strokeColor=None)
                # Hack for opacity if not supported directly in properties:
                # ReportLab standard shapes might not support alpha easily without extended states,
                # so we stick to solid or dim colors
                d.add(c)
            else:
                r = Rect(x, y, size, size, fillColor=colors.HexColor(color), strokeColor=None)
                d.add(r)
        return d

    def generate_carousel_pdf(
        self,
        slides: List[Dict[str, str]],
        title: str,
        theme: str = 'professional_blue'
    ) -> bytes:
        """
        Generate professional multi-page PDF carousel with AI-generated visuals
        
        Args:
            slides: List of slide dictionaries with 'title' and 'content'
            title: Overall carousel title
            theme: Color theme name (professional_blue, elegant_dark, modern_purple, etc.)
        """
        
        # LinkedIn Portrait 4:5
        page_width = 600
        page_height = 750
        
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=(page_width, page_height))
        
        # Get theme colors
        theme_colors = self.COLOR_THEMES.get(theme, self.COLOR_THEMES['professional_blue'])
        bg_color = colors.HexColor(theme_colors['bg'])
        accent_color = colors.HexColor(theme_colors['accent'])
        text_color = colors.HexColor(theme_colors['text'])
        dim_text = colors.HexColor(theme_colors['dim'])
        
        for idx, slide in enumerate(slides):
            # 1. Background
            c.setFillColor(bg_color)
            c.rect(0, 0, page_width, page_height, fill=1)
            
            # 2. Professional Header
            c.setFillColor(accent_color)
            c.rect(0, page_height - 10, page_width, 10, fill=1)
            
            # Page counter - subtle and elegant
            c.setFillColor(dim_text)
            c.setFont("Helvetica", 10)
            c.drawCentredString(page_width - 35, page_height - 28, f"{idx + 1}/{len(slides)}")

            # Check if this is a cover slide (no body content after removing visual prompt)
            slide_title = slide.get('title', f'Slide {idx + 1}')
            raw_content = slide.get('content', '').strip()
            import re
            content_no_visual = re.sub(r'\(Visual:\s*[^)]+\)', '', raw_content, flags=re.IGNORECASE).strip()
            is_cover_slide = not content_no_visual or idx == 0
            
            # Uppercase title on cover slides for impact
            if is_cover_slide:
                slide_title = slide_title.upper()
            
            c.setFillColor(text_color)
            
            # Position title with proper spacing from image
            if is_cover_slide:
                # Cover slide - higher position with padding above image
                title_y_pos = page_height - 150  # More space above image
            else:
                # Regular slide - standard top position
                title_y_pos = page_height - 58
            
            # Dynamic font sizing and wrapping for long titles
            if len(slide_title) > 50:
                # Very long - wrap to 2 lines
                c.setFont("Helvetica-Bold", 18)
                words = slide_title.split()
                line1 = " ".join(words[:len(words)//2])
                line2 = " ".join(words[len(words)//2:])
                if is_cover_slide:
                    c.drawCentredString(page_width / 2, title_y_pos + 30, line1)
                    c.drawCentredString(page_width / 2, title_y_pos, line2)
                else:
                    c.drawCentredString(page_width / 2, page_height - 50, line1)
                    c.drawCentredString(page_width / 2, page_height - 72, line2)
            elif len(slide_title) > 35:
                c.setFont("Helvetica-Bold", 22)
                c.drawCentredString(page_width / 2, title_y_pos, str(slide_title))
            elif len(slide_title) > 25:
                c.setFont("Helvetica-Bold", 26)
                c.drawCentredString(page_width / 2, title_y_pos, str(slide_title))
            else:
                c.setFont("Helvetica-Bold", 32)
                c.drawCentredString(page_width / 2, title_y_pos, str(slide_title))

            # 3. Dynamic Visual (Gemini 2.5 Flash Image generated AI image)
            # Area: x=50, y=page_height-380, w=500, h=300
            
            # Extract content and parse structure
            content_text = slide.get('content', '').strip()
            
            # Extract visual prompt if present
            import re
            visual_match = re.search(r'\(Visual:\s*([^)]+)\)', content_text, re.IGNORECASE)
            
            # Determine image generation strategy
            should_generate_image = False
            image_prompt_text = ""
            
            if visual_match:
                # Has explicit visual prompt
                image_prompt_text = visual_match.group(1).strip()
                should_generate_image = True
            elif content_text and len(content_text) > 10:
                # Has body text - use it for image concept
                image_prompt_text = content_text.split('.')[0][:100]  # First sentence
                should_generate_image = True
            elif idx == 0:
                # First slide (cover) - use title for generic professional image
                image_prompt_text = f"Professional corporate background related to {slide_title}"
                should_generate_image = True
            else:
                # No content, not cover - generic professional image
                image_prompt_text = f"Professional business concept for {slide_title}"
                should_generate_image = True
            
            try:
                if should_generate_image:
                    # Generate real AI image using Gemini 2.5 Flash Image
                    # CRITICAL: Image should NEVER contain the slide title text
                    # Theme-aware: Include background color for harmonic integration
                    theme_hint = f"Background color palette: {theme_colors['bg']} with {theme_colors['accent']} accents."
                    image_prompt = f"Professional LinkedIn visual: {image_prompt_text}. {theme_hint} Create a high-quality, photorealistic image that complements these colors. Modern, corporate style. DO NOT include any text or words in the image."
                    image_bytes = self._generate_ai_image_sync(image_prompt)
                
                if image_bytes:
                    # Load image from bytes
                    from PIL import Image
                    
                    img = Image.open(io.BytesIO(image_bytes))
                    
                    # FIT image within bounds - preserve full image, no cropping
                    max_width, max_height = 500, 300
                    img_ratio = img.width / img.height
                    box_ratio = max_width / max_height
                    
                    # Calculate dimensions to fit within box while preserving aspect ratio
                    if img_ratio > box_ratio:
                        # Image is wider - fit to width
                        new_width = max_width
                        new_height = int(max_width / img_ratio)
                    else:
                        # Image is taller - fit to height
                        new_height = max_height
                        new_width = int(max_height * img_ratio)
                    
                    # Resize image to fit (no cropping)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # Save to temporary file for reportlab
                    temp_img_path = f"temp_carousel_img_{idx}.png"
                    img.save(temp_img_path)
                    
                    # Draw image - position depends on whether it's a cover slide
                    # Center the image within the box area
                    x_offset = 50 + (max_width - new_width) // 2
                    
                    if is_cover_slide:
                        # Cover slide - vertically centered
                        image_y = page_height - 480 + (max_height - new_height) // 2
                    else:
                        # Regular slide - standard position
                        image_y = page_height - 380 + (max_height - new_height) // 2
                    
                    c.drawImage(temp_img_path, x_offset, image_y, width=new_width, height=new_height)
                    
                    # Clean up temp file
                    import os
                    os.remove(temp_img_path)
                else:
                     raise Exception("No image generated")
            except Exception as e:
                # Error fallback - draw subtle box with message
                c.setFillColor(colors.HexColor('#1E293B'))
                c.rect(50, page_height - 380, 500, 300, fill=1, stroke=0)
                c.setFillColor(dim_text)
                c.drawCentredString(page_width/2, page_height - 230, "[Image generation failed]")

            # 4. Professional Content - Beautiful bullets filling the page
            c.setFillColor(text_color)
            c.setFont("Helvetica", 16)
            
            # Get content and clean it
            content = slide.get('content', '').strip()
            
            # Remove visual prompt text - don't display (Visual: ...) in PDF
            content = re.sub(r'\(Visual:\s*[^)]+\)', '', content, flags=re.IGNORECASE).strip()
            
            # Remove markdown symbols: asterisks, hashes, underscores
            content = content.replace('*', '').replace('#', '').replace('_', '').strip()
            
            # CRITICAL: Don't show title as body text
            # If content is empty or same as title, show nothing
            if not content or content.lower() == slide_title.lower():
                content = ""
            
            # Split into bullet points
            max_chars_per_line = 45  # Slightly shorter for bullets
            bullet_points = []
            
            if content:
                # Split by newlines or periods to create natural bullet points
                raw_points = [p.strip() for p in content.replace('\n', '. ').split('.') if p.strip()]
                
                # Wrap each point if too long
                for point in raw_points[:6]:  # Max 6 bullet points
                    # Skip if point is same as title
                    if point.lower() == slide_title.lower():
                        continue
                        
                    if len(point) > max_chars_per_line:
                        # Wrap long points
                        words = point.split()
                        current_line = ""
                        wrapped_lines = []
                        for word in words:
                            if len(current_line) + len(word) + 1 <= max_chars_per_line:
                                current_line += (word + " ")
                            else:
                                if current_line:
                                    wrapped_lines.append(current_line.strip())
                                current_line = word + " "
                        if current_line.strip():
                            wrapped_lines.append(current_line.strip())
                        bullet_points.extend(wrapped_lines)
                    else:
                        bullet_points.append(point)

            # Start text position (will be used for bullets or footer check)
            text_start_y = page_height - 420
            
            # Only show bullets if we have content
            if bullet_points:
                # Dynamic spacing to fill page better
                available_height = text_start_y - 80  # Space until footer
                total_bullets = len(bullet_points[:12])  # Max 12 lines to fill page
                line_spacing = min(32, available_height // max(total_bullets, 1)) if total_bullets > 0 else 32
                
                # Left-aligned bullets with beautiful style
                bullet_x_start = 80  # Left margin for bullet
                text_x_start = 110   # Text starts after bullet
                
                for i, point in enumerate(bullet_points[:12]):  # Show up to 12 lines to fill page
                    # Draw elegant bullet point
                    c.setFillColor(accent_color)
                    c.circle(bullet_x_start, text_start_y + 5, 4, fill=1, stroke=0)
                    
                    # Draw text
                    c.setFillColor(text_color)
                    c.setFont("Helvetica", 16)
                    c.drawString(text_x_start, text_start_y, point.strip())
                    text_start_y -= line_spacing
            
            # Add subtle branded footer text
            c.setFillColor(dim_text)
            c.setFont("Helvetica", 9)
            c.drawCentredString(page_width / 2, 25, "LINKEDIN.COM/IN/LEARN")
            
            # 5. Footer
            c.setFillColor(accent_color)
            c.rect(0, 0, page_width, 10, fill=1)
            
            c.showPage()
        
        c.save()
        return buffer.getvalue()
    
    async def generate_interactive_html(
        self,
        prompt: str,
        title: str = "Interactive Demo"
    ) -> bytes:
        """
        Generate a self-contained interactive HTML file using AI
        """
        try:
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            system_prompt = f"""
            Create a single-file, self-contained HTML/JS/CSS interactive component.
            Topic: {title}
            Description of functionality: {prompt}
            
            Requirements:
            - Must be a single HTML file with embedded CSS and JS.
            - Design: Modern, professional, clean (like Stripe or Linear docs).
            - Use Tailwind CSS (include via CDN: <script src="https://cdn.tailwindcss.com"></script>).
            - Make it fully functional and interactive (buttons work, calcs work, etc.).
            - Do not include markdown formatting (like ```html), just return the raw HTML.
            """
            
            response = model.generate_content(system_prompt)
            html_content = response.text
            
            # Clean up markdown if present
            if "```" in html_content:
                html_content = html_content.replace("```html", "").replace("```", "")
            
            return html_content.encode('utf-8')
        except Exception as e:
            print(f"Error generating HTML: {e}")
            fallback = f"<html><body><h1>Generation Error</h1><p>{str(e)}</p></body></html>"
            return fallback.encode('utf-8')

    def _generate_ai_image_sync(
        self,
        prompt: str,
        style: str = "professional"
    ) -> bytes:
        """
        Synchronous version of generate_ai_image for use in PDF generation
        
        Returns: Image bytes (PNG, 1024x1024)
        """
        try:
            # Enhance prompt with style
            style_modifiers = {
                "professional": "Professional, clean, corporate style. High quality, modern design.",
                "artistic": "Artistic, creative, visually striking. Bold colors and unique composition.",
                "technical": "Technical, precise, clear diagrams. Clean lines and professional appearance.",
                "minimal": "Minimalist, simple, elegant. Clean design with focus on key elements."
            }
            
            enhanced_prompt = f"{prompt}. {style_modifiers.get(style, style_modifiers['professional'])}"
            
            # Save to GeminiImages directory
            output_dir = os.path.join(os.getcwd(), "GeminiImages")
            os.makedirs(output_dir, exist_ok=True)
            
            # Create unique filename
            import re
            safe_prompt = re.sub(r'[^\w\s-]', '', prompt)[:40].strip().replace(' ', '_')
            timestamp = int(time.time())
            filename = f"ai_gen_{safe_prompt}_{timestamp}.png"
            filepath = os.path.join(output_dir, filename)
            
            print(f"🎨 Generating real AI image with Gemini 2.5 Flash Image...")
            print(f"📝 Prompt: {enhanced_prompt[:100]}...")
            
            # Use Gemini 2.5 Flash Image API
            import google.generativeai as genai
            
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                raise Exception("GOOGLE_API_KEY not found in environment")
            
            genai.configure(api_key=api_key)
            
            model = genai.GenerativeModel('gemini-2.5-flash-image')
            response = model.generate_content(enhanced_prompt)
            
            # Extract image from response
            if hasattr(response, 'parts'):
                for part in response.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        inline = part.inline_data
                        if hasattr(inline, 'data') and inline.data:
                            # Save image
                            with open(filepath, 'wb') as f:
                                f.write(inline.data)
                            
                            file_size = os.path.getsize(filepath)
                            print(f"✅ Real AI image generated: {file_size:,} bytes")
                            print(f"📁 Saved to: {filepath}")
                            
                            return inline.data
            
            raise Exception("No image data in response")
                
        except Exception as e:
            print(f"❌ Error generating AI image: {e}")
            raise

    async def generate_ai_image(
        self,
        prompt: str,
        style: str = "professional"
    ) -> bytes:
        """
        Generate REAL AI images using Gemini 2.5 Flash Image API
        
        Returns: Image bytes (PNG, 1024x1024)
        """
        try:
            # Enhance prompt with style
            style_modifiers = {
                "professional": "Professional, clean, corporate style. High quality, modern design.",
                "artistic": "Artistic, creative, visually striking. Bold colors and unique composition.",
                "technical": "Technical, precise, clear diagrams. Clean lines and professional appearance.",
                "minimal": "Minimalist, simple, elegant. Clean design with focus on key elements."
            }
            
            enhanced_prompt = f"{prompt}. {style_modifiers.get(style, style_modifiers['professional'])}"
            
            # Save to GeminiImages directory
            output_dir = os.path.join(os.getcwd(), "GeminiImages")
            os.makedirs(output_dir, exist_ok=True)
            
            # Create unique filename
            safe_prompt = re.sub(r'[^\w\s-]', '', prompt)[:40].strip().replace(' ', '_')
            timestamp = int(time.time())
            filename = f"ai_gen_{safe_prompt}_{timestamp}.png"
            filepath = os.path.join(output_dir, filename)
            
            print(f"🎨 Generating real AI image with Gemini 2.5 Flash Image...")
            print(f"📝 Prompt: {enhanced_prompt[:100]}...")
            
            # Use Gemini 2.5 Flash Image API
            import google.generativeai as genai
            
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                raise Exception("GOOGLE_API_KEY not found in environment")
            
            genai.configure(api_key=api_key)
            
            model = genai.GenerativeModel('gemini-2.5-flash-image')
            response = model.generate_content(enhanced_prompt)
            
            # Extract image from response
            if hasattr(response, 'parts'):
                for part in response.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        inline = part.inline_data
                        if hasattr(inline, 'data') and inline.data:
                            # Save image
                            with open(filepath, 'wb') as f:
                                f.write(inline.data)
                            
                            file_size = os.path.getsize(filepath)
                            print(f"✅ Real AI image generated: {file_size:,} bytes")
                            print(f"📁 Saved to: {filepath}")
                            
                            return inline.data
            
            raise Exception("No image data in response")
                
        except Exception as e:
            print(f"❌ Error generating AI image: {e}")
            raise
    
    def _create_placeholder_with_instructions(self, prompt: str, filename: str) -> bytes:
        """Create placeholder image with instructions for manual generation"""
        try:
            width, height = 1024, 1024
            img = Image.new('RGB', (width, height), '#f0f4f8')
            draw = ImageDraw.Draw(img)
            
            # Draw border
            border_color = '#4285f4'
            draw.rectangle([20, 20, width-20, height-20], outline=border_color, width=4)
            
            # Load fonts
            try:
                title_font = ImageFont.truetype("arial.ttf", 44)
                text_font = ImageFont.truetype("arial.ttf", 24)
                small_font = ImageFont.truetype("arial.ttf", 18)
            except:
                title_font = ImageFont.load_default()
                text_font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            
            # Title
            draw.text((width // 2, 100), "🎨 IMAGE PLACEHOLDER", fill='#1a1a1a', font=title_font, anchor="mm")
            
            # Instructions
            instructions = [
                "📝 Open the prompt file in GeminiImages folder",
                "📋 Copy the Gemini prompt",
                "🚀 Generate in VS Code with MCP tool",
                f"💾 Save as: {filename}.png",
                "✅ Carousel will use your image!"
            ]
            
            y = 200
            for line in instructions:
                draw.text((width // 2, y), line, fill='#333333', font=text_font, anchor="mm")
                y += 50
            
            # Prompt preview (truncated)
            y += 50
            draw.text((width // 2, y), "Prompt Preview:", fill='#666666', font=small_font, anchor="mm")
            y += 30
            
            # Wrap prompt text
            words = prompt.split()
            lines = []
            current_line = []
            for word in words:
                current_line.append(word)
                if len(' '.join(current_line)) > 60:
                    lines.append(' '.join(current_line[:-1]))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))
            
            for line in lines[:4]:
                draw.text((width // 2, y), line, fill='#888888', font=small_font, anchor="mm")
                y += 25
            
            # Save to bytes
            output = io.BytesIO()
            img.save(output, format='PNG')
            return output.getvalue()
            
        except Exception as e:
            print(f"Error creating placeholder: {e}")
            # Simple fallback
            img = Image.new('RGB', (1024, 1024), '#e0e0e0')
            draw = ImageDraw.Draw(img)
            draw.text((512, 512), "Image Placeholder", fill='#000000', anchor="mm")
            output = io.BytesIO()
            img.save(output, format='PNG')
            return output.getvalue()
    
    async def _generate_via_api(
        self,
        prompt: str,
        filepath: str
    ) -> bytes:
        """
        Fallback: Try Google AI image generation, then styled placeholder
        """
        # First, try to use Google's Imagen API for real AI generation
        try:
            import google.generativeai as genai
            
            api_key = os.getenv('GOOGLE_API_KEY')
            if api_key:
                print(f"🎨 Attempting real AI generation via Google Imagen...")
                genai.configure(api_key=api_key)
                
                # Try Imagen model
                try:
                    model = genai.GenerativeModel('imagen-3.0-generate-001')
                    response = model.generate_images(
                        prompt=prompt,
                        number_of_images=1,
                        aspect_ratio="1:1"
                    )
                    
                    if response.images:
                        # Save the first image
                        response.images[0]._pil_image.save(filepath, format='PNG')
                        print(f"✅ Real AI image generated successfully!")
                        with open(filepath, 'rb') as f:
                            return f.read()
                except Exception as img_error:
                    print(f"⚠️ Imagen API not available: {str(img_error)[:100]}")
        except Exception as e:
            print(f"⚠️ AI generation unavailable: {str(e)[:100]}")
        
        # Fallback: Create styled placeholder
        try:
            print(f"📝 Creating styled placeholder for: {prompt[:50]}...")
            
            # Create a professional-looking styled image as fallback
            width, height = 1024, 1024
            
            # Create gradient background
            img = Image.new('RGB', (width, height), '#ffffff')
            draw = ImageDraw.Draw(img)
            
            # Draw gradient background
            for y in range(height):
                # Blue to purple gradient
                r = int(66 + (138 - 66) * (y / height))
                g = int(133 + (43 - 133) * (y / height))
                b = int(244 + (226 - 244) * (y / height))
                draw.line([(0, y), (width, y)], fill=(r, g, b))
            
            # Add semi-transparent overlay
            overlay = Image.new('RGBA', (width, height), (255, 255, 255, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            
            # Add decorative circles
            for i in range(5):
                x = width // 2 + (i - 2) * 150
                y = height // 2
                radius = 100 - i * 10
                overlay_draw.ellipse(
                    [x - radius, y - radius, x + radius, y + radius],
                    fill=(255, 255, 255, 30)
                )
            
            img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
            draw = ImageDraw.Draw(img)
            
            # Load fonts
            try:
                title_font = ImageFont.truetype("arial.ttf", 48)
                text_font = ImageFont.truetype("arial.ttf", 24)
                small_font = ImageFont.truetype("arial.ttf", 18)
            except:
                title_font = ImageFont.load_default()
                text_font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            
            # Draw title
            title = "AI Generated Image"
            draw.text((width // 2, 100), title, fill='#ffffff', font=title_font, anchor="mm")
            
            # Draw prompt (wrapped)
            words = prompt.split()
            lines = []
            current_line = ""
            for word in words:
                if len(current_line + word) < 50:
                    current_line += word + " "
                else:
                    lines.append(current_line)
                    current_line = word + " "
            lines.append(current_line)
            
            y_offset = 200
            for line in lines[:5]:  # Max 5 lines
                draw.text((width // 2, y_offset), line.strip(), fill='#ffffff', font=text_font, anchor="mm")
                y_offset += 40
            
            # Add watermark
            draw.text(
                (width // 2, height - 50),
                "Styled Placeholder | LinkedIn Post Factory",
                fill=(255, 255, 255),
                font=small_font,
                anchor="mm"
            )
            
            # Save
            img.save(filepath, format='PNG', quality=95)
            with open(filepath, 'rb') as f:
                return f.read()
                
        except Exception as e:
            print(f"Placeholder generation error: {e}")
            # Ultimate fallback - simple solid color image
            img = Image.new('RGB', (1024, 1024), '#4285f4')
            draw = ImageDraw.Draw(img)
            
            try:
                font = ImageFont.truetype("arial.ttf", 36)
            except:
                font = ImageFont.load_default()
            
            draw.text((512, 512), "AI Image", fill='#ffffff', font=font, anchor="mm")
            
            img.save(filepath, format='PNG')
            with open(filepath, 'rb') as f:
                return f.read()
    
    async def _create_error_placeholder(
        self,
        prompt: str,
        error: str
    ) -> bytes:
        """
        Create an error placeholder image
        """
        img = Image.new('RGB', (self.base_width, self.base_height), '#1e1e1e')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 20)
            title_font = ImageFont.truetype("arialbd.ttf", 28)
        except:
            font = ImageFont.load_default()
            title_font = ImageFont.load_default()
        
        draw.text((60, 100), "⚠️ AI Image Generation Error", fill='#ff6b6b', font=title_font)
        draw.text((60, 160), f"Prompt: {prompt[:100]}...", fill='#ffffff', font=font)
        draw.text((60, 200), f"Error: {error[:100]}...", fill='#ffcc00', font=font)
        
        output = io.BytesIO()
        img.save(output, format='PNG', quality=95)
        return output.getvalue()


# Global instance
media_generator = MediaGenerator()

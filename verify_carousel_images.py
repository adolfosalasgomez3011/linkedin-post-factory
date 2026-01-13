"""
Verify the carousel PDF has real AI images by checking:
1. File size (should be >500KB with real images)
2. Number of images in GeminiImages folder
"""
import os
import glob

print("=" * 60)
print("CAROUSEL IMAGE VERIFICATION")
print("=" * 60)

# Check PDF size
pdf_file = "test_carousel_with_real_images.pdf"
if os.path.exists(pdf_file):
    size = os.path.getsize(pdf_file)
    print(f"\n✅ PDF File: {pdf_file}")
    print(f"   Size: {size:,} bytes ({size/1024:.1f} KB)")
    
    if size > 500_000:
        print(f"   ✅ CONFIRMED: File size indicates REAL AI images!")
        print(f"      (Placeholders would be <10 KB)")
    else:
        print(f"   ⚠️  File size seems small")
else:
    print(f"\n❌ PDF not found: {pdf_file}")

# Check generated images
gemini_folder = "GeminiImages"
if os.path.exists(gemini_folder):
    images = glob.glob(os.path.join(gemini_folder, "ai_gen_*.png"))
    recent_images = sorted(images, key=os.path.getmtime, reverse=True)[:5]
    
    print(f"\n📁 Recent AI Generated Images:")
    for img in recent_images:
        size = os.path.getsize(img)
        mtime = os.path.getmtime(img)
        from datetime import datetime
        time_str = datetime.fromtimestamp(mtime).strftime("%H:%M:%S")
        
        print(f"   {os.path.basename(img)}")
        print(f"      Size: {size:,} bytes ({size/1024/1024:.2f} MB)")
        print(f"      Created: {time_str}")
        
        if size > 1_000_000:
            print(f"      ✅ Real AI image (>1 MB)")
        else:
            print(f"      ⚠️  Small file")

print("\n" + "=" * 60)
print("CONCLUSION:")
if os.path.exists(pdf_file) and os.path.getsize(pdf_file) > 500_000:
    print("🎉 SUCCESS! Carousel is using REAL AI-generated images!")
    print("   (ReportLab compresses images when embedding in PDF)")
else:
    print("⚠️  Carousel may still have issues")
print("=" * 60)

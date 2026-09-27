from pathlib import Path
import io
import cairosvg
from PIL import Image, ImageEnhance, ImageFilter

root = Path("recipe-book")
res = root / "app/src/main/res/drawable-nodpi"
res.mkdir(parents=True, exist_ok=True)
svg_path = Path(".recipebook/v150-night-art.svg")

png = cairosvg.svg2png(url=str(svg_path), output_width=720, output_height=1600)
home = Image.open(io.BytesIO(png)).convert("RGB")
home.save(res / "bg_mari_home.webp", "WEBP", quality=92, method=6)

screen = home.filter(ImageFilter.GaussianBlur(0.65))
screen = ImageEnhance.Brightness(screen).enhance(0.74)
screen = ImageEnhance.Contrast(screen).enhance(0.94)
screen.save(res / "bg_mari_screen.webp", "WEBP", quality=89, method=6)

edit = home.filter(ImageFilter.GaussianBlur(0.95))
edit = ImageEnhance.Brightness(edit).enhance(0.65)
edit = ImageEnhance.Contrast(edit).enhance(0.92)
edit.save(res / "bg_mari_edit.webp", "WEBP", quality=87, method=6)

icon = home.crop((250, 460, 630, 840)).resize((512, 512), Image.Resampling.LANCZOS)
icon.save(res / "ic_mari.webp", "WEBP", quality=94, method=6)

logo_svg = """<svg xmlns="http://www.w3.org/2000/svg" width="780" height="150" viewBox="0 0 780 150">
<rect width="780" height="150" fill="none"/>
<text x="390" y="102" text-anchor="middle" fill="#FFF4DD" font-family="DejaVu Serif,serif" font-size="82" font-style="italic">MariRecipe</text>
</svg>"""
logo_png = cairosvg.svg2png(bytestring=logo_svg.encode("utf-8"), output_width=780, output_height=150)
(res / "logo_marirecipe.png").write_bytes(logo_png)

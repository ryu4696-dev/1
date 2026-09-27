from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import random, math, os

random.seed(4696)
ROOT = Path("recipe-book/app/src/main/res/drawable-nodpi")
ROOT.mkdir(parents=True, exist_ok=True)

W, H = 720, 1600
NAVY = (5, 14, 34)
GOLD = (239, 199, 111)
CREAM = (255, 243, 214)

def gradient_bg(top=NAVY, bottom=(14, 35, 68)):
    im = Image.new("RGB", (W, H), top)
    d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / (H - 1)
        c = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
        d.line((0, y, W, y), fill=c)
    return im.convert("RGBA")

def add_stars(base, count=360, strength=1.0):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(count):
        x = random.randint(8, W - 8)
        y = random.randint(18, int(H * 0.83))
        r = random.choices([1, 1, 1, 2, 2, 3], [45, 25, 10, 10, 7, 3])[0]
        a = int(random.randint(60, 180) * strength)
        warm = random.random() < 0.26
        col = (255, 232, 170, a) if warm else (220, 235, 255, a)
        d.ellipse((x-r, y-r, x+r, y+r), fill=col)
        if r >= 2 and random.random() < 0.6:
            d.line((x-5*r, y, x+5*r, y), fill=(col[0], col[1], col[2], int(a*0.6)), width=1)
            d.line((x, y-5*r, x, y+5*r), fill=(col[0], col[1], col[2], int(a*0.6)), width=1)
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for _ in range(10):
        x = random.randint(70, W-70)
        y = random.randint(80, int(H*0.7))
        gd.ellipse((x-9, y-9, x+9, y+9), fill=(255, 220, 130, 85))
        d.line((x-14, y, x+14, y), fill=(255, 235, 180, 210), width=2)
        d.line((x, y-14, x, y+14), fill=(255, 235, 180, 210), width=2)
    base.alpha_composite(glow.filter(ImageFilter.GaussianBlur(8)))
    base.alpha_composite(layer)

def add_milkyway(base):
    tiny = Image.new("L", (W//2, H//2), 0)
    td = ImageDraw.Draw(tiny)
    for _ in range(1400):
        yy = random.randint(-30, H//2+30)
        center = int((W//2)*0.78 - yy*0.28)
        xx = int(random.gauss(center, 42))
        if 0 <= xx < W//2 and 0 <= yy < H//2:
            v = random.randint(6, 34)
            td.ellipse((xx, yy, xx+random.randint(1,3), yy+random.randint(1,3)), fill=v)
    alpha = tiny.filter(ImageFilter.GaussianBlur(9)).resize((W, H), Image.Resampling.BICUBIC)
    milky = Image.new("RGBA", (W, H), (120, 140, 220, 0))
    milky.putalpha(alpha)
    base.alpha_composite(milky)

def add_clouds(base, horizon=0.77, strength=1.0):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for side in ("left", "right", "mid"):
        n = 34 if side != "mid" else 24
        for _ in range(n):
            x = random.randint(-70,270) if side == "left" else random.randint(450,W+70) if side == "right" else random.randint(180,540)
            y = random.randint(int(H*horizon), int(H*(horizon+0.15)))
            rx, ry = random.randint(38,95), random.randint(22,55)
            col = random.choice([(23,43,87,210),(35,52,101,190),(65,54,110,130),(44,62,117,150)])
            d.ellipse((x-rx,y-ry,x+rx,y+ry), fill=col)
    base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(7)))
    rim = Image.new("RGBA", base.size, (0,0,0,0))
    rd = ImageDraw.Draw(rim)
    for _ in range(28):
        x = random.choice([random.randint(5,250), random.randint(470,W-5)])
        y = random.randint(int(H*horizon), int(H*(horizon+0.10)))
        rd.ellipse((x-20,y-9,x+20,y+9), fill=(246,197,123,int(25*strength)))
    base.alpha_composite(rim.filter(ImageFilter.GaussianBlur(10)))

def add_moon_cat(base, cx=500, cy=510, scale=1.0, alpha=255):
    glow = Image.new("RGBA", base.size, (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    R = int(165*scale)
    for rr, a in ((R+35,24),(R+22,34),(R+12,46)):
        gd.ellipse((cx-rr,cy-rr,cx+rr,cy+rr), fill=(255,203,104,int(a*alpha/255)))
    base.alpha_composite(glow.filter(ImageFilter.GaussianBlur(24)))

    moon = Image.new("RGBA", base.size, (0,0,0,0))
    md = ImageDraw.Draw(moon)
    md.ellipse((cx-R,cy-R,cx+R,cy+R), fill=(250,207,110,alpha))
    cut = int(125*scale)
    md.ellipse((cx-cut-45*scale,cy-cut-18*scale,cx+cut-45*scale,cy+cut-18*scale), fill=(7,20,45,255))
    for _ in range(42):
        x = int(random.gauss(cx+50*scale,50*scale))
        y = int(random.gauss(cy,80*scale))
        rr = random.randint(2,7)
        md.ellipse((x-rr,y-rr,x+rr,y+rr), fill=(227,174,82,random.randint(35,85)))
    base.alpha_composite(moon)

    cat = Image.new("RGBA", base.size, (0,0,0,0))
    cd = ImageDraw.Draw(cat)
    s = scale
    body = (cx-44*s, cy-22*s, cx+35*s, cy+102*s)
    head = (cx-58*s, cy-73*s, cx+12*s, cy-5*s)
    cd.ellipse(body, fill=(5,15,35,alpha))
    cd.ellipse(head, fill=(5,15,35,alpha))
    cd.polygon([(cx-49*s,cy-65*s),(cx-37*s,cy-95*s),(cx-27*s,cy-61*s)], fill=(5,15,35,alpha))
    cd.polygon([(cx-10*s,cy-65*s),(cx+5*s,cy-92*s),(cx+1*s,cy-56*s)], fill=(5,15,35,alpha))
    cd.ellipse((cx-47*s,cy+79*s,cx+2*s,cy+111*s), fill=(5,15,35,alpha))
    pts=[]
    for i in range(31):
        t=i/30
        x=cx+27*s-70*s*t+20*s*math.sin(t*math.pi)
        y=cy+55*s+118*s*t
        pts.append((x,y))
    cd.line(pts, fill=(5,15,35,alpha), width=max(8,int(18*s)))
    base.alpha_composite(cat)

    hi = Image.new("RGBA", base.size, (0,0,0,0))
    hd = ImageDraw.Draw(hi)
    hd.arc(head, 170, 330, fill=(255,232,176,int(210*alpha/255)), width=max(1,int(2*s)))
    hd.arc(body, 210, 355, fill=(255,220,150,int(150*alpha/255)), width=max(1,int(2*s)))
    hd.ellipse((cx-29*s,cy-45*s,cx-25*s,cy-41*s), fill=(249,208,111,int(230*alpha/255)))
    base.alpha_composite(hi)

def add_city(base, y0=0.84):
    layer = Image.new("RGBA", base.size, (0,0,0,0))
    d = ImageDraw.Draw(layer)
    ground = int(H*y0)
    x = -10
    random.seed(812)
    while x < W+20:
        ww, hh = random.randint(30,75), random.randint(55,170)
        top = ground-hh
        body = random.choice([(5,12,29,245),(7,17,37,240),(9,21,43,235)])
        d.rectangle((x,top,x+ww,ground+120), fill=body)
        if random.random() < 0.62:
            d.polygon([(x-5,top),(x+ww//2,top-random.randint(18,45)),(x+ww+5,top)], fill=(4,10,25,245))
        if random.random() < 0.16:
            sx=x+ww//2
            d.rectangle((sx-6,top-50,sx+6,top), fill=(4,10,25,245))
            d.polygon([(sx-12,top-50),(sx,top-95),(sx+12,top-50)], fill=(4,10,25,245))
        for yy in range(int(top+18),ground-10,26):
            for xx in range(int(x+10),int(x+ww-8),20):
                if random.random() < 0.45:
                    d.rectangle((xx,yy,xx+4,yy+7), fill=(244,177,75,random.randint(90,190)))
        x += ww-5
    base.alpha_composite(layer)

def add_shooting_stars(base):
    l=Image.new("RGBA",base.size,(0,0,0,0))
    d=ImageDraw.Draw(l)
    for x,y in ((100,280),(275,180)):
        d.arc((x,y,x+260,y+120),200,345,fill=(235,194,103,140),width=2)
    base.alpha_composite(l)

def veil(base, alpha_top=60, alpha_mid=45):
    l=Image.new("RGBA",base.size,(0,0,0,0))
    d=ImageDraw.Draw(l)
    for y in range(H):
        if y < 820:
            a=int(alpha_top-(alpha_top-alpha_mid)*y/820)
        else:
            a=int(alpha_mid+25*(y-820)/(H-820))
        d.line((0,y,W,y),fill=(3,10,27,a))
    base.alpha_composite(l)

def render(kind):
    base=gradient_bg()
    add_milkyway(base)
    add_stars(base, 330 if kind=="edit" else 430, 0.95)
    add_shooting_stars(base)
    if kind=="home":
        add_moon_cat(base,520,450,0.92)
        add_clouds(base,0.67)
        add_city(base,0.84)
        veil(base,72,48)
    elif kind=="screen":
        add_moon_cat(base,565,360,0.66,225)
        add_clouds(base,0.76,0.8)
        add_city(base,0.91)
        veil(base,105,78)
    else:
        add_moon_cat(base,595,300,0.48,160)
        add_clouds(base,0.84,0.45)
        veil(base,145,125)
    return base.convert("RGB")

for kind in ("home","screen","edit"):
    render(kind).save(ROOT/f"bg_mari_{kind}.webp","WEBP",quality=84,method=6)

# Dedicated MariRecipe logo resource.
LW,LH=780,150
logo=Image.new("RGBA",(LW,LH),(0,0,0,0))
d=ImageDraw.Draw(logo)
font_candidates=[
    "/usr/share/fonts/truetype/dejavu/DejaVuSerifCondensed-Italic.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSerif-Italic.ttf",
]
font_path=next((p for p in font_candidates if os.path.exists(p)),None)
font=ImageFont.truetype(font_path,82) if font_path else ImageFont.load_default()
glow=Image.new("RGBA",(LW,LH),(0,0,0,0))
gd=ImageDraw.Draw(glow)
gd.ellipse((8,37,80,109),fill=(239,199,111,60))
logo.alpha_composite(glow.filter(ImageFilter.GaussianBlur(12)))
d.arc((12,38,78,108),65,295,fill=GOLD+(255,),width=5)
d.text((91,23),"MariRecipe",font=font,fill=CREAM+(255,))
d.arc((330,103,735,148),190,348,fill=(223,183,100,230),width=2)
for x,y in ((700,35),(746,87)):
    d.line((x-7,y,x+7,y),fill=(250,225,164,230),width=2)
    d.line((x,y-7,x,y+7),fill=(250,225,164,230),width=2)
logo.save(ROOT/"logo_marirecipe.png")

# Dedicated launcher icon resource.
mini=gradient_bg()
add_milkyway(mini)
add_stars(mini,170,1.0)
add_moon_cat(mini,390,500,1.25)
add_clouds(mini,0.62)
veil(mini,35,25)
mini=mini.crop((90,180,630,720)).resize((512,512),Image.Resampling.LANCZOS)
mini.convert("RGB").save(ROOT/"ic_mari.webp","WEBP",quality=92,method=6)

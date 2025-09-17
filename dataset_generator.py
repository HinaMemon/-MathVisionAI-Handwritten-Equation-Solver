

from PIL import Image, ImageDraw, ImageFont
import os
import random


OUTPUT_DIR = 'samples'
FONTS_DIR = 'assets/fonts'


EQUATIONS = [
'3*x + 2 = 11',
'2*x**2 + 5*x - 3 = 0',
'integrate(x**2, x)',
'diff(sin(x), x)',
'x/2 + 3 = 7',
'1/2 + 3/4',
'sqrt(16)',
'x**3 + 2*x**2 - x + 1',
'sin(x)**2 + cos(x)**2',
'd/dx x**2'
]




def list_fonts():
fonts = []
for f in os.listdir(FONTS_DIR):
if f.lower().endswith('.ttf'):
fonts.append(os.path.join(FONTS_DIR, f))
return fonts




def make_image(text, font_path, outpath, size=(800,150)):
img = Image.new('RGB', size, color='white')
draw = ImageDraw.Draw(img)
try:
font = ImageFont.truetype(font_path, 36)
except Exception:
font = ImageFont.load_default()
# random vertical position for handwritten look
x = 10
y = random.randint(10, 40)
draw.text((x,y), text, font=font, fill='black')
# add noise lines
for _ in range(random.randint(0,3)):
x1 = random.randint(0, size[0])
y1 = random.randint(0, size[1])
x2 = random.randint(0, size[0])
y2 = random.randint(0, size[1])
draw.line((x1,y1,x2,y2), fill=(0,0,0), width=1)
img.save(outpath)




def generate(n_per_font=20):
os.makedirs(OUTPUT_DIR, exist_ok=True)
fonts = list_fonts()
if not fonts:
print('No fonts found in', FONTS_DIR)
return
count = 0
for font in fonts:
for i in range(n_per_font):
eq = random.choice(EQUATIONS)
fname = f'eq_{count}.png'
generate(30)
#!/usr/bin/env python3
"""Draw fresh reference UI; composite photo/brand assets with FFmpeg. No app code changes."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import subprocess

ROOT = Path(__file__).resolve().parent
A = ROOT / 'assets'
FONT = '/System/Library/Fonts/Supplemental/Arial.ttf'
BOLD = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'

def run(args):
    subprocess.run(['/opt/homebrew/bin/ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', *map(str,args)], check=True)

def text(d, value, y, size=36, color='#121925', bold=False, width=720):
    f=ImageFont.truetype(BOLD if bold else FONT,size)
    box=d.textbbox((0,0),value,font=f)
    d.text(((width-(box[2]-box[0]))/2,y),value,font=f,fill=color)

def screen(kind, dots=0):
    im=Image.new('RGB',(720,1440),'#000000' if kind=='calculator' else '#f5f6fa')
    d=ImageDraw.Draw(im)
    text(d,'9:41',30,22,'#eeeeee' if kind=='calculator' else '#121925')
    if kind=='calculator':
        text(d,'Calculator',150,38,'#ffffff',True)
        d.text((510,360),'42',font=ImageFont.truetype(FONT,100),fill='#ffffff')
        keys=[['AC','±','%','÷'],['7','8','9','×'],['4','5','6','−'],['1','2','3','+'],['0','.','=']]
        for row, ks in enumerate(keys):
            for col,key in enumerate(ks):
                x=36+col*166; y=605+row*153; ww=146
                if row==4:
                    x=[36,368,534][col]; ww=[312,146,146][col]
                operation=(row<4 and col==3) or (row==4 and col==2)
                color='#ff9f0a' if operation else '#a5a5a5' if row==0 else '#333333'
                d.rounded_rectangle((x,y,x+ww,y+134),67,fill=color)
                f=ImageFont.truetype(FONT,48); box=d.textbbox((0,0),key,font=f)
                d.text((x+(ww-box[2])/2,y+36),key,font=f,fill='#000000' if row==0 and col<3 else '#ffffff')
    elif kind=='pin':
        d.ellipse((310,220,410,320),outline='#b9c0cc',width=2)
        d.rounded_rectangle((336,265,384,298),6,outline='#121925',width=3)
        d.arc((345,242,375,278),180,360,fill='#121925',width=3)
        text(d,'Veilnest',357,52,bold=True)
        text(d,'Enter your 6-digit PIN',445,28,'#647083')
        for i in range(6):
            x=233+i*46
            d.ellipse((x,529,x+22,551),fill='#121925' if i<dots else '#d6dbe5')
        for n,key in enumerate(['1','2','3','4','5','6','7','8','9','','0','']):
            if not key: continue
            r,c=divmod(n,3); x=120+c*186;y=700+r*145
            d.ellipse((x,y,x+108,y+108),outline='#ccd2de',width=2)
            d.text((x+40,y+30),key,font=ImageFont.truetype(FONT,42),fill='#121925')
        text(d,'Your vault stays private.',1345,24,'#647083')
    else:
        text(d,'VAULT',140,56,bold=True)
        text(d,'Private photos',231,30,'#647083')
        d.rounded_rectangle((48,335,672,751),16,fill='#dde2e9')
        text(d,'6 personal memories',825,26,'#647083')
        d.line((40,1280,680,1280),fill='#d6dce6',width=2)
        text(d,'Photos     Albums     Favorites',1335,28,'#647083')
    d.rounded_rectangle((245,1403,475,1411),4,fill='#c1c4cc' if kind=='calculator' else '#121925')
    return im

def main():
    screen('calculator').save(A/'screen-calculator.png')
    screen('pin').save(A/'screen-pin.png')
    screen('vault').save(A/'screen-vault-base.png')
    run(['-i',A/'screen-vault-base.png','-i',A/'demo-photo-sheet.png','-filter_complex','[1:v]scale=624:416[photos];[0:v][photos]overlay=48:335','-frames:v',1,A/'screen-vault.png'])
    brand=Image.new('RGB',(720,1280),'#0b0d13');d=ImageDraw.Draw(brand)
    text(d,'Veilnest',600,66,'#ffffff',True)
    text(d,'Looks like a calculator.',724,32,'#c5cddd')
    text(d,'Keeps your photos private.',772,32,'#c5cddd')
    d.rounded_rectangle((160,886,560,964),39,fill='#ffffff')
    text(d,'Get it on iOS',907,32,'#10151f',True)
    brand.save(A/'end-card-base.png')
    run(['-i',A/'end-card-base.png','-i',A/'veilnest-icon.png','-filter_complex','[1:v]scale=210:210[icon];[0:v][icon]overlay=255:315','-frames:v',1,A/'end-card.png'])
    run(['-loop',1,'-framerate',24,'-i',A/'end-card.png','-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-t',3,'-c:v','libx264','-pix_fmt','yuv420p','-crf',18,'-c:a','aac','-movflags','+faststart',ROOT/'clip-c-end-card-3s.mp4'])
    for i in range(48):
        screen('pin',min(6,max(0,(i-4)//6+1))).save(A/f'pin-{i:03}.png')
    clips=[]
    for name,duration in [('calculator',1.5),('pin',2),('vault',4.5)]:
        out=ROOT/f'_screen-{name}.mp4';clips.append(out)
        inp=['-framerate',24,'-i',A/'pin-%03d.png'] if name=='pin' else ['-loop',1,'-framerate',24,'-i',A/f'screen-{name}.png']
        run([*inp,'-t',duration,'-c:v','libx264','-pix_fmt','yuv420p','-crf',18,'-an',out])
    listing=ROOT/'_screen-list.txt';listing.write_text('\n'.join(f"file '{p}'" for p in clips))
    run(['-f','concat','-safe',0,'-i',listing,'-c','copy','-movflags','+faststart',ROOT/'screen-demo-8s.mp4'])
    for p in clips+[listing]:p.unlink()
    for p in A.glob('pin-*.png'):p.unlink()
    print('Created three reference screens, six-photo demo sheet composite, 8s UI animation and 3s end card.')

if __name__=='__main__':main()

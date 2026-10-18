#!/usr/bin/env python3
"""Render a 15s review animatic. Actor pictures are composed by ffmpeg; Pillow draws new UI/caption graphics."""
from pathlib import Path
import argparse, array, json, math, shutil, subprocess, tempfile, wave
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
W, H, FPS = 1080, 1920, 30
FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
MONO = "/System/Library/Fonts/SFNSMono.ttf"
WHITE = "#f5f6fa"
BG = "#0b0d13"

def font(size, bold=False, mono=False):
    return ImageFont.truetype(MONO if mono else BOLD if bold else FONT, size)

def lines(d, text, y, size=56, fill=WHITE, gap=10, backing=False):
    f = font(size, bold=True)
    for line in text.split("\n"):
        box = d.textbbox((0,0), line, font=f)
        tw = box[2] - box[0]
        x = (W-tw)/2
        if backing:
            d.rounded_rectangle((x-24,y-12,x+tw+24,y+size+20), radius=18, fill=(0,0,0,195))
        d.text((x,y), line, font=f, fill=fill, stroke_width=0)
        y += size+gap

def annotation(d):
    d.rounded_rectangle((72,108,415,158), radius=12, fill="#1a202d")
    d.text((92,117), "ANIMATIC / AI STILLS", font=font(24,bold=True), fill="#c3cbd9")

def overlay(path, header="", caption=""):
    img=Image.new("RGBA",(W,H),(0,0,0,0))
    d=ImageDraw.Draw(img); annotation(d)
    if header: lines(d, header, 270, 60, backing=True)
    if caption: lines(d, caption, 1370, 54, backing=True)
    img.save(path)

def graphic(title, label, screen, dots=0, hold=0):
    img=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(img)
    annotation(d)
    lines(d,title,250,60)
    d.rounded_rectangle((270,450,750,1390),radius=70,fill="#252a35")
    d.rounded_rectangle((282,462,738,1378),radius=60,fill="#000000" if screen=="calc" else "#f3f5fa")
    d.rounded_rectangle((445,475,575,500),radius=15,fill="#000000")
    if screen=="calc":
        d.text((428,540),"Calculator",font=font(28,bold=True),fill="#cccccc")
        d.text((684,540),"···",font=font(26,bold=True),fill="#cccccc")
        d.text((585,680),"42",font=font(94),fill="#ffffff")
        keypad=[["AC","±","%","÷"],["7","8","9","×"],["4","5","6","−"],["1","2","3","+"],["0",".","="]]
        for row, keys in enumerate(keypad):
            yy=850+row*94
            for col,key in enumerate(keys):
                if row==4:
                    xx=[301,513,619][col]; ww=[198,92,92][col]
                    tone="#c57e00" if col==2 else "#333333"
                else:
                    xx=301+col*106; ww=92
                    tone="#c57e00" if col==3 else "#aaaaaa" if row==0 else "#333333"
                d.rounded_rectangle((xx,yy,xx+ww,yy+82),radius=41,fill=tone)
                f=font(35)
                bb=d.textbbox((0,0),key,font=f)
                d.text((xx+(ww-bb[2])/2,yy+20),key,font=f,fill="#000000" if row==0 and col<3 else "#ffffff")
        if hold:
            d.ellipse((475,523,535,583),outline="#8af0c7",width=3)
            d.arc((470,518,540,588),-90,-90+360*hold,fill="#8af0c7",width=7)
            d.text((374,760),"Hold title to continue",font=font(23),fill="#8af0c7")
    elif screen=="pin":
        # A controlled reconstruction of the separate lock screen.
        d.rounded_rectangle((485,652,535,698),radius=8,outline="#141b27",width=4)
        d.arc((493,625,527,675),180,360,fill="#141b27",width=4)
        d.text((392,725),"Veilnest",font=font(45,mono=True),fill="#111620")
        d.text((368,800),"Enter PIN to unlock",font=font(24),fill="#657189")
        for j in range(6):
            x=402+j*40
            d.ellipse((x,855,x+16,871),fill="#161e2b" if j<dots else "#dce1eb")
        for j,key in enumerate(["1","2","3","4","5","6","7","8","9","","0",""]):
            row,col=divmod(j,3); x=357+col*117; y=931+row*93
            if key:
                d.ellipse((x,y,x+72,y+72),outline="#dce1eb",width=2)
                d.text((x+25,y+16),key,font=font(32),fill="#141b27")
    else:
        d.text((312,554),"VAULT",font=font(42,mono=True),fill="#121925")
        d.text((313,620),"Private photos",font=font(25),fill="#6b7588")
        palettes=[("#acc3d0","#e8d9bb"),("#aecbb7","#e2ddce"),("#d6bca9","#ad9fa1")]
        for i in range(9):
            row,col=divmod(i,3); x=312+col*135; y=700+row*186
            p,q=palettes[i%3]
            d.rounded_rectangle((x,y,x+122,y+166),radius=18,fill=p)
            d.ellipse((x+65,y+23,x+95,y+53),fill="#fff1d2")
            d.polygon([(x,y+135),(x+44,y+70),(x+93,y+144),(x+122,y+94),(x+122,y+166),(x,y+166)],fill=q)
        d.text((376,1298),"Photo grid preview",font=font(22),fill="#6b7588")
    d.rounded_rectangle((444,1347,576,1353),radius=3,fill="#777b85")
    lines(d,label,1460,35,fill="#a1aec5")
    return img

def card():
    img=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(img); annotation(d)
    # Icon is added unaltered in identity by ffmpeg, not by image generation.
    lines(d,"Veilnest",960,88)
    lines(d,"A calculator cover.\nA private photo vault.",1095,43,fill="#c2cbdc")
    d.rounded_rectangle((295,1265,785,1360),radius=47,fill="#f5f6fa")
    lines(d,"Get it on iOS",1284,43,fill="#111620")
    return img

def run(cmd):
    subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL)

def encode(input_path,output_path,frames,filter_chain=None,caption=None,interval=None,zoom=None,icon=False,sequence=False,header=""):
    args=["ffmpeg","-hide_banner","-loglevel","error","-y"]
    if sequence:
        args+=["-framerate",str(FPS),"-i",str(input_path)]
    else:
        args+=["-loop","1","-framerate",str(FPS),"-i",str(input_path)]
    base="[0:v]setsar=1"
    if zoom:
        z,dx,dy=zoom
        base+=f",scale=2160:-1,zoompan=z='{z}+0.00035*on':x='iw*{dx}-iw/zoom/2':y='ih*{dy}-ih/zoom/2':d=1:s={W}x{H}:fps={FPS}"
    elif filter_chain:
        base+=","+filter_chain
    else:
        base+=f",scale={W}:{H}"
    base+="[base]"
    filters=[base]
    next_input=1
    if header or zoom:
        over=output_path.with_suffix(".overlay.png")
        overlay(over,header=header)
        args+=["-loop","1","-framerate",str(FPS),"-i",str(over)]
        filters.append(f"[base][{next_input}:v]overlay=0:0[marked]")
        next_input+=1; current="marked"
    else: current="base"
    if icon:
        args+=["-loop","1","-framerate",str(FPS),"-i",str(ASSETS/"veilnest-icon.png")]
        filters.append(f"[{next_input}:v]scale=340:340[icon]")
        filters.append(f"[{current}][icon]overlay=370:555[branded]")
        current="branded"; next_input+=1
    if caption:
        over=output_path.with_suffix(".caption.png")
        overlay(over,caption=caption)
        args+=["-loop","1","-framerate",str(FPS),"-i",str(over)]
        enable=f":enable='between(t,{interval[0]},{interval[1]})'" if interval else ""
        filters.append(f"[{current}][{next_input}:v]overlay=0:0{enable}[captioned]")
        current="captioned"
    filters.append(f"[{current}]format=yuv420p[out]")
    args+=["-filter_complex",";".join(filters),"-map","[out]","-frames:v",str(frames),"-an","-c:v","libx264","-preset","fast","-crf","20","-r",str(FPS),"-movflags","+faststart",str(output_path)]
    run(args)

def sounds(path):
    rate=48000; samples=[0.0]*(rate*15)
    def tone(start,duration,freq,amp=0.16,decay=8):
        for i in range(int(rate*duration)):
            t=i/rate; idx=int(start*rate)+i
            if idx<len(samples):
                env=min(1,t/0.006)*math.exp(-decay*t)
                samples[idx]+=amp*env*math.sin(2*math.pi*freq*t)
    tone(0.02,.12,150,.12,20)
    tone(6.97,.38,110,.15,12)
    tone(8.68,.1,650,.07,25)
    for n in range(6): tone(8.88+n*.14,.05,800+n*30,.035,30)
    tone(10.0,.35,660,.07,10); tone(10.07,.35,880,.06,10)
    tone(14.25,.4,98,.13,12)
    pcm=array.array("h",(int(max(-1,min(1,v))*32767) for v in samples))
    with wave.open(str(path),"wb") as out:
        out.setnchannels(1);out.setsampwidth(2);out.setframerate(rate);out.writeframes(pcm.tobytes())

def main():
    parser=argparse.ArgumentParser();parser.add_argument("--keep-intermediates",action="store_true")
    opts=parser.parse_args()
    for tool in ("ffmpeg","ffprobe"):
        if not shutil.which(tool): raise SystemExit(f"Missing {tool}")
    ASSETS.mkdir(exist_ok=True)
    if not (ASSETS/"actors-reference.png").exists(): raise SystemExit("Missing AI reference image")
    graphic("Looks like a calculator.","RECREATED UI / LOCKED SESSION","calc").save(ASSETS/"calculator.png")
    graphic("Unlocks your private vault.","RECREATED UI / SEPARATE PIN SCREEN","pin",dots=3).save(ASSETS/"pin.png")
    graphic("Your PIN.\nYour private photos.","RECREATED UI / DEMO PLACEHOLDERS","vault").save(ASSETS/"vault.png")
    card().save(ASSETS/"end-card.png")
    with tempfile.TemporaryDirectory(prefix="veilnest-animatic-") as tmp:
        work=Path(tmp); clips=[]
        def add(name,source,frames,**kwargs):
            target=work/f"{len(clips):02}-{name}.mp4"
            encode(source,target,frames,**kwargs);clips.append(target)
        actor=ASSETS/"actors-reference.png"
        add("hook",actor,60,zoom=(1.03,.5,.5),header="POV: your friend\nstarts snooping",caption="Lemme see your photos.",interval=(.15,1.85))
        add("friend",actor,45,zoom=(1.48,.66,.43),caption="Why are you always\non this calculator?",interval=(.1,1.5))
        add("calculator-insert",ASSETS/"calculator.png",18,caption="Why are you always\non this calculator?")
        add("friend-return",actor,33,zoom=(1.48,.66,.43),caption="Why are you always\non this calculator?",interval=(0,.95))
        add("answer",actor,60,zoom=(1.53,.32,.43),caption="I'm financially\nresponsible.",interval=(.1,1.75))
        for n in range(45):
            graphic("Looks like a calculator.","HOLD TITLE → ENTER PIN → VAULT","calc",hold=(n+1)/45).save(work/f"hold-{n:03}.png")
        add("hold",work/"hold-%03d.png",45,sequence=True)
        for n in range(39):
            dots=max(0,min(6,int((n-5)/4)+1))
            graphic("Unlocks your private vault.","SEPARATE PIN SCREEN / MASKED CODE","pin",dots=dots).save(work/f"pin-{n:03}.png")
        add("pin",work/"pin-%03d.png",39,sequence=True)
        add("vault",ASSETS/"vault.png",63)
        add("brand",ASSETS/"end-card.png",87,icon=True,caption="You still owe me\ntwelve bucks.",interval=(.25,2.1))
        listfile=work/"concat.txt"
        listfile.write_text("\n".join("file '"+str(p)+"'" for p in clips))
        sounds(ASSETS/"timing-sounds.wav")
        run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",str(listfile),"-i",str(ASSETS/"timing-sounds.wav"),"-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","160k","-t","15","-movflags","+faststart",str(ROOT/"preview.mp4")])
        if opts.keep_intermediates: shutil.copytree(work,ROOT/"intermediates",dirs_exist_ok=True)
    info=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(ROOT/"preview.mp4")]))
    video=next(s for s in info["streams"] if s["codec_type"]=="video")
    assert (video["width"],video["height"])==(W,H)
    assert int(video["nb_frames"])==450
    assert abs(float(info["format"]["duration"])-15)<.05
    (ROOT/"render-verification.json").write_text(json.dumps({"width":W,"height":H,"fps":video["r_frame_rate"],"frames":video["nb_frames"],"duration":info["format"]["duration"],"video_codec":video["codec_name"],"has_audio":any(s["codec_type"]=="audio" for s in info["streams"]),"spoken_dialogue":False,"type":"animatic"},indent=2)+"\n")
    for stamp,name in [(1,"hook"),(6,"answer"),(8.2,"hold"),(9.6,"pin"),(11,"vault"),(13.2,"end-card")]:
        run(["ffmpeg","-hide_banner","-loglevel","error","-y","-ss",str(stamp),"-i",str(ROOT/"preview.mp4"),"-frames:v","1",str(ASSETS/f"review-{name}.png")])
    print("Verified: 1080x1920, 30 fps, 450 frames, 15 seconds; captions and synthesized timing sounds, no speech.")

if __name__=="__main__": main()

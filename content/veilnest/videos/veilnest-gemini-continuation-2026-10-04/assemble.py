#!/usr/bin/env python3
"""Join the retained opening, completed Gemini continuation, and prepared end card."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parent
FFMPEG='/opt/homebrew/bin/ffmpeg'
FFPROBE='/opt/homebrew/bin/ffprobe'

def probe(path):
    return json.loads(subprocess.check_output([FFPROBE,'-v','error','-show_streams','-show_format','-of','json',str(path)]))

def normalize(source,target,start,frames):
    info=probe(source)
    duration=frames/24
    args=[FFMPEG,'-hide_banner','-loglevel','error','-y','-ss',str(start),'-i',str(source)]
    audio=any(s['codec_type']=='audio' for s in info['streams'])
    if not audio:args+=['-f','lavfi','-i','anullsrc=r=48000:cl=stereo']
    args+=['-map','0:v:0','-map','0:a:0' if audio else '1:a:0',
        '-vf','scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1,fps=24',
        '-af',f'apad,atrim=duration={duration},asetpts=PTS-STARTPTS',
        '-frames:v',str(frames),'-t',str(duration),'-c:v','libx264','-preset','fast','-crf','18',
        '-pix_fmt','yuv420p','-c:a','aac','-ar','48000','-ac','2','-b:a','192k',str(target)]
    subprocess.run(args,check=True)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--continuation',type=Path,required=True)
    parser.add_argument('--start',type=float,default=0.5,help='Start of the retained 8s segment in B')
    parser.add_argument('--output',type=Path,default=ROOT/'veilnest-18s.mp4')
    args=parser.parse_args()
    if not args.continuation.is_file():parser.error('Continuation file does not exist')
    if args.start<0:parser.error('Start must be nonnegative')
    info=probe(args.continuation)
    if float(info['format']['duration'])+0.02<args.start+8:
        parser.error('Continuation must contain eight full seconds after --start')
    if not any(s['codec_type']=='video' for s in info['streams']):parser.error('Continuation contains no video')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='veilnest-assembly-') as tmp:
        tmp=Path(tmp);normalized=[]
        for i,(source,start,frames) in enumerate([
            (ROOT/'clip-a-keep-0-6.96s.mp4',0,167),
            (args.continuation,args.start,192),
            (ROOT/'clip-c-end-card-3s.mp4',0,72),
        ]):
            target=tmp/f'{i}.mp4';normalize(source,target,start,frames);normalized.append(target)
        listing=tmp/'concat.txt';listing.write_text('\n'.join(f"file '{p}'" for p in normalized))
        subprocess.run([FFMPEG,'-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(listing),
            '-c:v','copy','-c:a','aac','-b:a','192k','-frames:v','431','-t',str(431/24),
            '-movflags','+faststart',str(args.output)],check=True)
    result=probe(args.output);video=next(s for s in result['streams'] if s['codec_type']=='video')
    assert (video['width'],video['height'])==(720,1280)
    assert int(video['nb_frames'])==431
    assert abs(float(result['format']['duration'])-431/24)<0.08
    verification={'width':720,'height':1280,'fps':video['r_frame_rate'],'frames':431,
        'duration':result['format']['duration'],'continuation':str(args.continuation.resolve()),
        'continuation_trim':[args.start,args.start+8],'phone_screen_compositing':False,
        'captions_burned_in':False,'audio':True}
    args.output.with_suffix('.verification.json').write_text(json.dumps(verification,indent=2)+'\n')
    print(f'Created {args.output.resolve()} — 431 frames, about 18s, with audio.')

if __name__=='__main__':main()

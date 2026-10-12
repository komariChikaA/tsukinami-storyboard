"""Render this project's native Storybrew OSB (linear commands) to H.264 video.

Reject unsupported commands rather than silently approximating another project.
Background/blur are composited before their identical transform for efficiency.
"""
import argparse, csv, json, math, subprocess, time
from pathlib import Path
import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
DEFAULTS={'M':[320.,240.],'S':[1.],'V':[1.,1.],'R':[0.],'F':[1.],'C':[255.,255.,255.]}
class Sprite:
    def __init__(self,row):
        if row[2]!='Centre': raise ValueError('Only Centre origin is supported')
        self.path=row[3].replace('\\','/')
        self.initial=[float(row[4]),float(row[5])]
        self.commands={};self.additive=False
        self.start=float('inf');self.end=0
    def add(self,row):
        name=row[0].strip()
        if name=='P':
            if row[-1]!='A': raise ValueError('Unsupported parameter '+str(row))
            self.additive=True;return
        if name not in DEFAULTS:raise ValueError('Unsupported OSB command '+name)
        if int(row[1])!=0:raise ValueError('Nonlinear easing requires an explicit implementation')
        start=float(row[2]);end=float(row[3]) if row[3] else start
        n=len(DEFAULTS[name]);values=[float(v) for v in row[4:] if v!='']
        if len(values)==n:a=values;b=values
        elif len(values)==2*n:a=values[:n];b=values[n:]
        else:raise ValueError('Invalid command '+str(row))
        self.commands.setdefault(name,[]).append([start,end,a,b])
        self.start=min(self.start,start);self.end=max(self.end,end)
    def finish(self):
        for k,rows in self.commands.items():
            rows.sort(key=lambda r:r[0])
            self.commands[k]=(np.array([r[0] for r in rows]),np.array([r[1] for r in rows]),np.array([r[2] for r in rows]),np.array([r[3] for r in rows]))
    def value(self,name,t):
        default=self.initial if name=='M' else DEFAULTS[name]
        if name not in self.commands:return np.array(default)
        starts,ends,a,b=self.commands[name]
        i=int(np.searchsorted(starts,t,side='right')-1)
        # osu! commands retain their initial value before the first command.
        if i<0:return a[0]
        f=np.clip((t-starts[i])/max(ends[i]-starts[i],1e-9),0,1)
        return a[i]+(b[i]-a[i])*f
    def pose(self,t):
        sx,sy=self.value('V',t) if 'V' in self.commands else np.repeat(self.value('S',t),2)
        return self.value('M',t),sx,sy,self.value('R',t)[0],self.value('F',t)[0]

def load_osb(path):
    sprites=[]
    for row in csv.reader(path.read_text(encoding='utf-8-sig').splitlines()):
        if not row or row[0].startswith('//') or row[0]=='[Events]':continue
        if row[0]=='Sprite':sprites.append(Sprite(row))
        elif row[0].startswith((' ','_')):sprites[-1].add([row[0].strip(' _')]+row[1:])
        else:raise ValueError('Unexpected OSB line '+str(row))
    for s in sprites:s.finish()
    return sprites

def verify(sprites):
    samples=json.loads((ROOT/'output/native-samples.json').read_text())
    errors=[]
    bypath={s.path:s for s in sprites}
    for a in samples:
        s=bypath[a['path']];p,sx,sy,r,f=s.pose(a['time'])
        actual=dict(x=p[0],y=p[1],sx=sx,sy=sy,rotation=r,opacity=f)
        for key,value in actual.items():
            error=abs(value-a[key])
            tolerance=.12 if key in ('x','y') else .0025
            if error>tolerance:errors.append(dict(path=s.path,time=a['time'],key=key,native=a[key],render=float(value)))
    report=dict(native_sample_count=len(samples),property_checks=len(samples)*6,errors=errors,
                note='Tolerance covers integer-millisecond OSB export and numerical rounding.')
    (ROOT/'output/parity.json').write_text(json.dumps(report,indent=2))
    if errors:raise AssertionError(f'{len(errors)} native/OSB evaluation mismatches; see output/parity.json')
    print(f'Native Storybrew parity: {len(samples)*6} property checks passed.',flush=True)

def read_image(path):
    im=cv2.imdecode(np.fromfile(str(path),dtype=np.uint8),cv2.IMREAD_UNCHANGED)
    if im is None:raise FileNotFoundError(path)
    if im.ndim==2:im=cv2.cvtColor(im,cv2.COLOR_GRAY2BGR)
    return im

class Renderer:
    def __init__(self,sprites,width=1920,height=1080):
        self.sprites=sprites;self.w=width;self.h=height;self.factor=height/480
        self.images={s.path:read_image(ROOT/'assets'/s.path) for s in sprites}
        self.sharp=self.images['bg.png'];self.blurred=self.images['sb/bg-blur.jpg']
        self.cache={}
        self.stats=dict(frames=0,lyric_frames=0)
    def frame(self,t):
        f=self.factor
        bg,blur=self.sprites[:2]
        p,sx,sy,r,opacity=bg.pose(t)
        bluralpha=blur.value('F',t)[0]
        source=cv2.addWeighted(self.sharp,opacity*(1-bluralpha),self.blurred,bluralpha,0)
        h,w=source.shape[:2]
        c=math.cos(r);s=math.sin(r)
        matrix=np.array([[c*sx*f,-s*sy*f,(p[0]+106.6666667)*f],[s*sx*f,c*sy*f,p[1]*f]],dtype=np.float32)
        matrix[:,2]-=matrix[:,:2]@np.array([w/2,h/2])
        out=cv2.warpAffine(source,matrix,(self.w,self.h),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
        for sp in self.sprites[2:]:
            if not (sp.start<=t<sp.end):continue
            pos,sx,sy,r,alpha=sp.pose(t)
            if alpha<.001:continue
            original=self.images[sp.path]
            color=sp.value('C',t)[::-1]/255
            if sp.path=='sb/pixel.png':
                if not sp.additive:raise ValueError('Pixel optimization requires additive blending')
                out=cv2.add(out,tuple(float(v*alpha*255) for v in color)+(0.,))
                continue
            key=(sp.path,round(float(sx*f),7),round(float(sy*f),7),tuple(color))
            if key not in self.cache:
                resized=cv2.resize(original,(max(1,round(original.shape[1]*sx*f)),max(1,round(original.shape[0]*sy*f))),interpolation=cv2.INTER_LINEAR)
                rgb=resized[:,:,:3].astype(np.float32)*color
                a=resized[:,:,3:4].astype(np.float32)/255 if resized.shape[2]==4 else np.ones((*resized.shape[:2],1),np.float32)
                # Store premultiplied color; all overlay sprites are unrotated.
                self.cache[key]=(rgb*a,a)
            rgb,a=self.cache[key];hh,ww=rgb.shape[:2]
            x=int(round((pos[0]+106.6666667)*f-ww/2));y=int(round(pos[1]*f-hh/2))
            x0=max(0,x);y0=max(0,y);x1=min(self.w,x+ww);y1=min(self.h,y+hh)
            if x1<=x0 or y1<=y0:continue
            crop=rgb[y0-y:y1-y,x0-x:x1-x];aa=a[y0-y:y1-y,x0-x:x1-x]*alpha
            target=out[y0:y1,x0:x1]
            if sp.additive:
                out[y0:y1,x0:x1]=cv2.addWeighted(target,1,crop,float(alpha),0,dtype=cv2.CV_8U)
            elif sp.path=='sb/vignette.png':
                maskkey=('shade-mask',key)
                if alpha==1 and maskkey in self.cache:mask=self.cache[maskkey]
                else:
                    mask=np.repeat(1-aa,3,axis=2)
                    if alpha==1:self.cache[maskkey]=mask
                out[y0:y1,x0:x1]=cv2.multiply(target,mask,dtype=cv2.CV_8U)
            else:
                result=target*(1-aa)+crop*alpha
                out[y0:y1,x0:x1]=np.clip(result,0,255).astype('uint8')
            if sp.path.startswith('sb/lyric-'):self.stats['lyric_frames']+=1
        self.stats['frames']+=1
        return out

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--start',type=float,default=0);parser.add_argument('--duration',type=float)
    parser.add_argument('--width',type=int,default=1920);parser.add_argument('--fps',type=int,default=30)
    parser.add_argument('--out',default='output/tsukinami-1080p.mp4');parser.add_argument('--stills',action='store_true');parser.add_argument('--verify-only',action='store_true')
    parser.add_argument('--encoder',choices=['libx264','h264_nvenc'],default='libx264')
    args=parser.parse_args();cv2.setNumThreads(4)
    sprites=load_osb(ROOT/'output/tsukinami.osb');verify(sprites)
    if args.verify_only:return
    height=round(args.width*9/16);renderer=Renderer(sprites,args.width,height)
    end=json.loads((ROOT/'data/animation.json').read_text())['duration_ms']/1000
    if args.stills:
        for t in [2.5,25.8,37.8,93.6,114.9,122.,173.8,204.4,219.5,245.,255.5,276.]:
            im=renderer.frame(t*1000);cv2.imencode('.jpg',im,[cv2.IMWRITE_JPEG_QUALITY,94])[1].tofile(str(ROOT/f'output/frame-{t:06.1f}.jpg'))
        return
    duration=args.duration if args.duration is not None else end-args.start
    output=ROOT/args.out;output.parent.mkdir(parents=True,exist_ok=True)
    log=open(ROOT/'work/encode.log','w',encoding='utf8')
    codec=['-c:v','h264_nvenc','-preset','p5','-rc','vbr','-cq','19','-b:v','0'] if args.encoder=='h264_nvenc' else ['-c:v','libx264','-preset','fast','-crf','18']
    cmd=['ffmpeg','-y','-hide_banner','-f','rawvideo','-pixel_format','bgr24','-video_size',f'{args.width}x{height}','-framerate',str(args.fps),'-i','pipe:0',
         '-ss',str(args.start),'-i',str(ROOT/'assets/audio.mp3'),'-map','0:v:0','-map','1:a:0','-t',str(duration),
         *codec,'-pix_fmt','yuv420p','-c:a','aac','-b:a','256k','-ar','48000',
         '-movflags','+faststart','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-metadata','title=ツキナミ — Storyboard',str(output)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log,bufsize=2**24)
    started=time.monotonic();n=math.ceil(duration*args.fps)
    try:
        for i in range(n):
            proc.stdin.write(renderer.frame((args.start+i/args.fps)*1000).tobytes())
            if i%(args.fps*10)==0:print(f'{i}/{n} frames; {i/max(time.monotonic()-started,.001):.1f} fps; music time {args.start+i/args.fps:.1f}s',flush=True)
        proc.stdin.close()
        if proc.wait()!=0:raise RuntimeError('ffmpeg encode failed; see work/encode.log')
    except BaseException:
        proc.kill();raise
    finally:log.close()
    (output.with_suffix('.render.json')).write_text(json.dumps(dict(**renderer.stats,seconds=duration,width=args.width,height=height,fps=args.fps,render_seconds=time.monotonic()-started),indent=2))
    print(str(output),flush=True)

if __name__=='__main__':main()

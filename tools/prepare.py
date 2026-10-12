"""Generate reusable textures and deterministic audio-driven camera tracks."""
import json, subprocess
from pathlib import Path
import numpy as np
from scipy.io import wavfile
from scipy.signal import stft, find_peaks
from scipy.ndimage import gaussian_filter1d
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
SB = ROOT / 'assets/sb'
SB.mkdir(parents=True, exist_ok=True)
work = ROOT / 'work'
work.mkdir(exist_ok=True)
wav = work / 'audio16.wav'
if not wav.exists():
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(ROOT/'assets/audio.mp3'),'-map','0:a:0','-ar','16000','-ac','1',str(wav)],check=True)
sr, audio = wavfile.read(wav)
audio = audio.astype(np.float64) / 32768
duration = len(audio)/sr
freq, times, spec = stft(audio, sr, nperseg=1024, noverlap=768)
mag = np.abs(spec)
bass = np.sqrt(np.mean(mag[(freq>35)&(freq<220)]**2,axis=0))
flux = np.maximum(np.diff(mag,axis=1,prepend=mag[:,:1]),0).mean(axis=0)
impact = gaussian_filter1d(flux,1)
impact /= max(np.percentile(impact,95),1e-8)
peaks,_ = find_peaks(impact, distance=int(.24/(times[1]-times[0])),prominence=.25,height=.5)
env = gaussian_filter1d(np.sqrt(np.mean(mag**2,axis=0)),10)
env = np.clip(env/max(np.percentile(env,90),1e-8),0,1)
ts=np.arange(0,duration+.05,.05)
ts[-1]=duration
kick=np.zeros_like(ts)
for p in peaks:
    dt=ts-times[p]
    kick+=np.clip(impact[p],0,1.4)*np.where((dt>=0)&(dt<.35),np.exp(-np.maximum(dt,0)/.085),0)
kick=np.clip(kick,0,1.5)
energy=np.interp(ts,times,env)
fade=np.minimum(np.clip(ts/1.8,0,1),np.clip((duration-ts)/3,0,1))
tracks=[]
for t,k,e,f in zip(ts,kick,energy,fade):
    tracks.append([round(float(t*1000),3),round(320+3*np.sin(t*.30)+k*1.5*np.sin(t*43),4),
        round(240+2*np.sin(t*.23)+k*np.cos(t*39),4),
        round((480/941)*(1.055+.013*np.sin(t*.19)+.009*k),7),
        round(.002*np.sin(t*.28)+.0018*k*np.sin(t*31),7),
        round(float(.025+.20*k),5),round(float(.045+.085*e+.045*k),5),
        round(float(.04*k),5),round(float(.06+.05*(1-e)),5),round(float(f),5)])
data=dict(duration_ms=duration*1000,columns=['time','x','y','scale','rotation','blur','glow','flash','shade','fade'],tracks=tracks,
          detected_onsets=len(peaks),source='16kHz mono STFT positive spectral flux; 50ms camera sampling')
(ROOT/'data/animation.json').write_text(json.dumps(data,separators=(',',':')),encoding='utf8')
bg=Image.open(ROOT/'assets/bg.png').convert('RGB')
bg.filter(ImageFilter.GaussianBlur(16)).save(SB/'bg-blur.jpg',quality=94)
Image.new('RGBA',(1,1),'white').save(SB/'pixel.png')
w,h=854,480
yy,xx=np.mgrid[0:h,0:w]
vignette=np.clip((((xx-w/2)/(w*.69))**2+((yy-h/2)/(h*.72))**2)*.34,0,.62)
bottom=np.clip((yy-330)/130,0,1)*.50
alpha=1-(1-vignette)*(1-bottom)
rgba=np.zeros((h,w,4),dtype=np.uint8);rgba[:,:,3]=(alpha*255).astype('uint8')
Image.fromarray(rgba).save(SB/'vignette.png')
n=512;yy,xx=np.mgrid[0:n,0:n]
glow=np.exp(-(((xx-256)/145)**2+((yy-256)/145)**2)*2)
arr=np.empty((n,n,4),dtype=np.uint8);arr[:,:,:3]=[255,216,141];arr[:,:,3]=(255*glow).astype('uint8')
Image.fromarray(arr).save(SB/'glow.png')
fontpath='C:/Windows/Fonts/meiryo.ttc'
def texture(text,path,size=64,maxwidth=1600):
    font=ImageFont.truetype(fontpath,size)
    while font.getlength(text)>maxwidth:
        size-=1; font=ImageFont.truetype(fontpath,size)
    box=font.getbbox(text); pad=18
    im=Image.new('RGBA',(box[2]-box[0]+pad*2,box[3]-box[1]+pad*2))
    d=ImageDraw.Draw(im)
    d.text((pad-box[0],pad-box[1]),text,font=font,fill=(255,250,240),stroke_width=2,stroke_fill=(15,20,36,235))
    im.save(path)
    return dict(path='sb/'+path.name,width=im.width,height=im.height)
texture('ツキナミ',SB/'title.png',104)
texture('心臓と脳が、尽きるまで',SB/'tagline.png',32)
cues=json.loads((ROOT/'data/lyrics.json').read_text(encoding='utf8')) if (ROOT/'data/lyrics.json').exists() else []
for i,cue in enumerate(cues):
    text=cue['text'];font=ImageFont.truetype(fontpath,58)
    breaks={
      '右手だってちゃんと働いているよ':['右手だってちゃんと','働いているよ'],
      'なりたいものの前で恥じてる様じゃ':['なりたいものの前で','恥じてる様じゃ'],
      '日々の忘却曲線のストッパーは':['日々の忘却曲線の','ストッパーは'],
      '心に映す事が許されている間に':['心に映す事が','許されている間に'],
      'いつかあなたがこの破片を拾って胸に飾る様な':['いつかあなたがこの破片を拾って','胸に飾る様な'],
      '思い出は網膜のシャッター音の数':['思い出は網膜の','シャッター音の数'],
      'なれないものの後ろで焦がれるのは':['なれないものの後ろで','焦がれるのは'],
      '手違いのエラー起こしたがっている':['手違いのエラー','起こしたがっている'],
      '尊さは一つだけしかない事みたい':['尊さは一つだけしか','ない事みたい'],
      'きっとあなたが微笑んだり涙を流す様な':['きっとあなたが微笑んだり','涙を流す様な']}
    parts=breaks.get(text,[text]);size=58
    while max(font.getlength(p) for p in parts)>900:
        size-=1;font=ImageFont.truetype(fontpath,size)
    assert ''.join(parts)==cue['text']
    text='\n'.join(parts)
    probe=ImageDraw.Draw(Image.new('RGBA',(1,1)))
    box=probe.multiline_textbbox((0,0),text,font=font,spacing=12,stroke_width=3)
    pad=28;im=Image.new('RGBA',(box[2]-box[0]+pad*2,box[3]-box[1]+pad*2))
    shadow=Image.new('RGBA',im.size);d=ImageDraw.Draw(shadow)
    pos=(pad-box[0],pad-box[1])
    d.multiline_text(pos,text,font=font,spacing=12,fill=(5,11,25,255),stroke_width=7,stroke_fill=(5,11,25,210))
    im=Image.alpha_composite(im,shadow.filter(ImageFilter.GaussianBlur(5)))
    ImageDraw.Draw(im).multiline_text(pos,text,font=font,spacing=12,fill=(255,250,235,255),stroke_width=2,stroke_fill=(17,24,39,220))
    path=SB/f'lyric-{i:03}.png';im.save(path)
    cue.update(path='sb/'+path.name,width=im.width,height=im.height,display_lines=parts)
    cue['scale']=.4444444
    corner=['upper-left','lower-right','upper-right','lower-left'][i%4]
    left=corner.endswith('left');upper=corner.startswith('upper')
    cue.update(layout=corner,x=(-54+im.width*cue['scale']/2 if left else 694-im.width*cue['scale']/2),
               y=(52+im.height*cue['scale']/2 if upper else 422-im.height*cue['scale']/2),
               drift_x=10 if left else -10,drift_y=5 if upper else -5)
(ROOT/'data/lyrics.json').write_text(json.dumps(cues,ensure_ascii=False,indent=2),encoding='utf8')
print(f'Prepared {duration:.3f}s, {len(peaks)} audio onsets, {len(tracks)} animation samples, {len(cues)} lyric cues.')

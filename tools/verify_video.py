"""Decode the entire delivered video and record inspectable stream checks."""
from pathlib import Path
import hashlib
import json,subprocess
ROOT=Path(__file__).resolve().parents[1]
video=ROOT/'output/tsukinami-1080p.mp4'
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(video)]))
v=next(s for s in probe['streams'] if s['codec_type']=='video')
a=next(s for s in probe['streams'] if s['codec_type']=='audio')
target=json.loads((ROOT/'data/animation.json').read_text())['duration_ms']/1000
assert v['codec_name']=='h264' and (v['width'],v['height'])==(1920,1080)
assert v['avg_frame_rate']=='30/1'
assert a['codec_name']=='aac' and a['sample_rate']=='48000' and a['channels']==2
assert abs(float(probe['format']['duration'])-target)<.10
decode=subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(video),'-map','0:v:0','-map','0:a:0','-f','null','-'],capture_output=True,text=True)
assert decode.returncode==0,decode.stderr
repro=ROOT/'work/repro'
reproduction={}
if repro.exists():
    for name in ['data/animation.json','data/lyrics.json','output/tsukinami.osb']:
        reproduction[name]=hashlib.sha256((ROOT/name).read_bytes()).digest()==hashlib.sha256((repro/name).read_bytes()).digest()
    assert all(reproduction.values()),'Clean copy reproduction differs'
report=dict(status='passed',video=dict(codec=v['codec_name'],width=v['width'],height=v['height'],fps=30,
       frames=int(v['nb_frames']),seconds=float(v['duration'])),
       audio=dict(codec=a['codec_name'],sample_rate=int(a['sample_rate']),channels=a['channels'],seconds=float(a['duration'])),
       full_decode_exit_code=decode.returncode,bytes=video.stat().st_size,
       storyboard=json.loads((ROOT/'output/delivery-checks.json').read_text()),
       native_parity=json.loads((ROOT/'output/parity.json').read_text()),
       clean_copy_reproduction=reproduction or 'not run in this workspace',
       review_status='Qualified; human visual and audible acceptance pending')
(ROOT/'output/validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report['video'],ensure_ascii=False));print('Full video and audio decode passed.')

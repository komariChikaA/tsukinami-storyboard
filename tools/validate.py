"""Delivery checks: exact lyric coverage, every cue's bounds, every camera sample."""
from pathlib import Path
import json,math
import numpy as np
from render import load_osb
ROOT=Path(__file__).resolve().parents[1]
cues=json.loads((ROOT/'data/lyrics.json').read_text(encoding='utf8'))
lyrics=(ROOT/'data/lyrics.txt').read_text(encoding='utf8').splitlines()
assert [c['text'] for c in cues]==lyrics,'Provided lyrics changed or omitted'
assert all(''.join(c['display_lines'])==c['text'] for c in cues)
assert all(c['start']<c['end'] and (i==0 or c['start']>=cues[i-1]['end']) for i,c in enumerate(cues))
sprites=load_osb(ROOT/'output/tsukinami.osb');byname={s.path:s for s in sprites}
layouts=set();motion=0
for cue in cues:
    sp=byname[cue['path']];layouts.add(cue['layout'])
    poses=[sp.pose(t*1000) for t in (cue['start']+.12,(cue['start']+cue['end'])/2,cue['end']-.12)]
    for pos,sx,sy,r,a in poses:
        x0=pos[0]-cue['width']*sx/2;x1=pos[0]+cue['width']*sx/2
        y0=pos[1]-cue['height']*sy/2;y1=pos[1]+cue['height']*sy/2
        assert -106.66<=x0<x1<=746.67 and 0<=y0<y1<=480,(cue['text'],x0,x1,y0,y1)
    motion+=int(np.linalg.norm(poses[0][0]-poses[-1][0])>3)
assert motion==len(cues),'Some lyrics are static'
tracks=json.loads((ROOT/'data/animation.json').read_text())['tracks']
corners=np.array([[-106.6667,0],[746.6667,0],[-106.6667,480],[746.6667,480]])
margin=1e9
for row in tracks:
    t,x,y,scale,r,*_=row
    rotation=np.array([[math.cos(r),-math.sin(r)],[math.sin(r),math.cos(r)]])
    pixels=(corners-[x,y])@rotation/scale+[1672/2,941/2]
    edge=min(pixels[:,0].min(),1672-pixels[:,0].max(),pixels[:,1].min(),941-pixels[:,1].max())
    assert edge>0,f'Exposed background border at {t}ms'
    margin=min(margin,edge)
report=dict(lyric_cues=len(cues),provided_lyrics_exact=True,semantic_wrapping_exact=True,
            moving_lyric_cues=motion,layouts=sorted(layouts),lyric_bound_checks=len(cues)*3,
            camera_samples=len(tracks),minimum_source_edge_margin_pixels=round(margin,3),
            status='passed',limitation='ASR-assisted line timing; detailed audible sync requires human review')
(ROOT/'output/delivery-checks.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))

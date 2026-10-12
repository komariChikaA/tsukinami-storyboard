"""Small portable OSB package. No caches, models, logs or encoded video."""
from pathlib import Path
import json,zipfile,hashlib
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'output';out.mkdir(exist_ok=True)
with zipfile.ZipFile(out/'tsukinami-storyboard.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for file in (ROOT/'assets').rglob('*'):
        if file.is_file():z.write(file,Path('tsukinami')/file.relative_to(ROOT/'assets'))
    z.write(out/'tsukinami.osb','tsukinami/tsukinami.osb')
cues=json.loads((ROOT/'data/lyrics.json').read_text(encoding='utf8'))
def stamp(t):
    ms=round(t*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'
(out/'lyrics.srt').write_text('\n\n'.join(f"{i+1}\n{stamp(c['start'])} --> {stamp(c['end'])}\n"+'\n'.join(c['display_lines']) for i,c in enumerate(cues))+'\n',encoding='utf8')
files=['tsukinami-1080p.mp4','tsukinami-storyboard.zip','lyrics.srt']
manifest=[]
for name in files:
    p=out/name
    if p.exists():manifest.append(dict(file=name,bytes=p.stat().st_size,sha256=hashlib.file_digest(p.open('rb'),'sha256').hexdigest()))
(out/'manifest.json').write_text(json.dumps(manifest,indent=2))
print('Packaged storyboard, Japanese SRT and SHA-256 manifest.')

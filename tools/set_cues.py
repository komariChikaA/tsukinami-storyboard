"""Editorial timing: boundaries checked against local ASR word timestamps.

Authoritative words come from data/lyrics.txt, never ASR guesses.
"""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
lines=(root/'data/lyrics.txt').read_text(encoding='utf8').splitlines()
intervals=[
 (23.54,26.4),(26.44,29.02),(29.06,31.8),(31.84,34.36),
 (34.42,37.68),(37.72,40.04),(40.1,43.25),(43.92,45.55),
 (65.88,70.56),(70.6,76.38),(76.44,78.12),(78.18,84.68),(84.74,86.6),
 (86.66,91.46),(91.52,96.08),(96.18,97.54),(97.6,99.84),
 (99.9,103.06),(103.12,108.0),(108.7,112.4),(112.46,114.02),
 (114.08,117.62),(117.68,125.24),(125.3,130.2),
 (150.44,155.62),(155.68,160.8),(160.86,162.84),(162.9,168.92),(168.98,171.1),
 (171.46,175.72),(175.78,180.5),(180.62,182.2),(182.26,184.22),
 (184.28,187.58),(187.64,192.74),(192.84,196.78),(196.84,197.88),
 (197.94,201.92),(201.98,209.3),(209.36,213.74),
 (213.8,218.18),(218.24,222.78),(222.84,228.38),(228.44,234.3),
 (234.68,238.4),(238.64,240.85),(240.92,244.45),(244.72,247.02),(247.08,249.65),
 (249.7,254.25),(254.5,259.65),(259.8,263.1)]
assert len(lines)==len(intervals)
items=[dict(start=a,end=b,text=text,source='provided Japanese lyrics; local ASR-assisted editorial timing') for text,(a,b) in zip(lines,intervals)]
(root/'data/lyrics.json').write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf8')

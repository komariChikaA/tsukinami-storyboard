"""Local timing aid. ASR output is never used as the authoritative lyric text."""
import json
from pathlib import Path
from faster_whisper import WhisperModel

root = Path(__file__).resolve().parents[1]
model = WhisperModel('small', device='cpu', compute_type='int8', cpu_threads=8,
                     download_root=str(root / 'work' / 'models'))
segments, info = model.transcribe(str(root / 'work' / 'audio16.wav'), language='ja',
                                 word_timestamps=True, vad_filter=False, beam_size=5)
result = []
for s in segments:
    item = dict(start=s.start, end=s.end, text=s.text,
                words=[dict(start=w.start, end=w.end, text=w.word) for w in s.words])
    result.append(item)
    print(f'{s.start:.2f} - {s.end:.2f}: {s.text}', flush=True)
    (root / 'work' / 'transcription.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf8')

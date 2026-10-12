import json
from pathlib import Path
from faster_whisper import WhisperModel
root=Path(__file__).resolve().parents[1]
model=WhisperModel('medium',device='cpu',compute_type='int8',cpu_threads=8,download_root=str(root/'work/models'))
prompt='今が欲しいなんて 叶いもしないなんて だから愛しくなるのかな 失って忘れない様に こうして歌っているんだよ 鼓動、脈を鳴らす 心臓と脳が 尽きるまで'
segments,_=model.transcribe(str(root/'work/tail.wav'),language='ja',word_timestamps=True,condition_on_previous_text=False,initial_prompt=prompt,beam_size=5)
results=[]
for s in segments:
    results.append(dict(start=s.start+230,end=s.end+230,text=s.text,words=[dict(start=w.start+230,end=w.end+230,text=w.word) for w in s.words]))
    print(f'{s.start+230:.2f} - {s.end+230:.2f}: {s.text}',flush=True)
    (root/'work/tail-transcription.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8')

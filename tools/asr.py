import sys,json,os
from faster_whisper import WhisperModel
name=sys.argv[2]; out=name[:-4]+'.asr.json'
if os.path.exists(out): sys.exit(0)
m=WhisperModel(sys.argv[1],device='cpu',compute_type='int8',cpu_threads=4)
segs,info=m.transcribe(name,language='ja',vad_filter=True,beam_size=5,condition_on_previous_text=False)
r=[{'start':round(s.start,2),'end':round(s.end,2),'text':s.text} for s in segs]
json.dump(r,open(out,'w',encoding='utf8'),ensure_ascii=False,indent=0); print(name,len(r),flush=True)

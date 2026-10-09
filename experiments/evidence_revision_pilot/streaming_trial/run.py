"""Causal packet replay with native video inputs and model-generated external memory."""
import pathlib,json,hashlib,time,datetime,argparse
import numpy as np
from PIL import Image
R=pathlib.Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def parse(text):
 try:return json.JSONDecoder().raw_decode(text[text.index('{'):])[0]
 except (ValueError,json.JSONDecodeError):return None
class Model:
 def __init__(self):
  import torch,transformers
  from transformers import Qwen3VLForConditionalGeneration,AutoProcessor
  self.torch=torch;torch.set_num_threads(4);torch.manual_seed(0)
  self.processor=AutoProcessor.from_pretrained(R/'model',local_files_only=True)
  self.model=Qwen3VLForConditionalGeneration.from_pretrained(R/'model',dtype=torch.bfloat16,attn_implementation='sdpa',local_files_only=True).eval()
  self.meta={'torch':torch.__version__,'transformers':transformers.__version__,'dtype':'bfloat16','device':'cpu','threads':4,'decoding':'greedy','max_new_tokens':180,'native_video':True,'custom_feature_cache':False,'video_pixels':{'shortest_edge':64*32*32,'longest_edge':128*32*32}}
 def generate(self,packets,prompt):
  content=[];videos=[];metadata=[]
  for packet in packets:
   content.extend([{'type':'text','text':f"Video packet: original capture time {packet['capture_start']}–{packet['capture_end']} seconds. Native frame timestamps refer to that original capture clock."},{'type':'video'}])
   videos.append(np.stack([np.asarray(Image.open(R/f['path']).convert('RGB')) for f in packet['frames']]))
   metadata.append({'fps':packet['source_fps'],'total_num_frames':packet['total_source_frames'],'frames_indices':[f['source_frame_index'] for f in packet['frames']]})
  content.append({'type':'text','text':prompt})
  txt=self.processor.apply_chat_template([{'role':'user','content':content}],tokenize=False,add_generation_prompt=True)
  inputs=self.processor(text=[txt],videos=videos,videos_kwargs={'do_sample_frames':False,'video_metadata':metadata,'size':self.meta['video_pixels']},return_tensors='pt') if videos else self.processor(text=[txt],return_tensors='pt')
  if videos:assert 'pixel_values_videos' in inputs and 'video_grid_thw' in inputs
  grids=inputs['video_grid_thw'].tolist() if videos else [];assert len(grids)==len(packets)
  start=time.perf_counter()
  with self.torch.inference_mode():out=self.model.generate(**inputs,max_new_tokens=180,do_sample=False)
  answer=self.processor.batch_decode(out[:,inputs['input_ids'].shape[1]:],skip_special_tokens=True)[0]
  return answer,time.perf_counter()-start,grids

def prompt(c,memory,latest):
 return ('You receive a video stream packet by packet. Capture time describes when something happened; arrival order may differ. A late packet is older evidence, not a new physical occurrence. Update the historical facts it supports, and preserve facts about later capture times. Base the current state on the latest CAPTURE time observed. Your earlier response may be incomplete; revise it when evidence warrants.\nLatest capture boundary received: '+str(latest)+' seconds.\nPrevious model-produced memory: '+memory+'\nTask: '+c['question']+'\nReturn only one JSON object with these keys: '+json.dumps(list(c['schema']))+'. Use unknown for unsupported fields. Do not give explanations.')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--smoke',action='store_true');a=ap.parse_args();p=json.loads((R/'protocol.json').read_text());model=Model();out=R/'results/run.json';rows=json.loads(out.read_text())['results'] if out.exists() else [];done={x['id']:x for x in rows}
 def save(row):
  rows.append(row);done[row['id']]=row;out.write_text(json.dumps({'protocol_sha256':sha(R/'protocol.json'),'model':json.loads((R/'model_manifest.json').read_text()),'environment':model.meta,'results':rows},indent=2));print(row['id'],repr(row['response']),round(row['seconds'],2),flush=True)
 # Perception gates precede the streaming runs. No case is discarded based on their results.
 for c in p['cases']:
  tests=[('historical_perception',c['late_packet'], 'What part is being detached from the camera body in this clip? Return JSON {"value":"lens"}, {"value":"cap"}, or {"value":"unknown"}.' if c['id']=='camera' else 'Around source time 72 seconds, is the large round tray resting on the table frame? Return JSON with key value, using yes, no, or unknown.', 'lens' if c['id']=='camera' else 'no'),('current_perception',3 if c['id']=='camera' else 5,'At the end of this clip, is the cylindrical lens attached to the camera body? Return JSON with key value, using yes, no, or unknown.' if c['id']=='camera' else 'At the end of this clip, is the large round tray resting on the table frame? Return JSON with key value, using yes, no, or unknown.','yes')]
  for label,k,q,expected in tests:
   id=f'{c["id"]}_{label}'
   if id in done:continue
   packets=[c['packets'][k]];ans,secs,grids=model.generate(packets,q);save({'id':id,'case':c['id'],'condition':label,'packets':packets,'prompt':q,'response':ans,'parsed':parse(ans),'expected':{'value':expected},'seconds':secs,'video_grids':grids})
   if a.smoke:return
 for c in p['cases']:
  for condition,key in [('chronological','chronological_order'),('delayed','delayed_order')]:
   memory='{}';arrived=[];latest=0
   for step,k in enumerate(c[key]):
    packet=c['packets'][k];arrived.append(k);latest=max(latest,packet['capture_end']);id=f'{c["id"]}_{condition}_{step}'
    q=prompt(c,memory,latest)
    if id in done:
     row=done[id];assert row['prompt']==q;memory=row['response'];continue
    ans,secs,grids=model.generate([packet],q)
    save({'id':id,'case':c['id'],'condition':condition,'step':step,'packet_id':k,'arrived_packet_ids':list(arrived),'latest_capture_boundary':latest,'packets':[packet],'input_memory':memory,'prompt':q,'response':ans,'parsed':parse(ans),'seconds':secs,'video_grids':grids});memory=ans
  # Same arrived packet multiset at the comparison point, with no model-generated memory bottleneck.
  upto=c['checkpoint_after_late']+1;ids=c['delayed_order'][:upto];packets=[c['packets'][k] for k in ids];id=c['id']+'_all_arrived_control'
  if id not in done:
   q=prompt(c,'{}',max(x['capture_end'] for x in packets));ans,secs,grids=model.generate(packets,q);save({'id':id,'case':c['id'],'condition':'all_arrived_control','arrived_packet_ids':ids,'packets':packets,'prompt':q,'response':ans,'parsed':parse(ans),'expected':c['expected_at_join'],'seconds':secs,'video_grids':grids})
if __name__=='__main__':main()

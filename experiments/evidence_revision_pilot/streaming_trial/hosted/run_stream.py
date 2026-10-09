"""Qualified paired streaming trial using the official hosted Qwen3-VL demo."""
import pathlib,json,hashlib,subprocess,time,datetime,re
from gradio_client import Client,handle_file
R=pathlib.Path(__file__).resolve().parent;BASE=R.parent

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def parse(text):
 try:return json.JSONDecoder().raw_decode(text[text.index('{'):])[0]
 except (ValueError,json.JSONDecodeError):return None
def passes(obj,expected):return isinstance(obj,dict) and all(obj.get(k)==v for k,v in expected.items())
def gate_value(text):
 obj=parse(text)
 if isinstance(obj,dict):return str(obj.get('value','')).strip().lower()
 return text.strip().strip('`').strip().lower()

p=json.loads((BASE/'protocol.json').read_text());meta=json.loads((R/'metadata.json').read_text());media=R/'media';media.mkdir(exist_ok=True)
for c in p['cases']:
 for packet in c['packets']:
  file=media/f'{c["id"]}_{packet["id"]}.mp4'
  if not file.exists():subprocess.run(['ffmpeg','-loglevel','error','-y','-framerate','1','-i',str(BASE/'packets'/f'{c["id"]}_{packet["id"]}_%d.png'),'-frames:v','4','-c:v','libx264','-crf','10','-pix_fmt','yuv420p',str(file)],check=True)
  packet['encoded_video']=str(file.relative_to(BASE));packet['encoded_sha256']=sha(file)
p['model']='Hosted qwen3-vl-235b-a22b-instruct; declared by official demo app';p['representation']='Each packet is the same four source frames encoded as a four-second H.264 video at 1fps. Capture-clock mapping is provided. Provider resampling and decoding parameters are not exposed.';p['service_app_revision']=meta['sha'];p['scope']+=' Hosted service results are preliminary; model weights and randomness are not controllable.'
(R/'protocol.json').write_text(json.dumps(p,indent=2));out=R/'run.json';report=json.loads(out.read_text()) if out.exists() else {'protocol_sha256':sha(R/'protocol.json'),'model':p['model'],'app_revision':meta['sha'],'results':[],'case_status':{}}
assert report['protocol_sha256']==sha(R/'protocol.json');rows=report['results'];done={x['id']:x for x in rows}
client=Client(meta['host'],hf_token=False,httpx_kwargs={'timeout':60})
def persist():out.write_text(json.dumps(report,indent=2))
def call(id,c,condition,packets,q,extra=None):
 if id in done:return done[id]
 mapping='\n'.join(f'Video {i+1}: original capture interval {v["capture_start"]}–{v["capture_end"]} seconds; its four frames have original capture timestamps '+json.dumps([round(f['source_time'],3) for f in v['frames']])+'.' for i,v in enumerate(packets))
 prompt='Playback time within each uploaded file is local to that file. Use the following original CAPTURE clock for event order and historical/current states:\n'+mapping+'\n'+q
 start=time.perf_counter();client.predict(api_name='/reset_state')
 for packet in packets:client.predict([],handle_file(str(BASE/packet['encoded_video'])),api_name='/add_file')
 # Visible chatbot history is separate from the server's own per-session file state.
 # Empty visible history avoids a demo file-message serialization error. reset_state
 # guarantees that server state contains only the packets uploaded for THIS call.
 h=client.predict([],prompt,api_name='/add_text');reply=client.predict(h,api_name='/predict');text=reply[-1][1]
 if not isinstance(text,str):raise ValueError('Expected text response')
 row={'id':id,'case':c['id'],'condition':condition,'packets':packets,'prompt':prompt,'response':text,'parsed':parse(text),'seconds':time.perf_counter()-start,'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),**(extra or {})};rows.append(row);done[id]=row;persist();print(id,repr(text),round(row['seconds'],1),flush=True);return row

def task(c,memory,latest):
 return 'You receive video packets sequentially. Capture time describes when something happened; arrival order may differ. A late packet is older evidence, not a new physical occurrence. Update supported historical facts and preserve later facts. Current state refers to the latest CAPTURE time received, not the last arrival. Earlier memory may be incomplete and may be corrected.\nLatest capture boundary received: '+str(latest)+' seconds.\nPrevious model-produced memory: '+memory+'\nTask: '+c['question']+'\nReturn only one JSON object with these keys: '+json.dumps(list(c['schema']))+'. Use unknown for unsupported fields. Do not give explanations.'

for c in p['cases']:
 if c['id']=='camera':tests=[('historical',1,'What part is being detached from the camera BODY in this clip: the cylindrical lens assembly or just its flat front cap? Return JSON with key value, using lens, cap, or unknown.','lens'),('current',3,'At the END of this clip, is the cylindrical lens attached to the camera body? Return JSON with key value, using yes, no, or unknown.','yes')]
 else:tests=[('historical',1,'Around original capture time 72 seconds, is the large round TRAY resting on the table frame? Distinguish the open frame rails from the solid tray. Return JSON with key value, using yes, no, or unknown.','no'),('current',5,'At the END of this clip, is the large round tray resting on the table frame? Return JSON with key value, using yes, no, or unknown.','yes')]
 gates=[]
 for label,k,q,expected in tests:
  row=call(f'{c["id"]}_{label}_gate',c,'perception_gate',[c['packets'][k]],q,{'expected':{'value':expected}});gates.append(gate_value(row['response'])==expected)
 if not all(gates):report['case_status'][c['id']]={'status':'ineligible_perception','gates':gates};persist();continue
 # Reject a prior-only answer shortcut: the requested task with no visual evidence.
 blind=call(c['id']+'_blind',c,'no_video_control',[],task(c,'{}',c['packets'][c['checkpoint_after_late']]['capture_end']),{'expected':c['schema']})
 if passes(blind['parsed'],c['expected_at_join']):report['case_status'][c['id']]={'status':'ineligible_blind_answer_shortcut'};persist();continue
 j=c['checkpoint_after_late'];ids=c['delayed_order'][:j+1];packets=[c['packets'][k] for k in ids];latest=max(v['capture_end'] for v in packets)
 full=call(c['id']+'_all_arrived',c,'all_arrived_control',packets,task(c,'{}',latest),{'expected':c['expected_at_join'],'arrived_packet_ids':ids})
 if not passes(full['parsed'],c['expected_at_join']):report['case_status'][c['id']]={'status':'ineligible_full_evidence'};persist();continue
 checkpoints={};stop=False
 for condition,key in [('chronological','chronological_order'),('delayed','delayed_order')]:
  memory='{}';arrived=[];latest=0
  for step,k in enumerate(c[key]):
   packet=c['packets'][k];arrived.append(k);latest=max(latest,packet['capture_end'])
   row=call(f'{c["id"]}_{condition}_{step}',c,condition,[packet],task(c,memory,latest),{'step':step,'input_memory':memory,'arrived_packet_ids':list(arrived),'latest_capture_boundary':latest});memory=row['response']
   if step==j:
    checkpoints[condition]=passes(row['parsed'],c['expected_at_join'])
    if condition=='chronological' and not checkpoints[condition]:stop=True;break
  if stop:break
 report['case_status'][c['id']]={'status':'ineligible_chronological' if stop else ('candidate_arrival_order_failure' if not checkpoints['delayed'] else 'no_arrival_order_failure_at_checkpoint'),'checkpoint_passes':checkpoints};persist()
report['finished']=True;persist();print('FINISHED',report['case_status'],flush=True)

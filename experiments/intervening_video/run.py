"""Nine-call sampled-video diagnostic; fixed conditions, isolated sessions, resumable."""
import json,hashlib,time,datetime,os,concurrent.futures
from pathlib import Path
from gradio_client import Client,handle_file
R=Path(__file__).resolve().parent
S=R.parent/'evidence_revision_pilot/streaming_trial'
HOST='https://qwen-qwen3-vl-235b-a22b-instruct-demo.hf.space'
ORDERS={'chronological':[[0],[1],[2,3,4,5],[6]],'delayed':[[0],[2,3,4,5],[1],[6]],'together':[[0,1,2,3,4,5]]}
INSTRUCTIONS='''You are observing a video stream delivered in packets. Use only evidence received so far and the supplied memory. Distinguish arrival time from capture time. A packet may depict an earlier event. Treat supplied capture timestamps as authoritative. Update historical facts only when supported. Do not treat older footage as the latest physical state. Preserve supported facts that incoming evidence does not change. Retain uncertainty when evidence is insufficient.'''
TASK='''Track the large round tray and the table frame.
earlier: Was the tray resting on the frame around original capture time 72 seconds?
latest: Was the tray resting on the frame at the latest capture time received?
An open frame is not the solid tray. Do not infer the earlier state solely from later footage. Use unknown when the relevant evidence has not been received.
Return only one JSON object with exactly two keys, earlier and latest; values must be yes, no, or unknown.'''
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,obj):
 t=p.with_suffix('.tmp')
 with t.open('w') as f:json.dump(obj,f,indent=2);f.flush();os.fsync(f.fileno())
 t.replace(p)
def setup():
 packets=next(c for c in json.loads((S/'hosted/protocol.json').read_text())['cases'] if c['id']=='table')['packets']
 for p in packets:assert digest(S/p['encoded_video'])==p['encoded_sha256']
 protocol={'orders':ORDERS,'packets':packets,'instructions':INSTRUCTIONS,'task':TASK,'host':HOST,'declared_model':'Qwen3-VL-235B-A22B-Instruct','expected_at_join_and_continuation':{'earlier':'no','latest':'yes'},'limits':['One HoloAssist episode','Four sampled frames per packet','Grouped intervening footage','Supplied capture times','External two-field model-generated memory','Uncontrolled public backend decoding','Instructions prepended to user message: no system-role endpoint'],'execution':'Independent conditions concurrent; steps sequential within condition. Fresh client/session per call. No retries. 300 second endpoint timeout.'}
 if (R/'protocol.json').exists():assert json.loads((R/'protocol.json').read_text())==protocol
 else:save(R/'protocol.json',protocol)
 (R/'responses').mkdir(exist_ok=True)
 return packets
def request(client,*args,api_name):
 job=client.submit(*args,api_name=api_name)
 try:return job.result(timeout=300)
 except Exception:job.cancel();raise

def run_condition(name,packets):
 memory='{}';arrived=[]
 for step,ids in enumerate(ORDERS[name]):
  arrived.extend(ids);latest=max(f['source_time'] for k in arrived for f in packets[k]['frames'])
  mapping='\n'.join(f'Uploaded video {i+1}, packet {k}: original capture timestamps '+json.dumps([round(f['source_time'],3) for f in packets[k]['frames']]) for i,k in enumerate(ids))
  prompt=INSTRUCTIONS+'\nINCOMING VIDEO PACKETS\n'+mapping+'\nPlayback time within each file is local, not the original capture clock.\nLATEST CAPTURE TIME RECEIVED: '+str(round(latest,3))+'\nPREVIOUS MODEL-PRODUCED MEMORY:\n'+memory+'\n'+TASK
  path=R/'responses'/f'{name}_{step}.json'
  if path.exists():
   row=json.loads(path.read_text());assert row['prompt']==prompt
   if row['status']!='completed':return
   memory=row['response'];continue
  row={'id':f'{name}_{step}','condition':name,'step':step,'packets':ids,'arrived':list(arrived),'input_memory':memory,'prompt':prompt,'latest_capture_time':latest,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};start=time.perf_counter()
  print('START',row['id'],flush=True)
  try:
   client=Client(HOST,hf_token=False,httpx_kwargs={'timeout':60},verbose=False)
   request(client,api_name='/reset_state')
   for k in ids:request(client,[],handle_file(str(S/packets[k]['encoded_video'])),api_name='/add_file')
   h=request(client,[],prompt,api_name='/add_text');reply=request(client,h,api_name='/predict');answer=reply[-1][1]
   if not isinstance(answer,str):raise TypeError('Expected textual answer')
   try:parsed=json.JSONDecoder().raw_decode(answer[answer.index('{'):])[0]
   except (ValueError,TypeError):parsed=None
   row.update(status='completed',response=answer,parsed=parsed,schema_valid=isinstance(parsed,dict) and set(parsed)=={'earlier','latest'} and all(v in ['yes','no','unknown'] for v in parsed.values()));memory=answer
  except Exception as e:row.update(status='error',error=repr(e))
  row['seconds']=time.perf_counter()-start;save(path,row)
  print('DONE',row['id'],row.get('parsed',row.get('error')),round(row['seconds'],1),flush=True)
  if row['status']=='error':return

def audit():
 rows=[json.loads(p.read_text()) for p in sorted((R/'responses').glob('*.json'))];by={r['id']:r for r in rows}
 for n in ['chronological','delayed']:
  for i in range(1,4):
   a=by.get(f'{n}_{i-1}');b=by.get(f'{n}_{i}')
   if a and b and a['status']=='completed':assert a['response']==b['input_memory']
 expected={'earlier':'no','latest':'yes'};keys=['together_0','chronological_2','delayed_2','chronological_3','delayed_3']
 checks={k:bool(by[k].get('schema_valid')) and by[k].get('parsed')==expected for k in keys if k in by and by[k]['status']=='completed'}
 complete=len(rows)==9 and all(r['status']=='completed' for r in rows)
 if not complete:verdict='incomplete'
 elif not checks['together_0']:verdict='Full-evidence control failed; streaming-specific inference not justified.'
 elif not checks['chronological_2'] or not checks['chronological_3']:verdict='Chronological control failed; delayed-evidence mechanism not isolated.'
 elif not checks['delayed_2'] or not checks['delayed_3']:verdict='Candidate arrival-order effect; requires independent replication.'
 else:verdict='No delayed-evidence failure at the comparison checkpoints.'
 save(R/'results.json',{'complete':complete,'completed_calls':sum(r['status']=='completed' for r in rows),'verdict':verdict,'checkpoint_matches':checks,'protocol_sha256':digest(R/'protocol.json'),'responses':rows});print('VERDICT',verdict,flush=True)
if __name__=='__main__':
 packets=setup()
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
  for f in concurrent.futures.as_completed([pool.submit(run_condition,n,packets) for n in ORDERS]):f.result()
 audit()

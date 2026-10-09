"""Six preregistered endpoint-image versus sampled-video recognition checks."""
import json,time,datetime,hashlib,concurrent.futures,os
from pathlib import Path
from gradio_client import Client,handle_file
R=Path(__file__).resolve().parent
HOST='https://qwen-qwen3-vl-235b-a22b-instruct-demo.hf.space'
CASES=[('camera','Is the cylindrical lens visibly mounted on the camera body, rather than held separately? Ignore the front lens cap.','yes'),('table','Is the large round tray resting on the table frame? An open frame is not the solid tray.','no'),('printer','Is the large central LCD displaying an illuminated interface? Ignore the small illuminated buttons and indicator lights.','no')]
def save(p,v):
 t=p.with_suffix('.tmp')
 with t.open('w') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
 t.replace(p)
def api(c,*args,api_name):
 j=c.submit(*args,api_name=api_name)
 try:return j.result(timeout=240)
 except Exception:j.cancel();raise

def trial(case,question,expected,kind):
 k=case+'_'+kind;out=R/'responses'/f'{k}.json';f=R/'inputs'/f'{case}.{ "png" if kind=="image" else "mp4"}'
 prompt=('Inspect the supplied image. ' if kind=='image' else 'Inspect the END of the supplied video. Answer for the final visible frame, not an earlier state. ')+question+' Return only JSON with key value and value yes, no, or unknown.'
 if out.exists():return json.loads(out.read_text())
 row={'id':k,'case':case,'kind':kind,'input':str(f.relative_to(R)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'prompt':prompt,'expected':expected,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};start=time.perf_counter();print('START',k,flush=True)
 try:
  c=Client(HOST,hf_token=False,httpx_kwargs={'timeout':60},verbose=False);api(c,api_name='/reset_state');api(c,[],handle_file(str(f)),api_name='/add_file');h=api(c,[],prompt,api_name='/add_text');reply=api(c,h,api_name='/predict');ans=reply[-1][1]
  try:obj=json.JSONDecoder().raw_decode(ans[ans.index('{'):])[0]
  except (ValueError,TypeError):obj=None
  # Fixed semantic scoring permits a renamed key only when there is exactly one scalar.
  value=next(iter(obj.values())) if isinstance(obj,dict) and len(obj)==1 else None
  if isinstance(value,bool):value='yes' if value else 'no'
  if isinstance(value,str):value=value.strip().lower()
  row.update(status='completed',response=ans,parsed=obj,semantic_value=value,correct=value==expected,exact_schema=isinstance(obj,dict) and set(obj)=={'value'} and obj['value'] in ['yes','no','unknown'])
 except Exception as e:row.update(status='error',error=repr(e))
 row['seconds']=time.perf_counter()-start;save(out,row);print('DONE',k,row.get('semantic_value',row.get('error')),flush=True);return row
if __name__=='__main__':
 (R/'responses').mkdir(exist_ok=True)
 protocol={'cases':CASES,'host':HOST,'calls':6,'retry_policy':'none','purpose':'Endpoint recognition controls. Images show only endpoints, videos also contain preceding frames; differences cannot uniquely identify provider ingestion failures.','limits':['Not original-event association','No native continuous stream','Labels visually checked by assistant only','Public backend sampling and decoding unverified'],'scoring':'One JSON scalar, case-normalized; boolean normalized. Exact schema separately reported.'}
 if (R/'protocol.json').exists():assert json.loads((R/'protocol.json').read_text())==json.loads(json.dumps(protocol))
 else:save(R/'protocol.json',protocol)
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  futures=[pool.submit(trial,*c,k) for c in CASES for k in ['image','video']];rows=[f.result() for f in futures]
 save(R/'results.json',{'rows':rows,'completed':sum(r['status']=='completed' for r in rows),'correct':sum(r.get('correct',False) for r in rows)});print('COMPLETE',flush=True)

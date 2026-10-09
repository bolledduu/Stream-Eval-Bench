import pathlib,json,urllib.request,hashlib,concurrent.futures
r=pathlib.Path(__file__).resolve().parent;p=r.parent;(p/'data').mkdir(exist_ok=True);(r/'model').mkdir(exist_ok=True)
sources=json.loads((p/'sources.json').read_text())
name='Qwen/Qwen3-VL-2B-Instruct';meta=json.load(urllib.request.urlopen('https://huggingface.co/api/models/'+name,timeout=60));(r/'model_metadata.json').write_text(json.dumps(meta,indent=2))
files=[x['rfilename'] for x in meta['siblings'] if '/' not in x['rfilename'] and x['rfilename'].endswith(('.json','.txt','.safetensors'))]
def get(url,path):
 with urllib.request.urlopen(url,timeout=120) as q,path.open('wb') as f:
  while b:=q.read(4*1024*1024):f.write(b)
 with path.open('rb') as f:h=hashlib.file_digest(f,'sha256').hexdigest()
 print('Downloaded',path.name,path.stat().st_size,flush=True);return h
def task(x):
 if isinstance(x,dict):
  h=get(x['url'],p/x['video']);assert h==x['sha256'];return None
 path=r/'model'/x;h=get(f'https://huggingface.co/{name}/resolve/{meta["sha"]}/{x}',path);return {'file':x,'bytes':path.stat().st_size,'sha256':h}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(task,sources+files))
(r/'model_manifest.json').write_text(json.dumps({'name':name,'revision':meta['sha'],'files':[x for x in rows if x]},indent=2))

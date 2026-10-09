"""Pin and download the official public Qwen snapshot, with per-file checksums."""
import concurrent.futures,hashlib,json,pathlib,urllib.request
ROOT=pathlib.Path(__file__).resolve().parent
name='Qwen/Qwen2-VL-2B-Instruct'
meta=json.load(urllib.request.urlopen('https://huggingface.co/api/models/'+name,timeout=30))
(ROOT/'model_metadata.json').write_text(json.dumps(meta,indent=2))
files=[r['rfilename'] for r in meta['siblings'] if '/' not in r['rfilename'] and r['rfilename'].endswith(('.json','.txt','.safetensors'))]
def fetch(filename):
 path=ROOT/'model'/filename;h=hashlib.sha256();total=0
 with urllib.request.urlopen(f'https://huggingface.co/{name}/resolve/{meta["sha"]}/{filename}',timeout=120) as r,path.open('wb') as f:
  while True:
   b=r.read(4*1024*1024)
   if not b:break
   f.write(b);h.update(b);total+=len(b)
 print(filename,total,flush=True)
 return {'file':filename,'bytes':total,'sha256':h.hexdigest()}
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(fetch,files))
(ROOT/'model_manifest.json').write_text(json.dumps({'name':name,'revision':meta['sha'],'files':rows},indent=2))

import pathlib,json,urllib.request,hashlib,concurrent.futures
root=pathlib.Path(__file__).resolve().parent
m=json.loads((root/'model_manifest.json').read_text());(root/'model').mkdir(exist_ok=True)
def run(row):
 p=root/'model'/row['file'];h=hashlib.sha256()
 with urllib.request.urlopen(f'https://huggingface.co/{m["name"]}/resolve/{m["revision"]}/{row["file"]}',timeout=120) as r,p.open('wb') as f:
  while b:=r.read(4*1024*1024): f.write(b);h.update(b)
 assert p.stat().st_size==row['bytes'] and h.hexdigest()==row['sha256'],row['file']
 print('Verified',row['file'],flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(run,m['files']))

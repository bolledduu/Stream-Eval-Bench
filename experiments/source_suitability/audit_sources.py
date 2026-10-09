"""Download pinned sources, verify hashes, and generate timestamped review sheets."""
import json,hashlib,urllib.request,concurrent.futures,subprocess
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent;P=R.parent/'evidence_revision_pilot'
sources=json.loads((P/'sources.json').read_text());D=R/'source_media';D.mkdir(exist_ok=True)
def review(s):
 v=D/(s['id']+'.mp4')
 if not v.exists():
  with urllib.request.urlopen(s['url'],timeout=90) as q,v.open('wb') as f:
   while b:=q.read(1024*1024):f.write(b)
 h=hashlib.sha256(v.read_bytes()).hexdigest();assert h==s['sha256']
 frames=D/s['id'];frames.mkdir(exist_ok=True)
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(v),'-vf','fps=1,scale=256:144','-q:v','3',str(frames/'%03d.jpg')],check=True)
 paths=sorted(frames.glob('*.jpg'));pages=[]
 for start in range(0,len(paths),48):
  group=paths[start:start+48];out=Image.new('RGB',(256*6,164*((len(group)+5)//6)),'white');draw=ImageDraw.Draw(out)
  for i,p in enumerate(group):
   x=(i%6)*256;y=(i//6)*164;out.paste(Image.open(p),(x,y+20));draw.text((x+3,y+3),f"{s['id']} approx {start+i+0.5:.1f}s",fill='black')
  name=f"{s['id']}_page{start//48+1}.jpg";out.save(R/name,quality=90);pages.append(name)
 return {'id':s['id'],'session':s['session'],'url':s['url'],'sha256':h,'duration':s['duration_seconds'],'sampled_frames':len(paths),'review_pages':pages,'method':'1 fps contact sheets; labels approximate ffmpeg fps sampling bins, not frame-exact event annotations.'}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 rows=list(pool.map(review,sources))
(R/'source_audit.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2),flush=True)

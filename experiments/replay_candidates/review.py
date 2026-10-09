from pathlib import Path
from PIL import Image,ImageDraw
import subprocess,sys
r=Path(__file__).resolve().parent
for name in sys.argv[1:]:
 d=r/(name+'_frames');d.mkdir(exist_ok=True)
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(r/(name+'.mp4')),'-vf','fps=1,scale=320:180',str(d/'%03d.jpg')],check=True)
 ps=sorted(d.glob('*.jpg'))
 for st in range(0,len(ps),36):
  group=ps[st:st+36];im=Image.new('RGB',(1280,200*((len(group)+3)//4)),'white');draw=ImageDraw.Draw(im)
  for i,f in enumerate(group):
   x=(i%4)*320;y=(i//4)*200;im.paste(Image.open(f),(x,y+20));draw.text((x+2,y+2),f'{name} ~{st+i+0.5}s',fill='black')
  im.save(r/f'{name}_sheet{st//36}.jpg',quality=90)
 print(name,'frames',len(ps))

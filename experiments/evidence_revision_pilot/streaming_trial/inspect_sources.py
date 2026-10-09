import pathlib,subprocess,io
from PIL import Image,ImageDraw
r=pathlib.Path(__file__).resolve().parent
for name,start,end,step in [('holo_1',0,32,2),('holo_3',64,121,4)]:
 times=list(range(start,end,step));sheet=Image.new('RGB',(4*320,((len(times)+3)//4)*204),'white');d=ImageDraw.Draw(sheet)
 for i,t in enumerate(times):
  b=subprocess.check_output(['ffmpeg','-loglevel','error','-ss',str(t),'-i',str(r.parent/'data'/f'{name}.mp4'),'-frames:v','1','-vf','scale=320:-1','-f','image2pipe','-vcodec','png','-'])
  im=Image.open(io.BytesIO(b));x=(i%4)*320;y=(i//4)*204;sheet.paste(im,(x,y+24));d.text((x+5,y+5),f'{name} source {t}s',fill='black')
 sheet.save(r/f'{name}_contact.png')

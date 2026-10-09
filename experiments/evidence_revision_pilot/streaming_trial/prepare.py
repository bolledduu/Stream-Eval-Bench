"""Freeze a paired arrival-order intervention on unmasked real video packets."""
import pathlib,json,hashlib
import av,numpy as np
from PIL import Image
r=pathlib.Path(__file__).resolve().parent;(r/'packets').mkdir(exist_ok=True);(r/'results').mkdir(exist_ok=True)
specs=[{'id':'camera','source':'holo_1','bounds':[6,9,12,15,18,21,24],'delayed_order':[0,2,3,1,4,5],'late_packet':1,'checkpoint_after_late':3,'question':'Track camera-part detachments in the capture-time interval 6–24 seconds. first_detached and second_detached name the first and second separate part-removal actions in CAPTURE-TIME order (lens or cap; unknown if not established). detachments is the number of distinct removals supported by the received footage, not the number of clips. lens_attached_now describes the latest capture time received, not the last packet arrival. Do not count putting a part back on as another removal.','schema':{'first_detached':'unknown','second_detached':'unknown','detachments':'unknown','lens_attached_now':'unknown'},'expected_at_join':{'first_detached':'lens','second_detached':'cap','detachments':2,'lens_attached_now':'yes'},'expected_final':{'first_detached':'lens','second_detached':'cap','detachments':2,'lens_attached_now':'yes'}}, {'id':'table','source':'holo_3','bounds':[60,64,76,88,100,112,120,121],'delayed_order':[0,2,3,4,5,1,6],'late_packet':1,'checkpoint_after_late':5,'question':'Track whether the large round tray rests on the table frame. tray_on_frame_at_72 describes the footage around capture time 72 seconds; answer unknown if footage for that time has not been received. tray_on_frame_now describes the latest capture time received, not the last packet arrival. Allowed values are yes, no, unknown. Never infer an earlier state solely from a later state.','schema':{'tray_on_frame_at_72':'unknown','tray_on_frame_now':'unknown'},'expected_at_join':{'tray_on_frame_at_72':'no','tray_on_frame_now':'yes'},'expected_final':{'tray_on_frame_at_72':'no','tray_on_frame_now':'yes'}}]
for c in specs:
 source=r.parent/'data'/f'{c["source"]}.mp4';container=av.open(str(source));st=container.streams.video[0];fps=float(st.average_rate);total=st.frames
 desired=[]
 for k,(a,b) in enumerate(zip(c['bounds'][:-1],c['bounds'][1:])):
  for i,t in enumerate(np.linspace(a,b-min(.1,(b-a)/8),4)):desired.append((float(t),k,i))
 targets=iter(desired);current=next(targets,None);frames={k:[] for k in range(len(c['bounds'])-1)}
 for f in container.decode(video=0):
  if current is None:break
  if f.time is None or f.time<current[0]:continue
  t,k,i=current;im=f.to_image().convert('RGB').resize((512,288),Image.Resampling.LANCZOS);path=r/'packets'/f'{c["id"]}_{k}_{i}.png';im.save(path)
  frames[k].append({'path':str(path.relative_to(r)),'source_time':float(f.time),'source_frame_index':round(float(f.time)*fps),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()});current=next(targets,None)
 container.close();assert current is None
 c['packets']=[{'id':k,'capture_start':a,'capture_end':b,'frames':frames[k],'source_fps':fps,'total_source_frames':total} for k,(a,b) in enumerate(zip(c['bounds'][:-1],c['bounds'][1:]))]
 for p in c['packets']:assert len(p['frames'])==4 and all(p['capture_start']<=f['source_time']<p['capture_end'] for f in p['frames'])
 c['chronological_order']=list(range(len(c['packets'])))
protocol={'scope':'Controlled out-of-order delivery of real video; no image masks or supplied answer memory. Not natural replay prevalence. Capture timestamps are supplied as available transport metadata; autonomous replay detection is not tested.','model':'Qwen/Qwen3-VL-2B-Instruct','representation':'Native video input: four chronological frames per packet, exact same pixels across delivery orders.','memory':'The preceding model response, generated from its own observations; no gold values injected.','baseline':'An ordinary external-memory streaming adapter around a VLM, not a novel method or specialized streaming architecture.','primary_contrast':'Chronological versus delayed arrival with identical packet multiset and matched calls/frame budget at the join.','frozen_before_model_outputs':True,'cases':specs}
(r/'protocol.json').write_text(json.dumps(protocol,indent=2));print('Frozen',sum(len(c['packets']) for c in specs),'packets from 2 recordings')

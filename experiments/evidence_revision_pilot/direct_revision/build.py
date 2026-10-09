"""Freeze a controlled, source-grounded partial-view / delayed-full-view diagnostic."""
import hashlib,json,pathlib,subprocess,sys
from PIL import Image,ImageDraw,ImageChops,ImageStat
ROOT=pathlib.Path(__file__).resolve().parent;PILOT=ROOT.parent
sys.path.insert(0,str(PILOT/'src'))
from revision_pilot.media import index_video,sha256

def main():
    specs=[
      {'id':'camera','source':'holo_1','times':[10.02,17.03],'field':'part_removed','values':['lens','cap'],'question':'What detached camera part is held separately in the right hand? lens means the cylindrical lens assembly; cap means the flat circular lens cover.','box':[80,55,460,288]},
      {'id':'printer','source':'holo_2','times':[19.30,42.65],'field':'display','values':['illuminated','dark'],'question':'Is the central rectangular printer display illuminated or dark? Ignore small indicator LEDs.','box':[100,40,450,230]},
      {'id':'table','source':'holo_3','times':[73.15,118.24],'field':'tray_on_frame','values':['no','yes'],'question':'Is the large round tray resting on top of the table frame? yes means resting on the frame; no means not resting on the frame.','box':[50,40,480,288]}
    ];episodes=[]
    sources={s['id']:s for s in json.loads((PILOT/'sources.json').read_text())}
    for spec in specs:
        source=sources[spec['source']];assert sha256(PILOT/source['video'])==source['sha256']
        frames=index_video(PILOT/source['video'],PILOT/'frames'/spec['source'])
        records=[]
        for i,t in enumerate(spec['times']):
            f=max((f for f in frames if f['time']<=t),key=lambda f:f['time'])
            full=Image.open(PILOT/'frames'/spec['source']/f['file']).convert('RGB')
            fullpath=ROOT/'inputs'/f"{spec['id']}_E{i+1}_full.png";full.save(fullpath)
            partial=full.copy();ImageDraw.Draw(partial).rectangle(spec['box'],fill=(127,127,127))
            partialpath=ROOT/'inputs'/f"{spec['id']}_E{i+1}_partial.png";partial.save(partialpath)
            records.append({'id':f'E{i+1}','source_time':f['time'],'full':str(fullpath.relative_to(ROOT)),'partial':str(partialpath.relative_to(ROOT)),'source_frame_sha256':f['sha256'],'full_sha256':sha256(fullpath),'partial_sha256':sha256(partialpath),'value':spec['values'][i]})
        mask=Image.new('L',full.size,255);ImageDraw.Draw(mask).rectangle(spec['box'],fill=0)
        distances=[]
        for target in records:
            delivered=Image.open(ROOT/target['full'])
            distances.append([sum(ImageStat.Stat(ImageChops.difference(delivered,Image.open(ROOT/r['partial'])),mask).mean)/3 for r in records])
        assert all(distances[i][i]==0 and distances[i][1-i]>0 for i in range(2))
        episodes.append({**spec,'records':records,'context_pixel_distances':distances,'initial_state':{'E1':'unknown','E2':'unknown','event_count':2,'device':spec['id']}})
    Image.new('RGB',(512,288),(127,127,127)).save(ROOT/'inputs/withheld.png')
    protocol={'design':'Controlled artificially delayed full view of previously redacted real footage; not natural livestream evidence.','initial_memory':'Two records, device and unknown field values supplied by experiment. No claim of model-generated memory or human impossibility of early inference.','replay_status':'New packet explicitly described as footage from one of two earlier records. Replay detection is given, not tested. Printer/table rows describe historical state observations; only camera rows depict detachment events.','conditions':['recognition','static_matching','visual_update','oracle_update','withheld_update'],'counterbalancing':'Both targets E1 and E2 tested for all three sessions, fixed reference order.','main_endpoint':'Correct target field, other field remains unknown, count remains 2, device preserved.','gates':'Only interpret revision failure beyond generic matching where full-view recognition AND static reference matching pass.','n_independent_sources':3,'cases':episodes,'frozen_before_qwen_predictions':True}
    (ROOT/'protocol.json').write_text(json.dumps(protocol,indent=2))
    print([(e['id'],e['context_pixel_distances']) for e in episodes],flush=True)
if __name__=='__main__':main()

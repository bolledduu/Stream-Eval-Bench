"""Fail-fast full-evidence qualification before spending on additional streaming traces."""
import json
from run import R,Model,prompt,parse
p=json.loads((R/'protocol.json').read_text());c=next(c for c in p['cases'] if c['id']=='table');ids=c['delayed_order'][:c['checkpoint_after_late']+1];packets=[c['packets'][k] for k in ids];q=prompt(c,'{}',max(x['capture_end'] for x in packets));m=Model();answer,seconds,grids=m.generate(packets,q)
row={'id':'table_all_arrived_control','case':'table','condition':'all_arrived_control','arrived_packet_ids':ids,'packets':packets,'prompt':q,'response':answer,'parsed':parse(answer),'expected':c['expected_at_join'],'seconds':seconds,'video_grids':grids}
f=R/'results/run.json';j=json.loads(f.read_text());assert not any(x['id']==row['id'] for x in j['results']);j['results'].append(row);f.write_text(json.dumps(j,indent=2));print(row['id'],repr(answer),seconds,flush=True)

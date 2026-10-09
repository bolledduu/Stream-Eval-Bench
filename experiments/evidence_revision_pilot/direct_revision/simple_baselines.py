"""Two prewritten post-hoc controls for the table E1 case; no novel-method claim."""
import json,pathlib
from experiment import Qwen,request,decode_object,digest
root=pathlib.Path(__file__).resolve().parent
p=json.loads((root/'protocol.json').read_text());c=next(c for c in p['cases'] if c['id']=='table');t=0
frames,_=request(c,t,'visual_update');expected=dict(c['initial_state']);expected['E1']=c['records'][t]['value']
plan=[
 {'id':'single_image_supplied_id','frames':[frames[2]],'prompt':'This complete image is from earlier record E1. The stored question is: '+c['question']+'\nExisting records: '+json.dumps(c['initial_state'])+'\nRead the answer from this image and replace ONLY E1 with that answer. Keep all other values unchanged. Return only JSON with keys E1, E2, event_count and device.','expected':expected},
 {'id':'read_then_write_three_images','frames':frames,'prompt':'The third image is a complete view from earlier record E1. The first two are covered reference views. The stored question is: '+c['question']+'\nExisting records: '+json.dumps(c['initial_state'])+'\nFirst report the answer seen in the third image as observed_value. Then put that value into E1 in memory; preserve E2, event_count and device. Return JSON with observed_value and memory; memory must contain E1, E2, event_count and device.','expected':{'observed_value':expected['E1'],'memory':expected}}
]
def serial(x):return {**x,'frames':[{'label':label,'path':str(path.relative_to(root)),'sha256':digest(path)} for label,path in x['frames']]}
(root/'simple_baseline_plan.json').write_text(json.dumps([serial(x) for x in plan],indent=2))
if __name__=='__main__':
 import sys
 if '--plan-only' in sys.argv:raise SystemExit(0)
 model=Qwen();rows=[]
 for trial in plan:
  answer,latency=model.generate(trial['frames'],trial['prompt']);obj=decode_object(answer)
  row={**serial(trial),'response':answer,'parsed':obj,'pass':obj==trial['expected'],'latency_seconds':latency};rows.append(row)
  (root/'results/simple_baselines.json').write_text(json.dumps({'scope':'Post-hoc diagnostic on one selected table view; these are standard prompt/input controls, not a novel method or independent cases.','environment':model.metadata,'results':rows},indent=2));print(trial['id'],repr(answer),'PASS',row['pass'],flush=True)

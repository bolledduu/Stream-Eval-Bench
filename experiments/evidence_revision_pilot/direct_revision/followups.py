"""Post-hoc replay of the previously selected table case after cache invalidation; separate from main results."""
import datetime,json,pathlib
from experiment import Qwen,request,decode_object,digest
ROOT=pathlib.Path(__file__).resolve().parent
protocol=json.loads((ROOT/'protocol.json').read_text());main=json.loads((ROOT/'results/qwen.json').read_text())
lookup={(r['case'],r['target'],r['condition']):r for r in main['results']}
eligible=[(c,0) for c in protocol['cases'] if c['id']=='table']
plan=[]
for c,t in eligible:
    record=c['records'][t]['id'];value=c['records'][t]['value'];frames,_=request(c,t,'visual_update')
    schema='Return only JSON with keys E1, E2, event_count and device.'
    prompt='Consider ONLY the THIRD image, the later delivered complete view. '+c['question']+' Return only JSON with key "value"; use unknown if not established.'
    plan.append({'id':f'{c["id"]}_{t}_context_recognition','frames':frames,'prompt':prompt,'expected':{'value':value}})
    expected=dict(c['initial_state']);expected[record]=value
    prompt='The third image is a complete view from earlier record '+record+'. The first two are covered reference views. The stored question for each record is: '+c['question']+'\nExisting records: '+json.dumps(c['initial_state'])+'\nRead the answer from the third image and replace ONLY '+record+' with that answer. Keep all other values unchanged. '+schema
    plan.append({'id':f'{c["id"]}_{t}_plain_oracle_update','frames':frames,'prompt':prompt,'expected':expected})
    prompt='Existing records: '+json.dumps(c['initial_state'])+'\nTrusted verified evidence establishes '+record+' = '+json.dumps(value)+'. Replace ONLY that record value with this verified value and preserve every other value. '+schema
    plan.append({'id':f'{c["id"]}_{t}_text_oracle_update','frames':[],'prompt':prompt,'expected':expected})
(ROOT/'followup_plan.json').write_text(json.dumps([{**p,'frames':[{'label':label,'path':str(path.relative_to(ROOT)),'sha256':digest(path)} for label,path in p['frames']]} for p in plan],indent=2))
model=Qwen();rows=[]
for p in plan:
    answer,latency=model.generate(p['frames'],p['prompt']);obj=decode_object(answer)
    norm={k:v.lower().strip() if isinstance(v,str) else v for k,v in (obj or {}).items()}
    row={'id':p['id'],'prompt':p['prompt'],'frames':[{'label':label,'path':str(path.relative_to(ROOT)),'sha256':digest(path)} for label,path in p['frames']],'response':answer,'parsed':obj,'expected':p['expected'],'pass':all(norm.get(k)==v for k,v in p['expected'].items()),'latency_seconds':latency}
    rows.append(row)
    (ROOT/'results/followups.json').write_text(json.dumps({'status':'Post-hoc diagnostic on the previously examined table E1 case; repeats the identical prompts without the invalidated cache. Selection predates the corrected run; not pooled with main trials.','environment':model.metadata,'results':rows},indent=2));print(row['id'],repr(answer),'PASS',row['pass'],flush=True)

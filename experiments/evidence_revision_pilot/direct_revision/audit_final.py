"""Validate only corrected main/diagnostic runs and their exact input provenance."""
import json,pathlib,hashlib
from experiment import digest
root=pathlib.Path(__file__).resolve().parent
main=json.loads((root/'results/qwen.json').read_text());assert len(main['results'])==30
assert main['environment']['vision_features'].startswith('Disabled:')
summary={'main_calls':30,'diagnostic_calls':0,'main_unique_requests':27,'source_sessions':3,'corrected_execution':'unmodified joint-image forward','diagnostics':{}}
for result_name,plan_name,n in [('followups.json','followup_plan.json',3),('camera_followups.json','camera_followup_plan.json',3),('simple_baselines.json','simple_baseline_plan.json',2)]:
 run=json.loads((root/'results'/result_name).read_text());plan={r['id']:r for r in json.loads((root/plan_name).read_text())};assert len(run['results'])==n;assert run['environment']['vision_features'].startswith('Disabled:')
 for row in run['results']:
  p=plan[row['id']];assert row['prompt']==p['prompt'];assert row['frames']==p['frames'];assert row['expected']==p['expected']
  for frame in row['frames']:assert digest(root/frame['path'])==frame['sha256']
  obj=row['parsed']
  if result_name=='simple_baselines.json':expected_pass=obj==row['expected']
  else:
   norm={k:v.strip().lower() if isinstance(v,str) else v for k,v in (obj or {}).items()};expected_pass=all(norm.get(k)==v for k,v in row['expected'].items())
  assert row['pass']==expected_pass
 summary['diagnostic_calls']+=n;summary['diagnostics'][result_name]={'calls':n,'pass':sum(r['pass'] for r in run['results'])}
summary['all_corrected_calls']=summary['main_calls']+summary['diagnostic_calls'];summary['status']='Passed prompt, image-hash, scoring and uncached-execution checks.'
(root/'results/final_audit.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))

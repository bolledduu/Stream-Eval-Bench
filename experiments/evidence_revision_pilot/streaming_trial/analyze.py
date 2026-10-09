"""Assess a within-model arrival-order contrast, never equate it with novelty."""
import json,pathlib,hashlib
R=pathlib.Path(__file__).resolve().parent
p=json.loads((R/'protocol.json').read_text());run=json.loads((R/'results/run.json').read_text());assert run['protocol_sha256']==hashlib.sha256((R/'protocol.json').read_bytes()).hexdigest();rows=run['results'];lookup={x['id']:x for x in rows};assert len(lookup)==len(rows)
def correct(row,expected):
 if row is None:return None
 obj=row['parsed'];return isinstance(obj,dict) and all(obj.get(k)==v for k,v in expected.items())
summary=[]
for c in p['cases']:
 orders=[c['chronological_order'],c['delayed_order']];assert sorted(orders[0])==sorted(orders[1]);j=c['checkpoint_after_late'];assert sorted(orders[0][:j+1])==sorted(orders[1][:j+1])
 for condition,order in zip(['chronological','delayed'],orders):
  prev='{}'
  for step,k in enumerate(order):
   row=lookup.get(f'{c["id"]}_{condition}_{step}')
   if row is None:break
   assert row['input_memory']==prev and row['packet_id']==k and row['arrived_packet_ids']==order[:step+1]
   assert row['packets']==[c['packets'][k]]
   assert all(f['source_time']<row['latest_capture_boundary'] for packet in row['packets'] for f in packet['frames'])
   prev=row['response']
 a=lookup.get(f'{c["id"]}_chronological_{j}');b=lookup.get(f'{c["id"]}_delayed_{j}');full=lookup.get(c['id']+'_all_arrived_control')
 ca=correct(a,c['expected_at_join']);cb=correct(b,c['expected_at_join']);cf=correct(full,c['expected_at_join'])
 summary.append({'case':c['id'],'matched_checkpoint_step':j,'expected':c['expected_at_join'],'chronological':a['parsed'] if a else None,'delayed':b['parsed'] if b else None,'all_arrived_control':full['parsed'] if full else None,'chronological_correct':ca,'delayed_correct':cb,'all_arrived_correct':cf,'candidate_arrival_order_failure':ca is True and cb is False and cf is True,'continuation_chronological_correct':correct(lookup.get(f'{c["id"]}_chronological_{len(orders[0])-1}'),c['expected_final']),'continuation_delayed_correct':correct(lookup.get(f'{c["id"]}_delayed_{len(orders[1])-1}'),c['expected_final'])})
for row in rows:
 for packet in row['packets']:
  for f in packet['frames']:assert hashlib.sha256((R/f['path']).read_bytes()).hexdigest()==f['sha256']
result={'completed_calls':len(rows),'planned_calls':32,'cases':summary,'audit':'Exact packet pixels, no future capture frames, matched packet sets at checkpoints, and model-produced memory transitions verified.','claim_limit':'Only a controlled arrival-order intervention in one small VLM with external text memory. No autonomous replay detection, real-time speed, natural-stream prevalence, or literature novelty established.'}
(R/'results/analysis.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

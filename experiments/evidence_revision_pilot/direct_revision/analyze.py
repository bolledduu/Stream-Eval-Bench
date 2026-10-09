"""Report gates and paired outcomes without inflating source or withheld-control counts."""
import collections,hashlib,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from experiment import request,score,digest

def main():
    protocol=json.loads((ROOT/'protocol.json').read_text());run=json.loads((ROOT/'results/qwen.json').read_text())
    assert run['protocol_sha256']==digest(ROOT/'protocol.json')
    cases={c['id']:c for c in protocol['cases']};lookup={};conditions=collections.defaultdict(list);seen_requests=set()
    for row in run['results']:
        case=cases[row['case']];frames,prompt=request(case,row['target'],row['condition'])
        assert prompt==row['prompt']
        expected_frames=[{'label':label,'path':str(path.relative_to(ROOT)),'sha256':digest(path)} for label,path in frames]
        assert row['frames']==expected_frames
        assert row['score']==score(case,row['target'],row['condition'],row['response'])
        key=(row['case'],row['target'],row['condition']);assert key not in lookup;lookup[key]=row
        request_hash=hashlib.sha256(json.dumps({'frames':row['frames'],'prompt':prompt},sort_keys=True).encode()).hexdigest()
        duplicate=request_hash in seen_requests;seen_requests.add(request_hash)
        if not duplicate:conditions[row['condition']].append(row)
    breakdown=[]
    for case in protocol['cases']:
        for target in [0,1]:
            def get(condition):return lookup.get((case['id'],target,condition),{}).get('score',{}).get('pass')
            perception=get('recognition');matching=get('static_matching');visual=get('visual_update');oracle=get('oracle_update')
            breakdown.append({'case':case['id'],'record':f'E{target+1}','expected':case['records'][target]['value'],'recognition_pass':perception,'static_match_pass':matching,'visual_update_pass':visual,'oracle_update_pass':oracle,'withheld_pass':get('withheld_update'),'eligible_for_combination_failure_check':perception is True and matching is True,'candidate_combination_failure':perception is True and matching is True and visual is False,'association_bottleneck_candidate':perception is True and matching is False and visual is False and oracle is True})
    summary={'completed_calls':len(run['results']),'unique_requests':len(seen_requests),'source_sessions':3,'conditions':{k:{'pass':sum(r['score']['pass'] for r in rows),'unique_trials':len(rows),'format_failures':sum(r['score']['format_failure'] for r in rows)} for k,rows in conditions.items()},'breakdown':breakdown,'audit':'Passed exact frame-byte, prompt, protocol and score checks for completed calls.','limitations':['Constructed redactions and delayed delivery; not natural livestream evidence.','Supplied initial memory and replay status; not autonomous replay detection.','Two historical state observations per printer/table session, not two necessarily distinct physical action events.','Only 3 independent source sessions; no population-level statistical claim.','One 2B model, not frontier model coverage.','Annotations assistant-screened, not independently human-validated.','Static matcher never selected E2; one correct E1 match does not establish robust association.','A candidate combination failure is not proof of a temporal-specific mechanism.','Inputs are sampled still images in one request, not an end-to-end continuous video stream.','The target update is unknown-to-known completion, not correction of a previously false belief.']}
    (ROOT/'results/analysis.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
if __name__=='__main__':main()

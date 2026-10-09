"""Assert completeness and input parity, preserving the failed first-pass record."""
import hashlib
import json
import shutil
from pathlib import Path

R=Path(__file__).resolve().parent
protocol=json.loads((R/'protocol.json').read_text())
expected=[case+'_'+condition for case in protocol['expected'] for condition in protocol['planned_conditions']]
rows={name:json.loads((R/'responses'/f'{name}.json').read_text()) for name in expected}
assert len(rows)==10 and all(row['status']=='completed' for row in rows.values())
assert all(isinstance(row.get('parsed'),dict) for row in rows.values())
checks={}
for case in protocol['expected']:
    joint,update=rows[case+'_joint'],rows[case+'_update']
    checks[case+'_equal_final_visual_input']=joint['sha256']==update['sha256']
    prefix=rows[case+'_prefix']
    history=' Your earlier model-produced answer, before the fuller view arrived, was:\n'+prefix['response']+'\nIt may be revised if evidence justifies it. '
    checks[case+'_prompt_only_difference_is_prior_answer']=update['prompt'].replace(history,'',1)==joint['prompt']
    checks[case+'_no_new_evidence_control_uses_original_image']=rows[case+'_withheld']['sha256']==prefix['sha256']
for name,row in rows.items():
    checks[name+'_input_unchanged']=hashlib.sha256((R/row['image']).read_bytes()).hexdigest()==row['sha256']
assert all(checks.values()),checks
first_pass=R/'first_pass_results.json'
if not first_pass.exists():
    shutil.copyfile(R/'results.json',first_pass)
errors=[json.loads(p.read_text()) for p in (R/'attempts').glob('*.json')]
result={'status':'all_ten_planned_conditions_completed','conditions':list(rows.values()),
        'completed_conditions':10,'archived_infrastructure_errors':errors,
        'total_requests_for_core_prototype':len(rows)+len(errors),'audit':checks,
        'replication_status':'Separately proposed four-request repeat check blocked by automatic approval review; zero repeat responses.'}
(R/'results.json').write_text(json.dumps(result,indent=2))
state=json.loads((R/'execution_status.json').read_text())
state['status']='core_prototype_completed'
state['scientific_result']='All ten planned conditions returned parseable answers. Analyze results by condition; completion does not imply that the failure hypothesis is established.'
state['total_core_requests']=len(rows)+len(errors)
state['recovery']='One documented recovery of an upstream error; original error retained.'
(R/'execution_status.json').write_text(json.dumps(state,indent=2))
(R/'final_audit.json').write_text(json.dumps({'all_passed':True,'checks':checks,'core_completed_conditions':10,'core_total_requests':len(rows)+len(errors)},indent=2))
print(f'COMPLETE: {len(rows)} conditions; {len(rows)+len(errors)} total requests; {len(checks)} integrity/parity checks passed.')

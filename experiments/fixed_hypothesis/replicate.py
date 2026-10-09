"""Post-hoc reproducibility check; preserve original results and identical prompts."""
import json
from run import R, CASES, save, request

if __name__=='__main__':
    protocol={
        'purpose':'Check response variability of the observed printer joint/update discrepancy.',
        'selection':'Printer selected AFTER the original discrepancy was observed. This is a post-hoc within-case diagnostic, not a held-out confirmation.',
        'planned_requests':4,
        'conditions':['joint_repeat1','update_repeat1','joint_repeat2','update_repeat2'],
        'inputs':'Byte-identical image and exact saved prompts from original printer_joint and printer_update requests.',
        'memory':'All update repeats reuse the same originally generated printer prefix, isolating downstream response variability. No independent prefix sampling.',
        'decoding':'Provider defaults; seed/temperature and backend weights are unverified.',
        'retries':0,
        'stop':'Execute all four conditions regardless of intermediate outputs; do not replace or selectively discard model responses.',
        'scope':'One source episode; no population failure-rate or novel-streaming-benchmark claim.'}
    path=R/'replication_protocol.json'
    if path.exists():
        assert json.loads(path.read_text())==protocol
    else:
        save(path,protocol)
    case=next(c for c in CASES if c['id']=='printer')
    results=[]
    for rep in [1,2]:
        for condition in ['joint','update']:
            original=json.loads((R/'responses'/f'printer_{condition}.json').read_text())
            assert original['status']=='completed'
            results.append(request(case,f'{condition}_repeat{rep}',original['image'],original['prompt']))
    save(R/'replication_results.json',results)

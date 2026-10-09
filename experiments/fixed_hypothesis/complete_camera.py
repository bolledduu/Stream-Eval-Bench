"""One transparent infrastructure-only recovery, without rerunning valid model answers."""
import json
from pathlib import Path
from run import R, CASES, save, case_run

if __name__=='__main__':
    amendment={
        'reason':'The camera prefix returned an upstream service exception, so its two dependent conditions could not run. User requests completion of every prototype step.',
        'scope':'Retry camera prefix once with unchanged prompt and image, then run the two originally planned dependent conditions if a valid prefix response arrives.',
        'unchanged':['case selection','media','questions','reference answers','joint results','recognition results','scoring rules'],
        'request_accounting':'Ten planned scientific conditions; at most eleven requests including the failed prefix attempt. No repeat of a completed model answer.',
        'retry_limit':1,
        'original_error_preserved':'attempts/camera_prefix_attempt1.json',
        'not_a_replication':'This recovers missing data after infrastructure failure; it does not test model-answer variability.'}
    p=R/'completion_amendment.json'
    if p.exists():
        assert json.loads(p.read_text())==amendment
    else:
        save(p,amendment)
    old=R/'responses'/'camera_prefix.json'
    archived=R/'attempts'/'camera_prefix_attempt1.json'
    archived.parent.mkdir(exist_ok=True)
    if not archived.exists():
        row=json.loads(old.read_text())
        assert row['status']=='error', 'Never discard or rerun a completed model response'
        old.rename(archived)
    elif old.exists() and json.loads(old.read_text())['status']=='error':
        raise SystemExit('The one allowed recovery attempt already failed; no further retry.')
    case=next(c for c in CASES if c['id']=='camera')
    result=case_run(case)
    save(R/'camera_completion.json',result)

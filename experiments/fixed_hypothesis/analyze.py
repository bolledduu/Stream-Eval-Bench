"""Apply frozen qualification rules. Infrastructure/schema failures are not semantic failures."""
import json
from pathlib import Path

R=Path(__file__).resolve().parent

def score(row, expected):
    if row is None:
        return 'unavailable'
    if row.get('status')!='completed':
        return row.get('status','unavailable')
    parsed=row.get('parsed')
    if not isinstance(parsed,dict) or any(k not in parsed for k in expected):
        return 'schema_error'
    if any(not isinstance(parsed[k],str) for k in expected):
        return 'schema_error'
    return 'pass' if all(parsed[k].strip().lower()==v for k,v in expected.items()) else 'fail'

def main():
    protocol=json.loads((R/'protocol.json').read_text())
    rows={p.stem:json.loads(p.read_text()) for p in (R/'responses').glob('*.json')}
    report={}
    lines=['# Fixed-hypothesis prototype: two HoloAssist sources','',
           'Primary question: can a fuller view update the correct earlier record while preserving the other record?', '',
           '| Source | Initial uncertainty | Recognition | Joint answer | Update | No-new-evidence control |',
           '|---|---|---|---|---|---|']
    for case,truth in protocol['expected'].items():
        scores={}
        for condition in protocol['planned_conditions']:
            expected=truth['prefix' if condition in ['prefix','withheld'] else 'recognition' if condition=='recognition' else 'joint_and_update']
            scores[condition]=score(rows.get(case+'_'+condition),expected)
        qualified=all(scores[k]=='pass' for k in ['prefix','recognition','joint'])
        if not qualified:
            decision='Not qualified for attributing an update failure; inspect the failed/missing gate.'
        elif scores['update']=='pass':
            decision='Qualified case: selective retrospective updating PASSED.'
        elif scores['update']=='fail':
            decision='Qualified case: candidate history-conditioned update failure; requires independent repetition.'
        else:
            decision='Qualified case but updating result is unavailable or unscorable.'
        report[case]={'scores':scores,'qualified':qualified,'decision':decision}
        lines.append('| '+case+' | '+' | '.join(scores[k] for k in ['prefix','recognition','joint','update','withheld'])+' |')
    lines+=['','## Case decisions','']+[f"- {case}: {r['decision']}" for case,r in report.items()]
    lines+=['','## Exact meaning of this test','',
        'Joint and update receive byte-identical final image panels. Only update also receives its own earlier answer. Thus a difference is an exploratory decision-history effect at equal visual evidence, not proof of a native streaming architecture defect.', '',
        'Initial ambiguity is experimentally imposed by masks. Full views are original frames, not generated imagery. Replay status and capture order are provided; target record and its revealed value are not. Association is a controlled same-frame matching task. Successful latest-record output is not autonomous replay detection.', '',
        'These are two independent recordings with one sampled episode each, not enough to estimate a population failure rate or establish novelty. No real-time latency claim; elapsed times include the public service queue. Recognition/schema errors and service errors are separate from semantic updating failures.', '',
        'A PASS is a valid positive result for this controlled prototype. It must not be dismissed because it fails to support the desired failure hypothesis.']
    completed=sum(r.get('status')=='completed' for r in rows.values())
    errors=sum(r.get('status')=='error' for r in rows.values())
    lines+=['',f'Saved requests: {len(rows)}; completed responses: {completed}; infrastructure errors: {errors}.']
    execution_path=R/'execution_status.json'
    if execution_path.exists():
        execution=json.loads(execution_path.read_text())
        if execution['status']=='blocked_by_automatic_approval_review' and not rows:
            lines[2:2]=['**Execution blocked by automatic approval review before any model responses were saved. This is not a completed inference experiment.**', '',
                        'The external upload requires explicit authorization for the image panels, prompts and Hugging Face destination. No retry or rerouting was attempted after rejection.', '']
    (R/'analysis.json').write_text(json.dumps(report,indent=2))
    (R/'RESULTS.md').write_text('\n'.join(lines)+'\n')
    print('\n'.join(lines))

if __name__=='__main__':
    main()

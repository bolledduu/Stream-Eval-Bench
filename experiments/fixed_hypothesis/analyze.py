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
    return 'pass' if all(parsed[k].strip().lower()==v.strip().lower() for k,v in expected.items()) else 'fail'

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
    lines+=['','## Every observed answer','',
            '| Source | Condition | E1 / standalone value | E2 | Matched record | Latest record |',
            '|---|---|---|---|---|---|']
    for case in protocol['expected']:
        for condition in protocol['planned_conditions']:
            row=rows.get(case+'_'+condition,{})
            parsed=row.get('parsed') or {}
            if not isinstance(parsed,dict):
                parsed={}
            absent=row.get('status','unavailable')
            standalone=next(iter(parsed.values())) if condition=='recognition' and len(parsed)==1 else absent
            fields=[str(parsed.get('E1',parsed.get('value',standalone))),str(parsed.get('E2','—')),
                    str(parsed.get('matched_record','—')),str(parsed.get('latest_record','—'))]
            lines.append('| '+case+' | '+condition+' | '+' | '.join(fields)+' |')
    lines+=['','## Reference answers','',
            '| Source | Prefix and withheld | Standalone recognition | Joint and update |',
            '|---|---|---|---|']
    for case,truth in protocol['expected'].items():
        final=truth['joint_and_update']
        lines.append(f"| {case} | E1=unknown; E2=unknown; match=none | {truth['recognition']['value']} | E1={final['E1']}; E2={final['E2']}; match={final['matched_record']} |")
    lines+=['','Latest record remains E2 in all record-based conditions. This is explicitly supplied capture-order metadata, not autonomous temporal inference.']
    lines+=['','## Recognition: semantic answer versus schema compliance','',
            'The strict table above requires the requested key `value`. The following transparent semantic audit reads a single scalar under a renamed key; it does not overwrite the strict scores or change original qualification decisions.','']
    for case,truth in protocol['expected'].items():
        parsed=rows.get(case+'_recognition',{}).get('parsed')
        value=next(iter(parsed.values())) if isinstance(parsed,dict) and len(parsed)==1 else None
        correct=isinstance(value,str) and value.strip().lower()==truth['recognition']['value']
        lines.append(f'- {case}: returned `{json.dumps(parsed)}`; semantic recognition correct: **{correct}**.')
    lines+=['','## Model explanations (verbatim raw outputs are in responses/)','']
    for key,row in rows.items():
        parsed=row.get('parsed')
        if isinstance(parsed,dict) and parsed.get('reason'):
            lines.append(f"- **{key}:** {parsed['reason']}")
        elif row.get('status')=='error':
            lines.append(f"- **{key}:** service error at `{row.get('stage','unknown')}`: `{row.get('error','')}`")
    lines+=['','## Exact meaning of this test','',
        'Joint and update receive byte-identical final image panels. Only update also receives its own earlier answer. Thus a difference is an exploratory decision-history effect at equal visual evidence, not proof of a native streaming architecture defect.', '',
        'Initial ambiguity is experimentally imposed by masks. Full views are original frames, not generated imagery. Replay status and capture order are provided; target record and its revealed value are not. Association is a controlled same-frame matching task. Successful latest-record output is not autonomous replay detection.', '',
        'These are two independent recordings with one sampled episode each, not enough to estimate a population failure rate or establish novelty. No real-time latency claim; elapsed times include the public service queue. Recognition/schema errors and service errors are separate from semantic updating failures.', '',
        'A PASS is a valid positive result for this controlled prototype. It must not be dismissed because it fails to support the desired failure hypothesis.']
    completed=sum(r.get('status')=='completed' for r in rows.values())
    errors=sum(r.get('status')=='error' for r in rows.values())
    lines+=['',f'Saved requests: {len(rows)}; completed responses: {completed}; infrastructure errors: {errors}.']
    archived_errors=list((R/'attempts').glob('*.json')) if (R/'attempts').exists() else []
    lines+=[f'Additional archived infrastructure attempts: {len(archived_errors)}. Total recorded attempts including these: {len(rows)+len(archived_errors)}.']
    if (R/'replication_protocol.json').exists():
        lines+=['','## Post-hoc printer repeat check','',
                'These repeats were added after observing the original printer discrepancy. They reuse the exact original prompts, image and prefix memory; this measures downstream response variability on ONE episode, not independent data generalization. All scheduled repeats are shown.','',
                '| Trial | Joint score | Update score |', '|---|---|---|']
        expected=protocol['expected']['printer']['joint_and_update']
        for suffix in ['', '_repeat1','_repeat2']:
            j=score(rows.get('printer_joint'+suffix),expected)
            u=score(rows.get('printer_update'+suffix),expected)
            lines.append(f"| {suffix.lstrip('_') or 'original'} | {j} | {u} |")
        status_path=R/'replication_execution_status.json'
        if status_path.exists():
            repeat_status=json.loads(status_path.read_text())
            lines+=['',f"**Repeat execution status: {repeat_status['status']}.** {repeat_status['reason']} No repeat result may be claimed."]
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

"""Frozen two-source test of selective retrospective updating with equal visual inputs."""
import concurrent.futures
import datetime
import hashlib
import json
import os
import time
from pathlib import Path
from gradio_client import Client, handle_file

R = Path(__file__).resolve().parent
HOST = 'https://qwen-qwen3-vl-235b-a22b-instruct-demo.hf.space'
CASES = json.loads((R/'cases.json').read_text())

def save(path, obj):
    temp = path.with_suffix('.tmp')
    with temp.open('w') as stream:
        json.dump(obj, stream, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    temp.replace(path)

def request(case, condition, image, prompt):
    name = case['id']+'_'+condition
    path = R/'responses'/f'{name}.json'
    if path.exists():
        return json.loads(path.read_text())
    row = {'id':name, 'case':case['id'], 'condition':condition, 'image':image,
           'sha256':hashlib.sha256((R/image).read_bytes()).hexdigest(), 'prompt':prompt,
           'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    started = time.monotonic()
    stage = 'connect'
    print('START',name,flush=True)
    try:
        client = Client(HOST,hf_token=False,httpx_kwargs={'timeout':40},verbose=False)
        def api(*args, api_name):
            nonlocal stage
            stage = api_name
            job = client.submit(*args,api_name=api_name)
            try:
                return job.result(timeout=180)
            except Exception:
                job.cancel()
                raise
        api(api_name='/reset_state')
        api([],handle_file(str(R/image)),api_name='/add_file')
        history = api([],prompt,api_name='/add_text')
        reply = api(history,api_name='/predict')
        answer = reply[-1][1]
        row.update(status='completed',response=answer)
        try:
            row['parsed'] = json.JSONDecoder().raw_decode(answer[answer.index('{'):])[0]
        except (ValueError,TypeError):
            row['parsed'] = None
    except Exception as exc:
        row.update(status='error',stage=stage,error=repr(exc))
    row['seconds'] = time.monotonic()-started
    save(path,row)
    print('DONE',name,row.get('response',row.get('error')),flush=True)
    return row

def record_prompt(case):
    return ('The panels labelled E1 and E2 are two historical observations in capture order. '
            'Gray rectangles hide visual evidence. Do not guess hidden details or transfer a fact between records. '
            'Record E2 is the latest capture. A fuller view of an old observation does not create a new observation. '
            +case['question']+' Allowed values for each record: '+', '.join(case['choices'])+'. '
            'Return only JSON containing: E1 and E2 (their respective answers); '
            'matched_record (E1, E2, or none, indicating which historical panel the newly available fuller view matches; none if no fuller view is present); '
            'latest_record (the most recent observation by capture order); '
            'reason (brief visible evidence for any association).')

def case_run(case):
    name=case['id']; base=record_prompt(case)
    prefix=request(case,'prefix',name+'_prefix.png',base+' No additional fuller view has arrived yet.')
    recognition=request(case,'recognition',name+'_recognition.png',
        case['question']+' Return only JSON with key value. Allowed values: '+', '.join(case['choices'])+'.')
    ending=(' The rightmost panel is newly available footage: a fuller view of exactly one earlier observation. '
            'Identify that observation from the unmasked visual context, update only the fact it establishes, '
            'and leave the other observation unknown unless its own evidence establishes its fact.')
    joint=request(case,'joint',name+'_complete.png',base+ending)
    if prefix['status']=='completed':
        history=' Your earlier model-produced answer, before the fuller view arrived, was:\n'+prefix['response']+'\nIt may be revised if evidence justifies it. '
        update=request(case,'update',name+'_complete.png',base+history+ending)
        withheld=request(case,'withheld',name+'_prefix.png',base+history+
            ' No additional fuller view has arrived. Reassess using only the displayed evidence.')
    else:
        update={'id':name+'_update','status':'skipped','reason':'Prefix request failed; do not invent model memory.'}
        withheld={'id':name+'_withheld','status':'skipped','reason':'Prefix request failed.'}
    return [prefix,recognition,joint,update,withheld]

if __name__=='__main__':
    (R/'responses').mkdir(exist_ok=True)
    protocol={
        'central_question':'Can later evidence resolve an earlier unknown observation while preserving unrelated historical facts and the latest capture identity?',
        'tested_hypothesis':'With equal final visual evidence, having issued an earlier answer can impair selective retrospective updating relative to joint answering.',
        'design':'Two real HoloAssist sources, controlled masks and delayed full frames. Frame-based diagnostic; not native video streaming.',
        'model_declared_by_public_app':'qwen3-vl-235b-a22b-instruct','host':HOST,
        'planned_conditions':['prefix','recognition','joint','update','withheld'],
        'maximum_initial_calls':10,'retry_policy':'No automatic retries; preserve all errors.',
        'source_count':2,'target_counterbalance':{'camera':'E1','printer':'E2'},
        'expected':{c['id']:{'prefix':{'E1':'unknown','E2':'unknown','matched_record':'none','latest_record':'E2'},
            'recognition':{'value':c['expected_value']},
            'joint_and_update':{'E1':c['expected_value'] if c['target']=='E1' else 'unknown',
                                'E2':c['expected_value'] if c['target']=='E2' else 'unknown',
                                'matched_record':c['target'],'latest_record':'E2'}} for c in CASES},
        'decision_rules':[
            'Backend errors and malformed answers are reported separately; neither is a demonstrated semantic failure.',
            'Qualification requires prefix unknown/unknown, full-view recognition correct, and joint selective update correct.',
            'For a qualified case, update failure is an exploratory history-conditioned failure; repeat on independent runs before claiming reproducibility.',
            'For a qualified case, update success is a pass, never relabelled as an irrelevant experiment.',
            'Withheld condition must retain unknown/unknown; otherwise report unsupported inference.',
            'No universal conclusion or novelty claim from two cases. Natural delayed evidence, autonomous replay detection and real-time latency are not tested.'
        ],
        'fairness':'Joint and update use byte-identical image inputs and common task instructions. Update additionally receives its own earlier answer. Visual context is retained; this isolates decision-history conditioning, not memory compression.',
        'given_information':'Replay status and E1/E2 capture order are supplied, target identity and value are not. Latest-record output tests instruction compliance only.',
        'hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(R.glob('*.png'))},
        'limitations':['Artificial occlusion and delayed frame delivery; natural case prevalence unknown',
                      'Single sampled frame per observation; no temporal-action understanding claim',
                      'Assistant-only labels; no independent annotation',
                      'Provider sampling, decoding and exact weights not controlled',
                      'One run per condition initially; no statistical inference']}
    path=R/'protocol.json'
    if path.exists():
        assert json.loads(path.read_text())==protocol
    else:
        save(path,protocol)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        rows=list(pool.map(case_run,CASES))
    save(R/'results.json',{'cases':rows})

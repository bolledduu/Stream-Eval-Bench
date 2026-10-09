"""Bounded four-call retrospective-contact diagnostic; no retries or cherry picking."""
import concurrent.futures, datetime, hashlib, json, os, time
from pathlib import Path
from gradio_client import Client, handle_file

ROOT = Path(__file__).resolve().parent
HOST = 'https://qwen-qwen3-vl-235b-a22b-instruct-demo.hf.space'
QUESTION = '''Identify the contact near the ball during the contested rebound between green and white uniforms. Did the white-uniformed player's reaching hand contact the green-uniformed player's hand holding the ball, or contact the ball directly? Report only what the visible evidence supports, not basketball rules or a remembered game. Use unknown if the view does not resolve the distinction. Return JSON: {"contact":"hand|direct_ball|unknown","green_uniform_present":true,"distinct_rebound_events":1,"visual_evidence":"brief explanation"}. The displayed values are a schema example, not supplied answers: set the boolean and count from the footage. Count physical rebound events, not camera views.'''

def save(path, obj):
    tmp = path.with_suffix('.tmp')
    with tmp.open('w') as stream:
        json.dump(obj, stream, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    tmp.replace(path)

def api(client, *args, api_name):
    job = client.submit(*args, api_name=api_name)
    try:
        return job.result(timeout=240)
    except Exception:
        job.cancel()
        raise

def trial(name, files, context):
    path = ROOT / 'responses' / (name + '.json')
    if path.exists():
        return json.loads(path.read_text())
    row = {'condition':name, 'prompt':context + '\n' + QUESTION,
           'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'inputs':[{'file':f, 'sha256':hashlib.sha256((ROOT/'inputs'/f).read_bytes()).hexdigest()} for f in files]}
    start = time.monotonic()
    print('START', name, flush=True)
    try:
        client = Client(HOST, hf_token=False, httpx_kwargs={'timeout':60}, verbose=False)
        api(client, api_name='/reset_state')
        for file in files:
            api(client, [], handle_file(str(ROOT/'inputs'/file)), api_name='/add_file')
        history = api(client, [], row['prompt'], api_name='/add_text')
        reply = api(client, history, api_name='/predict')
        row.update(status='completed', response=reply[-1][1])
        try:
            text = row['response']
            row['parsed'] = json.JSONDecoder().raw_decode(text[text.index('{'):])[0]
        except (ValueError, TypeError):
            row['parsed'] = None
    except Exception as error:
        row.update(status='error', error=repr(error))
    row['seconds'] = time.monotonic()-start
    save(path, row)
    print('DONE', name, row.get('response', row.get('error')), flush=True)
    return row

if __name__ == '__main__':
    (ROOT/'responses').mkdir(exist_ok=True)
    protocol = {'host':HOST, 'maximum_calls':4, 'retries':0,
       'source':'https://videorulebook.nba.com/archive/out-of-bounds-violation-hand-as-part-of-the-ball-on-an-out-of-bounds-play/',
       'intervals_seconds':{'initial':[0,9], 'later':[39,47]},
       'source_sha256':hashlib.sha256((ROOT/'nba_rulebook.mp4').read_bytes()).hexdigest(),
       'reference_contact':'hand', 'reference_basis':'Official NBA description; assistant visual review. No independent annotators.',
       'decision_rule':'Interpret updating only if later-only and together contact controls both return hand. A streaming-specific signal additionally requires an initial unknown/wrong contact and an update that remains wrong/unknown. Successful updating does not support a failure claim.',
       'limitations':['One selected edited replay case, not a natural-stream prevalence sample',
         'Model sees separate video uploads and explicit external response memory, not a native continuous stream',
         'Provider sampling and decoding unverified; prefix ambiguity not independently annotated',
         'No new-event, distractor, wrong-event, or matched-information controls; no novelty conclusion']}
    protocol_path = ROOT/'protocol.json'
    if protocol_path.exists():
        assert json.loads(protocol_path.read_text()) == protocol
    else:
        save(protocol_path, protocol)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        prefix = pool.submit(trial, 'prefix', ['initial.mp4'], 'This is the footage available so far.')
        control = pool.submit(trial, 'later_only', ['later.mp4'], 'Inspect the supplied footage.')
        first = prefix.result()
        if first['status'] == 'completed':
            update = pool.submit(trial, 'update', ['later.mp4'],
                'Additional footage has now arrived. Your earlier observation is below. Determine whether it shows a new event or another view of the earlier event, and revise the earlier contact description only if justified. Earlier observation:\n' + first['response'])
        else:
            update = None
        together = pool.submit(trial, 'together', ['initial.mp4','later.mp4'], 'The two supplied segments are in arrival order. Describe the contested rebound using all available evidence.')
        rows = [first, control.result(), together.result()]
        if update is not None:
            rows.append(update.result())
    save(ROOT/'results.json', {'rows':rows})

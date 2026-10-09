import json, pathlib, hashlib, time, datetime, base64
from gradio_client import Client, handle_file
R=pathlib.Path(__file__).resolve().parent
HOST='https://qwen-qwen3-vl-235b-a22b-instruct-demo.hf.space'
PLAN=[('together',['earlier','later'],None),('chronological_0',['earlier'],None),('chronological_1',['later'],'chronological_0'),('delayed_0',['later'],None),('delayed_1',['earlier'],'delayed_0')]
TIMES={'earlier': [64.019, 67.993, 71.934, 75.908], 'later': [112.009, 114.647, 117.285, 119.924]}
def pack(report):
    (R/'results.json').write_text(json.dumps(report,indent=2))
    files={p.name:p.read_text() for p in R.iterdir() if p.suffix in ['.py','.md','.json'] and p.name!='experiment_record.json'}
    data={'files':files,'binary_files':{p.name:base64.b64encode(p.read_bytes()).decode() for p in R.glob('*.mp4')}}
    (R/'experiment_record.json').write_text(json.dumps(data))
def main():
    report=json.loads((R/'results.json').read_text()) if (R/'results.json').exists() else {'design':'Frozen five-call, two-packet diagnostic; no selection or prompt changes based on outcomes. Model-produced text memory only. No statistical inference from one example.','host':HOST,'declared_model':'qwen3-vl-235b-a22b-instruct','limitations':['Four sampled source frames per video packet; not continuous streaming','Public demo decoding and backend weights not controlled','Supplied capture times; no autonomous replay detection'],'expected_final':{'earlier':'no','latest':'yes'},'media_sha256':{n:hashlib.sha256((R/(n+'.mp4')).read_bytes()).hexdigest() for n in TIMES},'results':[]}
    done={x['id']:x for x in report['results']}
    pending=next((x for x in PLAN if x[0] not in done),None)
    pack(report)
    if pending is None: print('COMPLETE');return
    name,clips,parent=pending
    memory=done[parent]['response'] if parent else '{}'
    latest=75.908 if name=='chronological_0' else 119.924
    mapping='\n'.join(f'Uploaded video {i+1} ({c}): its four frames have ORIGINAL capture timestamps {TIMES[c]} seconds.' for i,c in enumerate(clips))
    prompt=(mapping+'\nPlayback time is local to each uploaded file. Use original capture timestamps.\n'
      'Track whether the large round tray rests on the table frame. An open frame is not a tray.\n'
      'Answer two questions: earlier = was the tray resting on the frame around capture time 72 seconds? '
      'latest = was the tray resting on the frame at the latest capture time received? '
      'Use unknown when the relevant evidence has not been received. Do not infer an earlier state from later footage. '
      'An older clip arriving later can update history but does not become the latest capture time. '
      f'Latest capture time received: {latest} seconds.\nPrevious model-produced memory: {memory}\n'
      'Return only JSON with keys earlier and latest, each with value yes, no, or unknown.')
    started=time.perf_counter()
    try:
        client=Client(HOST,hf_token=False,httpx_kwargs={'timeout':60},verbose=False)
        client.predict(api_name='/reset_state')
        for c in clips:client.predict([],handle_file(str(R/(c+'.mp4'))),api_name='/add_file')
        history=client.predict([],prompt,api_name='/add_text')
        reply=client.predict(history,api_name='/predict')
        response=reply[-1][1]
        try:parsed=json.JSONDecoder().raw_decode(response[response.index('{'):])[0]
        except (ValueError,TypeError):parsed=None
        row={'id':name,'clips':clips,'input_memory':memory,'prompt':prompt,'response':response,'parsed':parsed,'elapsed_seconds':time.perf_counter()-started,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
        report['results'].append(row);report['finished']=len(report['results'])==5
        pack(report);print(json.dumps(row,indent=2),flush=True)
    except Exception as e:
        report.setdefault('errors',[]).append({'id':name,'error':repr(e),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()});pack(report);raise
if __name__=='__main__': main()

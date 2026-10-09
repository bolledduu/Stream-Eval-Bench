"""Original controlled evidence-update experiment; no novel method claimed."""
import argparse,datetime,hashlib,json,pathlib,re,time
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parent

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def decode_object(text):
    try:
        first=text.index('{');value,end=json.JSONDecoder().raw_decode(text[first:])
        return value if isinstance(value,dict) else None
    except (ValueError,json.JSONDecodeError):return None

class Qwen:
    def __init__(self):
        import torch,transformers
        from transformers import AutoProcessor,Qwen2VLForConditionalGeneration
        self.torch=torch;torch.set_num_threads(4);torch.manual_seed(0)
        self.processor=AutoProcessor.from_pretrained(ROOT/'model',min_pixels=64*28*28,max_pixels=256*28*28,local_files_only=True)
        self.model=Qwen2VLForConditionalGeneration.from_pretrained(ROOT/'model',torch_dtype=torch.bfloat16,low_cpu_mem_usage=True,attn_implementation='sdpa',local_files_only=True).eval()
        # Use the unmodified model forward. Per-image cache failed real-input equivalence audit.
        self.metadata={'model':'Qwen/Qwen2-VL-2B-Instruct','torch':torch.__version__,'transformers':transformers.__version__,'device':'cpu','dtype':'bfloat16','threads':4,'min_visual_tokens':64,'max_visual_tokens':256,'max_new_tokens':128,'decoding':'greedy','vision_features':'Disabled: unmodified joint-image vision forward; supersedes invalidated cached experiment'}
    def generate(self,frames,prompt):
        content=[];images=[]
        for label,path in frames:
            content.extend([{'type':'text','text':label},{'type':'image'}])
            with Image.open(path) as im:images.append(im.convert('RGB'))
        content.append({'type':'text','text':prompt})
        text=self.processor.apply_chat_template([{'role':'user','content':content}],tokenize=False,add_generation_prompt=True)
        inputs=self.processor(text=[text],images=images,return_tensors='pt') if images else self.processor(text=[text],return_tensors='pt')
        begin=time.perf_counter()
        with self.torch.inference_mode():out=self.model.generate(**inputs,max_new_tokens=128,do_sample=False)
        return self.processor.batch_decode(out[:,inputs['input_ids'].shape[1]:],skip_special_tokens=True)[0],time.perf_counter()-begin

def request(case,target,condition):
    record=case['records'][target];values=case['values']+['unknown']
    if condition=='recognition':
        return [('Full view',ROOT/record['full'])],case['question']+' Return only a JSON object with key "value". Allowed values: '+json.dumps(values)+'. Use unknown if the image does not establish the answer.'
    frames=[(f"Earlier partial view for record {r['id']}",ROOT/r['partial']) for r in case['records']]
    frames.append(('Later delivered image',ROOT/('inputs/withheld.png' if condition=='withheld_update' else record['full'])))
    if condition=='static_matching':
        return frames,'This is a static image-matching control. The third image is the full version of one of the first two images. Gray rectangles in the first two hide content. Match the visible, unmasked scene context. Return only JSON {"record":"E1"} or {"record":"E2"}; use {"record":"unknown"} if you cannot identify the match.'
    prompt='You maintain records of two earlier observations E1 and E2. The first two images are their partial reference views; gray rectangles hide content. The third image is a packet delivered later, from one of those SAME earlier observations, not a new occurrence. If that packet is completely gray, it provides no new visual evidence.\n'
    prompt+='Existing memory: '+json.dumps(case['initial_state'])+'\n'
    prompt+='The E1 and E2 values answer this question for their respective earlier observations: '+case['question']+'\n'
    prompt+='Match the later packet to the earlier record using visible scene context. Update ONLY the matched record using the newly visible evidence. Preserve the other record, device and event_count. If there is no new evidence or the match is uncertain, preserve unknown rather than guessing.\n'
    if condition=='oracle_update':prompt+='Trusted provenance: this packet belongs to '+record['id']+'.\n'
    prompt+='Return only a JSON object with exactly these keys: E1, E2, event_count, device. E1 and E2 values must be from '+json.dumps(values)+'.'
    return frames,prompt

def score(case,target,condition,text):
    obj=decode_object(text);r=case['records'][target];other=case['records'][1-target]['id']
    if condition=='recognition':
        return {'parsed':obj,'pass':bool(obj and str(obj.get('value','')).strip().lower()==r['value']),'format_failure':not isinstance(obj,dict) or 'value' not in obj}
    if condition=='static_matching':
        return {'parsed':obj,'pass':bool(obj and str(obj.get('record','')).strip().upper()==r['id']),'format_failure':not isinstance(obj,dict) or 'record' not in obj}
    expected=dict(case['initial_state'])
    if condition!='withheld_update':expected[r['id']]=r['value']
    norm={k:(v.lower().strip() if isinstance(v,str) else v) for k,v in (obj or {}).items()}
    return {'parsed':obj,'expected':expected,'pass':all(norm.get(k)==v for k,v in expected.items()),'target_correct':norm.get(r['id'])==expected[r['id']],'other_preserved':norm.get(other)=='unknown','count_preserved':norm.get('event_count')==2,'device_preserved':norm.get('device')==case['id'],'format_failure':not obj or any(k not in obj for k in expected)}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--dry-run',action='store_true');args=ap.parse_args()
    protocol=json.loads((ROOT/'protocol.json').read_text());trials=[]
    for condition in protocol['conditions']:
        for case in protocol['cases']:
            for target in [0,1]:
                frames,prompt=request(case,target,condition)
                trials.append({'trial_id':f"{case['id']}_{target}_{condition}",'case':case['id'],'target':target,'condition':condition,'frames':[{'label':label,'path':str(path.relative_to(ROOT)),'sha256':digest(path)} for label,path in frames],'prompt':prompt})
    (ROOT/'requests.json').write_text(json.dumps(trials,indent=2))
    if args.dry_run:print('Prepared',len(trials),'requests');return
    out=ROOT/'results/qwen.json';rows=[]
    if out.exists():
        old=json.loads(out.read_text());assert old['protocol_sha256']==digest(ROOT/'protocol.json');rows=old['results']
    done={r['trial_id'] for r in rows};model=Qwen();print('Model loaded',model.metadata,flush=True)
    cases={c['id']:c for c in protocol['cases']}
    for trial in trials:
        if trial['trial_id'] in done:continue
        frames=[(f['label'],ROOT/f['path']) for f in trial['frames']]
        answer,latency=model.generate(frames,trial['prompt'])
        s=score(cases[trial['case']],trial['target'],trial['condition'],answer)
        rows.append({**trial,'response':answer,'latency_seconds':latency,'score':s})
        report={'protocol_sha256':digest(ROOT/'protocol.json'),'requests_sha256':digest(ROOT/'requests.json'),'model':json.loads((ROOT/'model_manifest.json').read_text()),'environment':model.metadata,'saved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'results':rows}
        tmp=out.with_suffix('.partial');tmp.write_text(json.dumps(report,indent=2));tmp.replace(out)
        print(trial['trial_id'],repr(answer),'PASS',s['pass'],'SECONDS',round(latency,2),flush=True)
if __name__=='__main__':main()

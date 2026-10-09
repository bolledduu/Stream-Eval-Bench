import pathlib,json,base64
r=pathlib.Path(__file__).resolve().parent;record=pathlib.Path('/workspace/scratch/06f7a90cc9c6/recovered/streaming_video_experiment_record.json');j=json.loads(record.read_text())
for section in ['files','binary_files']:j[section]={k:v for k,v in j[section].items() if not k.startswith('streaming_trial/')}
for p in r.rglob('*'):
 if not p.is_file() or 'model' in p.relative_to(r).parts or '__pycache__' in p.parts:continue
 key=str(p.relative_to(r.parent))
 if p.suffix in ['.py','.md','.json','.txt','.log']:j['files'][key]=p.read_text()
 elif p.suffix in ['.png','.mp4']:j['binary_files'][key]=base64.b64encode(p.read_bytes()).decode()
j['streaming_test_status']='See streaming_trial/hosted/run.json and streaming_trial/results/run.json. Native video packet experiment, with chronological and delayed-arrival conditions. Local 2B failed qualification; official hosted 235B backend access succeeded and qualified paired test is in progress. Do not infer incomplete predictions.'
record.write_text(json.dumps(j,indent=2));print(record.stat().st_size)

"""Update the existing recovery record without including model weights or raw videos."""
import base64,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parent;PILOT=ROOT.parent
record=pathlib.Path('/workspace/scratch/06f7a90cc9c6/recovered/streaming_video_experiment_record.json')
data=json.loads(record.read_text())
for section in ['files','binary_files']:
 data[section]={k:v for k,v in data.get(section,{}).items() if not k.startswith('direct_revision/')}
for p in ROOT.rglob('*'):
 if p.is_file() and 'model' not in p.relative_to(ROOT).parts and '__pycache__' not in p.parts:
  name=str(p.relative_to(PILOT))
  if p.suffix in ['.py','.json','.txt','.log','.md']:data['files'][name]=p.read_text()
  elif p.suffix in ['.png','.pt']:data.setdefault('binary_files',{})[name]=base64.b64encode(p.read_bytes()).decode()
data['direct_test_status']='COMPLETED: 30 main calls plus 8 post-hoc diagnostic calls with unmodified joint-image inference; final_audit.json passed. Earlier cache equivalence audit failed; invalidated_cached results must not be used. Corrected results show a small-model visual-to-record failure, not an established streaming-specific research gap. See RESULTS.md. Protocol, inputs, code and raw outputs included.'
record.write_text(json.dumps(data,indent=2));print(record.stat().st_size)

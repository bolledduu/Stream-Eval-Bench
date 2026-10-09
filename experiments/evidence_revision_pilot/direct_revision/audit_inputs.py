"""Audit frozen real-image interventions and expose the trivial pixel-match control."""
import json,pathlib,hashlib
import numpy as np
from PIL import Image
root=pathlib.Path(__file__).resolve().parent;p=json.loads((root/'protocol.json').read_text());rows=[]
for c in p['cases']:
 full=[np.asarray(Image.open(root/r['full']).convert('RGB'),dtype=np.int16) for r in c['records']]
 partial=[np.asarray(Image.open(root/r['partial']).convert('RGB'),dtype=np.int16) for r in c['records']]
 x0,y0,x1,y1=c['box'];outside=np.ones(full[0].shape[:2],dtype=bool);outside[y0:y1+1,x0:x1+1]=False  # PIL rectangle includes the endpoint
 for t in [0,1]:
  assert np.array_equal(full[t][outside],partial[t][outside])
  mask_values=np.unique(partial[t][~outside]);assert len(mask_values)==1
  distances=[float(np.abs(full[t][outside]-ref[outside]).mean()) for ref in partial]
  match=int(np.argmin(distances));assert match==t
  rows.append({'case':c['id'],'target':t,'outside_mask_unchanged':True,'mask_value':int(mask_values[0]),'pixel_distances':distances,'pixel_match_correct':match==t})
report={'rows':rows,'pixel_matching_correct':sum(x['pixel_match_correct'] for x in rows),'trials':len(rows),'interpretation':'Same-frame constructed reveals make association exactly solvable by pixel matching. This is a sanity baseline, not a novel method or proof of natural-stream difficulty.'}
(root/'results/input_audit.json').write_text(json.dumps(report,indent=2));print('Input audit passed; trivial pixel matching: 6/6')

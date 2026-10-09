"""Rebuild controlled panels from the existing, source-hashed pilot frames."""
import json
from pathlib import Path
from PIL import Image, ImageDraw

R=Path(__file__).resolve().parent
P=R.parent/'evidence_revision_pilot'/'direct_revision'
original=json.loads((P/'protocol.json').read_text())
cases=[]
for name,target in [('camera',0),('printer',1)]:
    case=next(c for c in original['cases'] if c['id']==name)
    panels=[Image.open(P/record['partial']).convert('RGB') for record in case['records']]
    reveal=Image.open(P/case['records'][target]['full']).convert('RGB')
    variants=[('prefix',panels,['Earlier record E1','Later record E2']),
              ('complete',panels+[reveal],['Earlier record E1','Later record E2','Newly available fuller view']),
              ('recognition',[reveal],['Full view'])]
    for kind,images,labels in variants:
        sheet=Image.new('RGB',(512*len(images),320),'white')
        draw=ImageDraw.Draw(sheet)
        for i,(im,label) in enumerate(zip(images,labels)):
            sheet.paste(im,(512*i,32))
            draw.text((512*i+10,10),label,fill='black')
        sheet.save(R/f'{name}_{kind}.png')
    cases.append({'id':name,'target':f'E{target+1}','question':case['question'],
                  'choices':list(case['values'])+['unknown'],'expected_value':case['values'][target],
                  'source':case['source'],'records':case['records'],'mask':case['box']})
(R/'cases.json').write_text(json.dumps(cases,indent=2))

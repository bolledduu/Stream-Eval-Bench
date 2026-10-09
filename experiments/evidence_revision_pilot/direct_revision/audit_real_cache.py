"""Verify image-feature caching against a joint encoding of actual trial inputs."""
import json, pathlib, torch
from PIL import Image
from experiment import Qwen,request,digest
root=pathlib.Path(__file__).resolve().parent
model=Qwen()
# Deliberately reinstall the legacy optimization only inside this historical audit.
from vision_cache import install
install(model.model,root)
p=json.loads((root/'protocol.json').read_text());c=next(c for c in p['cases'] if c['id']=='camera')
frames,prompt=request(c,1,'visual_update')
images=[Image.open(path).convert('RGB') for _,path in frames]
content=[]
for label,path in frames:content.extend([{'type':'text','text':label},{'type':'image'}])
content.append({'type':'text','text':prompt})
text=model.processor.apply_chat_template([{'role':'user','content':content}],tokenize=False,add_generation_prompt=True)
inputs=model.processor(text=[text],images=images,return_tensors='pt')
pixels=inputs['pixel_values'].to(model.model.visual.get_dtype());grid=inputs['image_grid_thw']
# Class method is the original forward; the optimization only replaces the instance attribute.
with torch.inference_mode():
 joint=type(model.model.visual).forward(model.model.visual,pixels,grid_thw=grid)
 separate=model.model.visual.forward(pixels,grid_thw=grid)
maximum=float((joint-separate).abs().max());equal=torch.equal(joint,separate)
row={'test':'Real camera E2 multi-image trial: joint versus cached per-image encoding','bitwise_equal':equal,'max_absolute_difference':maximum,'shape':list(joint.shape),'frames':[{'path':str(path.relative_to(root)),'sha256':digest(path)} for _,path in frames]}
(root/'results/real_cache_audit.json').write_text(json.dumps(row,indent=2));print(json.dumps(row,indent=2));assert equal

import json,pathlib,time
from gradio_client import Client,handle_file
r=pathlib.Path(__file__).resolve().parent;m=json.loads((r/'metadata.json').read_text());client=Client(m['host'],hf_token=False,httpx_kwargs={'timeout':45})
h=client.predict(api_name='/reset_state');print('reset',flush=True)
h=client.predict(h,handle_file(str(r.parent.parent/'direct_revision/inputs/camera_E1_full.png')),api_name='/add_file');print('uploaded',repr(h),flush=True)
h=client.predict([],'What detached part is held in the right hand: a cylindrical camera lens assembly, or a flat lens cap? Return only the name.',api_name='/add_text');print('text added',repr(h),flush=True)
out=client.predict(h,api_name='/predict');(r/'smoke_output.json').write_text(json.dumps(out,indent=2));print('OUTPUT',repr(out),flush=True)

import json,pathlib
from gradio_client import Client
r=pathlib.Path(__file__).resolve().parent;m=json.loads((r/'metadata.json').read_text());c=Client(m['host'],hf_token=False,httpx_kwargs={'timeout':30})
a=c.view_api(return_format='dict');(r/'api.json').write_text(json.dumps(a,indent=2))

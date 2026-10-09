import json,pathlib,time
from gradio_client import Client,handle_file
ROOT=pathlib.Path(__file__).resolve().parent
client=Client('Qwen/Qwen2.5-VL-32B-Instruct',verbose=False)
history=client.predict(api_name='/reset_state')
history=client.predict(history,handle_file(str(ROOT/'inputs/camera_E1_full.png')),api_name='/add_file')
print('UPLOAD_HISTORY',repr(history),flush=True)
prompt='What detached camera part is held separately in the right hand? lens means the cylindrical lens assembly; cap means the flat circular lens cover. Return only a JSON object with key "value". Allowed values: ["lens", "cap", "unknown"]. Use unknown if the image does not establish the answer.'
history=client.predict(history,prompt,api_name='/add_text')
start=time.perf_counter();job=client.submit(history,api_name='/predict')
try:
 answer=job.result(timeout=120)
 (ROOT/'results/hosted_smoke.json').write_text(json.dumps({'prompt':prompt,'response':answer[-1][1],'seconds':time.perf_counter()-start},indent=2));print(answer[-1][1],flush=True)
except Exception as error:
 job.cancel();(ROOT/'results/hosted_error.json').write_text(json.dumps({'type':type(error).__name__,'message':str(error)},indent=2));raise

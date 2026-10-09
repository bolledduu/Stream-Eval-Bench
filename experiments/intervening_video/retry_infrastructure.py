"""One explicit infrastructure-only retry; never replace a completed answer."""
import datetime,json
import run
r=run.R;p=r/'responses/chronological_1.json'
row=json.loads(p.read_text());assert row['status']=='error' and 'AppError' in row['error']
assert not (r/'retry_amendment.json').exists(),'Retry already used'
run.save(r/'retry_amendment.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reason':'Upstream Gradio AppError without a model response. Complete the interrupted chronological chain.','scope':'Exactly one retry of chronological_1; its descendants run once. All completed model responses unchanged. Original error retained.','change':'Initial protocol had no automatic retries. This explicit post-error amendment permits one infrastructure retry only.'})
(r/'infrastructure_errors').mkdir(exist_ok=True);p.rename(r/'infrastructure_errors/chronological_1_attempt1.json')
run.run_condition('chronological',run.setup())
run.audit()

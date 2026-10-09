"""User-requested resumption of the infrastructure-interrupted condition."""
import datetime,json
import run
r=run.R;p=r/'responses/chronological_1.json'
row=json.loads(p.read_text());assert row['status']=='error' and 'AppError' in row['error']
archive=r/'infrastructure_errors/chronological_1_attempt2.json'
assert not archive.exists(),'This resumption has already been attempted'
run.save(r/'completion_amendment.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reason':'User requested completion after the partial run. Resume only the infrastructure-interrupted chronological branch, sequentially.','scope':'One further attempt at chronological_1, then its two dependent steps. No successful model response replaced. Original inputs, prompts and scoring unchanged.','limit':'If a further service error occurs, retain it and stop. This is an additional explicit deviation from the original no-retry protocol.'})
p.rename(archive)
run.run_condition('chronological',run.setup())
run.audit()

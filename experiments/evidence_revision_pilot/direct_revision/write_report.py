"""Summarize only the corrected, unmodified-forward results; never pool invalidated trials."""
import json,pathlib
r=pathlib.Path(__file__).resolve().parent
a=json.loads((r/'results/analysis.json').read_text());run=json.loads((r/'results/qwen.json').read_text())
assert a['completed_calls']==30
assert run['environment']['vision_features'].startswith('Disabled:')
lines=['# Corrected controlled evidence-update pilot','', 'Model: Qwen/Qwen2-VL-2B-Instruct, pinned revision '+run['model']['revision']+'. CPU bfloat16, greedy decoding, unmodified joint-image inference.', '', '**Scope:** six reference views from three HoloAssist recordings. Content was artificially masked and then revealed; the initial memory and old-record status were supplied. Each request contains still images. The target is unknown-to-known completion, not correction of a previously false assertion. This is not an end-to-end livestream benchmark, natural delayed-evidence dataset, or test of autonomous replay detection.', '', '**Correction:** the earlier per-image feature cache failed an audit against normal joint-image encoding (maximum feature difference 25.125). Its research results are invalidated and retained under `results/invalidated_cached`. Every main trial and both diagnostic triplets were rerun without that cache. Do not cite old accuracy counts as evidence.', '', '| Test | Correct / unique requests |','|---|---:|']
for k,v in a['conditions'].items():lines.append(f"| {k} | {v['pass']} / {v['unique_trials']} |")
lines += ['', 'The unchanged-background pixel-match sanity baseline obtains 6/6. It is not a novel method or evidence about naturally changing viewpoints. Thirty main calls represent 27 unique requests: each source has two identical withheld-evidence controls. They are not independent observations. There are only three source sessions.', '', '| Source / record | Target value | Read fact | Match record | Update | Update with supplied ID |','|---|---|---|---|---|---|']
for row in a['breakdown']:
 vals=[row[k] for k in ['recognition_pass','static_match_pass','visual_update_pass','oracle_update_pass']]
 lines.append('| '+row['case']+' / '+row['record']+' | '+row['expected']+' | '+' | '.join('Pass' if x else 'Fail' for x in vals)+' |')
lines += ['', '## Separate post-hoc diagnostics', '', 'These cases were selected during exploration, not a held-out test. Text-supplied facts remove perception and are a diagnostic control, not a proposed novel method.']
for file in ['followups.json','camera_followups.json','simple_baselines.json']:
 j=json.loads((r/'results'/file).read_text());lines += ['','### '+file,'']
 for row in j['results']:
  lines += ['- '+row['id']+': '+('PASS' if row['pass'] else 'FAIL')+'; actual output `'+json.dumps(row['parsed'])+'`; expected `'+json.dumps(row['expected'])+'`.']
lines += ['', '## Interpretation limits', '', 'A correct answer in isolation does not guarantee correct perception in a multi-image request; use the context-recognition diagnostic before attributing an update error to memory. One correct E1 match does not establish robust matching; inspect both E1 and E2 and position bias.', '', 'No novelty, model-population failure rate, real-time throughput, or CVPR suitability follows from this pilot. Labels were assistant-screened and need independent human validation. A stronger-model replication and naturally occurring delayed evidence remain untested. The attempted hosted larger-model run produced no predictions.', '', 'All exact prompts, PNG input hashes, raw responses, expected values, per-field scoring, source references and invalidation history are retained.']
(r/'RESULTS.md').write_text('\n'.join(lines)+'\n')
print(r/'RESULTS.md')

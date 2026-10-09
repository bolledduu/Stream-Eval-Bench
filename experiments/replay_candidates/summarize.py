"""Report primary contact results without converting service failures to model errors."""
import json
from pathlib import Path

root = Path(__file__).resolve().parent
rows = {p.stem:json.loads(p.read_text()) for p in (root/'responses').glob('*.json')}
def contact(name):
    row = rows.get(name, {})
    parsed = row.get('parsed')
    return parsed.get('contact') if isinstance(parsed, dict) else None

gate = all(rows.get(k, {}).get('status') == 'completed' and contact(k) == 'hand'
           for k in ['later_only', 'together'])
if not gate:
    conclusion = 'INCONCLUSIVE: the two evidence-understanding controls have not both passed. No streaming-specific failure may be claimed.'
elif rows.get('update', {}).get('status') != 'completed':
    conclusion = 'INCONCLUSIVE: controls passed but no completed update response is available.'
elif contact('update') == 'hand':
    conclusion = 'UPDATE SUCCEEDED on this one case; this does not support a retrospective-updating failure claim.'
elif contact('update') in ['unknown', 'direct_ball'] and contact('prefix') in ['unknown', 'direct_ball']:
    conclusion = 'CANDIDATE SIGNAL ONLY: controls passed and the update did not recover the reference contact. Replication and matched-information controls are required.'
else:
    conclusion = 'INCONCLUSIVE or a different failure pattern; inspect raw responses.'

lines = ['# Retrospective-contact diagnostic results', '', conclusion, '',
         '| Condition | Request status | Contact answer |', '|---|---|---|']
for name in ['prefix', 'later_only', 'together', 'update']:
    row = rows.get(name, {})
    lines.append(f"| {name} | {row.get('status', 'not run / unavailable')} | {contact(name) or 'No usable contact answer'} |")
lines += ['', '## Interpretation', '',
          'The official NBA reference is hand contact. An initial unknown answer is acceptable uncertainty, not a failure. Service errors are not model errors. Auxiliary preservation/count outputs are excluded because the schema example cues their values.', '',
          'This is one edited basketball replay pair, not a validated multi-domain benchmark or a native livestream. The initial prefix and later evidence have not been rated by independent human annotators. Public model identity, sampling and decoding are not independently verified. No claim of novelty or general failure rate follows.', '',
          'See README.md for candidate decisions, source provenance, exact intervals, reproduction and limitations. Raw prompts and responses are in responses/.']
if contact('prefix') == 'hand':
    lines += ['', 'The prefix response already gives the reference contact. Consequently this run does not exhibit an initial uncertain/wrong belief that later evidence must repair. Its confident description does not establish that the wide view truly resolves contact: guessing, memorization and visual recognition are not separated. Do not replace that answer with a manufactured error.']
(root/'RESULTS.md').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines))

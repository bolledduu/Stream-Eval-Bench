import json,pathlib,unittest
from experiment import request,score
ROOT=pathlib.Path(__file__).resolve().parent
P=json.loads((ROOT/'protocol.json').read_text())
class DesignTests(unittest.TestCase):
 def test_oracle_changes_only_provenance_text(self):
  for c in P['cases']:
   for t in [0,1]:
    a,p=request(c,t,'visual_update');b,q=request(c,t,'oracle_update')
    self.assertEqual(a,b)
    self.assertEqual(p,q.replace('Trusted provenance: this packet belongs to '+c['records'][t]['id']+'.\n',''))
 def test_target_is_not_given_in_visual_prompt(self):
  for c in P['cases']:
   _,a=request(c,0,'visual_update');_,b=request(c,1,'visual_update')
   self.assertEqual(a,b)
 def test_withheld_targets_are_duplicate_controls(self):
  for c in P['cases']:self.assertEqual(request(c,0,'withheld_update'),request(c,1,'withheld_update'))
 def test_wrong_record_update_fails(self):
  for c in P['cases']:
   value=dict(c['initial_state']);value['E2']=c['records'][0]['value']
   self.assertFalse(score(c,0,'visual_update',json.dumps(value))['pass'])
 def test_inventing_new_event_fails(self):
  for c in P['cases']:
   value=dict(c['initial_state']);value['E1']=c['records'][0]['value'];value['event_count']=3
   self.assertFalse(score(c,0,'visual_update',json.dumps(value))['pass'])
 def test_no_evidence_preserves_memory(self):
  for c in P['cases']:self.assertTrue(score(c,0,'withheld_update',json.dumps(c['initial_state']))['pass'])
if __name__=='__main__':unittest.main()

import unittest
from analyze import score

class Scoring(unittest.TestCase):
    def test_infrastructure_not_failure(self):
        self.assertEqual(score({'status':'error'}, {'E1':'lens'}),'error')
    def test_missing_answer_not_failure(self):
        self.assertEqual(score({'status':'completed','parsed':{}},{'E1':'lens'}),'schema_error')
    def test_unrelated_overwrite_fails(self):
        row={'status':'completed','parsed':{'E1':'lens','E2':'cap'}}
        self.assertEqual(score(row,{'E1':'lens','E2':'unknown'}),'fail')
    def test_selective_update_passes(self):
        row={'status':'completed','parsed':{'E1':'lens','E2':'unknown'}}
        self.assertEqual(score(row,{'E1':'lens','E2':'unknown'}),'pass')

if __name__=='__main__':
    unittest.main()

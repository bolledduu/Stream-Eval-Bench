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
    def test_record_identifiers_keep_correct_case_insensitive_comparison(self):
        row={'status':'completed','parsed':{'E1':'unknown','E2':'dark','matched_record':'E2','latest_record':'E2'}}
        expected={'E1':'unknown','E2':'dark','matched_record':'E2','latest_record':'E2'}
        self.assertEqual(score(row,expected),'pass')
    def test_wrong_record_identifier_fails(self):
        row={'status':'completed','parsed':{'matched_record':'E1'}}
        self.assertEqual(score(row,{'matched_record':'E2'}),'fail')

if __name__=='__main__':
    unittest.main()

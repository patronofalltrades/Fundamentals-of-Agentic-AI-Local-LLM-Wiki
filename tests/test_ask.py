import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import wiki


class AskTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root/'vault/raw').mkdir(parents=True); (self.root/'data').mkdir()
        (self.root/'prompts').mkdir()
        (self.root/'prompts/ask.txt').write_text('Use only the supplied passages.')
        self.text = '---\ntype: note\n---\n\n# Topic\n\nA loop limits steps and time.\n'
        path=self.root/'vault/raw/Topic.md';path.write_text(self.text)
        self.source={'id':'S01','title':'Topic','path':'vault/raw/Topic.md',
                     'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        wiki.write_json(self.root/'data/source-catalog.json',{'sources':[self.source]})
        self.answer={'insufficient_evidence':False,'answer':'The note recommends limits on steps and time.','citations':[]}
        self.calls=[]

    def local_api(self,method,path,payload=None,timeout=180):
        self.calls.append((method,path,payload,timeout))
        if path=='/api/tags': return {'models':[{'name':wiki.MODEL,'digest':'test'}]}
        if path=='/api/show': return {'capabilities':['completion']}
        return {'done':True,'done_reason':'stop','prompt_eval_count':12,'eval_count':18,
                'message':{'content':json.dumps(self.answer)}}

    def hit(self):
        return {'citation_id':'S01-123456789abc-L8-L8','title':'Topic','source_id':'S01',
                'source_path':self.source['path'],'source_sha256':self.source['sha256'],
                'section':'Topic','start_line':8,'end_line':8,'text':'A loop limits steps and time.'}

    def test_only_a_retrieved_citation_is_accepted_and_history_is_absent(self):
        self.answer['citations']=[self.hit()['citation_id']]
        with patch('wiki.search',return_value={'hits':[self.hit()],'generation_used':False}), patch('wiki.local_api',side_effect=self.local_api):
            result=wiki.ask(self.root,'What does this note limit?')
        self.assertIn('steps and time',result['answer'])
        self.assertIn(self.hit()['citation_id'],result['citation_ids'])
        payload=[c[2] for c in self.calls if c[1]=='/api/chat'][0]
        self.assertEqual(len(payload['messages']),2)
        self.assertNotIn('history',json.dumps(payload).lower())
        allowed=payload['format']['properties']['citations']['items']['enum']
        self.assertEqual(allowed,[self.hit()['citation_id']])
        self.assertEqual(payload['format']['properties']['answer']['type'],'string')

    def test_unretrieved_citation_is_rejected(self):
        self.answer['citations']=['S99-invented-L1-L2']
        with patch('wiki.search',return_value={'hits':[self.hit()]}), patch('wiki.local_api',side_effect=self.local_api):
            with self.assertRaisesRegex(ValueError,'not retrieved'):
                wiki.ask(self.root,'Question')

    def test_no_retrieved_passages_abstains_without_calling_gemma(self):
        with patch('wiki.search',return_value={'hits':[]}), patch('wiki.local_api') as api:
            result=wiki.ask(self.root,'No matching evidence?')
        self.assertTrue(result['insufficient_evidence'])
        self.assertEqual(result['citation_ids'],[])
        api.assert_not_called()

    def test_offline_marker_is_saved_on_a_new_run(self):
        with patch.dict(os.environ, {'WIKI_OFFLINE_PROOF': '1'}), \
                patch('wiki.search', return_value={'hits': []}):
            result=wiki.ask(self.root,'No matching evidence?')
        record=wiki.read_json(self.root/'evidence/ask'/result['run_id']/'run.json')
        self.assertTrue(record['offline_proof'])

    def test_insufficient_answer_must_have_no_citations(self):
        bad={'insufficient_evidence':True,'answer':'Guess','citations':['S99']}
        with self.assertRaisesRegex(ValueError,'must not include citations'):
            wiki.validate_answer(bad,[self.hit()])

    def test_abstention_must_explain_missing_information(self):
        bad={'insufficient_evidence':True,'answer':'insufficient_evidence=true','citations':[]}
        with self.assertRaisesRegex(ValueError,'plain language'):
            wiki.validate_answer(bad,[self.hit()])
        vague={'insufficient_evidence':True,'answer':'The notes do not say.','citations':[]}
        with self.assertRaisesRegex(ValueError,'plain language'):
            wiki.validate_answer(vague,[self.hit()])

    def test_harness_normalizes_a_flagged_but_unhelpful_abstention(self):
        raw={'insufficient_evidence':True,'answer':'insufficient_evidence=true','citations':[]}
        answer,changed,cleared=wiki.normalize_abstention(raw)
        self.assertTrue(changed)
        self.assertFalse(cleared)
        self.assertEqual(raw['answer'],'insufficient_evidence=true')
        self.assertIn('retrieved passages',answer['answer'])
        self.assertEqual(wiki.validate_answer(answer,[self.hit()]),answer)

    def test_harness_clears_citations_on_flagged_abstention_and_preserves_raw(self):
        raw={'insufficient_evidence':True,
             'answer':'The passages do not give an exact step or time limit for this project.',
             'citations':[self.hit()['citation_id']]}
        answer,changed,cleared=wiki.normalize_abstention(raw)
        self.assertFalse(changed)
        self.assertTrue(cleared)
        self.assertEqual(raw['citations'],[self.hit()['citation_id']])
        self.assertEqual(answer['citations'],[])
        self.assertEqual(wiki.validate_answer(answer,[self.hit()]),answer)

    def test_every_supported_claim_needs_a_citation(self):
        bad={'insufficient_evidence':False,'answer':'Claim','citations':[]}
        with self.assertRaisesRegex(ValueError,'must include 1-5 citations'):
            wiki.validate_answer(bad,[self.hit()])

    def test_model_failure_is_recorded(self):
        with patch('wiki.search',return_value={'hits':[self.hit()]}), patch('wiki.local_api',side_effect=ValueError('local model unavailable')):
            with self.assertRaisesRegex(ValueError,'unavailable'):
                wiki.ask(self.root,'Question')
        record=next((self.root/'evidence/ask').glob('*/run.json'))
        self.assertEqual(wiki.read_json(record)['status'],'failed')

    def test_only_retrieved_text_enters_model_prompt(self):
        self.answer['citations']=[self.hit()['citation_id']]
        with patch('wiki.search',return_value={'hits':[self.hit()]}), patch('wiki.local_api',side_effect=self.local_api):
            wiki.ask(self.root,'What does this note limit?')
        payload=[c[2] for c in self.calls if c[1]=='/api/chat'][0]
        user_message=payload['messages'][1]['content']
        self.assertIn(self.hit()['text'],user_message)
        self.assertNotIn('Review the evaluation rubric in another file.',user_message)
        self.assertNotIn('Answer key:',user_message)



if __name__=='__main__':
    unittest.main()

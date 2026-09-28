import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import retrieval
import wiki


class SearchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root/'vault/raw').mkdir(parents=True)
        (self.root/'data').mkdir()
        self.original = '---\ntags: secretmetadata\n---\n\n# Source\n\n## Controls\n\nEnforce budgets for tokens and time.\n\nKeep a record of failures.\n'
        self.path = self.root/'vault/raw/Note.md'
        self.path.write_text(self.original)
        self.source = {'id':'S01','title':'Control note','path':'vault/raw/Note.md',
                       'sha256':hashlib.sha256(self.path.read_bytes()).hexdigest()}
        wiki.write_json(self.root/'data/source-catalog.json', {'sources':[self.source]})

    def test_only_cataloged_originals_are_searchable(self):
        for relative in ('vault/wiki/Generated.md','evaluation/answer-key.md','learning/quiz.md','vault/raw/Unselected.md'):
            p=self.root/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('contaminationmarker')
        self.assertEqual(wiki.search(self.root,'contaminationmarker')['hits'],[])
        self.assertEqual(wiki.search(self.root,'secretmetadata')['hits'],[])

    def test_passages_and_ids_survive_rebuild(self):
        first=wiki.search(self.root,'budgets')
        second=wiki.search(self.root,'budgets',rebuild=True)
        self.assertEqual(first['hits'],second['hits'])
        hit=first['hits'][0]
        self.assertEqual(hit['text'],'\n'.join(self.original.splitlines()[hit['start_line']-1:hit['end_line']]))
        self.assertEqual(hit['section'],'Controls')

    def test_changed_original_blocks_cached_search(self):
        wiki.search(self.root,'budgets')
        self.path.write_text('Changed source')
        with self.assertRaisesRegex(ValueError,'hash changed'):
            wiki.search(self.root,'budgets')

    def test_catalog_change_rebuilds_index(self):
        wiki.search(self.root,'budgets')
        self.source['title']='Updated control note'
        wiki.write_json(self.root/'data/source-catalog.json',{'sources':[self.source]})
        result=wiki.search(self.root,'budgets')
        self.assertTrue(result['index_rebuilt'])
        self.assertEqual(result['hits'][0]['title'],'Updated control note')

    def test_network_and_model_are_never_called(self):
        with patch('socket.socket',side_effect=AssertionError('Network forbidden')) as network, patch('wiki.local_api',side_effect=AssertionError('Model forbidden')) as model:
            self.assertTrue(wiki.search(self.root,'budgets',rebuild=True)['hits'])
            network.assert_not_called();model.assert_not_called()

    def test_fts_syntax_is_treated_as_literal_terms(self):
        wiki.search(self.root,'budgets" OR NEAR(x*) : DROP TABLE passages; --')
        self.assertTrue(wiki.search(self.root,'budgets')['hits'])

    def test_empty_commonword_and_limit_errors(self):
        for query in ('', 'the and what'):
            with self.assertRaises(ValueError):
                wiki.search(self.root,query)
        with self.assertRaisesRegex(ValueError,'between 1 and 20'):
            wiki.search(self.root,'budget',limit=0)

    def test_expansion_is_visible_and_returns_original_text(self):
        result=wiki.search(self.root,'unlimited resources')
        self.assertIn('budgets',result['expanded_terms'])
        self.assertIn('Enforce budgets',result['hits'][0]['text'])

    def test_chunk_boundaries_keep_all_source_body_lines(self):
        original='# Note\n\n## Long section\n\n'+'\n\n'.join('Paragraph %s %s' % (i,'words '*80) for i in range(8))
        chunks=retrieval.chunks(self.source,original)
        covered={n for h in chunks for n in range(h['start_line'],h['end_line']+1)}
        for n,line in enumerate(original.splitlines(),1):
            if line.startswith('Paragraph'):
                self.assertIn(n,covered)
        self.assertGreater(len(chunks),1)

    def test_duplicate_summary_is_removed_when_richer_passage_contains_it(self):
        summary='Five agent architecture patterns are mapped onto a perceive decide act evaluate loop.'
        richer=summary+' Single Agent uses one model in a loop; Sequential uses step by step handoffs.'
        short={'source_id':'S01','text':summary}
        long={'source_id':'S01','text':richer}
        distinct, skipped=retrieval.deduplicate_passages([short,long])
        self.assertEqual(distinct,[long])
        self.assertEqual(skipped,1)


if __name__=='__main__':
    unittest.main()

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import wiki


class IngestionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'vault/raw').mkdir(parents=True)
        (self.root / 'data').mkdir()
        (self.root / 'prompts').mkdir()
        (self.root / 'prompts/ingest.txt').write_text('Summarize the original.')
        self.original = 'First original passage.\n\nSecond original passage.\n\nThird original passage.\n'
        (self.root / 'vault/raw/Note.md').write_text(self.original)
        self.source = {'id': 'S01', 'title': 'Note', 'path': 'vault/raw/Note.md',
                       'sha256': hashlib.sha256(self.original.encode()).hexdigest()}
        wiki.write_json(self.root / 'data/source-catalog.json', {'sources': [self.source]})
        self.plan = {'S01': {'title': 'Test Subject', 'related': {}}}
        wiki.write_json(self.root / 'data/wiki-plan.json', self.plan)
        self.draft = {'summary': 'A short summary.', 'points': [
            {'text': 'A statement.', 'evidence_id': pid} for pid in wiki.evidence_passages(self.original)],
            'limitations': ['A small source.']}

    def api(self, method, path, *args, **kwargs):
        if path == '/api/tags':
            return {'models': [{'name': wiki.MODEL, 'digest': 'test-only'}]}
        if path == '/api/show':
            return {'capabilities': ['completion']}
        if path == '/api/ps':
            return {'models': []}
        return {'done': True, 'done_reason': 'stop', 'message': {'content': json.dumps(self.draft)}}

    def test_changed_original_rejected_before_model_call(self):
        (self.root / self.source['path']).write_text('Modified source.')
        with patch('wiki.local_api') as api:
            with self.assertRaisesRegex(ValueError, 'hash changed'):
                wiki.ingest(self.root, ['S01'])
            api.assert_not_called()

    def test_passage_labels_preserve_text_and_line_locations(self):
        original = '# Title\n\n1. Change the artifact\nAdd a criterion.\n\n2. Run it\nCheck the result.\n'
        passages = wiki.evidence_passages(original)
        self.assertEqual(passages['P002']['text'], '1. Change the artifact\nAdd a criterion.')
        self.assertEqual(passages['P002']['start_line'], 3)
        for passage in passages.values():
            lines = original.splitlines()[passage['start_line'] - 1:passage['end_line']]
            self.assertEqual('\n'.join(lines), passage['text'])

    def test_source_outside_raw_rejected(self):
        source = dict(self.source, path='data/source-catalog.json')
        with self.assertRaisesRegex(ValueError, 'within vault/raw'):
            wiki.source_text(self.root, source)

    def test_invented_passage_id_rejected(self):
        bad = copy.deepcopy(self.draft)
        bad['points'][0]['evidence_id'] = 'P999'
        with self.assertRaisesRegex(ValueError, 'does not exist'):
            wiki.validate_draft(bad, self.original)

    def test_repeat_ingestion_has_one_page_and_archives_old_draft(self):
        with patch('wiki.local_api', side_effect=self.api):
            wiki.ingest(self.root, ['S01'])
            wiki.ingest(self.root, ['S01'])
        self.assertEqual(len(list((self.root / 'vault/wiki').glob('*.md'))), 1)
        self.assertEqual(len(list((self.root / 'evidence/ingestion').glob('*/S01-previous-page.md'))), 1)
        self.assertEqual((self.root / self.source['path']).read_text(), self.original)

    def test_reviewed_page_requires_explicit_replacement(self):
        target = wiki.page_path(self.root, self.plan, 'S01')
        wiki.atomic_write(target, '---\nreview_status: reviewed\n---\nReviewed content.')
        with patch('wiki.local_api') as api:
            with self.assertRaisesRegex(ValueError, 'is reviewed'):
                wiki.ingest(self.root, ['S01'])
            api.assert_not_called()

    def test_failed_generation_preserves_existing_page_and_records_failure(self):
        target = wiki.page_path(self.root, self.plan, 'S01')
        wiki.atomic_write(target, 'Existing draft.')
        self.draft['points'][0]['evidence_id'] = 'P999'
        with patch('wiki.local_api', side_effect=self.api):
            with self.assertRaisesRegex(ValueError, 'does not exist'):
                wiki.ingest(self.root, ['S01'])
        self.assertEqual(target.read_text(), 'Existing draft.')
        record = next((self.root / 'evidence/ingestion').glob('*/run.json'))
        self.assertEqual(wiki.read_json(record)['status'], 'failed')
        self.assertTrue((record.parent / 'S01-response.json').is_file())

    def test_truncated_response_rejected(self):
        def truncated(method, path, *args, **kwargs):
            result = self.api(method, path, *args)
            if path == '/api/chat':
                result['done_reason'] = 'length'
            return result
        with patch('wiki.local_api', side_effect=truncated):
            with self.assertRaisesRegex(ValueError, 'incomplete'):
                wiki.ingest(self.root, ['S01'])
        self.assertFalse(wiki.page_path(self.root, self.plan, 'S01').exists())


if __name__ == '__main__':
    unittest.main()

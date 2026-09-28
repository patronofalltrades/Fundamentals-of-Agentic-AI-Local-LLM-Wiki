#!/usr/bin/env python3
"""Local study wiki CLI for ingestion, search, cited answers, and chat."""
import argparse
from datetime import datetime, timezone
import hashlib
import http.client
import json
import os
from pathlib import Path
import re
import sys
import sqlite3
import time
import uuid

ROOT = Path(__file__).resolve().parent
MODEL = 'gemma4:e2b-mlx'
OPTIONS = {'temperature': 0, 'seed': 42, 'num_ctx': 8192, 'num_predict': 1200}
ASK_OPTIONS = {'temperature': 0, 'seed': 42, 'num_ctx': 8192, 'num_predict': 900}
CHAT_OPTIONS = {'temperature': 0.3, 'seed': 42, 'num_ctx': 8192, 'num_predict': 700}
SCHEMA = {
    'type': 'object', 'additionalProperties': False,
    'properties': {
        'summary': {'type': 'string'},
        'points': {'type': 'array', 'minItems': 3, 'maxItems': 7, 'items': {
            'type': 'object', 'additionalProperties': False,
            'properties': {'text': {'type': 'string'}, 'evidence_id': {'type': 'string'}},
            'required': ['text', 'evidence_id']}},
        'limitations': {'type': 'array', 'minItems': 1, 'maxItems': 3,
                        'items': {'type': 'string'}}},
    'required': ['summary', 'points', 'limitations']}


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write_json(path, data):
    atomic_write(path, json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        temporary.write_text(text, encoding='utf-8')
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def local_api(method, path, payload=None, timeout=180):
    # Literal loopback address, no proxy, no redirect handling, no cloud fallback.
    connection = http.client.HTTPConnection('127.0.0.1', 11434, timeout=timeout)
    try:
        body = json.dumps(payload).encode() if payload is not None else None
        connection.request(method, path, body, {'Content-Type': 'application/json'})
        response = connection.getresponse()
        data = response.read()
        if response.status != 200:
            raise ValueError('Local Ollama returned HTTP %s: %s' %
                             (response.status, data.decode(errors='replace')[:500]))
        result = json.loads(data)
        if 'error' in result:
            raise ValueError('Local Ollama: ' + str(result['error']))
        return result
    except (OSError, http.client.HTTPException) as exc:
        raise ValueError('Cannot reach local Ollama at 127.0.0.1:11434. '
                         'Start Ollama and retry. Detail: ' + str(exc)) from exc
    finally:
        connection.close()


def load_sources(root):
    catalog = read_json(root / 'data/source-catalog.json')
    return {s['id']: s for s in catalog['sources']}


def source_text(root, source):
    path = (root / source['path']).resolve()
    raw = (root / 'vault/raw').resolve()
    if raw not in path.parents or path.suffix != '.md':
        raise ValueError('Source must be a Markdown file within vault/raw/.')
    content = path.read_bytes()
    if hashlib.sha256(content).hexdigest() != source['sha256']:
        raise ValueError('Source hash changed for %s. Review and freeze the corpus again.' % source['id'])
    return content.decode('utf-8')


def page_path(root, plan, sid):
    title = plan[sid]['title']
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9 -]{1,79}', title):
        raise ValueError('Unsafe wiki title in plan.')
    return root / 'vault/wiki' / (title + '.md')


def evidence_passages(original):
    """Label contiguous source paragraphs without rewriting their text."""
    passages = {}
    for index, match in enumerate(re.finditer(r'\S[^\n]*(?:\n(?!\s*\n)[^\n]+)*', original), 1):
        quote = match.group(0)
        start = original[:match.start()].count('\n') + 1
        passages['P%03d' % index] = {'text': quote, 'start_line': start,
                                    'end_line': start + quote.count('\n')}
    return passages


def validate_draft(draft, original):
    if not isinstance(draft, dict) or set(draft) != {'summary', 'points', 'limitations'}:
        raise ValueError('Draft has unexpected fields.')
    def plain(value):
        if not isinstance(value, str) or not value.strip() or len(value) > 2000:
            raise ValueError('Draft text is missing or too long.')
        if any(mark in value for mark in ('\n', '\r', '[[', ']]', '<', '>', '](', '#')):
            raise ValueError('Draft prose must be plain text without markup or links.')
    plain(draft['summary'])
    if not isinstance(draft['points'], list) or not 3 <= len(draft['points']) <= 7:
        raise ValueError('Draft must contain 3-7 points.')
    passages = evidence_passages(original)
    for point in draft['points']:
        if not isinstance(point, dict) or set(point) != {'text', 'evidence_id'}:
            raise ValueError('Each point needs text and an evidence ID.')
        plain(point['text'])
        evidence_id = point['evidence_id']
        if not isinstance(evidence_id, str) or evidence_id not in passages:
            raise ValueError('Evidence ID does not exist in original passages: ' + str(evidence_id))
        point['evidence'] = passages[evidence_id]['text']
    if not isinstance(draft['limitations'], list) or not 1 <= len(draft['limitations']) <= 3:
        raise ValueError('Draft must contain 1-3 limitations.')
    for limit in draft['limitations']:
        plain(limit)
    return draft


def render_page(source, title, draft, original, run_id):
    source_link = '[[raw/%s|%s]]' % (Path(source['path']).stem, source['title'])
    lines = ['---', 'source_id: ' + source['id'], 'source_sha256: ' + source['sha256'],
             'model: ' + MODEL, 'run_id: ' + run_id, 'review_status: draft', '---', '',
             '# ' + title, '', '> Draft from local Gemma. Review against the original before use.', '',
             '## Summary', '', draft['summary'], '', '## Key points', '']
    for point in draft['points']:
        start = original[:original.index(point['evidence'])].count('\n') + 1
        end = start + point['evidence'].count('\n')
        lines.append('- %s (Original lines %s–%s.)' % (point['text'], start, end))
    lines += ['', '## Limits', ''] + ['- ' + value for value in draft['limitations']]
    lines += ['', '## Original source', '', source_link,
              '', 'The original preserves the upstream author and URL. Line references use the unchanged file, including its metadata.',
              '', '## Related pages', '', '<!-- related:start -->', '<!-- related:end -->', '']
    return '\n'.join(lines)


def refresh_navigation(root, sources, plan):
    available = {sid: page_path(root, plan, sid) for sid in plan
                 if page_path(root, plan, sid).is_file()}
    for sid, path in available.items():
        links = ['- [[wiki/%s|%s]] — %s' % (plan[other]['title'], plan[other]['title'], reason)
                 for other, reason in plan[sid]['related'].items() if other in available]
        replacement = '<!-- related:start -->\n' + '\n'.join(links) + '\n<!-- related:end -->'
        content, count = re.subn(r'<!-- related:start -->.*?<!-- related:end -->',
                                lambda _: replacement, path.read_text(), flags=re.S)
        if count != 1:
            raise ValueError('Missing related-page markers in ' + path.name)
        atomic_write(path, content)
    lines = ['# Agentic AI Assignment Wiki', '',
             'Use these notes to recall agent patterns, learn from evaluations, and explain reliability controls.',
             '', '## Wiki pages', '']
    for sid, path in available.items():
        reviewed = '\nreview_status: reviewed\n' in path.read_text()
        lines.append('- [[wiki/%s|%s]] — %s' %
                     (plan[sid]['title'], plan[sid]['title'], 'Reviewed' if reviewed else 'Draft; review pending'))
    if not available:
        lines.append('No wiki pages yet.')
    lines += ['', '## Original notes', '']
    lines += ['- [[raw/%s|%s]]' % (Path(s['path']).stem, s['title']) for s in sources.values()]
    lines += ['', '## How to use this vault', '',
              'Start with a wiki page. Follow its original-source link to check a claim. Related-page links connect the three subjects.', '',
              'Keep these study notes unchanged after review. Each note credits the post that inspired it.', '',
              'This vault is separate from Hanif\'s Brain. Code, quizzes, evaluation answers, and run logs stay outside it.', '']
    atomic_write(root / 'vault/index.md', '\n'.join(lines))


def ingest(root, ids, replace_reviewed=False, timeout=180):
    sources = load_sources(root)
    plan = read_json(root / 'data/wiki-plan.json')
    template = (root / 'prompts/ingest.txt').read_text()
    jobs = []
    # Check every requested source before any model call or page mutation.
    for sid in dict.fromkeys(ids):
        if sid not in sources or sid not in plan:
            raise ValueError('Unknown source ID: ' + sid)
        source = sources[sid]
        original = source_text(root, source)
        target = page_path(root, plan, sid)
        if target.exists() and '\nreview_status: reviewed\n' in target.read_text() and not replace_reviewed:
            raise ValueError(sid + ' is reviewed. Use --replace-reviewed to archive and replace it with a new draft.')
        passages = evidence_passages(original)
        labeled = '\n\n'.join('[%s; lines %s-%s]\n%s' %
                              (pid, p['start_line'], p['end_line'], p['text'])
                              for pid, p in passages.items())
        messages = [{'role': 'system', 'content': template}, {'role': 'user', 'content':
            'Source ID: %s\nWiki subject: %s\nOriginal passages:\n%s' % (sid, plan[sid]['title'], labeled)}]
        # Conservative byte bound, plus room for template overhead and generated tokens.
        if sum(len(m['content'].encode()) for m in messages) + OPTIONS['num_predict'] + 512 > OPTIONS['num_ctx']:
            raise ValueError(sid + ' exceeds the input budget. Add explicit chunking before ingesting larger notes.')
        jobs.append((sid, source, original, target, messages))
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]
    run_dir = root / 'evidence/ingestion' / run_id
    run_dir.mkdir(parents=True)
    record = {'run_id': run_id, 'mode': 'ingest', 'endpoint': 'http://127.0.0.1:11434',
              'model': MODEL, 'options': OPTIONS, 'evidence_method': 'paragraph_ids_v1',
              'offline_proof': os.environ.get('WIKI_OFFLINE_PROOF') == '1',
              'sources': [], 'status': 'running'}
    start = time.monotonic()
    try:
        installed = local_api('GET', '/api/tags', timeout=timeout)['models']
        model = next((m for m in installed if m.get('name') == MODEL or m.get('model') == MODEL), None)
        if model is None or model.get('remote_model') or model.get('remote_host'):
            raise ValueError('Required local model is unavailable: ' + MODEL)
        details = local_api('POST', '/api/show', {'model': MODEL}, timeout)
        if details.get('remote_model') or details.get('remote_host'):
            raise ValueError('Cloud-backed model tags are not allowed.')
        record['installed_model'] = model
        write_json(run_dir / 'model-info.json', details)
        for sid, source, original, target, messages in jobs:
            item = {'id': sid, 'source_sha256': source['sha256'], 'status': 'running'}
            record['sources'].append(item)
            if target.exists():
                atomic_write(run_dir / (sid + '-previous-page.md'), target.read_text())
            schema = json.loads(json.dumps(SCHEMA))
            schema['properties']['points']['items']['properties']['evidence_id']['enum'] = list(evidence_passages(original))
            payload = {'model': MODEL, 'messages': messages, 'format': schema,
                       'stream': False, 'think': False, 'options': OPTIONS, 'keep_alive': '5m'}
            write_json(run_dir / (sid + '-request.json'), payload)
            print('Ingesting %s with local %s...' % (sid, MODEL), flush=True)
            called = time.monotonic()
            response = local_api('POST', '/api/chat', payload, timeout)
            item['wall_seconds'] = round(time.monotonic() - called, 3)
            write_json(run_dir / (sid + '-response.json'), response)
            item.update(prompt_tokens=response.get('prompt_eval_count'),
                        output_tokens=response.get('eval_count'))
            if not response.get('done') or response.get('done_reason') == 'length':
                raise ValueError(sid + ': incomplete model output; saved response, kept previous page.')
            draft = validate_draft(json.loads(response['message']['content']), original)
            write_json(run_dir / (sid + '-resolved-draft.json'), draft)
            source_text(root, source)  # Detect edits during generation.
            page = render_page(source, plan[sid]['title'], draft, original, run_id)
            atomic_write(run_dir / (sid + '-draft.md'), page)
            atomic_write(target, page)
            refresh_navigation(root, sources, plan)
            item.update(status='draft_written', page=str(target.relative_to(root)))
            try:
                item['loaded_model_snapshot'] = local_api('GET', '/api/ps', timeout=10)
            except ValueError as exc:
                item['memory_snapshot_error'] = str(exc)
            print('Saved %s (%.1fs). Review pending.' % (target.relative_to(root), item['wall_seconds']), flush=True)
        record['status'] = 'completed'
    except Exception as exc:
        record['status'] = 'failed'
        record['error'] = str(exc)
        if record['sources'] and record['sources'][-1]['status'] == 'running':
            record['sources'][-1]['status'] = 'failed'
        raise
    finally:
        record['wall_seconds'] = round(time.monotonic() - start, 3)
        write_json(run_dir / 'run.json', record)
        print('Run record: ' + str(run_dir.relative_to(root) / 'run.json'), flush=True)


def search(root, query, limit=5, rebuild=False):
    import retrieval
    sources = load_sources(root)
    originals = {sid: source_text(root, source) for sid, source in sources.items()}
    start = time.monotonic()
    result = retrieval.search(root, sources, originals, query, limit, rebuild)
    result['wall_seconds'] = round(time.monotonic() - start, 6)
    return result


def run_search(root, query, limit=5, rebuild=False, json_output=False):
    result = search(root, query, limit, rebuild)
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]
    record_path = root / 'evidence/search' / (run_id + '.json')
    result['run_id'] = run_id
    result['record_path'] = str(record_path.relative_to(root))
    result['offline_proof'] = os.environ.get('WIKI_OFFLINE_PROOF') == '1'
    write_json(record_path, result)
    if json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print('Search: original passages only. No model generation.')
        if not result['hits']:
            print('No matching passages. Try different source terms.')
        for i, hit in enumerate(result['hits'], 1):
            print('\n%s. [%s] %s' % (i, hit['citation_id'], hit['title']))
            print('%s:%s-%s | %s' % (hit['source_path'], hit['start_line'], hit['end_line'], hit['section']))
            print(hit['text'])
        print('\nSearch record: ' + result['record_path'])


def ask_schema(hits):
    citation_ids = [hit['citation_id'] for hit in hits]
    if not citation_ids:
        raise ValueError('Cannot build answer schema without retrieved passages.')
    return {
        'type': 'object', 'additionalProperties': False,
        'properties': {
            'insufficient_evidence': {'type': 'boolean'},
            'answer': {'type': 'string'},
            'citations': {'type': 'array', 'maxItems': 5, 'items': {
                'type': 'string', 'enum': citation_ids}}},
        'required': ['insufficient_evidence', 'answer', 'citations']}


def validate_answer(answer, hits):
    if not isinstance(answer, dict) or set(answer) != {'insufficient_evidence', 'answer', 'citations'}:
        raise ValueError('Answer has unexpected fields.')
    if not isinstance(answer['insufficient_evidence'], bool):
        raise ValueError('insufficient_evidence must be true or false.')
    text = answer['answer']
    if not isinstance(text, str) or not text.strip() or len(text) > 3000:
        raise ValueError('Answer text is missing or too long.')
    if answer['insufficient_evidence']:
        if answer['citations']:
            raise ValueError('Insufficient-evidence answers must not include citations.')
        if 'insufficient_evidence' in text.lower() or len(text.strip()) < 40:
            raise ValueError('An insufficient-evidence answer must explain the missing information in plain language.')
        return answer
    citations = answer['citations']
    if not isinstance(citations, list) or not 1 <= len(citations) <= 5:
        raise ValueError('A supported answer must include 1-5 citations.')
    retrieved = {hit['citation_id'] for hit in hits}
    if len(citations) != len(set(citations)) or not set(citations) <= retrieved:
        raise ValueError('Answer cites a passage that was not retrieved.')
    return answer


def normalize_abstention(answer):
    """Normalize a flagged abstention; retain the raw model response separately."""
    if not isinstance(answer, dict) or answer.get('insufficient_evidence') is not True:
        return answer, False, False
    normalized = dict(answer)
    citations_cleared = isinstance(normalized.get('citations'), list) and bool(normalized['citations'])
    if citations_cleared:
        normalized['citations'] = []
    text = normalized.get('answer')
    text_changed = isinstance(text, str) and ('insufficient_evidence' in text.lower() or len(text.strip()) < 40)
    if text_changed:
        normalized['answer'] = ('The retrieved passages do not provide the specific information '
                                'requested, so I cannot give an evidence-based answer.')
    return normalized, text_changed, citations_cleared


def ask(root, question, limit=3, rebuild=False, timeout=180):
    if not isinstance(question, str) or not question.strip() or len(question) > 3000:
        raise ValueError('Ask a question with 1-3000 characters.')
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]
    run_dir = root / 'evidence/ask' / run_id
    run_dir.mkdir(parents=True)
    record = {'run_id': run_id, 'mode': 'ask', 'question': question, 'model': MODEL,
              'endpoint': 'http://127.0.0.1:11434', 'options': ASK_OPTIONS,
              'history_used': False, 'generation_used': False,
              'offline_proof': os.environ.get('WIKI_OFFLINE_PROOF') == '1',
              'status': 'running'}
    started = time.monotonic()
    try:
        retrieved = search(root, question, limit, rebuild)
        record['retrieval'] = retrieved
        write_json(run_dir / 'retrieval.json', retrieved)
        if not retrieved['hits']:
            answer = {'insufficient_evidence': True,
                      'answer': 'Insufficient evidence: no matching passages were found in the original notes.',
                      'citations': []}
            result = {'answer': 'Insufficient evidence: no matching passages were found in the original notes.',
                      'insufficient_evidence': True, 'citation_ids': [], 'retrieval': retrieved,
                      'run_id': run_id}
            record['answer'] = result
            record['status'] = 'completed_without_generation'
            return result
        evidence = '\n\n'.join('[%s] %s (%s:%s-%s, section %s)\n%s' %
            (hit['citation_id'], hit['title'], hit['source_path'], hit['start_line'],
             hit['end_line'], hit['section'], hit['text']) for hit in retrieved['hits'])
        template = (root / 'prompts/ask.txt').read_text()
        messages = [{'role': 'system', 'content': template}, {'role': 'user', 'content':
            'New question: %s\n\nRetrieved original passages:\n%s' % (question, evidence)}]
        if sum(len(message['content'].encode()) for message in messages) + ASK_OPTIONS['num_predict'] + 512 > ASK_OPTIONS['num_ctx']:
            raise ValueError('Retrieved evidence exceeds the ask context budget. Lower --limit or use shorter query terms.')
        installed = local_api('GET', '/api/tags', timeout=timeout)['models']
        model = next((m for m in installed if m.get('name') == MODEL or m.get('model') == MODEL), None)
        if model is None or model.get('remote_model') or model.get('remote_host'):
            raise ValueError('Required local model is unavailable: ' + MODEL)
        details = local_api('POST', '/api/show', {'model': MODEL}, timeout)
        if details.get('remote_model') or details.get('remote_host'):
            raise ValueError('Cloud-backed model tags are not allowed.')
        record['installed_model'] = model
        write_json(run_dir / 'model-info.json', details)
        payload = {'model': MODEL, 'messages': messages, 'format': ask_schema(retrieved['hits']),
                   'stream': False, 'think': False, 'options': ASK_OPTIONS, 'keep_alive': '5m'}
        write_json(run_dir / 'request.json', payload)
        print('Answering with local %s (new question, no chat history)...' % MODEL, flush=True)
        called = time.monotonic()
        record['generation_attempted'] = True
        response = local_api('POST', '/api/chat', payload, timeout)
        record['model_call_seconds'] = round(time.monotonic() - called, 3)
        record['model_response'] = response
        write_json(run_dir / 'response.json', response)
        record['generation_used'] = True
        record['prompt_tokens'] = response.get('prompt_eval_count')
        record['output_tokens'] = response.get('eval_count')
        if not response.get('done') or response.get('done_reason') == 'length':
            raise ValueError('Gemma returned an incomplete answer. See the saved model response.')
        answer, text_changed, citations_cleared = normalize_abstention(json.loads(response['message']['content']))
        record['abstention_text_normalized_by_harness'] = text_changed
        record['abstention_citations_cleared_by_harness'] = citations_cleared
        answer = validate_answer(answer, retrieved['hits'])
        if answer['insufficient_evidence']:
            display = answer['answer']
            citations = []
        else:
            by_id = {hit['citation_id']: hit for hit in retrieved['hits']}
            citation_details = ['[%s] %s:%s-%s' % (cid, by_id[cid]['source_path'],
                                 by_id[cid]['start_line'], by_id[cid]['end_line'])
                                for cid in answer['citations']]
            display = answer['answer'] + ' Sources: ' + '; '.join(citation_details)
            citations = answer['citations']
        result = {'answer': display, 'insufficient_evidence': answer['insufficient_evidence'],
                  'citation_ids': citations, 'retrieval': retrieved, 'run_id': run_id}
        record['answer'] = result
        record['status'] = 'completed'
        return result
    except Exception as exc:
        record['status'] = 'failed'
        record['error'] = str(exc)
        raise
    finally:
        record['wall_seconds'] = round(time.monotonic() - started, 3)
        write_json(run_dir / 'run.json', record)
        print('Ask record: ' + str(run_dir.relative_to(root) / 'run.json'), flush=True)


def run_ask(root, question, limit=3, rebuild=False, json_output=False, timeout=180):
    result = ask(root, question, limit, rebuild, timeout)
    if json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print('\n' + result['answer'])
        if not result['insufficient_evidence']:
            for citation in result['citation_ids']:
                hit = next(h for h in result['retrieval']['hits'] if h['citation_id'] == citation)
                print('Citation: [%s] %s:%s-%s | %s' % (citation, hit['source_path'],
                      hit['start_line'], hit['end_line'], hit['section']))
        print('\nRun record: evidence/ask/%s/run.json' % result['run_id'])


def chat_needs_retrieval(message):
    text = message.lower()
    cues = (r'\b(?:my|our|the|these)\s+(?:original\s+)?(?:notes|wiki|vault)\b',
            r'\baccording to\b', r'\b(?:cite|cited|citation|citations|source passage)\b',
            r'\b(?:agent architecture patterns|product.memory note|production.ready note)\b')
    return any(re.search(cue, text) for cue in cues)


def chat_schema(hits, allow_suggestion=True):
    if not hits:
        raise ValueError('A note-grounded chat schema needs retrieved passages.')
    citations = {'type': 'array', 'maxItems': 5,
                 'items': {'type': 'string', 'enum': [hit['citation_id'] for hit in hits]}}
    return {'type': 'object', 'additionalProperties': False,
            'properties': {
                'reply': {'type': 'string'},
                'suggestions': {'type': 'array', 'maxItems': 1 if allow_suggestion else 0,
                                'items': {'type': 'string'}},
                'uses_note_evidence': {'type': 'boolean'},
                'citations': citations},
            'required': ['reply', 'suggestions', 'uses_note_evidence', 'citations']}


def validate_chat_reply(reply, hits):
    if not isinstance(reply, dict) or set(reply) != {'reply', 'suggestions', 'uses_note_evidence', 'citations'}:
        raise ValueError('Chat reply has unexpected fields.')
    if not isinstance(reply['reply'], str) or not reply['reply'].strip() or len(reply['reply']) > 3000:
        raise ValueError('Chat reply text is missing or too long.')
    suggestions = reply['suggestions']
    if (not isinstance(suggestions, list) or len(suggestions) > 1 or
            any(not isinstance(item, str) or not item.strip() or len(item) > 500 for item in suggestions)):
        raise ValueError('Chat suggestions must be a list of up to one short string.')
    citations = reply['citations']
    retrieved = {hit['citation_id'] for hit in hits}
    if (not isinstance(reply['uses_note_evidence'], bool) or not isinstance(citations, list) or
            any(not isinstance(item, str) for item in citations) or
            len(citations) != len(set(citations)) or len(citations) > 5 or not set(citations) <= retrieved):
        raise ValueError('Chat citations must be unique IDs from this turn\'s retrieved passages.')
    if reply['uses_note_evidence'] != bool(citations):
        raise ValueError('Note-based chat replies need citations; other replies must not cite notes.')
    return reply


def chat_turn(root, message, history, session_dir, turn_index, timeout=180):
    if not isinstance(message, str) or not message.strip() or len(message) > 3000:
        raise ValueError('Chat message must contain 1-3000 characters.')
    turn_dir = session_dir / ('turn-%02d' % turn_index)
    turn_dir.mkdir(parents=True, exist_ok=True)
    previous_note_answer = bool(history and 'Sources: [S' in history[-1]['content'])
    note_follow_up = previous_note_answer and bool(re.search(
        r'\b(?:make that|shorten that|summarize that|rephrase that|expand on that|explain that)\b',
        message.lower()))
    shortening = bool(re.search(r'\b(?:shorter|shorten|brief|condense)\b', message.lower()))
    needs_notes = chat_needs_retrieval(message) or note_follow_up
    search_query = (history[-2]['content'] + ' ' + message) if note_follow_up else message
    record = {'turn': turn_index, 'message': message, 'mode': 'chat', 'model': MODEL,
              'endpoint': 'http://127.0.0.1:11434', 'options': CHAT_OPTIONS,
              'retrieval_requested': needs_notes, 'note_follow_up': note_follow_up,
              'search_query': search_query if needs_notes else None, 'shortening_request': shortening,
              'retrieval_used': False,
              'generation_used': False,
              'offline_proof': os.environ.get('WIKI_OFFLINE_PROOF') == '1', 'status': 'running'}
    started = time.monotonic()
    try:
        hits = []
        if needs_notes:
            try:
                retrieved = search(root, search_query, limit=3)
            except ValueError as exc:
                if 'at least one search term' not in str(exc):
                    raise
                retrieved = {'query': message, 'hits': [], 'reason': str(exc), 'generation_used': False}
            record['retrieval'] = retrieved
            write_json(turn_dir / 'retrieval.json', retrieved)
            hits = retrieved['hits']
            record['retrieval_used'] = True
            if not hits:
                result = {'reply': 'Please name a topic to search in the original notes.',
                          'suggestions': [], 'citation_ids': [], 'retrieval_used': True,
                          'generation_used': False, 'history_turns_used': 0,
                          'record_path': str((turn_dir / 'run.json').relative_to(root))}
                record['result'] = result
                record['status'] = 'completed_without_generation'
                history.extend([{'role': 'user', 'content': message},
                                {'role': 'assistant', 'content': result['reply']}])
                return result
        prompt_name = 'chat.txt' if hits else 'chat-casual.txt'
        template = (root / 'prompts' / prompt_name).read_text(encoding='utf-8')
        evidence = '\n\n'.join('[%s] %s (%s:%s-%s)\n%s' %
            (hit['citation_id'], hit['title'], hit['source_path'], hit['start_line'],
             hit['end_line'], hit['text']) for hit in hits)
        current = message if not hits else ('User request: %s\n\nRetrieved original passages:\n%s' % (message, evidence))
        recent = list(history[-6:])
        messages = [{'role': 'system', 'content': template}] + recent + [{'role': 'user', 'content': current}]
        def over_budget(items):
            return sum(len(item['content'].encode()) for item in items) + CHAT_OPTIONS['num_predict'] + 512 > CHAT_OPTIONS['num_ctx']
        while recent and over_budget(messages):
            recent = recent[2:]
            messages = [{'role': 'system', 'content': template}] + recent + [{'role': 'user', 'content': current}]
        if over_budget(messages):
            raise ValueError('Chat prompt exceeds the context budget. Use a shorter request.')
        record['history_turns_used'] = len(recent) // 2
        installed = local_api('GET', '/api/tags', timeout=timeout)['models']
        model = next((item for item in installed if item.get('name') == MODEL or item.get('model') == MODEL), None)
        if model is None or model.get('remote_model') or model.get('remote_host'):
            raise ValueError('Required local model is unavailable: ' + MODEL)
        details = local_api('POST', '/api/show', {'model': MODEL}, timeout)
        if details.get('remote_model') or details.get('remote_host'):
            raise ValueError('Cloud-backed model tags are not allowed.')
        record['installed_model'] = model
        write_json(turn_dir / 'model-info.json', details)
        payload = {'model': MODEL, 'messages': messages, 'stream': False, 'think': False,
                   'options': CHAT_OPTIONS, 'keep_alive': '5m'}
        if hits:
            payload['format'] = chat_schema(hits, allow_suggestion=not shortening)
        write_json(turn_dir / 'request.json', payload)
        record['generation_attempted'] = True
        called = time.monotonic()
        response = local_api('POST', '/api/chat', payload, timeout)
        record['model_call_seconds'] = round(time.monotonic() - called, 3)
        record['generation_used'] = True
        record['model_response'] = response
        write_json(turn_dir / 'response.json', response)
        if not response.get('done') or response.get('done_reason') == 'length':
            raise ValueError('Gemma returned an incomplete chat reply. See the saved response.')
        if hits:
            reply = validate_chat_reply(json.loads(response['message']['content']), hits)
            citation_details = []
            by_id = {hit['citation_id']: hit for hit in hits}
            for cid in reply['citations']:
                hit = by_id[cid]
                citation_details.append('[%s] %s:%s-%s' %
                                        (cid, hit['source_path'], hit['start_line'], hit['end_line']))
            displayed = reply['reply']
            if reply['suggestions']:
                displayed += '\n' + '\n'.join('Suggestion: ' + item for item in reply['suggestions'])
            if citation_details:
                displayed += '\nSources: ' + '; '.join(citation_details)
            suggestions = reply['suggestions']
            citations = reply['citations']
        else:
            displayed = response['message']['content'].strip()
            if not displayed or len(displayed) > 3000:
                raise ValueError('Chat reply text is missing or too long.')
            suggestions = [line.split('Suggestion:', 1)[1].strip() for line in displayed.splitlines()
                           if line.startswith('Suggestion:')]
            citations = []
        result = {'reply': displayed, 'suggestions': suggestions,
                  'citation_ids': citations, 'retrieval_used': bool(hits),
                  'generation_used': True, 'history_turns_used': len(recent) // 2,
                  'record_path': str((turn_dir / 'run.json').relative_to(root))}
        history.extend([{'role': 'user', 'content': message},
                        {'role': 'assistant', 'content': displayed}])
        record['result'] = result
        record['status'] = 'completed'
        return result
    except Exception as exc:
        record['status'] = 'failed'
        record['error'] = str(exc)
        raise
    finally:
        record['wall_seconds'] = round(time.monotonic() - started, 3)
        write_json(turn_dir / 'run.json', record)


def run_chat(root, timeout=180):
    session_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]
    session_dir = root / 'evidence/chat' / session_id
    session_dir.mkdir(parents=True)
    history = []
    session = {'session_id': session_id, 'mode': 'chat', 'model': MODEL,
               'offline_proof': os.environ.get('WIKI_OFFLINE_PROOF') == '1',
               'turns': [], 'status': 'running'}
    print('Local Gemma chat (%s). I can brainstorm and draft. Ask about your notes for cited passages. Type /exit to stop.' % MODEL, flush=True)
    try:
        while True:
            if sys.stdin.isatty():
                print('chat> ', end='', flush=True)
            line = sys.stdin.readline()
            if not line:
                break
            message = line.strip()
            if message in ('/exit', '/quit'):
                break
            if not message:
                continue
            turn_index = len(session['turns']) + 1
            result = chat_turn(root, message, history, session_dir, turn_index, timeout)
            session['turns'].append({'message': message, 'record_path': result['record_path']})
            print('\n' + result['reply'] + '\n', flush=True)
        session['status'] = 'completed'
    except Exception as exc:
        session['status'] = 'failed'
        session['error'] = str(exc)
        raise
    finally:
        write_json(session_dir / 'session.json', session)
        print('Chat record: ' + str((session_dir / 'session.json').relative_to(root)), flush=True)


def main():
    parser = argparse.ArgumentParser(description='Personal wiki with local Gemma. Commands: ingest, search, ask, chat, help.')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('help', help='Show available commands.')
    command = sub.add_parser('ingest', help='Draft wiki pages from hash-verified originals using local Gemma.')
    select = command.add_mutually_exclusive_group(required=True)
    select.add_argument('--source', nargs='+', metavar='ID', help='Catalog IDs, e.g. S01 S02.')
    select.add_argument('--all', action='store_true', help='Ingest all catalog sources.')
    command.add_argument('--replace-reviewed', action='store_true', help='Archive reviewed pages and replace with new drafts.')
    command.add_argument('--timeout', type=int, default=180, help='Local API timeout in seconds (default: 180).')
    command = sub.add_parser('chat', help='Brainstorm and draft with session context; retrieve notes when relevant.')
    command.add_argument('--timeout', type=int, default=180, help='Local API timeout in seconds (default: 180).')
    command = sub.add_parser('search', help='Find original passages locally without Gemma.')
    command.add_argument('query', help='Question or keywords in quotes.')
    command.add_argument('--limit', type=int, default=5, help='Number of passages, 1-20 (default: 5).')
    command.add_argument('--rebuild', action='store_true', help='Rebuild the local index from verified originals.')
    command.add_argument('--json', action='store_true', dest='json_output', help='Show full machine-readable results.')
    command = sub.add_parser('ask', help='Answer one new question from original notes with local Gemma and checked citations.')
    command.add_argument('question', help='A new factual question. Prior chat is never included.')
    command.add_argument('--limit', type=int, default=3, help='Retrieved passages, 1-20 (default: 3).')
    command.add_argument('--rebuild', action='store_true', help='Rebuild the local retrieval index first.')
    command.add_argument('--json', action='store_true', dest='json_output', help='Show full machine-readable results.')
    command.add_argument('--timeout', type=int, default=180, help='Local API timeout in seconds (default: 180).')
    args = parser.parse_args()
    if args.command == 'help':
        parser.print_help()
        return 0
    try:
        if args.command == 'search':
            run_search(ROOT, args.query, args.limit, args.rebuild, args.json_output)
            return 0
        if args.command == 'ask':
            if args.timeout <= 0:
                raise ValueError('Timeout must be positive.')
            run_ask(ROOT, args.question, args.limit, args.rebuild, args.json_output, args.timeout)
            return 0
        if args.command == 'chat':
            if args.timeout <= 0:
                raise ValueError('Timeout must be positive.')
            run_chat(ROOT, args.timeout)
            return 0
        if args.timeout <= 0:
            raise ValueError('Timeout must be positive.')
        ingest(ROOT, list(load_sources(ROOT)) if args.all else args.source, args.replace_reviewed, args.timeout)
    except (ValueError, OSError, KeyError, TypeError, sqlite3.Error) as exc:
        print('Error: ' + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())

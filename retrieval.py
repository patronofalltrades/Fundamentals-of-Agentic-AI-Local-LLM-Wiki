"""Local lexical retrieval. Receives only hash-verified catalog originals."""
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import uuid

VERSION = 'fts5-paragraphs-v3'
MAX_WORDS = 220
QUERY_EXPANSIONS = {
    'architecture': ['single', 'sequential', 'parallel', 'hierarchical', 'evaluator'],
    'resources': ['budgets', 'tokens', 'memory'],
    'unlimited': ['unbounded', 'budgets'],
}
STOPWORDS = set('a an and are as at be been but by can could do does for from had has have how i if in into is it its me my of on or our should so than that the their them then these they this those to using was we were what when where which who why will with would you your according note notes explain'.split())


def chunks(source, original):
    lines = original.splitlines()
    start = 0
    if lines and lines[0].strip() == '---':
        start = next((i + 1 for i in range(1, len(lines)) if lines[i].strip() == '---'), len(lines))
    sections = []
    heading = 'Introduction'
    paragraphs = []
    paragraph_start = None
    for i in range(start, len(lines) + 1):
        line = lines[i] if i < len(lines) else ''
        is_heading = re.match(r'^#{1,6}\s+(.+)', line)
        if not line.strip() or is_heading:
            if paragraph_start is not None:
                text = '\n'.join(lines[paragraph_start:i])
                # Navigation and URL-only blocks are not evidence passages.
                if not (text.startswith('**Linked topics:**') or re.fullmatch(r'\[[^\]]+\]\(https?://[^)]+\)', text)):
                    paragraphs.append((paragraph_start + 1, i))
                paragraph_start = None
            if is_heading:
                if paragraphs:
                    sections.append((heading, paragraphs))
                paragraphs = []
                heading = is_heading.group(1)
        elif paragraph_start is None:
            paragraph_start = i
    if paragraphs:
        sections.append((heading, paragraphs))
    result = []
    for section, blocks in sections:
        group = []
        count = 0
        for block in blocks:
            words = len(' '.join(lines[block[0]-1:block[1]]).split())
            if group and count + words > MAX_WORDS:
                result.append(make_chunk(source, lines, section, group))
                # One paragraph overlap retains context at a boundary.
                last = group[-1]
                last_words = len(' '.join(lines[last[0]-1:last[1]]).split())
                group = [last] if len(group) > 1 and last_words + words <= MAX_WORDS else []
                count = last_words if group else 0
            group.append(block)
            count += words
        if group:
            result.append(make_chunk(source, lines, section, group))
    return result


def make_chunk(source, lines, section, group):
    start, end = group[0][0], group[-1][1]
    return {'citation_id': '%s-%s-L%s-L%s' % (source['id'], source['sha256'][:12], start, end),
            'source_id': source['id'], 'source_path': source['path'], 'source_sha256': source['sha256'],
            'title': source['title'], 'section': section, 'start_line': start, 'end_line': end,
            'text': '\n'.join(lines[start-1:end])}


def query_terms(query):
    if not query.strip() or len(query) > 1000:
        raise ValueError('Search query must contain 1-1000 characters.')
    words = re.findall(r'[^\W_]+', query.lower(), flags=re.UNICODE)
    terms = list(dict.fromkeys(word for word in words if word not in STOPWORDS))
    if not terms:
        raise ValueError('Enter at least one search term beyond common words.')
    return terms


def signature(sources):
    value = {'version': VERSION, 'max_words': MAX_WORDS, 'sources': [
        {k: source[k] for k in ('id', 'title', 'path', 'sha256')} for source in sources.values()]}
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def deduplicate_passages(candidates):
    def normalized(text):
        return ' '.join(re.findall(r'[^\W_]+', text.lower(), flags=re.UNICODE))
    normalized_candidates = [(hit, normalized(hit['text'])) for hit in candidates]
    kept = []
    skipped = 0
    for hit, text in normalized_candidates:
        redundant = any(other['source_id'] == hit['source_id'] and len(other_text) > len(text)
                        and len(text.split()) >= 12 and (' ' + text + ' ') in (' ' + other_text + ' ')
                        for other, other_text in normalized_candidates)
        if redundant:
            skipped += 1
        else:
            kept.append(hit)
    return kept, skipped


def build_index(path, sources, originals, fingerprint):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(uuid.uuid4().hex + '.db')
    try:
        with sqlite3.connect(str(temporary)) as db:
            db.execute('CREATE TABLE metadata (signature TEXT NOT NULL)')
            db.execute('INSERT INTO metadata VALUES (?)', (fingerprint,))
            db.execute("CREATE VIRTUAL TABLE passages USING fts5(title, section, text, payload UNINDEXED, tokenize='porter unicode61')")
            for sid, source in sources.items():
                for passage in chunks(source, originals[sid]):
                    db.execute('INSERT INTO passages VALUES (?,?,?,?)',
                               (passage['title'], passage['section'], passage['text'], json.dumps(passage)))
        # Close SQLite before replacing the prior database.
        db.close()
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def search(root, sources, originals, query, limit=5, rebuild=False):
    if not 1 <= limit <= 20:
        raise ValueError('Search limit must be between 1 and 20.')
    original_terms = query_terms(query)
    terms = list(dict.fromkeys(original_terms + [extra for term in original_terms
                                               for extra in QUERY_EXPANSIONS.get(term, [])]))
    fingerprint = signature(sources)
    path = root / 'runtime/search.db'
    current = None
    if path.exists() and not rebuild:
        try:
            with sqlite3.connect(str(path)) as db:
                current = db.execute('SELECT signature FROM metadata').fetchone()[0]
            db.close()
        except (sqlite3.Error, TypeError, IndexError):
            current = None
    rebuilt = rebuild or current != fingerprint
    if rebuilt:
        build_index(path, sources, originals, fingerprint)
    # Tokens are quoted literal terms. User text never becomes SQL or raw FTS syntax.
    expression = ' OR '.join('"' + term.replace('"', '""') + '"' for term in terms)
    with sqlite3.connect(str(path)) as db:
        rows = db.execute('SELECT payload, bm25(passages, 0.2, 0.3, 1.0) AS score FROM passages '
                          'WHERE passages MATCH ? ORDER BY score, rowid LIMIT ?',
                          (expression, min(200, limit * 10))).fetchall()
        count = db.execute('SELECT count(*) FROM passages').fetchone()[0]
    db.close()
    candidates = []
    for payload, score in rows:
        hit = json.loads(payload)
        sid = hit['source_id']
        if sid not in sources:
            raise ValueError('Cached index contains an unknown source; run search with --rebuild.')
        actual = '\n'.join(originals[sid].splitlines()[hit['start_line']-1:hit['end_line']])
        if (hit['text'] != actual or hit['source_path'] != sources[sid]['path']
                or hit['source_sha256'] != sources[sid]['sha256']):
            raise ValueError('Cached passage differs from original; run search with --rebuild.')
        hit['bm25_score'] = score
        candidates.append(hit)
    distinct, skipped = deduplicate_passages(candidates)
    hits = distinct[:limit]
    return {'query': query, 'terms': terms, 'original_terms': original_terms,
            'expanded_terms': [term for term in terms if term not in original_terms],
            'method': VERSION, 'limit': limit, 'candidate_count': len(candidates),
            'redundant_passages_skipped': skipped,
            'index_signature': fingerprint, 'index_rebuilt': rebuilt, 'indexed_passages': count,
            'source_hashes': {sid: s['sha256'] for sid, s in sources.items()},
            'generation_used': False, 'hits': hits}

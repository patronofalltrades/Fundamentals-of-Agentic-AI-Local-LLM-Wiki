"""Read frozen expectations to evaluate search. The retrieval code never reads this file."""
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import wiki


def run(label):
    expected = ROOT / 'private-archive/corpus-v2/expectations.md'
    text = expected.read_text()
    cases = []
    for section in re.split(r'(?=^## Q\d)', text, flags=re.M)[1:]:
        qid = re.match(r'## (Q\d)', section).group(1)
        query = re.search(r'^\*\*Question:\*\* (.+)', section, re.M).group(1)
        ranges = [(sid, int(start), int(end)) for sid, start, end in re.findall(
            r'\*\*Expected evidence:\*\* (S\d+), `[^`]+`, lines (\d+)–(\d+)', section)]
        result = wiki.search(ROOT, query)
        coverage = []
        for sid, start, end in ranges:
            covered = {line for hit in result['hits'] if hit['source_id'] == sid
                       for line in range(hit['start_line'], hit['end_line'] + 1)}
            coverage.append({'source_id': sid, 'start_line': start, 'end_line': end,
                             'covered': set(range(start, end+1)).issubset(covered)})
        case = {'id': qid, 'expected_coverage': coverage, 'all_expected_passages_found':
                all(x['covered'] for x in coverage) if coverage else None, 'search': result}
        cases.append(case)
        print(qid, case['all_expected_passages_found'], [(h['source_id'], h['start_line'], h['end_line']) for h in result['hits']])
    output = ROOT / 'evidence/search' / (label + '.json')
    if output.exists():
        raise SystemExit('Do not overwrite earlier evidence: ' + str(output))
    wiki.write_json(output, {'expectations_sha256': hashlib.sha256(expected.read_bytes()).hexdigest(),
                            'scope': 'Retrieval coverage only. Q4 has no expected answer passage; hits are not answer support.',
                            'cases': cases})


if __name__ == '__main__':
    run(sys.argv[1])

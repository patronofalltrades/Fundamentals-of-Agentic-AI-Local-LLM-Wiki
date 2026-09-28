"""Run the four frozen questions. Expected answers are evaluation-only and never sent to Gemma."""
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import wiki


def run(label):
    expected_file=Path(os.environ.get('WIKI_EVAL_EXPECTATIONS_PATH', ROOT/'private-archive/corpus-v2/expectations.md'))
    source_text=expected_file.read_text()
    cases=[]
    for section in source_text.split('\n## Q')[1:]:
        section = '## Q' + section
        qid = section.splitlines()[0].split()[1]
        question = next(line.split('**Question:** ',1)[1] for line in section.splitlines() if line.startswith('**Question:** '))
        behavior = next((line.split('**Expected behavior:** ',1)[1] for line in section.splitlines() if line.startswith('**Expected behavior:** ')), None)
        expected_lines = []
        for line in section.splitlines():
            if line.startswith('**Expected evidence:** '):
                parts = line.split('**Expected evidence:** ',1)[1].split(', ')
                sid = parts[0]
                range_text = parts[2].split('lines ',1)[1]
                start, end = range_text.split('–')
                expected_lines.append((sid,int(start),int(end)))
        retrieval_limit = 1 if qid == 'Q1' else 3
        selected = set(sys.argv[2:])
        if selected and qid not in selected:
            continue
        print('Running %s with limit %s'%(qid,retrieval_limit),flush=True)
        run_id = None
        try:
            result=wiki.ask(ROOT,question,limit=retrieval_limit)
            run_id=result.get('run_id')
            run_record=wiki.read_json(ROOT/'evidence/ask'/run_id/'run.json')
            retrieved={(hit['source_id'], line) for hit in result['retrieval']['hits']
                       for line in range(hit['start_line'],hit['end_line']+1)}
            coverage=[]
            for sid,start,end in expected_lines:
                lines={line for source_id,line in retrieved if source_id==sid}
                coverage.append({'source_id':sid,'start_line':start,'end_line':end,
                                 'returned':set(range(start,end+1)).issubset(lines)})
            citations=set(result['citation_ids'])
            hit_ids={hit['citation_id'] for hit in result['retrieval']['hits']}
            cited_sources={hit['source_id'] for hit in result['retrieval']['hits']
                           if hit['citation_id'] in citations}
            expected_sources={sid for sid,_,_ in expected_lines}
            case={'id':qid,'question':question,'retrieval_limit':retrieval_limit,'expected_behavior':behavior,
                  'expected_line_coverage':coverage,'all_expected_lines_retrieved':
                  (all(c['returned'] for c in coverage) if coverage else None),
                  'expected_sources_cited':sorted(expected_sources),
                  'all_expected_sources_cited':expected_sources <= cited_sources,
                  'abstained_without_citations':result['insufficient_evidence'] and not citations,
                  'abstention_text_normalized_by_harness':run_record.get('abstention_text_normalized_by_harness',False),
                  'abstention_citations_cleared_by_harness':run_record.get('abstention_citations_cleared_by_harness',False),
                  'supported_response':not result['insufficient_evidence'],
                  'all_citations_were_retrieved':citations<=hit_ids,
                  'answer':result,'review_status':'pending manual claim-by-claim check'}
        except Exception as exc:
            case={'id':qid,'question':question,'retrieval_limit':retrieval_limit,'run_id':run_id,'error':str(exc),'review_status':'failed'}
        cases.append(case)
        print(json.dumps({'id':qid,'error':case.get('error'),'all_expected_lines_retrieved':case.get('all_expected_lines_retrieved'),'all_expected_sources_cited':case.get('all_expected_sources_cited'),'abstained_without_citations':case.get('abstained_without_citations'),'abstention_text_normalized_by_harness':case.get('abstention_text_normalized_by_harness'),'abstention_citations_cleared_by_harness':case.get('abstention_citations_cleared_by_harness'),'supported_response':case.get('supported_response')},ensure_ascii=False),flush=True)
    target=ROOT/'evidence/ask'/('%s.json'%label)
    if target.exists():raise SystemExit('Refusing to overwrite '+str(target))
    wiki.write_json(target,{'expectations_sha256':hashlib.sha256(expected_file.read_bytes()).hexdigest(),
                            'scope':'Model run records and preliminary checks only. Human citation-support review remains pending.',
                            'cases':cases})
    print('Evaluation record: '+str(target.relative_to(ROOT)))


if __name__=='__main__':
    run(sys.argv[1])

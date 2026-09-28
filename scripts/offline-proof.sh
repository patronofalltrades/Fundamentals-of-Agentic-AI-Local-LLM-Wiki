#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "$0")/.." && pwd)"
run_tag="$(date -u +%Y%m%dT%H%M%SZ)-$$"
run_dir="$project_root/evidence/offline/$run_tag"
replay_dir=""
mkdir -p "$run_dir"

finish() {
  exit_code=$?
  if [ -n "$replay_dir" ] && [ -d "$replay_dir/evidence/ingestion" ] && [ ! -d "$run_dir/ingestion" ]; then
    cp -R "$replay_dir/evidence/ingestion" "$run_dir/ingestion" || true
  fi
  if [ "$exit_code" -eq 0 ]; then
    printf 'completed\n' > "$run_dir/status.txt"
  else
    printf 'failed (exit %s)\n' "$exit_code" > "$run_dir/status.txt"
  fi
  printf 'Offline evidence: %s\n' "$run_dir"
}
trap finish EXIT
printf 'running\n' > "$run_dir/status.txt"
exec > >(tee "$run_dir/terminal.txt") 2>&1

cd "$project_root"
printf 'Offline proof started: %s\n' "$(date -u)"
printf 'Project: %s\n' "$project_root"
printf 'Run: %s\n' "$run_tag"
printf 'Python: '
python3 --version
printf 'macOS: '
sw_vers -productVersion

for tool in curl ollama networksetup awk; do
  command -v "$tool" >/dev/null || { printf 'Missing command: %s\n' "$tool"; exit 1; }
done

wifi_device="$(networksetup -listallhardwareports | awk '/Hardware Port: Wi-Fi/{getline; print $2}')"
if [ -n "$wifi_device" ]; then
  wifi_state="$(networksetup -getairportpower "$wifi_device")"
  printf '%s\n' "$wifi_state" | tee "$run_dir/wifi-state.txt"
  case "$wifi_state" in
    *": On") printf 'Turn Wi-Fi off, then rerun this script.\n'; exit 1 ;;
  esac
else
  printf 'No Wi-Fi hardware port found. Check other connections manually.\n' | tee "$run_dir/wifi-state.txt"
fi

if curl --head --location --silent --show-error --max-time 5 https://example.com > "$run_dir/connectivity-check.txt" 2>&1; then
  printf 'Internet is reachable. Disconnect all network paths, then rerun.\n'
  exit 1
fi
printf 'External HTTPS check failed while disconnected. See connectivity-check.txt.\n'
printf 'The CLI uses only 127.0.0.1 for Ollama.\n'
export WIKI_OFFLINE_PROOF=1

# The project folder may be cloud-backed. Private inputs must be materialized
# on local disk before disconnection; never print or copy their text to Git.
offline_input_dir="/private/tmp/agentic-wiki-offline-inputs-$(id -u)"
for name in expectations.md chat-checks-revised.txt chat-note-follow-up.txt; do
  if [ ! -s "$offline_input_dir/$name" ]; then
    printf 'Missing local private input: %s. Reconnect and run python3 scripts/prepare-offline-inputs.py before the offline test.\n' "$name"
    exit 1
  fi
done
export WIKI_EVAL_EXPECTATIONS_PATH="$offline_input_dir/expectations.md"
printf 'Three private test inputs are present on local disk.\n'

printf '\nInstalled local model:\n'
ollama list
printf '\nLoaded model before test:\n'
ollama ps
printf '\nMemory before test:\n'
vm_stat

printf '\nUnload Gemma, then search without a loaded model:\n'
ollama stop gemma4:e2b-mlx || true
python3 wiki.py search "max steps tokens" --limit 1

printf '\nIngest all three originals into an isolated replay workspace:\n'
replay_dir="$(mktemp -d -t wiki-offline)"
mkdir -p "$replay_dir/vault"
cp "$project_root/wiki.py" "$project_root/retrieval.py" "$replay_dir/"
cp -R "$project_root/data" "$project_root/prompts" "$replay_dir/"
cp -R "$project_root/vault/raw" "$replay_dir/vault/"
python3 "$replay_dir/wiki.py" ingest --all
cp -R "$replay_dir/evidence/ingestion" "$run_dir/ingestion"
cp -R "$replay_dir/vault/wiki" "$run_dir/generated-wiki"

printf '\nLoaded model after ingestion:\n'
ollama ps
printf '\nMemory after ingestion:\n'
vm_stat

printf '\nRun code checks:\n'
python3 -m unittest discover -s tests -v

printf '\nRun the four frozen ask questions:\n'
ask_label="offline-$run_tag"
python3 evaluation/run_ask_eval.py "$ask_label"
cp "$project_root/evidence/ask/$ask_label.json" "$run_dir/ask-evaluation.json"
python3 - "$run_dir/ask-evaluation.json" <<'PY'
import json
from pathlib import Path
import sys

cases = json.loads(Path(sys.argv[1]).read_text())['cases']
if len(cases) != 4 or [item['id'] for item in cases] != ['Q1', 'Q2', 'Q3', 'Q4']:
    raise SystemExit('Offline ask run did not contain all four questions.')
for item in cases[:3]:
    if (item.get('error') or not item.get('supported_response') or
            not item.get('all_expected_lines_retrieved') or
            not item.get('all_expected_sources_cited') or
            not item.get('all_citations_were_retrieved')):
        raise SystemExit('Offline ask check failed: ' + item['id'])
last = cases[3]
if last.get('error') or last.get('supported_response') or not last.get('abstained_without_citations'):
    raise SystemExit('Offline unsupported-question check failed.')
print('Four offline ask checks passed. Review each answer against its cited passage.')
PY

printf '\nRun casual, draft, follow-up, and note chat checks:\n'
python3 wiki.py chat < "$offline_input_dir/chat-checks-revised.txt"
python3 - 4 <<'PY'
import json
from pathlib import Path
import sys

sessions = list(Path('evidence/chat').glob('*/session.json'))
current = max(sessions, key=lambda path: path.stat().st_mtime)
session = json.loads(current.read_text())
expected = int(sys.argv[1])
if session['status'] != 'completed' or len(session['turns']) != expected:
    raise SystemExit('Offline chat session did not complete.')
records = [json.loads((current.parent / ('turn-%02d' % n) / 'run.json').read_text())
           for n in range(1, expected + 1)]
if any(item['retrieval_used'] for item in records[:3]) or not records[3]['retrieval_used']:
    raise SystemExit('Offline chat retrieval routing failed.')
if not records[3]['result']['citation_ids']:
    raise SystemExit('Offline note chat has no citation.')
print('Four-turn chat check passed:', current)
PY

printf '\nRun a cited note follow-up:\n'
python3 wiki.py chat < "$offline_input_dir/chat-note-follow-up.txt"
python3 - 2 <<'PY'
import json
from pathlib import Path
import sys

sessions = list(Path('evidence/chat').glob('*/session.json'))
current = max(sessions, key=lambda path: path.stat().st_mtime)
session = json.loads(current.read_text())
if session['status'] != 'completed' or len(session['turns']) != int(sys.argv[1]):
    raise SystemExit('Offline note follow-up session did not complete.')
records = [json.loads((current.parent / ('turn-%02d' % n) / 'run.json').read_text())
           for n in (1, 2)]
if not all(item['retrieval_used'] and item['result']['citation_ids'] for item in records):
    raise SystemExit('Offline note follow-up lost its source.')
if not records[1]['note_follow_up'] or records[1]['result']['suggestions']:
    raise SystemExit('Offline note follow-up did not shorten cleanly.')
print('Cited note follow-up passed:', current)
PY

printf '\nLoaded model after checks:\n'
ollama ps
printf '\nMemory after checks:\n'
vm_stat
printf '\nOffline proof commands completed. Review the saved answers and Obsidian vault after reconnecting.\n'

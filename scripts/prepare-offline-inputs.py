#!/usr/bin/env python3
"""Keep private evaluation inputs on local disk for the disconnected run."""

import os
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'private-archive' / 'corpus-v2'
DEST = Path('/private/tmp') / ('agentic-wiki-offline-inputs-' + str(os.getuid()))
NAMES = ('expectations.md', 'chat-checks-revised.txt', 'chat-note-follow-up.txt')


def main():
    DEST.mkdir(mode=0o700, exist_ok=True)
    if DEST.is_symlink() or not DEST.is_dir() or DEST.stat().st_uid != os.getuid():
        raise SystemExit('Unsafe offline input directory: ' + str(DEST))
    DEST.chmod(0o700)
    for name in NAMES:
        data = (SOURCE / name).read_bytes()
        if not data:
            raise SystemExit('Private input is empty: ' + name)
        with tempfile.NamedTemporaryFile(dir=DEST, prefix=name + '.', delete=False) as handle:
            temporary = Path(handle.name)
            try:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            except BaseException:
                temporary.unlink(missing_ok=True)
                raise
        temporary.chmod(0o600)
        temporary.replace(DEST / name)
        local = DEST / name
        if local.read_bytes() != data or local.stat().st_blocks == 0:
            raise SystemExit('Local copy could not be verified: ' + name)
        print('Local private input ready:', name)
    print('Offline inputs ready on local disk. No question text was printed.')


if __name__ == '__main__':
    main()

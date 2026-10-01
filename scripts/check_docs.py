#!/usr/bin/env python3
"""Check committed documentation links without installing or controlling hardware."""
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]

def main():
    files = subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','*.md'], cwd=ROOT,text=True).splitlines()
    errors = []
    for name in sorted(set(files)):
        path = ROOT/name
        if not path.exists(): continue
        for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
            target = target.strip().split(' "')[0].strip('<>')
            if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',target) or target.startswith('#'): continue
            destination = unquote(target.split('#')[0])
            if not (path.parent/destination).exists(): errors.append(name+': '+target)
    if errors:
        print('\n'.join(errors),file=sys.stderr)
        return 1
    print('Local documentation links OK.')
    return 0

if __name__ == '__main__': sys.exit(main())

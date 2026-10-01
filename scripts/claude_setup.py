#!/usr/bin/env python3
"""Merge/remove local Claude Code lifecycle hooks; preserve unrelated settings."""
import argparse
import json
from pathlib import Path
import shlex
import shutil
import time

ROOT = Path(__file__).resolve().parents[1]
SETTINGS = Path.home() / '.claude' / 'settings.json'
RUNTIME = Path.home() / '.local' / 'share' / 'trafficlights'
MARKER = 'Traffic light: Claude '
EVENTS = {'SessionStart':'G', 'UserPromptSubmit':'Y', 'PreToolUse':'Y',
          'PostToolUse':'Y', 'PostToolUseFailure':'Y', 'PermissionRequest':'B',
          'Stop':'G', 'StopFailure':'R', 'SessionEnd':'O'}

def remove_ours(data):
    for event, groups in list(data.get('hooks', {}).items()):
        retained = []
        for group in groups:
            group = dict(group)
            group['hooks'] = [h for h in group.get('hooks', [])
                              if not h.get('statusMessage', '').startswith(MARKER)]
            if group['hooks']:
                retained.append(group)
        if retained:
            data['hooks'][event] = retained
        else:
            del data['hooks'][event]

def configure(enable):
    data = json.loads(SETTINGS.read_text()) if SETTINGS.exists() else {}
    if enable and data.get('disableAllHooks'):
        raise RuntimeError('Claude hooks are disabled in user settings; resolve that preference explicitly first.')
    remove_ours(data)
    if enable:
        python = RUNTIME / 'venv' / 'bin' / 'python'
        if not python.exists():
            raise RuntimeError('Install the shared Mac bridge with install.py first.')
        base = shlex.quote(str(python)) + ' ' + shlex.quote(str(ROOT / 'scripts' / 'traffic.py'))
        for event, state in EVENTS.items():
            group = {'hooks':[{'type':'command', 'command':base + ' ' + state + ' --provider claude --silent',
                               'timeout':3, 'statusMessage':MARKER + event}]}
            if event in ('PreToolUse','PostToolUse','PostToolUseFailure','PermissionRequest'):
                group['matcher'] = '.*'
            data.setdefault('hooks', {}).setdefault(event, []).append(group)
    if SETTINGS.exists():
        backup = ROOT / '.backups' / ('claude-settings-' + str(time.time_ns()) + '.json')
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SETTINGS, backup)
    SETTINGS.parent.mkdir(parents=True, exist_ok=True)
    temporary = SETTINGS.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, indent=2) + '\n')
    temporary.replace(SETTINGS)
    print(('Installed' if enable else 'Removed') + ' owned Claude Code hooks: ' + str(SETTINGS))
    if enable:
        print('Review /hooks in Claude Code; restart an existing session if needed. Workspace trust/policy still applies.')
    else:
        print('Shared bridge and Codex hooks remain installed. Existing session records expire or can be cleared separately.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['enable','disable'])
    configure(parser.parse_args().action == 'enable')

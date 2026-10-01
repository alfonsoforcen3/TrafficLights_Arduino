#!/usr/bin/env python3
"""Detect supported local AI apps and merge their owned traffic-light hooks."""
import argparse
import json
from pathlib import Path
import shlex
import shutil
import time

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = Path.home() / '.local/share/trafficlights'
SUPPORTED = ('codex','claude','gemini','cursor')
EVENTS = {
    'gemini': {'SessionStart':'G','BeforeAgent':'Y','BeforeModel':'Y',
               'BeforeTool':'Y','AfterTool':'Y','AfterAgent':'G','Notification':'','SessionEnd':'O'},
    # Avoid Cursor permission/tool-gating hooks: this integration observes lifecycle only.
    'cursor': {'sessionStart':'G','beforeSubmitPrompt':'Y','afterAgentThought':'Y',
               'afterAgentResponse':'Y','stop':'G','sessionEnd':'O'},
}

def settings_path(provider):
    return Path.home() / ('.cursor/hooks.json' if provider == 'cursor' else '.' + provider + '/settings.json')

def detect():
    """Evidence of installation: executable, app bundle, or actual settings file; never execute an AI request."""
    evidence = {}
    for provider in SUPPORTED:
        hits = []
        executables = {'cursor':('cursor','cursor-agent','agent')}.get(provider,(provider,))
        for executable in executables:
            found = shutil.which(executable)
            # A generic 'agent' executable alone is not sufficient evidence of Cursor.
            if found and (executable != 'agent' or 'cursor' in found.lower()):
                hits.append(found)
        app_names = {'codex':('Codex.app','ChatGPT.app'),'claude':('Claude.app',),'cursor':('Cursor.app',)}
        for app in app_names.get(provider,()):
            for directory in (Path('/Applications'),Path.home()/'Applications'):
                path = directory/app
                if path.exists(): hits.append(str(path))
        config = Path.home()/'.codex/hooks.json' if provider == 'codex' else settings_path(provider)
        if config.exists(): hits.append(str(config))
        if hits: evidence[provider] = hits
    return evidence

def remove_ours(data, provider):
    if provider == 'cursor':
        for event, hooks in list(data.get('hooks',{}).items()):
            # Cursor has no nested hook marker. Only remove commands with our script and namespace.
            retained = [h for h in hooks if not (
                'traffic.py' in h.get('command','') and '--provider cursor' in h.get('command','')
                and '--trafficlights-hook' in h.get('command',''))]
            if retained: data['hooks'][event] = retained
            else: del data['hooks'][event]
    else:
        for event, groups in list(data.get('hooks',{}).items()):
            retained = []
            for group in groups:
                group = dict(group)
                group['hooks'] = [h for h in group.get('hooks',[])
                                  if not h.get('name','').startswith('trafficlights-gemini-')]
                if group['hooks']: retained.append(group)
            if retained: data['hooks'][event] = retained
            else: del data['hooks'][event]

def configure(provider, enable=True):
    if provider == 'codex':
        try: from scripts import codex_setup
        except ModuleNotFoundError: import codex_setup
        if not enable: raise RuntimeError('Use manage_hooks.py disable for Codex/shared service removal.')
        codex_setup.enable(install_login_service=False)
        return
    if provider == 'claude':
        try: from scripts import claude_setup
        except ModuleNotFoundError: import claude_setup
        claude_setup.configure(enable)
        return
    path = settings_path(provider)
    if not enable and not path.exists(): return
    data = json.loads(path.read_text()) if path.exists() else {}
    if provider == 'cursor' and data.get('version',1) != 1:
        raise RuntimeError('Unsupported Cursor hook schema version; settings left unchanged.')
    if enable and provider == 'gemini' and data.get('hooksConfig',{}).get('enabled') is False:
        raise RuntimeError('Gemini hooks are disabled; settings left unchanged.')
    python = RUNTIME/'venv/bin/python'
    if enable and not python.exists(): raise RuntimeError('Install the shared Mac bridge first.')
    remove_ours(data,provider)
    if enable:
        base = shlex.quote(str(python)) + ' ' + shlex.quote(str(ROOT/'scripts/traffic.py'))
        if provider == 'cursor': data.setdefault('version',1)
        for event,state in EVENTS[provider].items():
            command = base + (' ' + state if state else '') + ' --provider ' + provider
            if provider == 'cursor':
                command += ' --trafficlights-hook'
                if event == 'beforeSubmitPrompt': command += ' --cursor-prompt'
                data.setdefault('hooks',{}).setdefault(event,[]).append({'command':command,'timeout':3})
            else:
                group = {'hooks':[{'name':'trafficlights-gemini-'+event,'type':'command',
                                   'command':command,'timeout':3000}]}
                if event in ('BeforeTool','AfterTool'): group['matcher'] = '.*'
                data.setdefault('hooks',{}).setdefault(event,[]).append(group)
    if path.exists():
        backup = ROOT/'.backups'/(provider+'-settings-'+str(time.time_ns())+'.json')
        backup.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(path,backup)
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data,indent=2)+'\n')
    temporary.replace(path)
    print(('Installed' if enable else 'Removed') + ' owned '+provider+' hooks: '+str(path))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--detect',action='store_true',help='Read-only inventory; no configuration changes')
    parser.add_argument('--providers',nargs='+',choices=SUPPORTED)
    parser.add_argument('--disable',action='store_true',help='Remove selected adapters, leaving shared service running')
    args = parser.parse_args()
    found = detect()
    print('Detected providers: '+(', '.join(found) or 'none'))
    if args.detect: return
    for provider in args.providers or found:
        configure(provider,not args.disable)
    print('Review provider hook/workspace trust and policy; configured hooks still require live acceptance tests.')

if __name__ == '__main__': main()

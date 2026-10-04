#!/usr/bin/env python3
"""Validate source syntax and reject common private-data leaks without launching apps."""
import ast
import json
from pathlib import Path
import re
import subprocess
ROOT=Path(__file__).resolve().parents[1]
errors=[]
for p in ROOT.rglob('*'):
    if not p.is_file() or any(x in p.relative_to(ROOT).parts for x in ['.git','staged-home','__pycache__']):continue
    try:s=p.read_text()
    except UnicodeError:
        errors.append(f'Unexpected binary: {p.relative_to(ROOT)}');continue
    rel=str(p.relative_to(ROOT))
    if re.search(r'/' + r'home/[^\s/]+/|BEGIN (?:OPENSSH|RSA|EC) PRIVATE KEY|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}',s):
        errors.append(f'Potential private data: {rel}')
    if p.suffix=='.json':
        try:json.loads(s)
        except ValueError as exc:errors.append(f'{rel}: {exc}')
    if p.suffix=='.py' or (s.startswith('#!/usr/bin/python') and p.suffix==''):
        try:ast.parse(s,filename=rel)
        except SyntaxError as exc:errors.append(f'{rel}: {exc}')
    if p.suffix=='.sh':
        result=subprocess.run(['bash','-n',str(p)],capture_output=True,text=True)
        if result.returncode:errors.append(f'{rel}: {result.stderr}')
if errors:raise SystemExit('\n'.join(errors))
print('Source syntax, JSON, shell syntax and private-data pattern checks passed.')

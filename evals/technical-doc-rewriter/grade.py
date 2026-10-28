#!/usr/bin/env python3
"""Score rewritten fixtures against cases.json.

Usage: grade.py OUT_DIR [OUT_DIR...]

Each OUT_DIR holds one rewrite of each fixture, with the fixture's file name.
The script prints one Markdown table row for each (OUT_DIR, fixture) pair.
Exit status 1 when any assertion fails. Standard library only; Python 3.8+.
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'skills', 'technical-doc-rewriter', 'scripts'))

import check  # noqa: E402

HEADING = re.compile(r'^\s*#{1,6}\s')


def warning_order(lines, case):
    """Return a failure message, or '' when each warning comes before its step."""
    # The step is the line that gives the command, also when it is a continuation line of a
    # numbered item. A warning in the same item counts when it comes before that line.
    warnings = [
        i for i, l in enumerate(lines)
        if check.WARNING_LABEL.search(l) and any(k in l.lower() for k in case['keywords'])
    ]  # fmt: skip
    step = next((i for i, l in enumerate(lines) if case['step'] in l and i not in warnings), None)
    if step is None:
        return f'no line gives the command `{case["step"]}`'
    if not any(i < step for i in warnings):
        return f'no warning before the step `{case["step"]}`'
    end = next((i for i in range(step + 1, len(lines)) if HEADING.match(lines[i])), len(lines))
    if any(step < i < end for i in warnings):
        return f'a warning still follows the step `{case["step"]}`'
    return ''


def planned(lines, case):
    """Each sentence about the planned item says that it is planned and not that it is done."""
    heading = ''
    for line in lines:
        if HEADING.match(line):
            heading = line
            continue
        for sentence in re.split(r'[。；;]|(?<=\.)\s', line):
            if case['keyword'] not in sentence:
                continue
            is_planned = any(m in sentence or m in heading for m in case['markers'])
            if not is_planned or re.search(case['done'], sentence):
                return f'"{case["keyword"]}" is still written as done'
    return ''


def grade(out_dir, name, case):
    original = open(os.path.join(HERE, 'fixtures', name), encoding='utf-8').read()
    try:
        rewritten = open(os.path.join(out_dir, name), encoding='utf-8').read()
    except OSError:
        return {'missing': True}
    findings = check.check_text(rewritten)
    result = check.compare(original, rewritten)
    lines = rewritten.split('\n')
    failures = [m for m in (warning_order(lines, c) for c in case['warnings']) if m]
    failures += [m for m in (planned(lines, c) for c in case['planned']) if m]
    return {
        'hard': sum(f.level == 'hard' for f in findings),
        'convention': sum(f.level == 'convention' for f in findings),
        'lost': [f'{k} {v}' for k, v in result['lost']],
        'added_numbers': [v for k, v in result['added'] if k == 'number'],
        'warnings': result['warnings'],
        'failures': failures,
    }


def main(argv):
    if not argv:
        print(__doc__.strip())
        return 2
    cases = json.load(open(os.path.join(HERE, 'cases.json'), encoding='utf-8'))
    print('| Run | Fixture | Hard | Convention | Lost items | New numbers | Warning labels | Order / plan | Pass |')
    print('| --- | --- | --- | --- | --- | --- | --- | --- | --- |')
    failed = False
    for out_dir in argv:
        for name, case in cases.items():
            r = grade(out_dir, name, case)
            run = os.path.basename(os.path.normpath(out_dir))
            if r.get('missing'):
                print(f'| {run} | {name} | – | – | – | – | – | file missing | no |')
                failed = True
                continue
            ok = r['hard'] == 0 and not r['lost'] and not r['added_numbers'] and not r['failures']
            failed = failed or not ok
            lost = '<br>'.join(r['lost']) or '0'
            added = '<br>'.join(r['added_numbers']) or '0'
            order = '<br>'.join(r['failures']) or 'ok'
            before, after = r['warnings']
            print(
                f'| {run} | {name} | {r["hard"]} | {r["convention"]} | {lost} | {added} | '
                f'{before} → {after} | {order} | {"yes" if ok else "no"} |'
            )
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

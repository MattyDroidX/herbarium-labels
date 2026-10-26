"""Require immutable upstream action references in workflow files."""
from pathlib import Path
import re


def check(root=Path('.github/workflows')):
    for path in sorted(root.glob('*.yml')):
        for line in path.read_text(encoding='utf-8').splitlines():
            match = re.match(r'\s*(?:-\s*)?uses:\s*([^\s#]+)', line)
            if match and not re.fullmatch(r'[\w.-]+/[\w./-]+@[0-9a-f]{40}', match[1]):
                raise ValueError(f'{path}: actions must use full commit SHAs.')
    print('Workflow action references use full commit SHAs.')


if __name__ == '__main__':
    check()

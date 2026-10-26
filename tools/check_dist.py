"""Validate public distribution contents without extracting untrusted archives."""
import argparse
from email.parser import BytesParser
from email.policy import default
from pathlib import Path, PurePosixPath
import re
import tarfile
import zipfile


ROOT_FILES = {
    'LICENSE', 'NOTICE.md', 'README.md', 'CHANGELOG.md', 'CONTRIBUTING.md',
    'SECURITY.md',
    'pyproject.toml', 'MANIFEST.in', 'PKG-INFO', 'setup.cfg',
    'requirements.lock', 'requirements-compat.lock', 'requirements-dev.in', 'requirements-dev.lock', '.env.example', '.gitignore',
}
SECRET = re.compile(
    rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'
    rb'|\bsk-ant-[A-Za-z0-9_-]{20,}'
    rb'|\b(?:ghp_|github_pat_)[A-Za-z0-9_]{20,}'
    rb'|\bAKIA[A-Z0-9]{16}\b'
    rb'|\bpypi-[A-Za-z0-9_-]{30,}'
)


def allowed_source(path):
    parts = path.parts
    if len(parts) == 1:
        return path.name in ROOT_FILES
    if parts[:2] == ('src', 'herbarium_labels'):
        return path.suffix == '.py'
    if parts[:2] == ('src', 'herbarium_labels.egg-info'):
        return path.name in {'PKG-INFO', 'SOURCES.txt', 'dependency_links.txt',
                             'entry_points.txt', 'requires.txt', 'top_level.txt'}
    return ((parts[0] in {'tests', 'tools'} and path.suffix == '.py')
            or (parts[0] == 'docs' and path.suffix in {'.md', '.mmd', '.svg'})
            or (parts[:2] == ('examples', 'synthetic') and path.suffix in {'.md', '.jpg', '.png', '.pdf', '.xlsx', '.json'})
            or (parts[0] == 'library' and path.suffix == '.json')
            or ((parts[:2] == ('.github', 'workflows') or parts == ('.github', 'dependabot.yml')) and path.suffix == '.yml'))


def allowed_wheel(path):
    if path.parts[0] == 'herbarium_labels':
        return path.suffix == '.py'
    if not path.parts[0].endswith('.dist-info'):
        return False
    return path.name in {'METADATA', 'WHEEL', 'RECORD', 'entry_points.txt',
                         'top_level.txt', 'LICENSE', 'NOTICE.md'}


def members(archive):
    if archive.suffix == '.whl':
        with zipfile.ZipFile(archive) as bundle:
            if bundle.testzip() is not None:
                raise ValueError('Corrupt wheel')
            for item in bundle.infolist():
                if not item.is_dir():
                    if (item.external_attr >> 16) & 0o170000 == 0o120000:
                        raise ValueError('Archive links are not allowed')
                    yield item.filename, bundle.read(item)
    elif archive.name.endswith('.tar.gz'):
        with tarfile.open(archive, 'r:gz') as bundle:
            for item in bundle:
                if item.isdir():
                    continue
                if not item.isfile():
                    raise ValueError('Archive links and special files are not allowed')
                stream = bundle.extractfile(item)
                yield item.name, stream.read()
    else:
        raise ValueError('Expected a wheel or .tar.gz source distribution')


def check(archive):
    wheel = archive.suffix == '.whl'
    seen = set()
    roots = set()
    metadata = None
    for name, content in members(archive):
        path = PurePosixPath(name)
        if '\\' in name or path.is_absolute() or '..' in path.parts:
            raise ValueError(f'Unsafe archive path: {name}')
        if not wheel:
            roots.add(path.parts[0])
            path = PurePosixPath(*path.parts[1:])
        if not path.parts:
            raise ValueError(f'Empty archive path: {name}')
        if path in seen:
            raise ValueError(f'Duplicate archive member: {name}')
        seen.add(path)
        if not (allowed_wheel(path) if wheel else allowed_source(path)):
            raise ValueError(f'Unexpected distribution file: {name}')
        if SECRET.search(content):
            raise ValueError(f'Possible credential in {name}; value withheld')
        if path.name == ('METADATA' if wheel else 'PKG-INFO') and len(path.parts) <= 2:
            metadata = BytesParser(policy=default).parsebytes(content)
    if not wheel and len(roots) != 1:
        raise ValueError('Source distribution must have one root directory')
    names = {path.name for path in seen}
    required = {'LICENSE', 'NOTICE.md', 'bryophytes.py', 'sennen.py', 'cache.py', 'catalog.py', 'legacy.py', 'demo.py',
                'imaging.py', 'provider.py', 'profiles.py', 'pipeline.py', 'pricing.py', 'errors.py', 'suggestions.py', 'cli.py',
                'existing.py', 'report_messages.py', 'sennen_suggestions.py'}
    if not wheel:
        required |= {'README.md', 'catalog.json', 'catalog.schema.json', 'requirements.lock'}
    if required - names:
        raise ValueError(f'Missing required files: {sorted(required - names)}')
    if metadata is None or metadata['Name'] != 'herbarium-labels':
        raise ValueError('Missing or unexpected package metadata')
    if metadata['License-Expression'] != 'MIT' or metadata['Requires-Python'] != '>=3.11':
        raise ValueError('Unexpected license or Python requirement')
    print(f'{archive.name}: {len(seen)} files allowed; metadata/license and credential-pattern checks passed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archives', type=Path, nargs='+')
    args = parser.parse_args()
    for archive in args.archives:
        check(archive)


if __name__ == '__main__':
    main()

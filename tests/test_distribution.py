import contextlib
import io
from pathlib import Path
import runpy
import tempfile
import tarfile
import unittest
import zipfile


CHECK = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'tools/check_dist.py'))['check']


class DistributionTests(unittest.TestCase):
    def wheel(self, folder, extra=None, *, omit=()):
        target = Path(folder) / 'synthetic.whl'
        entries = {f'herbarium_labels/{name}.py': b'# synthetic module'
                   for name in ('bryophytes', 'sennen', 'cache', 'catalog', 'legacy', 'demo', 'imaging', 'provider', 'profiles', 'pipeline',
                                'pricing', 'errors', 'suggestions', 'cli', 'existing', 'report_messages',
                                'sennen_suggestions', 'prompts', 'messages')}
        entries.update({f'herbarium_labels/locales/{lang}.json': b'{}' for lang in ('en', 'pt', 'es')})
        entries.update({
            'herbarium_labels-0.1.0a2.dist-info/licenses/LICENSE': b'MIT License',
            'herbarium_labels-0.1.0a2.dist-info/licenses/NOTICE.md': b'Synthetic notice',
            'herbarium_labels-0.1.0a2.dist-info/METADATA': (
                b'Metadata-Version: 2.4\nName: herbarium-labels\nVersion: 0.1.0a2\n'
                b'License-Expression: MIT\nRequires-Python: >=3.11\n\nSynthetic README\n'),
        })
        entries.update(extra or {})
        for name in omit:
            entries.pop(name)
        with zipfile.ZipFile(target, 'w') as bundle:
            for name, content in entries.items():
                bundle.writestr(name, content)
        return target

    def test_expected_runtime_files_are_accepted(self):
        with tempfile.TemporaryDirectory() as folder, contextlib.redirect_stdout(io.StringIO()):
            CHECK(self.wheel(folder))

    def test_private_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError, 'Unexpected distribution file'):
                CHECK(self.wheel(folder, {'.env': b'private settings'}))

    def test_every_wheel_locale_is_required_at_its_package_path(self):
        for lang in ('en', 'pt', 'es'):
            with self.subTest(lang=lang), tempfile.TemporaryDirectory() as folder:
                with self.assertRaisesRegex(ValueError, 'Missing required locales'):
                    CHECK(self.wheel(folder, omit=(f'herbarium_labels/locales/{lang}.json',)))

    def test_sdist_requires_locales_too(self):
        with tempfile.TemporaryDirectory() as folder:
            wheel = self.wheel(folder)
            source = Path(folder) / 'synthetic.tar.gz'
            with zipfile.ZipFile(wheel) as bundle:
                entries = {'src/' + name: bundle.read(name) for name in bundle.namelist()
                           if name.startswith('herbarium_labels/')}
                entries['PKG-INFO'] = bundle.read('herbarium_labels-0.1.0a2.dist-info/METADATA')
            entries.update({name: b'synthetic' for name in
                            ('LICENSE', 'NOTICE.md', 'README.md', 'library/catalog.json',
                             'library/catalog.schema.json', 'requirements.lock')})
            for missing in (None, 'src/herbarium_labels/locales/pt.json'):
                with tarfile.open(source, 'w:gz') as bundle:
                    for name, content in entries.items():
                        if name == missing:
                            continue
                        member = tarfile.TarInfo('synthetic/' + name)
                        member.size = len(content)
                        bundle.addfile(member, io.BytesIO(content))
                if missing:
                    with self.assertRaisesRegex(ValueError, 'Missing required locales'):
                        CHECK(source)
                else:
                    with contextlib.redirect_stdout(io.StringIO()):
                        CHECK(source)

    def test_archive_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError, 'Unsafe archive path'):
                CHECK(self.wheel(folder, {'../outside.py': b''}))

    def test_possible_credential_is_rejected_without_echoing_value(self):
        with tempfile.TemporaryDirectory() as folder:
            marker = b'sk-ant-' + b'x' * 40
            with self.assertRaisesRegex(ValueError, 'value withheld') as error:
                CHECK(self.wheel(folder, {'herbarium_labels/example.py': marker}))
            self.assertNotIn(marker.decode(), str(error.exception))

    def test_missing_license_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'missing.whl'
            with zipfile.ZipFile(path, 'w') as bundle:
                bundle.writestr('herbarium_labels/example.py', '')
            with self.assertRaisesRegex(ValueError, 'Missing required files'):
                CHECK(path)

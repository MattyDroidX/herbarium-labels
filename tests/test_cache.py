import io
import json
import os
from pathlib import Path
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from threading import Event, Lock
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from PIL import Image

from herbarium_labels import bryophytes as b


class FakeAPIError(Exception):
    pass


class CacheTests(unittest.TestCase):
    @contextmanager
    def batch(self, count=1, parse=None):
        reading = {key: '' for key in b.BryophyteReading.model_fields}
        reading.update(rotation_degrees=0, uncertainties=[], literal_text='Synthetic literal text')
        response = SimpleNamespace(stop_reason='end_turn', parsed_output=b.BryophyteReading(**reading),
                                   usage=SimpleNamespace(input_tokens=10, output_tokens=20))
        calls = []
        calls_lock = Lock()

        def record(**kwargs):
            with calls_lock:
                calls.append(kwargs)
            return parse(**kwargs) if parse else response

        fake = SimpleNamespace(APIError=FakeAPIError, Anthropic=lambda **kw:
                               SimpleNamespace(messages=SimpleNamespace(parse=record)))
        with tempfile.TemporaryDirectory() as folder, \
                patch.dict(sys.modules, {'anthropic': fake}), \
                patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'unit-test-placeholder'}):
            root = Path(folder)
            photos = root / 'photos'
            photos.mkdir()
            for index in range(count):
                Image.new('RGB', (50, 60), (index, 0, 0)).save(photos / f'{index:02}.jpg')
            args = SimpleNamespace(images=photos, output=root / 'out', limit=None, sample=False)
            yield args, calls

    def test_content_change_is_blocked_and_previous_result_preserved(self):
        with self.batch() as (args, calls):
            b.transcribe(args)
            target = args.output / 'json/00.json'
            before = target.read_bytes()
            Image.new('RGB', (50, 60), 'white').save(args.images / '00.jpg')
            with self.assertRaisesRegex(ValueError, 'new output directory'):
                b.transcribe(args)
            self.assertEqual(len(calls), 1)
            self.assertEqual(target.read_bytes(), before)
            self.assertFalse((args.output / '.transcription.lock').exists())
            args.no_pdf = True
            with self.assertRaisesRegex(ValueError, 'image differs'):
                b.report(args)
            self.assertFalse((args.output / 'transcriptions.xlsx').exists())

    def test_configuration_changes_are_blocked(self):
        with self.batch() as (args, calls):
            b.transcribe(args)
            for name, value in [('MODEL', 'different-model'), ('PROMPT', 'different-prompt')]:
                with self.subTest(name=name), patch.object(b, name, value):
                    with self.assertRaisesRegex(ValueError, 'new output directory'):
                        b.transcribe(args)
            schema = b.BryophyteReading.model_json_schema()
            schema['description'] = 'changed schema'
            with patch.object(b.BryophyteReading, 'model_json_schema', return_value=schema):
                with self.assertRaisesRegex(ValueError, 'new output directory'):
                    b.transcribe(args)
            with patch.object(b, 'version', return_value='different-image-codec'):
                with self.assertRaisesRegex(ValueError, 'new output directory'):
                    b.transcribe(args)
            self.assertEqual(len(calls), 1)

    def test_valid_human_correction_is_preserved_on_resume(self):
        with self.batch() as (args, calls):
            b.transcribe(args)
            target = args.output / 'json/00.json'
            item = json.loads(target.read_text())
            item['reading']['literal_text'] = 'Human correction with lines\npreserved'
            target.write_text(json.dumps(item), encoding='utf-8')
            before = target.read_bytes()
            totals = b.transcribe(args)
            self.assertEqual(totals.reused, 1)
            self.assertEqual((totals.photos, totals.input_tokens, totals.output_tokens), (0, 0, 0))
            self.assertEqual(len(calls), 1)
            self.assertEqual(target.read_bytes(), before)

    def test_legacy_readable_but_not_silently_reused(self):
        with self.batch() as (args, calls):
            b.transcribe(args)
            target = args.output / 'json/00.json'
            item = json.loads(target.read_text())
            del item['cache']
            target.write_text(json.dumps(item), encoding='utf-8')
            before = target.read_bytes()
            self.assertEqual(b.read_records(args.output)[0]['reading'], item['reading'])
            with self.assertRaisesRegex(ValueError, 'new output directory'):
                b.transcribe(args)
            self.assertEqual(len(calls), 1)
            self.assertEqual(target.read_bytes(), before)

    def test_entire_batch_checked_before_any_request(self):
        with self.batch(count=3) as (args, calls):
            (args.output / 'json').mkdir(parents=True)
            target = args.output / 'json/02.json'
            for content in ('{broken', '[]', '{"reading": {}}'):
                with self.subTest(content=content):
                    target.write_text(content)
                    with self.assertRaisesRegex(ValueError, 'new output directory'):
                        b.transcribe(args)
                    self.assertEqual(calls, [])
                    self.assertEqual(target.read_text(), content)

    def test_overlapping_runs_do_not_repeat_calls(self):
        entered, release = Event(), Event()

        def blocking(**kwargs):
            entered.set()
            if not release.wait(10):
                raise RuntimeError('Test synchronization timed out')
            raise FakeAPIError()

        with self.batch(parse=blocking) as (args, calls), ThreadPoolExecutor(1) as pool:
            future = pool.submit(b.transcribe, args)
            try:
                self.assertTrue(entered.wait(10))
                with self.assertRaisesRegex(ValueError, 'locked'):
                    b.transcribe(args)
            finally:
                release.set()
            self.assertEqual(future.result().failures, 1)
            self.assertEqual(len(calls), 1)
            self.assertFalse((args.output / '.transcription.lock').exists())

    def test_parallel_totals_include_incomplete_usage_and_resume(self):
        def parse(**kwargs):
            # Pick the result from the actual submitted image, independent of scheduling.
            import base64
            content = kwargs['messages'][0]['content'][0]['source']['data']
            with Image.open(io.BytesIO(base64.b64decode(content))) as image:
                index = round(image.getpixel((0, 0))[0] / 10)
            if index % 3 == 0:
                raise FakeAPIError()
            return SimpleNamespace(stop_reason='max_tokens' if index % 3 == 1 else 'end_turn',
                                   parsed_output=None if index % 3 == 1 else reading,
                                   usage=SimpleNamespace(input_tokens=10, output_tokens=20))

        reading = {key: '' for key in b.BryophyteReading.model_fields}
        reading.update(rotation_degrees=0, uncertainties=[], literal_text='Synthetic')
        reading = b.BryophyteReading(**reading)
        with self.batch(count=18, parse=parse) as (args, calls):
            for index, path in enumerate(sorted(args.images.iterdir())):
                Image.new('RGB', (50, 60), (index * 10, 0, 0)).save(path)
            totals = b.transcribe(args)
            self.assertEqual((totals.photos, totals.failures), (6, 12))
            self.assertEqual((totals.input_tokens, totals.output_tokens), (120, 240))
            self.assertEqual(len(list((args.output / 'json').glob('*.json'))), 6)
            resumed = b.transcribe(args)
            self.assertEqual((resumed.photos, resumed.failures, resumed.reused), (0, 12, 6))
            self.assertEqual(len(calls), 30)

    def test_lock_released_after_write_failure(self):
        with self.batch() as (args, calls):
            with patch.object(Path, 'replace', side_effect=OSError('synthetic disk failure')):
                with self.assertRaises(OSError):
                    b.transcribe(args)
            self.assertFalse((args.output / 'json/00.json').exists())
            self.assertFalse((args.output / '.transcription.lock').exists())
            b.transcribe(args)
            self.assertEqual(len(calls), 2)
            self.assertFalse(list(args.output.rglob('*.partial')))

    def test_batch_refuses_archive_after_incomplete_response(self):
        def parse(**kwargs):
            return SimpleNamespace(stop_reason='max_tokens', parsed_output=None,
                                   usage=SimpleNamespace(input_tokens=10, output_tokens=20))

        with self.batch(parse=parse) as (args, calls):
            args.pdf = False
            with self.assertRaises(SystemExit):
                b.batch(args)
            self.assertFalse((args.images / 'transcriptions.zip').exists())
            self.assertFalse((Path(args.output) / '.transcription.lock').exists())


if __name__ == '__main__':
    unittest.main()

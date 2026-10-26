"""Host integration and collection contracts, using only synthetic images/clients."""
import base64
from contextlib import contextmanager
from dataclasses import replace
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from zipfile import ZipFile

from PIL import Image
from pydantic import BaseModel

from herbarium_labels import TranscriptionError, TranscriptionOptions, read_image
from herbarium_labels import bryophytes as b, pipeline, sennen as s
from herbarium_labels.imaging import ImagePolicy, prepare_images
from herbarium_labels.profiles import TranscriptionProfile, get_profile
from herbarium_labels.suggestions import DEFAULT_MESSAGES


def photo(size=(100, 200)):
    buffer = io.BytesIO()
    Image.new('RGB', size, 'white').save(buffer, 'JPEG')
    return buffer.getvalue()


def sheet(**overrides):
    data = {name: '' for name in s.SheetReading.model_fields}
    data.update(labels=[s.Label(origin='Sennen', literal_text='= SYNTHETIC A\nLine 2'),
                        s.Label(origin='Porto', literal_text='SYNTHETIC B')], uncertainties=[])
    data.update(overrides)
    return s.SheetReading(**data)


def provider(reading=None, *, complete=True):
    response = SimpleNamespace(stop_reason='end_turn' if complete else 'max_tokens',
                               parsed_output=reading or sheet() if complete else None,
                               usage=SimpleNamespace(input_tokens=10, output_tokens=20))
    return SimpleNamespace(messages=SimpleNamespace(parse=Mock(return_value=response)), close=Mock())


class HostIntegrationTests(unittest.TestCase):
    def test_field_mapping_reads_and_emits_host_keys(self):
        reading = sheet(shelfmark='68/9')
        same = s.suggestions({'cota': '68/9', 'transcription': 'Reviewed'}, reading, 'sheet.jpg',
                             field_map={'shelfmark': 'cota'})
        self.assertNotIn('cota', [field for field, _, _ in same])
        changed = s.suggestions({'cota': '12', 'transcription': 'Reviewed'}, reading, 'sheet.jpg',
                                field_map={'shelfmark': 'cota'})
        self.assertEqual(changed[0][:2], ('cota', '68/9'))
        self.assertIn('«12»', changed[0][2])
        self.assertEqual(s.suggestions({}, reading, 'sheet.jpg')[1][0], 'shelfmark')

    def test_invalid_mapping_is_rejected_before_suggestions(self):
        for mapping in ({'typo': 'cota'}, {'shelfmark': ''}, {'shelfmark': 'transcription'}):
            with self.subTest(mapping=mapping), self.assertRaises(ValueError):
                s.suggestions({}, sheet(), 'sheet.jpg', field_map=mapping)

    def test_host_owns_all_review_text_with_literal_uncertainties_preserved(self):
        calls = []
        def translate(key, context):
            calls.append((key, context))
            return f"HOST:{key}:{context['uncertainties']}"
        reading = sheet(shelfmark='68/9', uncertainties=['Cota ilegível no círculo'])
        rows = s.suggestions({}, reading, 'sheet.jpg', messages=translate, field_map={'shelfmark': 'cota'})
        self.assertTrue(all(text.startswith('HOST:source:') for _, _, text in rows))
        self.assertNotIn('Automatic suggestion', str(rows))
        self.assertIn('Cota ilegível no círculo', rows[-1][2])
        self.assertEqual(reading.uncertainties, ['Cota ilegível no círculo'])
        self.assertEqual(next(c for k, c in calls if k == 'shelfmark')['host_field'], 'cota')

    def test_template_mapping_and_default_english_text(self):
        rows = s.suggestions({}, sheet(), 'sheet.jpg', messages={'source': 'HOST {filename}', 'transcription': 'TEXT'})
        self.assertEqual(rows[0][2], 'HOST sheet.jpg TEXT')
        self.assertIn('Literal transcription of the labels.', s.suggestions({}, sheet(), 'sheet.jpg')[0][2])
        self.assertNotIn(' das ', str(DEFAULT_MESSAGES))
        with self.assertRaises(ValueError):
            s.suggestions({}, sheet(), 'sheet.jpg', messages={'typo': 'x'})

    def test_missing_key_is_public_error_without_sdk_or_key_disclosure(self):
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': '   '}):
            with self.assertRaisesRegex(TranscriptionError, 'ANTHROPIC_API_KEY'):
                s.read_labels(photo())

    def test_injected_client_needs_no_key_and_remains_open(self):
        client = provider()
        with patch.dict(os.environ, {}, clear=True):
            reading, usage = s.read_labels(photo(), client=client)
        self.assertEqual(len(reading.labels), 2)
        self.assertEqual(usage, {'input_tokens': 10, 'output_tokens': 20})
        client.close.assert_not_called()
        self.assertEqual(len(client.messages.parse.call_args.kwargs['messages'][0]['content']), 3)

    def test_incomplete_reading_keeps_known_usage_and_client_open(self):
        client = provider(complete=False)
        with self.assertRaises(TranscriptionError) as caught:
            s.read_labels(photo(), client=client)
        self.assertEqual((caught.exception.input_tokens, caught.exception.output_tokens), (10, 20))
        client.close.assert_not_called()

    def test_owned_client_is_closed_even_after_failure(self):
        client = provider(complete=False)
        with patch('herbarium_labels.provider.create_client', return_value=client):
            with self.assertRaises(TranscriptionError):
                s.read_labels(photo())
        client.close.assert_called_once()

    def test_host_request_context_is_optional_and_balanced(self):
        events = []
        @contextmanager
        def limit():
            events.append('enter')
            try:
                yield
            finally:
                events.append('exit')
        with self.assertRaises(TranscriptionError):
            s.read_labels(photo(), client=provider(complete=False), request_context=limit)
        self.assertEqual(events, ['enter', 'exit'])
        with self.assertRaisesRegex(TranscriptionError, 'host-owned limiter'):
            s.check_rate('synthetic')
        limiter = Mock()
        s.check_rate('synthetic', limiter=limiter)
        limiter.assert_called_once_with('synthetic')

    def test_options_are_per_call_and_snapshot_model_environment(self):
        client = provider()
        with patch.dict(os.environ, {'TRANSCRIPTION_MODEL': 'first-model'}):
            options = TranscriptionOptions(max_tokens=1234)
        with patch.dict(os.environ, {'TRANSCRIPTION_MODEL': 'second-model'}):
            s.read_labels(photo(), client=client, options=options)
        self.assertEqual(client.messages.parse.call_args.kwargs['model'], 'first-model')
        self.assertEqual(client.messages.parse.call_args.kwargs['max_tokens'], 1234)
        for kwargs in ({'workers': 0}, {'timeout': float('nan')}, {'max_retries': -1}, {'max_tokens': 0}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                TranscriptionOptions(**kwargs)


class ImageContractTests(unittest.TestCase):
    def sizes(self, blocks):
        result = []
        for block in blocks:
            with Image.open(io.BytesIO(base64.b64decode(block['source']['data']))) as image:
                result.append(image.size)
        return result

    def test_small_images_are_not_upscaled_and_source_unchanged(self):
        content = photo()
        before = hashlib.sha256(content).hexdigest()
        self.assertEqual(self.sizes(s.images(content)), [(100, 200), (100, 80)])
        self.assertEqual(self.sizes(prepare_images(content)), [(100, 200)])
        self.assertEqual(hashlib.sha256(content).hexdigest(), before)

    def test_large_images_are_bounded_and_tiny_crop_is_nonempty(self):
        self.assertTrue(all(max(size) <= 1568 for size in self.sizes(s.images(photo((2400, 3200))))))
        self.assertEqual(self.sizes(s.images(photo((1, 1)))), [(1, 1), (1, 1)])

    def test_exif_orientation_is_applied_before_crop(self):
        image = Image.new('RGB', (100, 200), 'white')
        metadata = Image.Exif()
        metadata[274] = 6
        buffer = io.BytesIO()
        image.save(buffer, 'JPEG', exif=metadata)
        self.assertEqual(self.sizes(s.images(buffer.getvalue())), [(200, 100), (200, 40)])

    def test_invalid_image_uses_public_error(self):
        client = provider()
        with self.assertRaisesRegex(TranscriptionError, 'prepare'):
            s.read_labels(b'not an image', client=client)
        client.messages.parse.assert_not_called()


class ProfilePipelineTests(unittest.TestCase):
    def test_sennen_batch_cache_reports_and_zip_preserve_labels_and_original(self):
        from openpyxl import load_workbook
        with tempfile.TemporaryDirectory() as folder:
            images = Path(folder) / 'input'
            images.mkdir()
            image = images / 'sheet.jpg'
            image.write_bytes(photo())
            original = image.read_bytes()
            client = provider()
            args = SimpleNamespace(images=images, pdf=True)
            pipeline.batch(args, profile='sennen', client=client, options=TranscriptionOptions(workers=1))
            output = images / 'transcription'
            target = output / 'json/sheet.json'
            record = json.loads(target.read_text())
            self.assertEqual(record['profile'], 'sennen')
            self.assertEqual(len(record['reading']['labels']), 2)
            record['reading']['labels'][0]['literal_text'] = '= HUMAN CORRECTION\nLine 2'
            target.write_text(json.dumps(record))
            corrected = target.read_bytes()
            totals = pipeline.transcribe(SimpleNamespace(images=images, output=output, sample=False, limit=None),
                                         profile='sennen', client=client, options=TranscriptionOptions(workers=1))
            self.assertEqual(totals.reused, 1)
            self.assertEqual(target.read_bytes(), corrected)
            self.assertEqual(client.messages.parse.call_count, 1)
            client.close.assert_not_called()
            pipeline.report(SimpleNamespace(images=images, output=output, no_pdf=True), profile='sennen')
            book = load_workbook(output / 'transcriptions.xlsx')
            try:
                self.assertIn('[Sennen]\n= HUMAN CORRECTION', book.worksheets[0]['C2'].value)
                self.assertIn('[Porto]\nSYNTHETIC B', book.worksheets[0]['C2'].value)
                self.assertEqual(book.worksheets[0]['C2'].data_type, 's')
                self.assertIn('Shelfmark', [cell.value for cell in book.worksheets[1][1]])
            finally:
                book.close()
            with ZipFile(images / 'transcriptions.zip') as archive:
                self.assertIsNone(archive.testzip())
                self.assertIn('transcription/review.pdf', archive.namelist())
            self.assertEqual(image.read_bytes(), original)
            with self.assertRaisesRegex(ValueError, 'profile differs'):
                pipeline.read_records(output, profile='po-bryophytes')

    def test_custom_profile_uses_shared_provider_and_cache_contract(self):
        class Reading(BaseModel):
            literal_text: str
            accession: str
            uncertainties: list[str]
        profile = TranscriptionProfile('custom-labels', 'Copy literal text.', Reading,
                    (('filename', 'Filename'), ('accession', 'Accession')))
        reading, usage = read_image(photo(), profile=profile,
                                   client=provider(Reading(literal_text='Literal', accession='001', uncertainties=[])))
        self.assertEqual(reading.accession, '001')
        first = pipeline.cache_configuration(profile, TranscriptionOptions(model='test'))
        second = pipeline.cache_configuration(replace(profile, images=ImagePolicy(long_edge=1000)),
                                               TranscriptionOptions(model='test'))
        self.assertNotEqual(first, second)
        self.assertNotEqual(first, pipeline.cache_configuration(replace(profile, prompt='Different policy.'),
                                                               TranscriptionOptions(model='test')))
        with self.assertRaises(ValueError):
            replace(profile, columns=(('missing', 'Missing'),))

    def test_switching_profile_cannot_reuse_cache_or_make_request(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            images = root / 'input'
            images.mkdir()
            (images / 'sheet.jpg').write_bytes(photo())
            args = SimpleNamespace(images=images, output=root / 'output', limit=None, sample=False)
            client = provider()
            pipeline.transcribe(args, profile='sennen', client=client)
            with self.assertRaisesRegex(ValueError, 'new output directory'):
                pipeline.transcribe(args, profile='po-bryophytes', client=client)
            self.assertEqual(client.messages.parse.call_count, 1)

    def test_reuse_needs_no_provider_key_or_client(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'sheet.jpg').write_bytes(photo())
            args = SimpleNamespace(images=root, output=root / 'output', limit=None, sample=False)
            pipeline.transcribe(args, profile='sennen', client=provider())
            with patch.dict(os.environ, {}, clear=True):
                self.assertEqual(pipeline.transcribe(args, profile='sennen').reused, 1)

    def test_cli_exposes_profile_and_failure_exit_status(self):
        from herbarium_labels import cli
        with tempfile.TemporaryDirectory() as folder:
            argv = ['herbarium-labels', 'transcribe', '--profile', 'sennen', '--images', folder,
                    '--output', folder + '/out', '--workers', '1']
            with patch.object(sys, 'argv', argv), patch.object(pipeline, 'transcribe_folder',
                    return_value=SimpleNamespace(failures=1)) as run:
                with self.assertRaises(SystemExit) as caught:
                    cli.main()
            self.assertEqual(caught.exception.code, 1)
            self.assertEqual(run.call_args.kwargs['profile'], 'sennen')
            self.assertEqual(run.call_args.kwargs['options'].workers, 1)


if __name__ == '__main__':
    unittest.main()

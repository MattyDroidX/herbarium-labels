"""Regression checks for the English API and literal-preserving legacy reads."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace

from PIL import Image
from pydantic import ValidationError

from herbarium_labels import bryophytes as b, sennen as s
from herbarium_labels.cache import output_lock
from herbarium_labels.catalog import Catalog, HandAttribution, Person
from herbarium_labels.legacy import normalize_record


def legacy_reading():
    # Deliberately retain old keys and source-language evidence in this fixture.
    return {
        'rotacao_para_ler': 90, 'herbario': '', 'serie_colecao': '',
        'nome_como_escrito': '', 'especie': '', 'autor': '', 'determinador': '',
        'pais_provincia': '', 'localidade': '', 'ecologia': '', 'altitude': '', 'utm': '',
        'data_como_escrita': '03/04/05', 'data_iso': '', 'coletor': '', 'numero': '001',
        'anotacoes_manuscritas': '', 'texto_literal': 'Herbário sintético\nLeitura: [ilegível]',
        'duvidas': ['Data ambígua'],
    }


class EnglishAPITests(unittest.TestCase):
    def test_bryophyte_legacy_input_serializes_english_without_translating_text(self):
        reading = b.BryophyteReading.model_validate(legacy_reading())
        self.assertEqual(reading.literal_text, 'Herbário sintético\nLeitura: [ilegível]')
        self.assertEqual(reading.uncertainties, ['Data ambígua'])
        self.assertEqual(reading.collection_number, '001')
        self.assertEqual(reading.date_as_written, '03/04/05')
        self.assertEqual(reading.date_iso, '')
        self.assertIn('rotation_degrees', reading.model_dump())
        self.assertNotIn('rotacao_para_ler', reading.model_dump())

    def test_legacy_report_preserves_source_json_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            images = root / 'images'
            images.mkdir()
            Image.new('RGB', (100, 200), 'white').save(images / 'sample.jpg')
            output = root / 'output'
            (output / 'json').mkdir(parents=True)
            path = output / 'json/sample.json'
            path.write_text(json.dumps({'ficheiro': 'sample.jpg', 'modelo': 'legacy-synthetic',
                                        'input_tokens': 10, 'output_tokens': 20,
                                        'leitura': legacy_reading()}, ensure_ascii=False), encoding='utf-8')
            before = hashlib.sha256(path.read_bytes()).hexdigest()
            b.report(SimpleNamespace(images=images, output=output, no_pdf=True))
            self.assertEqual(before, hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertTrue((output / 'transcriptions.xlsx').is_file())
            self.assertEqual(b.read_records(output)[0]['reading']['collection_number'], '001')

    def test_sheet_legacy_labels_stay_separate(self):
        fields = {name: '' for name in s.SheetReading.model_fields}
        del fields['labels']
        fields.update(etiquetas=[{'origem': 'Sennen', 'texto_literal': 'Etiquette A'},
                                 {'origem': 'Porto', 'texto_literal': 'Etiqueta B'}], uncertainties=[])
        reading = s.SheetReading.model_validate(fields)
        self.assertEqual([label.literal_text for label in reading.labels], ['Etiquette A', 'Etiqueta B'])
        self.assertEqual(list(reading.model_dump()['labels'][0]), ['origin', 'literal_text'])

    def test_conflicting_legacy_and_english_values_are_rejected(self):
        with self.assertRaisesRegex(ValidationError, 'Conflicting'):
            b.BryophyteReading.model_validate({**legacy_reading(), 'literal_text': 'conflict'})
        with self.assertRaisesRegex(ValueError, 'Conflicting'):
            normalize_record({'ficheiro': 'a.jpg', 'filename': 'b.jpg', 'leitura': legacy_reading()})

    def test_unknown_record_schema_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unsupported'):
            normalize_record({'schema_version': '99.0.0', 'filename': 'a.jpg', 'reading': {}})

    def test_unexpected_reading_field_is_rejected(self):
        with self.assertRaises(ValidationError):
            b.BryophyteReading.model_validate({**legacy_reading(), 'invented_field': 'value'})

    def test_model_schemas_expose_english_fields(self):
        fields = b.BryophyteReading.model_json_schema()['properties']
        self.assertIn('taxonomic_author', fields)
        self.assertIn('literal_text', fields)
        self.assertNotIn('autor', fields)
        self.assertIn('labels', s.SheetReading.model_json_schema()['properties'])
        self.assertNotIn('etiquetas', s.SheetReading.model_json_schema()['properties'])

    def test_legacy_catalogue_statuses_are_read_as_english(self):
        catalog = Catalog.model_validate({'schema_version': '0.1.0', 'persons': [
            {'person_id': 'synthetic', 'display_name': 'Synthetic person', 'status': 'rascunho'}]})
        self.assertEqual(catalog.schema_version, '0.2.0')
        self.assertEqual(catalog.persons[0].status, 'draft')
        self.assertEqual(HandAttribution(attribution_id='a', hand_id='h', person_id='p',
                                         status='candidata').status, 'candidate')
        with self.assertRaises(ValidationError):
            HandAttribution(attribution_id='a', hand_id='h', person_id='p', status='confirmada')

    def test_invalid_status_type_is_a_validation_error(self):
        with self.assertRaises(ValidationError):
            Person(person_id='synthetic', display_name='Synthetic person', status=[])

    def test_legacy_lock_blocks_new_run(self):
        with tempfile.TemporaryDirectory() as folder:
            legacy = Path(folder) / '.transcricao.lock'
            legacy.write_text('Existing run')
            with self.assertRaisesRegex(ValueError, 'legacy run'):
                with output_lock(folder):
                    self.fail('Legacy lock must block the run')
            self.assertEqual(legacy.read_text(), 'Existing run')
            self.assertFalse((Path(folder) / '.transcription.lock').exists())

    def test_cli_help_exposes_english_commands_and_options(self):
        command = subprocess.run([sys.executable, '-m', 'herbarium_labels', '--help'],
                                 capture_output=True, text=True, timeout=30)
        self.assertEqual(command.returncode, 0, command.stderr)
        self.assertIn('transcribe,report,batch', command.stdout)
        help_result = subprocess.run([sys.executable, '-m', 'herbarium_labels', 'transcribe', '--help'],
                                     capture_output=True, text=True, timeout=30)
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        self.assertIn('--images', help_result.stdout)
        self.assertIn('--output', help_result.stdout)
        self.assertNotIn('--fotos', help_result.stdout)

    def test_offline_demo_cli_verifies_delivery_without_api_key(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder) / 'demo'
            environment = dict(os.environ)
            environment.pop('ANTHROPIC_API_KEY', None)
            environment['PYTHONDONTWRITEBYTECODE'] = '1'
            result = subprocess.run([sys.executable, '-m', 'herbarium_labels', 'demo',
                                     '--output', str(destination), '--pdf'], env=environment,
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            checks = json.loads((destination / 'verification.json').read_text())
            self.assertTrue(checks['all_passed'])
            self.assertEqual(checks['simulated_calls'], 2)
            record = json.loads((destination / 'input/transcription/json/synthetic.json').read_text())
            self.assertEqual(record['schema_version'], '0.2.0')
            self.assertNotIn('leitura', record)
            self.assertTrue((destination / 'input/transcription/review.pdf').read_bytes().startswith(b'%PDF'))
            self.assertEqual(set(record['reading']), set(b.BryophyteReading.model_fields))

    def test_demo_refuses_to_overwrite_existing_directory(self):
        from herbarium_labels.demo import run_demo
        with tempfile.TemporaryDirectory() as folder:
            marker = Path(folder) / 'keep.txt'
            marker.write_text('Original contents')
            with self.assertRaises(FileExistsError):
                run_demo(folder)
            self.assertEqual(marker.read_text(), 'Original contents')

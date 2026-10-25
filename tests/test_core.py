import base64
import io
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from PIL import Image
from pydantic import ValidationError
from herbarium_labels import bryophytes as b, sennen as s
from herbarium_labels.catalog import Catalog, HandAttribution

class FakeAPIError(Exception):
    pass

class CoreTests(unittest.TestCase):
    def reading(self):
        value={key:'' for key in b.BryophyteReading.model_fields}
        value.update(rotation_degrees=0,uncertainties=[],literal_text='= synthetic text\nLine 2')
        return value

    def test_bad_rotation_rejected(self):
        with self.assertRaises(ValidationError):
            b.BryophyteReading.model_validate({**self.reading(),'rotation_degrees':45})

    def test_collision_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            Path(folder,'same.jpg').touch();Path(folder,'same.png').touch()
            with self.assertRaises(ValueError): b.photos(folder)

    def test_path_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError): b.safe_photo(folder,'../private.jpg')

    def test_unknown_cost_is_not_guessed(self):
        with patch.dict(os.environ,{},clear=True):
            self.assertIn('unknown',b.cost_text(100,100))
            self.assertIsNone(s.estimated_cost(s.MODEL,100,100))
        with patch.dict(os.environ,{'TRANSCRIPTION_PRICE_IN':'0.1','TRANSCRIPTION_PRICE_OUT':'0.5'}):
            self.assertEqual(b.cost_text(3000,1000),'0.0008 USD')

    def test_invalid_price_rejected(self):
        with patch.dict(os.environ,{'TRANSCRIPTION_PRICE_IN':'nan','TRANSCRIPTION_PRICE_OUT':'1'}):
            with self.assertRaises(ValueError): b.cost_text(1,1)

    def test_sheet_and_crop(self):
        stream=io.BytesIO();Image.new('RGB',(100,200),'white').save(stream,'JPEG')
        blocks=s.images(stream.getvalue())
        self.assertEqual(len(blocks),2)
        sizes=[Image.open(io.BytesIO(base64.b64decode(x['source']['data']))).size for x in blocks]
        self.assertGreater(sizes[0][1]/sizes[0][0],sizes[1][1]/sizes[1][0])

    def test_provider_incomplete_result_rejected(self):
        stream=io.BytesIO();Image.new('RGB',(100,200)).save(stream,'JPEG')
        client=SimpleNamespace(messages=SimpleNamespace(parse=lambda **kw: SimpleNamespace(stop_reason='max_tokens',parsed_output=None)))
        with patch.dict(sys.modules,{'anthropic':SimpleNamespace(APIError=FakeAPIError)}):
            with self.assertRaises(s.TranscriptionError): s.read_labels(stream.getvalue(),client=client)

    def test_catalog_drafts_have_no_invented_roles(self):
        root=Path(__file__).resolve().parents[1]
        catalog=Catalog.model_validate_json((root/'library/catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(len(catalog.persons),4)
        self.assertTrue(all(p.status=='draft' and not p.documented_roles for p in catalog.persons))

    def test_confirmation_requires_evidence(self):
        with self.assertRaises(ValidationError):
            HandAttribution(attribution_id='a',hand_id='h',person_id='p',status='confirmed')

    def test_missing_catalog_source_rejected(self):
        with self.assertRaises(ValidationError):
            Catalog(persons=[dict(person_id='p',display_name='P',source_ids=['absent'])])

    def test_atomic_json_and_resume(self):
        reading=b.BryophyteReading.model_validate(self.reading())
        response=SimpleNamespace(stop_reason='end_turn',parsed_output=reading,usage=SimpleNamespace(input_tokens=10,output_tokens=20))
        calls=[]
        def parse(**kw): calls.append(kw);return response
        fake=SimpleNamespace(APIError=FakeAPIError,Anthropic=lambda **kw:SimpleNamespace(messages=SimpleNamespace(parse=parse)))
        with tempfile.TemporaryDirectory() as folder, patch.dict(sys.modules,{'anthropic':fake}), patch.dict(os.environ,{'ANTHROPIC_API_KEY':'unit-test-placeholder'}):
            root=Path(folder);photos=root/'input';photos.mkdir();Image.new('RGB',(50,60)).save(photos/'demo.jpg')
            args=SimpleNamespace(images=photos,output=root/'out',limit=None,sample=False)
            b.transcribe(args);b.transcribe(args)
            self.assertEqual(len(calls),1)
            self.assertFalse(list((root/'out').rglob('*.partial')))
            self.assertEqual(b.read_records(root/'out')[0]['reading']['literal_text'],reading.literal_text)

    def test_offline_report_text_links_and_original(self):
        from openpyxl import load_workbook
        import hashlib
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);photos=root/'photos';photos.mkdir();output=root/'out';(output/'json').mkdir(parents=True)
            image=photos/'demo.jpg';Image.new('RGB',(100,200),'white').save(image)
            before=hashlib.sha256(image.read_bytes()).hexdigest()
            item=dict(filename=image.name,model='simulated',input_tokens=0,output_tokens=0,reading=self.reading())
            (output/'json/demo.json').write_text(json.dumps(item),encoding='utf-8')
            with patch.dict(os.environ,{},clear=True):
                b.report(SimpleNamespace(images=photos,output=output,no_pdf=True))
            book=load_workbook(output/'transcriptions.xlsx')
            self.assertEqual(book.worksheets[0]['C2'].data_type,'s')
            target=book.worksheets[0]['A2'].hyperlink.target
            self.assertTrue((output/target).is_file())
            book.close()
            self.assertEqual(before,hashlib.sha256(image.read_bytes()).hexdigest())

class DeliveryTests(unittest.TestCase):
    reading = CoreTests.reading
    def test_full_sheet_success_keeps_labels_separate(self):
        stream=io.BytesIO();Image.new('RGB',(100,200),'white').save(stream,'JPEG')
        reading=s.SheetReading(labels=[s.Label(origin='Sennen',literal_text='Label A'),s.Label(origin='Porto',literal_text='Label B')],general_accession_number='',order_number='',sennen_exsiccata_number='',shelfmark='',sennen_label_name='',porto_label_name='',locality='',altitude='',collection_date='',collector='',uncertainties=[])
        sent=[]
        def parse(**kw):
            sent.append(kw)
            return SimpleNamespace(stop_reason='end_turn',parsed_output=reading,usage=SimpleNamespace(input_tokens=10,output_tokens=20))
        client=SimpleNamespace(messages=SimpleNamespace(parse=parse))
        with patch.dict(sys.modules,{'anthropic':SimpleNamespace(APIError=FakeAPIError)}):
            result,usage=s.read_labels(stream.getvalue(),client=client)
        self.assertEqual([x.literal_text for x in result.labels],['Label A','Label B'])
        self.assertEqual(len([x for x in sent[0]['messages'][0]['content'] if x['type']=='image']),2)

    def test_batch_zip_offline_provider_and_pdf(self):
        from zipfile import ZipFile
        reading=b.BryophyteReading.model_validate(self.reading())
        response=SimpleNamespace(stop_reason='end_turn',parsed_output=reading,usage=SimpleNamespace(input_tokens=10,output_tokens=20))
        fake=SimpleNamespace(APIError=FakeAPIError,Anthropic=lambda **kw:SimpleNamespace(messages=SimpleNamespace(parse=lambda **kw:response)))
        with tempfile.TemporaryDirectory() as folder, patch.dict(sys.modules,{'anthropic':fake}), patch.dict(os.environ,{'ANTHROPIC_API_KEY':'unit-test-placeholder'}):
            root=Path(folder);Image.new('RGB',(100,200),'white').save(root/'demo.jpg')
            b.batch(SimpleNamespace(images=root,pdf=True))
            with ZipFile(root/'transcriptions.zip') as z:
                self.assertIsNone(z.testzip())
                self.assertIn('transcription/review.pdf',z.namelist())
                self.assertIn('transcription/images/demo.jpg',z.namelist())
                self.assertFalse(any('env' in name for name in z.namelist()))
                self.assertTrue(z.read('transcription/review.pdf').startswith(b'%PDF'))

if __name__=='__main__': unittest.main()

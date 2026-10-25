"""Exercise the installed SDK's request/response contract without network access."""
import io
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from PIL import Image

from herbarium_labels import bryophytes as b, sennen as s


class SDKTests(unittest.TestCase):
    def test_structured_outputs_through_mock_http_transport(self):
        try:
            import anthropic
            import httpx2
        except ImportError:
            self.skipTest('Optional Anthropic/httpx2 SDK is not installed')

        bryophyte = {key: '' for key in b.BryophyteReading.model_fields}
        bryophyte.update(rotation_degrees=0, uncertainties=[], literal_text='Synthetic literal text')
        sheet = {key: '' for key in s.SheetReading.model_fields}
        sheet.update(labels=[{'origin': 'outra', 'literal_text': 'Label A'},
                                {'origin': 'outra', 'literal_text': 'Label B'}], uncertainties=[])
        requests = []

        def handle(request):
            self.assertEqual(request.url.path, '/v1/messages')
            body = json.loads(request.content)
            self.assertEqual(body['output_config']['format']['type'], 'json_schema')
            requests.append(body)
            properties = body['output_config']['format']['schema']['properties']
            reading = sheet if 'labels' in properties else bryophyte
            return httpx2.Response(200, json={
                'id': 'msg_synthetic', 'type': 'message', 'role': 'assistant',
                'model': body['model'], 'stop_reason': 'end_turn', 'stop_sequence': None,
                'content': [{'type': 'text', 'text': json.dumps(reading)}],
                'usage': {'input_tokens': 10, 'output_tokens': 20},
            })

        transport = httpx2.MockTransport(handle)
        with anthropic.Anthropic(api_key='unit-test-placeholder', max_retries=0,
                                 base_url='https://provider.invalid',
                                 http_client=httpx2.Client(transport=transport)) as client:
            with tempfile.TemporaryDirectory() as folder, \
                    patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'unit-test-placeholder'}), \
                    patch.object(anthropic, 'Anthropic', return_value=client):
                root = Path(folder)
                image = root / 'demo.jpg'
                Image.new('RGB', (100, 200), 'white').save(image)
                totals = b.transcribe(SimpleNamespace(images=root, output=root / 'out',
                                                      limit=None, sample=False))
                self.assertEqual((totals.photos, totals.input_tokens, totals.output_tokens), (1, 10, 20))
                reading, usage = s.read_labels(image.read_bytes(), client=client)
                self.assertEqual(len(reading.labels), 2)
                self.assertEqual(usage, {'input_tokens': 10, 'output_tokens': 20})
        self.assertEqual(len(requests), 2)
        self.assertEqual(requests[0]['messages'][0]['content'][-1]['text'], b.PROMPT)
        self.assertEqual(requests[1]['messages'][0]['content'][-1]['text'], s.PROMPT)
        self.assertEqual(sum(block['type'] == 'image'
                             for block in requests[1]['messages'][0]['content']), 2)


if __name__ == '__main__':
    unittest.main()

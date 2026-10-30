"""Label routing by origin and structured provenance of review suggestions (0.1.0a5)."""
import unittest

from herbarium_labels import TranscriptionProfile, get_profile
from herbarium_labels.messages import load_messages
from herbarium_labels.sennen import SheetReading, suggestions
from herbarium_labels.sennen_suggestions import Suggestion


def reading(*labels):
    return SheetReading(labels=[{'origin': origin, 'literal_text': text} for origin, text in labels],
                        general_accession_number='', order_number='', sennen_exsiccata_number='', shelfmark='',
                        sennen_label_name='', porto_label_name='', locality='', altitude='', collection_date='',
                        collector='', uncertainties=[])


SHEET = reading(('Sennen', 'Plantes d’Espagne'), ('Porto', 'N.º geral 1'), ('other', 'Exchange label'))


OWN = get_profile('sennen').own_label_origins


class LabelRoutingTests(unittest.TestCase):
    def test_own_labels_are_the_transcription_and_others_are_associated(self):
        result = dict((field, value) for field, value, _ in suggestions({}, SHEET, 'a.jpg', own_label_origins=OWN))
        self.assertEqual(result['transcription'], '[Sennen]\nPlantes d’Espagne\n\n[Porto]\nN.º geral 1')
        self.assertEqual(result['associated_labels'], '[other]\nExchange label')

    def test_hosts_map_the_canonical_field_and_filled_fields_are_left_alone(self):
        fields = [f for f, _, _ in suggestions({'notes_from_exchange': 'kept'}, SHEET, 'a.jpg', own_label_origins=OWN,
                                               field_map={'associated_labels': 'notes_from_exchange'})]
        self.assertIn('transcription', fields)
        self.assertNotIn('notes_from_exchange', fields)

    def test_empty_origins_keep_every_label_in_the_transcription(self):
        result = dict((field, value) for field, value, _ in suggestions({}, SHEET, 'a.jpg', own_label_origins=()))
        self.assertNotIn('associated_labels', result)
        self.assertIn('[other]\nExchange label', result['transcription'])

    def test_default_keeps_the_previous_behaviour_and_announces_the_change(self):
        with self.assertWarnsRegex(FutureWarning, '0.1.0a6'):
            result = dict((field, value) for field, value, _ in suggestions({}, SHEET, 'a.jpg'))
        self.assertNotIn('associated_labels', result)
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter('error')
            suggestions({}, reading(('Sennen', 'only own labels')), 'a.jpg')  # nothing would change: no warning

    def test_profiles_declare_their_own_origins(self):
        self.assertEqual(get_profile('sennen').own_label_origins, ('Sennen', 'Porto'))
        self.assertEqual(get_profile('po-bryophytes').own_label_origins, ())
        custom = TranscriptionProfile('my-herbarium', 'Read it.', SheetReading, (('filename', 'File'),), own_label_origins=['A'])
        self.assertEqual(custom.own_label_origins, ('A',))


class ProvenanceTests(unittest.TestCase):
    def test_records_carry_structured_provenance_and_tuples_stay_compatible(self):
        records = suggestions({}, SHEET, 'a.jpg', model_label='Model X', records=True, own_label_origins=OWN,
                              provenance={'agent': 'Assistant', 'requester': 'Curator', 'image_sha256': 'f' * 64})
        self.assertTrue(all(isinstance(r, Suggestion) for r in records))
        self.assertEqual(records[0].provenance, {'model': 'Model X', 'image': 'a.jpg', 'agent': 'Assistant',
                                                 'requester': 'Curator', 'image_sha256': 'f' * 64})
        self.assertTrue(records[0].text.startswith('Automatic suggestion by Assistant (Model X), requested by Curator, from image a.jpg.'))
        self.assertEqual([(r.field, r.value, r.text) for r in records],
                         suggestions({}, SHEET, 'a.jpg', model_label='Model X', own_label_origins=OWN,
                                     provenance={'agent': 'Assistant', 'requester': 'Curator', 'image_sha256': 'f' * 64}))

    def test_without_agent_and_requester_the_plain_source_text_is_used(self):
        text = suggestions({}, SHEET, 'a.jpg', model_label='Model X', own_label_origins=OWN, provenance={'agent': 'Assistant'})[0][2]
        self.assertTrue(text.startswith('Automatic suggestion (Model X) from image a.jpg.'))

    def test_catalogues_translate_the_new_messages(self):
        for lang in ('pt', 'es'):
            messages = load_messages(lang, kind='review')
            text = suggestions({}, SHEET, 'a.jpg', messages=messages, model_label='M', own_label_origins=OWN,
                               provenance={'agent': 'A', 'requester': 'R'})
            self.assertTrue(all('{' not in t for _, _, t in text), lang)
        self.assertIn('Etiqueta correspondente', load_messages('pt', kind='review')['associated_labels'])


if __name__ == '__main__':
    unittest.main()

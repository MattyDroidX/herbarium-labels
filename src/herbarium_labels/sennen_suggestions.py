"""Sennen review suggestions with canonical fields and caller-defined presentation."""
from collections.abc import Mapping
from difflib import SequenceMatcher
from types import MappingProxyType

from .sennen import _date, _norm, _shelfmark

FIELDS = ('transcription', 'shelfmark', 'exsiccata_number', 'collection_date', 'original_locality')
DEFAULT_MESSAGES = MappingProxyType({
    'source': 'Automatic suggestion ({model}) from image {filename}. Check the image before accepting.',
    'transcription': 'Literal transcription of the labels.',
    'shelfmark': 'Current shelfmark: «{current}». Reading: «{reading}».',
    'exsiccata_number': 'Current exsiccata number: «{current}». Sennen label reading: «{reading}».',
    'collection_date': 'Current date: «{current}». Reading: «{reading}».',
    'original_locality': 'Current original locality: «{current}». Reading: «{reading}».',
    'uncertainties': '\n\nUncertainties flagged by the model:\n- {uncertainties}',
})
DOUBT_WORDS = {'transcription': ('',), 'shelfmark': ('shelfmark', 'circle', 'cota', 'circulo'),
               'exsiccata_number': ('exsiccata', 'collection_number', 'numero'),
               'collection_date': ('date', 'data'), 'original_locality': ('local', 'loc')}


def build_suggestions(item, reading, filename, *, field_map=None, messages=None, model_label='Claude'):
    """field_map maps canonical keys to host keys on both input and output.

    messages may be a mapping overriding English templates, or a callable
    (message_id, context) -> text for a host's own translation framework.
    Context contains canonical field, current/read values and literal uncertainty
    strings. A callback owns all presentation; scientific text is never translated.
    """
    mapping = dict(zip(FIELDS, FIELDS))
    supplied = dict(field_map or {})
    if supplied.keys() - mapping.keys():
        raise ValueError('Unknown canonical suggestion field.')
    mapping.update(supplied)
    if any(not isinstance(value, str) or not value.strip() for value in mapping.values()):
        raise ValueError('Host field names must be nonempty strings.')
    if len(set(mapping.values())) != len(mapping):
        raise ValueError('Host field names must be unique.')
    if messages is not None and not callable(messages) and not isinstance(messages, Mapping):
        raise TypeError('messages must be a mapping or callable.')
    if isinstance(messages, Mapping) and messages.keys() - DEFAULT_MESSAGES.keys():
        raise ValueError('Unknown review message identifier.')

    def message(key, context):
        if callable(messages):
            return messages(key, dict(context))
        return (messages or {}).get(key, DEFAULT_MESSAGES[key]).format_map(context)

    def current(field):
        return item.get(mapping[field]) or ''

    def review(field, value, words):
        doubts = [d for d in reading.uncertainties if any(w in _norm(d) for w in words)]
        context = {'field': field, 'host_field': mapping[field], 'current': current(field) or '—',
                   'reading': value, 'filename': filename, 'model': model_label,
                   'uncertainties': '\n- '.join(doubts)}
        text = message('source', context) + ' ' + message(field, context)
        if doubts:
            text += message('uncertainties', context)
        return text

    def append(field, value, source):
        result.append((mapping[field], value, review(field, source, DOUBT_WORDS[field])))

    import re
    result = []
    if not current('transcription').strip():
        literal = '\n\n'.join(f'[{label.origin}]\n{label.literal_text.strip()}' for label in reading.labels)
        if literal.strip():
            append('transcription', literal, literal)
    shelfmark = _shelfmark(reading.shelfmark)
    if shelfmark and shelfmark != _shelfmark(current('shelfmark')):
        append('shelfmark', shelfmark, reading.shelfmark)
    number = re.sub(r'\D', '', reading.sennen_exsiccata_number)
    if number and number != current('exsiccata_number').strip():
        append('exsiccata_number', number, reading.sennen_exsiccata_number)
    date, old_date = _date(reading.collection_date), current('collection_date')
    if reading.collection_date and date and (not old_date or (_date(old_date) and date != _date(old_date))):
        append('collection_date', reading.collection_date, reading.collection_date)
    if reading.locality and SequenceMatcher(None, _norm(reading.locality), _norm(current('original_locality'))).ratio() < 0.9:
        append('original_locality', reading.locality, reading.locality)
    return result

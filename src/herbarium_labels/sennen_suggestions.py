"""Sennen review suggestions with canonical fields, caller-defined presentation and structured provenance."""
from collections.abc import Mapping
from dataclasses import dataclass, field as dataclass_field
from difflib import SequenceMatcher
from types import MappingProxyType

from .sennen import _date, _norm, _shelfmark

FIELDS = ('transcription', 'associated_labels', 'shelfmark', 'exsiccata_number', 'collection_date', 'original_locality')
DEFAULT_MESSAGES = MappingProxyType({
    'source': 'Automatic suggestion ({model}) from image {filename}. Check the image before accepting.',
    'source_agent': 'Automatic suggestion by {agent} ({model}), requested by {requester}, from image {filename}. Check the image before accepting.',
    'transcription': 'Literal transcription of the labels.',
    'associated_labels': 'Labels that came with another specimen or collection.',
    'shelfmark': 'Current shelfmark: «{current}». Reading: «{reading}».',
    'exsiccata_number': 'Current exsiccata number: «{current}». Sennen label reading: «{reading}».',
    'collection_date': 'Current date: «{current}». Reading: «{reading}».',
    'original_locality': 'Current original locality: «{current}». Reading: «{reading}».',
    'uncertainties': '\n\nUncertainties flagged by the model:\n- {uncertainties}',
})
DOUBT_WORDS = {'transcription': ('',), 'associated_labels': ('',), 'shelfmark': ('shelfmark', 'circle', 'cota', 'circulo'),
               'exsiccata_number': ('exsiccata', 'collection_number', 'numero'),
               'collection_date': ('date', 'data'), 'original_locality': ('local', 'loc')}


@dataclass(frozen=True)
class Suggestion:
    """One pending review: host field, proposed value, review text and where it came from.

    provenance always has model and image; hosts may add agent, requester, image_sha256, prompt_sha256 or anything
    their audit trail needs. It is returned as given, never translated.
    """
    field: str
    value: str
    text: str
    provenance: Mapping = dataclass_field(default_factory=dict)


def build_suggestions(item, reading, filename, **options):
    """(host field, value, review text) tuples; see build_suggestion_records for the options."""
    return [(s.field, s.value, s.text) for s in build_suggestion_records(item, reading, filename, **options)]


def build_suggestion_records(item, reading, filename, *, field_map=None, messages=None, model_label='Claude',
                             provenance=None, own_label_origins=None):
    """Suggestion records for each reading that differs from the record; records are never edited.

    field_map maps canonical keys to host keys on both input and output.
    messages may be a mapping overriding English templates, or a callable
    (message_id, context) -> text for a host's own translation framework.
    Context contains canonical field, current/read values, literal uncertainty strings, and the
    provenance agent/requester. A callback owns all presentation; scientific text is never translated.
    own_label_origins: label origins that are the specimen's own, for example
    get_profile('sennen').own_label_origins; the others are suggested as associated_labels. An empty tuple keeps
    every label in the transcription. None keeps the 0.1.0a4 behaviour (every label in the transcription) and warns
    when a reading has labels of another origin: from 0.1.0a6 the profile's origins become the default.
    """
    from .profiles import get_profile
    provenance = {'model': model_label, 'image': filename, **dict(provenance or {})}
    agent, requester = str(provenance.get('agent') or ''), str(provenance.get('requester') or '')
    origins = () if own_label_origins is None else tuple(own_label_origins)
    if own_label_origins is None:
        profile_origins = {_norm(origin) for origin in get_profile('sennen').own_label_origins}
        if any(_norm(label.origin) not in profile_origins for label in reading.labels):
            import warnings
            warnings.warn('From herbarium-labels 0.1.0a6, labels of other origins are suggested as associated_labels. '
                          "Pass own_label_origins=get_profile('sennen').own_label_origins to adopt it now, "
                          'or own_label_origins=() to keep every label in the transcription.', FutureWarning, stacklevel=3)
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
                   'reading': value, 'filename': filename, 'model': model_label, 'agent': agent,
                   'requester': requester, 'uncertainties': '\n- '.join(doubts)}
        text = message('source_agent' if agent and requester else 'source', context) + ' ' + message(field, context)
        if doubts:
            text += message('uncertainties', context)
        return text

    def append(field, value, source):
        result.append(Suggestion(mapping[field], value, review(field, source, DOUBT_WORDS[field]), dict(provenance)))

    import re
    result = []
    own_keys = {_norm(origin) for origin in origins}
    own = [label for label in reading.labels if not own_keys or _norm(label.origin) in own_keys]
    associated = [label for label in reading.labels if label not in own]
    for field, labels in (('transcription', own), ('associated_labels', associated)):
        literal = '\n\n'.join(f'[{label.origin}]\n{label.literal_text.strip()}' for label in labels)
        if literal.strip() and not current(field).strip():
            append(field, literal, literal)
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

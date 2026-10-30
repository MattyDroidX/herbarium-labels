"""Label transcription with Claude: readings become pending reviews, never direct edits."""
import os
import re
import unicodedata

from pydantic import BaseModel, ConfigDict, model_validator
from .errors import TranscriptionError
from .imaging import ImagePolicy, encoded, prepare_images
from .legacy import LABEL_FIELDS, SHEET_FIELDS, rename_keys
from .provider import TranscriptionOptions, read_image

def _model_label(model):
    return {'claude-haiku-5-5': 'Claude Haiku 5.5', 'claude-sonnet-5-5': 'Claude Sonnet 5.5',
            'claude-opus-5-5': 'Claude Opus 5.5'}.get(model, model)


def __getattr__(name):
    # Compatibility attributes are resolved at access time, never at module import.
    if name == 'MODEL':
        return TranscriptionOptions().resolved_model
    if name == 'MODEL_LABEL':
        return _model_label(TranscriptionOptions().resolved_model)
    raise AttributeError(name)


ROMAN = {'I':1,'II':2,'III':3,'IV':4,'V':5,'VI':6,'VII':7,'VIII':8,'IX':9,'X':10,'XI':11,'XII':12}


class Label(BaseModel):
    model_config = ConfigDict(extra='forbid')

    @model_validator(mode='before')
    @classmethod
    def read_legacy_fields(cls, value):
        return rename_keys(value, LABEL_FIELDS)

    origin: str
    literal_text: str


class SheetReading(BaseModel):
    model_config = ConfigDict(extra='forbid')

    @model_validator(mode='before')
    @classmethod
    def read_legacy_fields(cls, value):
        return rename_keys(value, SHEET_FIELDS)

    labels: list[Label]
    general_accession_number: str
    order_number: str
    sennen_exsiccata_number: str
    shelfmark: str
    sennen_label_name: str
    porto_label_name: str
    locality: str
    altitude: str
    collection_date: str
    collector: str
    uncertainties: list[str]


PROMPT = """Transcribe the labels on this herbarium sheet from the F. Sennen collection at Herbário da Universidade do Porto.
The first image is the full sheet; the second is a crop of its lower label region.

There are usually two labels:
- A printed Sennen label ("Plantes d'Espagne — F. Sennen"): exsiccata number ("N.º ..."), scientific name with author, locality, altitude, and date.
- A partly handwritten label from Instituto de Botânica "Dr. Gonçalo Sampaio" (Porto): "N.º geral", "N.º de ordem", name, date, "Loc.", "Colector", and "Obs.". A number inside a red circle, sometimes followed by another number (for example 68/9), is the shelfmark.

Rules:
- Copy text as written without correcting names, spelling, or abbreviations, and without completing unreadable text. Preserve the source language; do not translate label text into English.
- Use an empty string for an absent or illegible field. Never invent information.
- In uncertainties, list each uncertain reading with its field, proposed reading, and reason.
- labels: one entry per label, with origin "Sennen", "Porto", or "other", and its complete literal_text with original line breaks. Keep separate labels separate."""


def estimated_cost(model, input_tokens, output_tokens, *, prices=None):
    from .pricing import estimate_cost
    if prices is None and model != TranscriptionOptions().resolved_model:
        return None
    return estimate_cost(input_tokens, output_tokens, prices=prices, model=model)


def enabled():
    return bool(os.environ.get('ANTHROPIC_API_KEY', '').strip())


def check_rate(user_id, *, limiter=None):
    """Compatibility hook: the host supplies any per-user rate policy."""
    if limiter is None:
        raise TranscriptionError('Supply a host-owned limiter when calling check_rate.')
    limiter(user_id)


def _jpeg(image, long_edge=1568):
    return encoded(image, long_edge)


def images(content):
    """Full sheet and lower-label crop; neither view is upscaled."""
    return prepare_images(content, ImagePolicy(lower_crop=0.6, draft_decode=True))


def read_labels(content, client=None, *, options=None, request_context=None):
    return read_image(content, profile='sennen', client=client,
                      options=options or TranscriptionOptions(),
                      request_context=request_context)


COLUMNS = [('filename', 'Filename')] + [
    (name, name.replace('_', ' ').capitalize()) for name in SheetReading.model_fields
]


def _norm(value):
    value = unicodedata.normalize('NFKD', str(value or '')).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', ' ', value).strip()


def _date(value):
    value = value or ''
    match = re.match(r'(\d{4})-(\d{2})-(\d{2})', value)
    if match:
        return int(match[1]), int(match[2]), int(match[3])
    match = re.search(r'(\d{1,2})\s*[-.\s]\s*([IVX]+)\s*[-.\s]\s*(\d{4})', value)
    if match and match[2] in ROMAN:
        return int(match[3]), ROMAN[match[2]], int(match[1])
    return None


def _shelfmark(value):
    return '/'.join(re.findall(r'\d+', value or ''))


def suggestions(item, reading, filename, *, field_map=None, messages=None, model_label=None, options=None,
                provenance=None, own_label_origins=None, records=False):
    """Host-mapped (field, value, review text) tuples, or Suggestion records with records=True; never edits records."""
    from .sennen_suggestions import build_suggestion_records
    built = build_suggestion_records(item, reading, filename, field_map=field_map, messages=messages,
                                     model_label=model_label if model_label is not None else
                                     _model_label((options or TranscriptionOptions()).resolved_model),
                                     provenance=provenance, own_label_origins=own_label_origins)
    return built if records else [(s.field, s.value, s.text) for s in built]

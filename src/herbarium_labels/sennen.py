"""Label transcription with Claude: readings become pending reviews, never direct edits."""
import base64
import io
import os
import re
import threading
import time
import unicodedata
from collections import defaultdict, deque
from difflib import SequenceMatcher

from PIL import Image, ImageOps
try:
    from pillow_heif import register_heif_opener
except ImportError:
    register_heif_opener = None
from pydantic import BaseModel, ConfigDict, model_validator
from .legacy import LABEL_FIELDS, SHEET_FIELDS, rename_keys

MODEL = os.environ.get('TRANSCRIPTION_MODEL', 'claude-haiku-5-5')
MODEL_LABEL = {'claude-haiku-5-5':'Claude Haiku 5.5', 'claude-sonnet-5-5':'Claude Sonnet 5.5',
               'claude-opus-5-5':'Claude Opus 5.5'}.get(MODEL, MODEL)
RATE_LIMIT, RATE_WINDOW = 30, 600  # Per person: 30 photographs every 10 minutes.
ROMAN = {'I':1,'II':2,'III':3,'IV':4,'V':5,'VI':6,'VII':7,'VIII':8,'IX':9,'X':10,'XI':11,'XII':12}

if register_heif_opener is not None:
    register_heif_opener()
_calls = defaultdict(deque)
_calls_lock = threading.Lock()
_slots = threading.BoundedSemaphore(2)  # The server sends at most two photographs at a time.


class TranscriptionError(Exception):
    pass


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
The first image is the full sheet; the second is an enlarged crop of its lower label region.

There are usually two labels:
- A printed Sennen label ("Plantes d'Espagne — F. Sennen"): exsiccata number ("N.º ..."), scientific name with author, locality, altitude, and date.
- A partly handwritten label from Instituto de Botânica "Dr. Gonçalo Sampaio" (Porto): "N.º geral", "N.º de ordem", name, date, "Loc.", "Colector", and "Obs.". A number inside a red circle, sometimes followed by another number (for example 68/9), is the shelfmark.

Rules:
- Copy text as written without correcting names, spelling, or abbreviations, and without completing unreadable text. Preserve the source language; do not translate label text into English.
- Use an empty string for an absent or illegible field. Never invent information.
- In uncertainties, list each uncertain reading with its field, proposed reading, and reason.
- labels: one entry per label, with origin "Sennen", "Porto", or "other", and its complete literal_text with original line breaks. Keep separate labels separate."""


def estimated_cost(model, input_tokens, output_tokens):
    # Model-specific tariffs are supplied by the host, never guessed.
    if model != MODEL:
        return None
    from .bryophytes import cost_text
    value = cost_text(input_tokens, output_tokens)
    return float(value.split()[0]) if value.endswith(' USD') else None


def enabled():
    return bool(os.environ.get('ANTHROPIC_API_KEY', '').strip())


def check_rate(user_id):
    now = time.monotonic()
    with _calls_lock:
        calls = _calls[user_id]
        while calls and now - calls[0] > RATE_WINDOW:
            calls.popleft()
        if len(calls) >= RATE_LIMIT:
            raise TranscriptionError('Transcription rate limit reached. Wait a few minutes and try again.')
        calls.append(now)


def _jpeg(image, long_edge=1568):
    image = image.copy()
    scale = long_edge / max(image.size)
    image = image.resize((max(1, round(image.width * scale)), max(1, round(image.height * scale))), Image.LANCZOS)
    buffer = io.BytesIO()
    image.save(buffer, 'JPEG', quality=92)
    return {'type':'image', 'source':{'type':'base64', 'media_type':'image/jpeg',
                                      'data':base64.standard_b64encode(buffer.getvalue()).decode()}}


def images(content):
    """The sheet and an enlarged crop of its lower part, where the labels are."""
    with Image.open(io.BytesIO(content)) as original:
        if original.format in ('JPEG', 'MPO'):
            original.draft('RGB', (3000, 3000))
        sheet = ImageOps.exif_transpose(original).convert('RGB')
    labels = sheet.crop((0, round(sheet.height * 0.6), sheet.width, sheet.height))
    return [_jpeg(sheet), _jpeg(labels)]


def read_labels(content, client=None):
    import anthropic
    try:
        blocks = images(content)
    except (OSError, ValueError, Image.DecompressionBombError):
        raise TranscriptionError('Could not prepare this image for transcription.') from None
    client = client or anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'], timeout=120, max_retries=2)
    if not _slots.acquire(timeout=60):
        raise TranscriptionError('The transcription service is busy. Try again shortly.')
    try:
        response = client.messages.parse(model=MODEL, max_tokens=16000, output_format=SheetReading,
            messages=[{'role':'user', 'content':blocks + [{'type':'text', 'text':PROMPT}]}])
    except anthropic.APIError:
        raise TranscriptionError('The transcription service did not respond. Try again later.') from None
    finally:
        _slots.release()
    if response.stop_reason != 'end_turn' or response.parsed_output is None:
        raise TranscriptionError('Could not obtain a complete reading of this image.')
    return response.parsed_output, {'input_tokens':response.usage.input_tokens, 'output_tokens':response.usage.output_tokens}


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


def _doubts(reading, *words):
    found = [d for d in reading.uncertainties if any(w in _norm(d) for w in words)]
    return ('\n\nUncertainties flagged by the model:\n- ' + '\n- '.join(found)) if found else ''


def suggestions(item, reading, filename):
    """(field, value, review text) for each reading that differs from the record."""
    source = f'Automatic suggestion ({MODEL_LABEL}) from image {filename}. Check the image before accepting.'
    result = []
    if not (item.get('transcription') or '').strip():
        text = '\n\n'.join(f'[{label.origin}]\n{label.literal_text.strip()}' for label in reading.labels)
        if text.strip():
            result.append(('transcription', text, source + ' Literal transcription das labels.' + _doubts(reading, '')))
    read_shelfmark = _shelfmark(reading.shelfmark)
    if read_shelfmark and read_shelfmark != _shelfmark(item.get('shelfmark')):
        result.append(('shelfmark', read_shelfmark, f"{source} Current shelfmark: «{item.get('shelfmark') or '—'}». Reading: «{reading.shelfmark}»." + _doubts(reading, 'shelfmark', 'circle')))
    read_exs, current_exs = re.sub(r'\D', '', reading.sennen_exsiccata_number), (item.get('exsiccata_number') or '').strip()
    if read_exs and read_exs != current_exs:
        result.append(('exsiccata_number', read_exs, f"{source} Current exsiccata number: «{current_exs or '—'}». Sennen label reading: «{reading.sennen_exsiccata_number}»." + _doubts(reading, 'exsiccata', 'collection_number')))
    read_date, current_date = _date(reading.collection_date), item.get('collection_date') or ''
    if reading.collection_date and read_date and (not current_date or (_date(current_date) and read_date != _date(current_date))):
        result.append(('collection_date', reading.collection_date, f"{source} Current date: «{current_date or '—'}». Reading: «{reading.collection_date}»." + _doubts(reading, 'date')))
    current_locality = item.get('original_locality') or ''
    if reading.locality and SequenceMatcher(None, _norm(reading.locality), _norm(current_locality)).ratio() < 0.9:
        result.append(('original_locality', reading.locality, f"{source} Current original locality: «{current_locality or '—'}». Reading: «{reading.locality}»." + _doubts(reading, 'local', 'loc')))
    return result

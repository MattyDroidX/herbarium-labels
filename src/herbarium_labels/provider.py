"""One structured Claude request with caller-owned configuration and resources."""
from contextlib import nullcontext
from dataclasses import dataclass
import os

from PIL import Image
from pydantic import ValidationError

from .errors import TranscriptionError
from .imaging import prepare_images
from .profiles import get_profile
from .pricing import TokenPrices
from .prompts import effective_prompt


DEFAULT_MAX_RETRIES = 2


@dataclass(frozen=True)
class TranscriptionOptions:
    model: str | None = None
    max_tokens: int = 16000
    timeout: float = 120
    max_retries: int = DEFAULT_MAX_RETRIES
    workers: int = 6
    prices: TokenPrices | None = None
    notes_language: str | None = None

    def __post_init__(self):
        import math
        if self.notes_language is not None and self.notes_language not in ('en', 'pt', 'es'):
            raise ValueError('notes_language must be en, pt, es, or None.')
        if self.prices is not None and not isinstance(self.prices, TokenPrices):
            raise ValueError('prices must be a TokenPrices instance.')
        if self.model is None:
            object.__setattr__(self, 'model', os.environ.get('TRANSCRIPTION_MODEL', 'claude-haiku-5-5'))
        if self.model is not None and (not isinstance(self.model, str) or not self.model.strip()):
            raise ValueError('model must be a nonempty string.')
        if type(self.max_tokens) is not int or self.max_tokens <= 0:
            raise ValueError('max_tokens must be a positive integer.')
        if not math.isfinite(self.timeout) or self.timeout <= 0:
            raise ValueError('timeout must be finite and positive.')
        if type(self.max_retries) is not int or self.max_retries < 0:
            raise ValueError('max_retries must be a nonnegative integer.')
        if type(self.workers) is not int or self.workers <= 0:
            raise ValueError('workers must be a positive integer.')

    @property
    def resolved_model(self):
        return self.model


def create_client(options):
    key = os.environ.get('ANTHROPIC_API_KEY', '').strip()
    if not key:
        raise TranscriptionError('Set ANTHROPIC_API_KEY in the environment or supply a client.')
    try:
        import anthropic
    except ImportError:
        raise TranscriptionError('Install herbarium-labels[claude] to use Claude.') from None
    return anthropic.Anthropic(api_key=key, timeout=options.timeout, max_retries=options.max_retries)


def close_client(client):
    close = getattr(client, 'close', None)
    if close is not None:
        close()


def request_reading(client, blocks, profile, options, request_context=None):
    with request_context() if request_context else nullcontext():
        return _request_reading(client, blocks, profile, options)


def _request_reading(client, blocks, profile, options):
    try:
        import anthropic
    except ImportError:
        anthropic = None  # Injected offline clients need no optional SDK.
    try:
        response = client.messages.parse(model=options.resolved_model, max_tokens=options.max_tokens,
            output_format=profile.schema, messages=[{'role': 'user',
            'content': blocks + [{'type': 'text', 'text': effective_prompt(profile, options.notes_language)}]}])
    except Exception as error:
        if anthropic is not None and isinstance(error, anthropic.APIError):
            raise TranscriptionError('The transcription service did not respond.') from None
        raise
    usage = getattr(response, 'usage', None)
    counts = {name: getattr(usage, name, 0) for name in ('input_tokens', 'output_tokens')}
    if response.stop_reason != 'end_turn' or response.parsed_output is None:
        raise TranscriptionError('Could not obtain a complete reading of this image.', **counts)
    try:
        reading = profile.schema.model_validate(response.parsed_output)
    except ValidationError:
        raise TranscriptionError('The transcription service returned an invalid reading.', **counts) from None
    return reading, counts


def read_image(content, *, profile='po-bryophytes', client=None, options=None, request_context=None):
    """Return (validated reading, usage); no hidden limiter, file writes, or client closure.

    A client created here is closed here. An injected client remains caller-owned.
    request_context is an optional factory of context managers (for example a
    host-owned semaphore); per-user rate policies belong to the host.
    """
    profile, options = get_profile(profile), options or TranscriptionOptions()
    try:
        blocks = prepare_images(content, profile.images)
    except (OSError, ValueError, Image.DecompressionBombError):
        raise TranscriptionError('Could not prepare this image for transcription.') from None
    owned = client is None
    if owned:
        client = create_client(options)
    try:
        return request_reading(client, blocks, profile, options, request_context)
    finally:
        if owned:
            close_client(client)

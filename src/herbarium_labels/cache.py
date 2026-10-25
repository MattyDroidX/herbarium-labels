"""Conservative reuse of readings without replacing existing research results."""
from contextlib import contextmanager
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

from .legacy import LEGACY_LOCK_NAME, normalize_record


def digest(content):
    return hashlib.sha256(content).hexdigest()


def identity(path, configuration):
    serialized = json.dumps(configuration, sort_keys=True, ensure_ascii=False,
                            separators=(',', ':')).encode('utf-8')
    return {'version': 1, 'image_sha256': digest(path.read_bytes()),
            'configuration_sha256': digest(serialized)}


def reusable(target, filename, expected, schema):
    if not target.exists():
        return False
    try:
        item = normalize_record(json.loads(target.read_text(encoding='utf-8')))
        if not isinstance(item, dict):
            raise ValueError('JSON must be an object.')
        schema.model_validate(item['reading'])
        if item['filename'] != filename or item.get('cache') != expected:
            raise ValueError('Source/configuration is missing or different.')
        if any(type(item[key]) is not int or item[key] < 0
               for key in ('input_tokens', 'output_tokens')):
            raise ValueError('Invalid token count.')
    except (ValueError, KeyError, TypeError) as error:
        raise ValueError(
            f'{target.name}: Existing JSON is incompatible or has no verifiable identity. '
            'Keep it for review/report and use a new output directory '
            '(for batch conflicts, use transcribe --output DIR and then report).'
        ) from error
    return True


@contextmanager
def output_lock(output):
    """Exclusive across processes; an interrupted run may leave a lock for review."""
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    lock = output / '.transcription.lock'
    if (output / LEGACY_LOCK_NAME).exists():
        raise ValueError('Output is locked by a legacy run. Check for an active process before removing the lock.')
    try:
        stream = lock.open('x', encoding='utf-8')
    except FileExistsError:
        raise ValueError('Output is locked by .transcription.lock. Check for an '
                         'active run before removing an abandoned lock.') from None
    try:
        with stream:
            stream.write('Transcription in progress. Do not remove during an active run.\n')
        yield
    finally:
        lock.unlink()


@dataclass(frozen=True)
class TaskResult:
    photos: int = 0
    failures: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    reused: int = 0

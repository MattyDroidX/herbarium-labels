"""Explicit reuse of earlier readings without changing their JSON or provenance."""
from datetime import datetime, timezone
import json
from pathlib import Path
import re

from .cache import digest, reusable
from .legacy import normalize_record

_LEDGER = '.accepted-existing.json'
_SHA256 = re.compile(r'[0-9a-f]{64}')


class AcceptedReadings:
    def __init__(self, output):
        self.path = Path(output) / _LEDGER
        self.records = {}
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding='utf-8'))
                if data['version'] != 1 or not isinstance(data['records'], dict):
                    raise ValueError
                for name, entry in data['records'].items():
                    if Path(name).name != name or not name.endswith('.json'):
                        raise ValueError
                    if any(not isinstance(entry[key], str) or not _SHA256.fullmatch(entry[key])
                           for key in ('record_sha256', 'image_sha256')):
                        raise ValueError
                    if not isinstance(entry['profile'], str):
                        raise ValueError
                self.records = data['records']
            except (ValueError, KeyError, TypeError):
                raise ValueError('Invalid existing-reading acceptance record; restore it before continuing.') from None
        self.pending = {}
        self.checks = []

    def reusable(self, target, image, expected, profile, *, accept_existing=False):
        entry = self.records.get(target.name)
        if not target.exists():
            if entry:
                raise ValueError(f'{target.name}: an accepted reading is missing; restore it before continuing.')
            return False
        content = target.read_bytes()
        try:
            item = normalize_record(json.loads(content))
            profile.schema.model_validate(item['reading'])
            if item['filename'] != image.name or item.get('profile', profile.name) != profile.name:
                raise ValueError
            if any(type(item[key]) is not int or item[key] < 0 for key in ('input_tokens', 'output_tokens')):
                raise ValueError
            old_cache = item.get('cache')
            if old_cache is not None and not isinstance(old_cache, dict):
                raise ValueError
        except (ValueError, KeyError, TypeError):
            raise ValueError(f'{target.name}: invalid existing reading; acceptance cannot bypass validation. Keep it and use a new output directory.') from None
        if old_cache and old_cache.get('image_sha256') not in (None, expected['image_sha256']):
            raise ValueError(f'{target.name}: source image differs; acceptance cannot bypass a recorded image hash. Keep it and use a new output directory.')
        if entry:
            if entry['profile'] != profile.name or entry['image_sha256'] != expected['image_sha256']:
                raise ValueError(f'{target.name}: accepted profile/source image differs; restore the original.')
            if entry['record_sha256'] == digest(content):
                self.checks.append((target, digest(content), image, expected['image_sha256']))
                return True
            if not accept_existing:
                raise ValueError(f'{target.name}: accepted reading changed; review it and use --accept-existing again.')
        else:
            try:
                if reusable(target, image.name, expected, profile.schema):
                    return True
            except ValueError:
                if not accept_existing:
                    raise
        self.pending[target.name] = {
            'profile': profile.name, 'record_sha256': digest(content),
            'image_sha256': expected['image_sha256'],
            'historical_source_verified': bool(old_cache and old_cache.get('image_sha256') == expected['image_sha256']),
            'accepted_at': datetime.now(timezone.utc).isoformat(),
            'decision': 'reuse-existing-reading; not a new transcription or scientific approval',
            'previous_acceptance': entry,
        }
        self.checks.append((target, digest(content), image, expected['image_sha256']))
        return True

    def commit(self):
        """Called under the output lock, after the complete selected-batch preflight."""
        for target, record_hash, image, image_hash in self.checks:
            if digest(target.read_bytes()) != record_hash or digest(image.read_bytes()) != image_hash:
                raise ValueError('An existing reading or image changed during preflight; no acceptance was saved.')
        if self.pending:
            data = {'version': 1, 'records': {**self.records, **self.pending}}
            partial = self.path.with_suffix('.json.partial')
            partial.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
            partial.replace(self.path)
            self.records = data['records']
            self.pending.clear()

    def validate_report(self, target, image=None):
        entry = self.records.get(target.name)
        if entry and (digest(target.read_bytes()) != entry['record_sha256'] or
                      (image is not None and digest(image.read_bytes()) != entry['image_sha256'])):
            raise ValueError(f'{target.name}: reading/image changed after explicit acceptance; review before reporting.')
        return entry

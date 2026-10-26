"""Bundled presentation catalogues; literal evidence is never translated here."""
from importlib.resources import files
import json

from .profiles import get_profile


def load_messages(lang, *, kind='report', profile=None):
    """Return a fresh template mapping for en/pt/es and a report or Sennen review.

    Reports default to po-bryophytes; reviews default to sennen. External
    profiles receive translated common report labels and their own column names.
    Callers may override the returned mapping without changing later loads.
    """
    if lang not in ('en', 'pt', 'es'):
        raise ValueError('lang must be en, pt, or es.')
    if kind not in ('report', 'review'):
        raise ValueError('kind must be report or review.')
    profile = get_profile(profile if profile is not None else
                          ('sennen' if kind == 'review' else 'po-bryophytes'))
    data = json.loads(files('herbarium_labels').joinpath('locales', lang + '.json').read_text(encoding='utf-8'))
    if kind == 'review':
        if profile.name not in data['review']:
            raise ValueError('Bundled review messages are available only for sennen.')
        return dict(data['review'][profile.name])
    columns = {f'field.{key}': label for key, label in profile.columns if key is not None}
    columns.update(data['report']['profiles'].get(profile.name, {}))
    if profile.name not in data['report']['profiles'] and 'field.filename' in columns:
        columns['field.filename'] = data['report']['common']['column.filename']
    return {**data['report']['common'], **columns}

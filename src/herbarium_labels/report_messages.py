"""Resolve report presentation once, independently of literal specimen evidence."""
from collections.abc import Mapping
import re
from types import MappingProxyType

DEFAULT_REPORT_MESSAGES = MappingProxyType({
    'sheet.literal': 'Literal transcription',
    'sheet.fields': 'Fields',
    'column.filename': 'Filename',
    'column.image': 'Image',
    'column.literal_text': 'Literal transcription',
    'column.handwritten_notes': 'Handwritten notes',
    'column.uncertainties': 'Reading uncertainties',
    'column.reviewed': 'Reviewed',
    'pdf.title': '{profile} transcription review',
    'review.choices': '[ ] yes    [ ] corrected',
})


def report_messages(profile, messages=None):
    """Accept overrides or (message_id, context) -> text; include field.<canonical_key>."""
    defaults = {**DEFAULT_REPORT_MESSAGES,
                **{f'field.{key}': label for key, label in profile.columns if key is not None}}
    if messages is not None and not isinstance(messages, Mapping) and not callable(messages):
        raise TypeError('Report messages must be a mapping or callable.')
    if isinstance(messages, Mapping) and messages.keys() - defaults.keys():
        raise ValueError('Unknown report message identifier.')
    result = {}
    for key, default in defaults.items():
        context = {'profile': profile.name, 'default': default}
        if callable(messages):
            text = messages(key, dict(context))
        else:
            template = (messages or {}).get(key, default)
            if not isinstance(template, str):
                raise ValueError('Report messages must be strings.')
            text = template.format_map(context)
        if not isinstance(text, str) or not text.strip():
            raise ValueError('Report messages must be nonempty strings.')
        result[key] = text
    titles = result['sheet.literal'], result['sheet.fields']
    if any(len(title) > 31 or re.search(r'[\\/*?:\[\]]', title) or
           title.startswith("'") or title.endswith("'") for title in titles):
        raise ValueError('Translated Excel sheet names must be valid and at most 31 characters.')
    if titles[0].casefold() == titles[1].casefold():
        raise ValueError('Translated Excel sheet names must be distinct.')
    return MappingProxyType(result)

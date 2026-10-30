"""Collection contracts; profiles never imply automatic handwriting attribution."""
from dataclasses import dataclass, field
from importlib.metadata import entry_points
from threading import RLock

from .errors import TranscriptionError
import re

from pydantic import BaseModel

from .imaging import ImagePolicy


@dataclass(frozen=True)
class TranscriptionProfile:
    name: str
    prompt: str
    schema: type[BaseModel]
    columns: tuple[tuple[str | None, str], ...]
    images: ImagePolicy = field(default_factory=ImagePolicy)
    # Label origins that belong to the specimen itself; other labels (exchange, determination slips, labels sent
    # with another specimen) are suggested as associated labels. Empty: every label is the specimen's own.
    own_label_origins: tuple[str, ...] = ()

    def __post_init__(self):
        object.__setattr__(self, 'columns', tuple(tuple(column) for column in self.columns))
        object.__setattr__(self, 'own_label_origins', tuple(str(origin) for origin in self.own_label_origins))
        if not re.fullmatch(r'[a-z][a-z0-9-]*', self.name):
            raise ValueError('Profile names must use lowercase words separated by hyphens.')
        if not self.prompt.strip() or not issubclass(self.schema, BaseModel):
            raise ValueError('A profile requires a prompt and a Pydantic schema.')
        keys = [key for key, label in self.columns if key is not None]
        if len(keys) != len(set(keys)):
            raise ValueError('Profile columns must have unique field names.')
        if any(key != 'filename' and key not in self.schema.model_fields for key in keys):
            raise ValueError('Profile columns must refer to schema fields or filename.')
        fields = self.schema.model_fields
        if 'uncertainties' not in fields or not ({'literal_text', 'labels'} & fields.keys()):
            raise ValueError('Profiles must provide uncertainties and literal_text or labels.')

    def literal(self, reading):
        if 'literal_text' in reading:
            return reading['literal_text']
        return '\n\n'.join(f"[{label['origin']}]\n{label['literal_text']}"
                            for label in reading['labels'])


def po_bryophytes_profile():
    from . import bryophytes
    return TranscriptionProfile('po-bryophytes', bryophytes.PROMPT, bryophytes.BryophyteReading,
                                tuple(bryophytes.COLUMNS))


def sennen_profile():
    from . import sennen
    return TranscriptionProfile('sennen', sennen.PROMPT, sennen.SheetReading,
                                tuple(sennen.COLUMNS), ImagePolicy(lower_crop=0.6, draft_decode=True),
                                own_label_origins=('Sennen', 'Porto'))


_BUILTINS = {'po-bryophytes': po_bryophytes_profile, 'sennen': sennen_profile}
_REGISTRY = dict(_BUILTINS)
_REGISTRY_LOCK = RLock()
_GROUP = 'herbarium_labels.profiles'


def _plugins():
    result = {}
    for ep in entry_points(group=_GROUP):
        # This distribution advertises its built-ins too; source checkouts need no installation.
        own = _BUILTINS.get(ep.name)
        if own and ep.value == f'{own.__module__}:{own.__name__}':
            continue
        if ep.name in _BUILTINS or ep.name in result:
            raise TranscriptionError(f'Duplicate installed profile name: {ep.name!r}.')
        if not re.fullmatch(r'[a-z][a-z0-9-]*', ep.name):
            raise TranscriptionError('Installed profile names must use lowercase words and hyphens.')
        result[ep.name] = ep
    return result


def register_profile(profile, *, name=None):
    """Register a profile or zero-argument factory in this process; reject collisions."""
    if isinstance(profile, TranscriptionProfile):
        if name is not None and name != profile.name:
            raise ValueError('Registered name must match the profile name.')
        name = profile.name
    elif not callable(profile) or not isinstance(name, str):
        raise ValueError('Supply a profile, or a factory with an explicit name.')
    if not re.fullmatch(r'[a-z][a-z0-9-]*', name):
        raise ValueError('Profile names must use lowercase words separated by hyphens.')
    plugins = _plugins()
    with _REGISTRY_LOCK:
        if name in _REGISTRY or name in plugins:
            raise ValueError(f'Profile name is already registered: {name!r}.')
        _REGISTRY[name] = profile
    return profile


def list_profiles():
    """List names without executing third-party profile factories."""
    plugins = _plugins()
    with _REGISTRY_LOCK:
        overlap = plugins.keys() & _REGISTRY.keys()
        if overlap:
            raise TranscriptionError(f'Duplicate installed/registered profile name: {sorted(overlap)[0]!r}.')
        return tuple(sorted(_REGISTRY.keys() | plugins.keys()))


def get_profile(profile='po-bryophytes'):
    if isinstance(profile, TranscriptionProfile):
        return profile
    plugins = _plugins()
    with _REGISTRY_LOCK:
        factory = _REGISTRY.get(profile)
    if factory is not None and profile in plugins:
        raise TranscriptionError(f'Duplicate installed/registered profile name: {profile!r}.')
    if factory is None:
        if profile not in plugins:
            raise ValueError(f'Unknown transcription profile: {profile!r}.')
        try:
            factory = plugins[profile].load()
        except Exception:
            raise TranscriptionError(f'Could not load installed profile: {profile!r}.') from None
    if isinstance(factory, TranscriptionProfile):
        result = factory
    elif callable(factory):
        result = factory()
    else:
        raise TranscriptionError('Profile entry points must provide a profile or a callable factory.')
    if not isinstance(result, TranscriptionProfile) or result.name != profile:
        raise TranscriptionError('Profile factories must return a matching TranscriptionProfile.')
    return result

"""Documentary catalogue; does not perform automatic handwriting attribution."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator, field_validator
from .legacy import PERSON_STATUSES, ATTRIBUTION_STATUSES

class Entry(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)

class Source(Entry):
    source_id: str = Field(min_length=1)
    citation: str = Field(min_length=1)
    locator: str = Field(min_length=1)

class Person(Entry):
    person_id: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    aliases: list[str] = Field(default_factory=list)
    documented_roles: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    status: Literal['draft', 'reviewed'] = 'draft'

    @field_validator('status', mode='before')
    @classmethod
    def read_legacy_status(cls, value):
        return PERSON_STATUSES.get(value, value) if isinstance(value, str) else value


    @model_validator(mode='after')
    def sourced(self):
        if (self.status == 'reviewed' or self.documented_roles) and not self.source_ids:
            raise ValueError('A reviewed person or documented historical role requires sources.')
        return self

class HandSample(Entry):
    sample_id: str = Field(min_length=1)
    hand_id: str = Field(min_length=1)
    image_sha256: str = Field(pattern=r'^[a-f0-9]{64}$')
    source_ids: list[str] = Field(min_length=1)
    literal_text: str
    local_use_allowed: bool = False
    api_use_allowed: bool = False
    redistribution_allowed: bool = False
    rights_statement: str = Field(min_length=1)
    reviewed_by: str = Field(min_length=1)

class HandAttribution(Entry):
    attribution_id: str = Field(min_length=1)
    hand_id: str = Field(min_length=1)
    person_id: str = Field(min_length=1)
    status: Literal['candidate', 'confirmed', 'contested'] = 'candidate'

    @field_validator('status', mode='before')
    @classmethod
    def read_legacy_status(cls, value):
        return ATTRIBUTION_STATUSES.get(value, value) if isinstance(value, str) else value

    sample_ids: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    evidence: str = ''
    reviewed_by: str | None = None

    @model_validator(mode='after')
    def documented_confirmation(self):
        if self.status == 'confirmed' and not (self.sample_ids and self.source_ids and self.evidence and self.reviewed_by):
            raise ValueError('Confirmation requires a sample, source, evidence, and reviewer.')
        return self

class Catalog(Entry):
    schema_version: Literal['0.2.0'] = '0.2.0'

    @field_validator('schema_version', mode='before')
    @classmethod
    def read_legacy_version(cls, value):
        return '0.2.0' if value == '0.1.0' else value

    persons: list[Person] = Field(default_factory=list)
    sources: list[Source] = Field(default_factory=list)
    samples: list[HandSample] = Field(default_factory=list)
    attributions: list[HandAttribution] = Field(default_factory=list)

    @model_validator(mode='after')
    def references(self):
        def ids(items, field):
            result = [getattr(item, field) for item in items]
            if len(set(result)) != len(result):
                raise ValueError('Duplicate catalogue IDs.')
            return set(result)
        persons = ids(self.persons, 'person_id')
        sources = ids(self.sources, 'source_id')
        samples = ids(self.samples, 'sample_id')
        ids(self.attributions, 'attribution_id')
        hands = {sample.hand_id for sample in self.samples}
        for item in [*self.persons, *self.samples, *self.attributions]:
            if not set(item.source_ids) <= sources:
                raise ValueError('Unknown source reference.')
        for item in self.attributions:
            if item.person_id not in persons or not set(item.sample_ids) <= samples:
                raise ValueError('Unknown person or sample.')
            if any(sample.hand_id != item.hand_id for sample in self.samples if sample.sample_id in item.sample_ids):
                raise ValueError('Sample belongs to another hand.')
            if item.status == 'confirmed' and item.hand_id not in hands:
                raise ValueError('Confirmed hand has no sample.')
        return self

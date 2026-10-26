"""PO/LISU scientific contract and compatible Python entry points."""
import os
from typing import Literal
from importlib.metadata import version

from pydantic import BaseModel, ConfigDict, model_validator
from .legacy import BRYOPHYTE_FIELDS, rename_keys
from .imaging import upright, encoded

MODEL = os.environ.get('TRANSCRIPTION_MODEL', 'claude-haiku-5-5')

from .pricing import cost_text


class BryophyteReading(BaseModel):
    model_config = ConfigDict(extra='forbid')

    @model_validator(mode='before')
    @classmethod
    def read_legacy_fields(cls, value):
        return rename_keys(value, BRYOPHYTE_FIELDS)

    rotation_degrees: Literal[0, 90, 180, 270]
    herbarium: str
    collection_series: str
    name_as_written: str
    species: str
    taxonomic_author: str
    determiner: str
    country_province: str
    locality: str
    ecology: str
    altitude: str
    utm: str
    date_as_written: str
    date_iso: str
    collector: str
    collection_number: str
    handwritten_notes: str
    literal_text: str
    uncertainties: list[str]


PROMPT = """This photograph shows a bryophyte herbarium label, usually from "Herbário da Universidade do Porto — Instituto de Botânica Dr. Gonçalo Sampaio (PO)", the "Briófitas das comunidades de Sphagnum" series, or the herbarium of Museu, Laboratório e Jardim Botânico de Lisboa (LISU). The label may be rotated.

Usual fields: scientific name with author; "Det." (determiner); "Stat." (station: a country/province code such as "Lu: TM", "Lu: Mi", or "Be:", followed by locality); "Ecol." (ecology); "Alt."; "UTM"; "Data" (date); "Leg." (collector); "Nº" (collection number).

Rules:
- Copy the text exactly as written. Do not correct names, spelling, or abbreviations, and do not complete unreadable text. Use an empty string for an absent or illegible field. Never invent information. Preserve the source language; do not translate label text into English.
- rotation_degrees: clockwise degrees (0, 90, 180, or 270) needed to make the photograph readable.
- name_as_written: the entire name as it appears, including varieties, forms, and parenthesized synonyms. species: the scientific name only (genus, epithet, and infraspecific designation, without author). taxonomic_author: the author only.
- country_province: the complete country/province code at the start of "Stat." (for example "Lu: TM", "Lu: Mi", "Be:"), even when its colon is absent. locality: the remaining text without that code.
- date_iso: YYYY-MM-DD only when the date is unambiguous. These labels often use YY/MM/DD (for example 89/05/09 = 1989-05-09), but also D/M/YY (for example 15/3/93). If the order is uncertain, leave date_iso empty and explain in uncertainties.
- handwritten_notes: handwritten text, such as name corrections, "Rev.", or signatures, with its position.
- literal_text: the most faithful possible transcription, formatted as follows:
  * first line: an editorial origin marker, [Porto] for PO, [LISU] for Lisbon, or [Other: name];
  * then reproduce each line in label order, including printed field labels (Det., Stat., Ecol., Alt., UTM, Data, Leg., Nº);
  * fields on the same label line remain on the same line, separated by four spaces;
  * place handwriting where it appears, within the editorial marker [handwritten: ...];
  * if the photograph contains several labels, use a separate block for each, separated by a blank line. Do not merge them.
  Example format (retain the original-language text):
  [Porto]
  Herbário da Universidade do Porto
  Instituto de Botânica Dr. Gonçalo Sampaio (PO)
  Briófitas das comunidades de Sphagnum
  Sphagnum palustre L.
  Det. Ana Séneca
  Stat. Lu: TM, Vila Real, Lamas de Olo, PNSA, antes da ponte da aldeia
  Ecol. com Molinia
  Alt. 1000 m    UTM PF0180    Data 15/3/93
  Leg. Ana Séneca    Nº 565
- uncertainties: genuinely uncertain readings only, identifying the field, proposed reading, and reason. Do not list confirmations or absent fields."""

COLUMNS = [('filename', 'Filename'), (None, 'Image'), ('herbarium', 'Herbarium'), ('collection_series', 'Collection / series'),
           ('name_as_written', 'Name as written'), ('species', 'Species'), ('taxonomic_author', 'Taxonomic author'),
           ('determiner', 'Determiner'), ('country_province', 'Country / province'), ('locality', 'Locality (Stat.)'),
           ('ecology', 'Ecology'), ('altitude', 'Altitude'), ('utm', 'UTM'), ('date_as_written', 'Date as written'),
           ('date_iso', 'ISO date'), ('collector', 'Collector (Leg.)'), ('collection_number', 'Nº'), ('handwritten_notes', 'Handwritten notes'),
           ('uncertainties', 'Reading uncertainties'), ('literal_text', 'Literal text'), (None, 'Reviewed')]



def _settings(profile=None, options=None):
    from .profiles import get_profile
    from .provider import TranscriptionOptions
    return get_profile(profile or 'po-bryophytes'), options or TranscriptionOptions(model=MODEL)


def cache_configuration(profile=None, options=None):
    from .pipeline import cache_configuration as configuration
    profile, options = _settings(profile, options)
    return configuration(profile, options, version_fn=version)


def transcribe(args, *, profile=None, options=None, client=None):
    from . import pipeline
    profile, options = _settings(profile or getattr(args, 'profile', None), options)
    return pipeline.transcribe(args, profile=profile, options=options, client=client,
                               _configuration=cache_configuration(profile, options))


def read_records(output, *, profile='po-bryophytes'):
    from .pipeline import read_records as load
    return load(output, profile=profile)


def report(args, *, profile=None):
    from .pipeline import report as render
    return render(args, profile=profile or getattr(args, 'profile', 'po-bryophytes'))


def batch(args, *, profile=None, options=None, client=None):
    from . import pipeline
    profile, options = _settings(profile or getattr(args, 'profile', None), options)
    return pipeline.batch(args, profile=profile, options=options, client=client,
                          _configuration=cache_configuration(profile, options))


def main():
    from .cli import main as run
    return run()


if __name__ == '__main__':
    main()


def safe_photo(folder, name):
    from .pipeline import safe_photo as resolve
    return resolve(folder, name)


def photos(folder):
    from .pipeline import photos as list_photos
    return list_photos(folder)


def build_pdf(target, data, images_dir):
    from .pipeline import build_pdf as render
    return render(target, data, images_dir)

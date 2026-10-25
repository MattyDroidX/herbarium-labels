"""Read legacy Portuguese keys without rewriting source files or literal text."""

RECORD_SCHEMA_VERSION = '0.2.0'
LEGACY_LOCK_NAME = '.transcricao.lock'
BRYOPHYTE_FIELDS = {
    'rotacao_para_ler': 'rotation_degrees', 'herbario': 'herbarium',
    'serie_colecao': 'collection_series', 'nome_como_escrito': 'name_as_written',
    'especie': 'species', 'autor': 'taxonomic_author', 'determinador': 'determiner',
    'pais_provincia': 'country_province', 'localidade': 'locality', 'ecologia': 'ecology',
    'data_como_escrita': 'date_as_written', 'data_iso': 'date_iso', 'coletor': 'collector',
    'numero': 'collection_number', 'anotacoes_manuscritas': 'handwritten_notes',
    'texto_literal': 'literal_text', 'duvidas': 'uncertainties',
}
SHEET_FIELDS = {
    'etiquetas': 'labels', 'numero_geral_po': 'general_accession_number',
    'numero_ordem': 'order_number', 'numero_exsiccata_sennen': 'sennen_exsiccata_number',
    'cota': 'shelfmark', 'nome_etiqueta_sennen': 'sennen_label_name',
    'nome_etiqueta_porto': 'porto_label_name', 'localidade': 'locality',
    'data_colheita': 'collection_date', 'coletor': 'collector', 'duvidas': 'uncertainties',
}
LABEL_FIELDS = {'origem': 'origin', 'texto_literal': 'literal_text'}
ENVELOPE_FIELDS = {'ficheiro': 'filename', 'modelo': 'model', 'segundos': 'elapsed_seconds',
                   'leitura': 'reading'}
PERSON_STATUSES = {'rascunho': 'draft', 'revisado': 'reviewed'}
ATTRIBUTION_STATUSES = {'candidata': 'candidate', 'confirmada': 'confirmed',
                        'contestada': 'contested'}


def rename_keys(value, mapping):
    """Return a copy; reject ambiguous aliases instead of dropping either value."""
    if not isinstance(value, dict):
        return value
    result = dict(value)
    for old, new in mapping.items():
        if old in result:
            if new in result and result[new] != result[old]:
                raise ValueError(f'Conflicting legacy and English values for {new}.')
            result[new] = result.pop(old)
    return result


def normalize_record(value):
    if not isinstance(value, dict):
        raise ValueError('A transcription record must be a JSON object.')
    result = rename_keys(value, ENVELOPE_FIELDS)
    if result.get('schema_version') not in (None, '0.1.0', RECORD_SCHEMA_VERSION):
        raise ValueError('Unsupported transcription record schema version.')
    result['reading'] = rename_keys(result['reading'], BRYOPHYTE_FIELDS)
    result['schema_version'] = RECORD_SCHEMA_VERSION
    return result

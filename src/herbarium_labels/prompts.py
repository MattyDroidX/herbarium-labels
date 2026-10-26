"""Optional instructions shared by built-in and external collection profiles."""

_LANGUAGES = {'en': 'English', 'pt': 'Portuguese', 'es': 'Spanish'}


def effective_prompt(profile, notes_language=None):
    """Keep the original prompt byte-identical unless a notes language is selected."""
    if notes_language is None:
        return profile.prompt
    return profile.prompt + (
        '\n\nWrite only the entries of `uncertainties` in '
        f'{_LANGUAGES[notes_language]}. Do not translate or normalize any transcribed '
        'text: `literal_text`, `labels`, `name_as_written`, `handwritten_notes`, '
        'and all other transcribed reading fields must remain in their original language.'
    )

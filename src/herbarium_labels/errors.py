"""Stable public failures; provider internals and credentials are never displayed."""


class TranscriptionError(ValueError):
    """A configuration, image, provider, or incomplete-reading failure."""

    def __init__(self, message, *, input_tokens=0, output_tokens=0):
        super().__init__(message)
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens

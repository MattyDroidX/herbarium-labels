"""Thin command-line adapters for the public folder APIs."""
import argparse
import json
from pathlib import Path
import sys

from . import pipeline
from .errors import TranscriptionError
from .pricing import TokenPrices
from .profiles import list_profiles
from .provider import DEFAULT_MAX_RETRIES, TranscriptionOptions
from .messages import load_messages


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    demo = commands.add_parser('demo', help='Create a synthetic delivery without network or API usage.')
    demo.add_argument('--output', required=True)
    demo.add_argument('--pdf', action='store_true')
    commands.add_parser('profiles', help='List built-in, registered, and installed profile names.')
    for name in ('transcribe', 'report', 'batch'):
        command = commands.add_parser(name)
        command.add_argument('--profile', default='po-bryophytes',
                             help='Registered or installed collection profile; see the profiles command.')
        command.add_argument('--images', required=True)
        command.add_argument('--output', required=name != 'batch')
        command.add_argument('--price-in', type=float, help='USD per million input tokens.')
        command.add_argument('--price-out', type=float, help='USD per million output tokens.')
        command.add_argument('--price-model', help='Model covered by these rates (recommended for historical/mixed reports).')
        if name == 'report':
            command.add_argument('--no-pdf', action='store_true')
        else:
            command.add_argument('--notes-language', choices=('en', 'pt', 'es'),
                                 help='Language of model uncertainties only; transcribed text stays original.')
            command.add_argument('--model', help='Overrides TRANSCRIPTION_MODEL for this invocation.')
            command.add_argument('--workers', type=int, default=6)
            command.add_argument('--max-tokens', type=int, default=16000)
            command.add_argument('--timeout', type=float, default=120)
            command.add_argument('--max-retries', type=int, default=DEFAULT_MAX_RETRIES)
            command.add_argument('--accept-existing', action='store_true',
                                 help='Explicitly reuse valid earlier readings and record their hashes separately; never overwrite JSON.')
        if name in ('report', 'batch'):
            command.add_argument('--lang', choices=('en', 'pt', 'es'),
                                 help='Report presentation language; does not change model notes.')
            command.add_argument('--messages-json', type=Path, help='Report-message translations as a JSON object.')
        if name == 'batch':
            command.add_argument('--pdf', action='store_true')
        if name == 'transcribe':
            command.add_argument('--limit', type=int)
            command.add_argument('--sample', action='store_true')
    args = parser.parse_args()
    if args.command == 'demo':
        from .demo import run_demo
        run_demo(args.output, include_pdf=args.pdf)
        return
    if args.command == 'profiles':
        print('\n'.join(list_profiles()))
        return
    if not Path(args.images).is_dir():
        parser.error(f'Image directory not found: {args.images}')
    if (args.price_in is None) != (args.price_out is None):
        parser.error('Supply both --price-in and --price-out.')
    if args.price_model and args.price_in is None:
        parser.error('--price-model requires explicit input/output prices.')
    try:
        prices = TokenPrices(args.price_in, args.price_out, model=args.price_model) if args.price_in is not None else None
        messages = load_messages(args.lang, profile=args.profile) if getattr(args, 'lang', None) else None
        if getattr(args, 'messages_json', None):
            overrides = json.loads(args.messages_json.read_text(encoding='utf-8'))
            if not isinstance(overrides, dict):
                raise ValueError('Report-message JSON must contain an object.')
            messages = {**(messages or {}), **overrides}
        if args.command == 'report':
            pipeline.create_report(args.images, args.output, profile=args.profile,
                                   include_pdf=not args.no_pdf, messages=messages, prices=prices)
            return
        options = TranscriptionOptions(model=args.model, workers=args.workers, max_tokens=args.max_tokens,
                                       timeout=args.timeout, max_retries=args.max_retries, prices=prices,
                                       notes_language=args.notes_language)
        if args.command == 'transcribe':
            result = pipeline.transcribe_folder(args.images, args.output, profile=args.profile, options=options,
                                                limit=args.limit, sample=args.sample,
                                                accept_existing=args.accept_existing)
            if result.failures:
                sys.exit(1)
        else:
            pipeline.batch_folder(args.images, args.output, profile=args.profile, options=options,
                                  include_pdf=args.pdf, messages=messages,
                                  accept_existing=args.accept_existing)
    except (ValueError, OSError) as error:
        parser.exit(1, str(error) + '\n')

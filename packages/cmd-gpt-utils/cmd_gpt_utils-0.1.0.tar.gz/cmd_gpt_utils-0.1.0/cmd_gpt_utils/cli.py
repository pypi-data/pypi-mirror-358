import argparse
from typing import List, Optional, Any
import argcomplete

from .config import ConfigLoader, Model
from .exceptions import ConfigError

class ModelIdCompleter:
    def __init__(self, config_loader: ConfigLoader):
        self.config_loader = config_loader

    def __call__(self, prefix: str, **kwargs: Any) -> List[str]:
        try:
            config = self.config_loader.load()
            return [
                str(m.id) for m in config.models 
                if str(m.id).startswith(prefix)
            ]
        except ConfigError:
            return []

class ModelNameCompleter:
    def __init__(self, config_loader: ConfigLoader):
        self.config_loader = config_loader

    def __call__(self, prefix: str, **kwargs: Any) -> List[str]:
        try:
            config = self.config_loader.load()
            return [
                m.model_name for m in config.models 
                if m.model_name and m.model_name.startswith(prefix)
            ]
        except ConfigError:
            return []

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="A simple command-line tool for GPT interaction.")
    
    config_loader = ConfigLoader()

    parser.add_argument(
        '-f', '--file', 
        dest='conf_files',
        action='append',
        help="Specify configuration files to load. Can be used multiple times. Overrides previous settings."
    )
    
    model_completer = lambda prefix, parsed_args, **kwargs: (
        list(ModelIdCompleter(config_loader)(prefix, **kwargs)) +
        list(ModelNameCompleter(config_loader)(prefix, **kwargs))
    )
    parser.add_argument(
        '-m', '--model', 
        dest='model_identifier',
        help="Specify model by id or name prefix."
    ).completer = model_completer # type: ignore

    parser.add_argument(
        '-p', '--prompt-file',
        dest='prompt_file',
        help="Path to a file containing the prompt (relative or absolute)."
    )

    parser.add_argument(
        '-B', '--prompt-before',
        dest='prompt_before',
        action='append',
        help="Add a prompt segment before the main prompt. Can be used multiple times."
    )

    parser.add_argument(
        '-A', '--prompt-after',
        dest='prompt_after',
        action='append',
        help="Add a prompt segment after the main prompt. Can be used multiple times."
    )

    parser.add_argument(
        '-k', '--cot',
        dest='cot_tag',
        nargs='?',
        const=True, # if -k is present without argument
        default=None,
        help="Enable Chain-of-Thought filtering. Optionally specify a custom tag to filter."
    )
    
    parser.add_argument(
        '-sse',
        dest='use_sse',
        choices=['true', 'false'],
        help="Override SSE setting from config files."
    )
    
    parser.add_argument(
        '-c', '--context',
        dest='context_mode',
        nargs='?',
        const='io',
        choices=['i', 'o', 'io'],
        default=None,
        help="Enable context mode. 'i': stdin is history JSON, 'o': stdout is history JSON, 'io': both. Defaults to 'io' if flag is present."
    )

    parser.add_argument(
        '-n', '--stop-at-newline',
        dest='stop_at_newline',
        action='store_true',
        help="Stop reading prompt from stdin at the first newline."
    )

    parser.add_argument(
        '-v', '--verbose',
        action='count',
        default=0,
        help="Increase verbosity. -v prints the final prompt to stderr, -vv prints the full messages JSON to stderr."
    )

    parser.add_argument(
        'prompt',
        nargs='*',
        help="The prompt text. All positional arguments are concatenated. If not provided, reads from stdin."
    )

    argcomplete.autocomplete(parser)
    return parser

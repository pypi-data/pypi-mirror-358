import shlex
from typing import Iterable

from prompt_toolkit.completion import Completer, Completion

from falyx.parser.command_argument_parser import CommandArgumentParser


class FalyxCompleter(Completer):
    def __init__(self, falyx: "Falyx") -> None:
        self.falyx = falyx

    def get_completions(self, document, complete_event) -> Iterable[Completion]:
        text = document.text_before_cursor.strip()
        if not text:
            yield from self._complete_command("")
            return

        try:
            tokens = shlex.split(text)
        except ValueError:
            return  # unmatched quotes or syntax error

        if not tokens:
            yield from self._complete_command("")
            return

        command_token = tokens[0]
        command_key = command_token.lstrip("?").upper()
        command = self.falyx._name_map.get(command_key)

        if command is None:
            yield from self._complete_command(command_token)
            return

        used_flags = set(tokens[1:])  # simplistic
        parser: CommandArgumentParser = command.arg_parser or CommandArgumentParser()
        for arg in parser._keyword_list:
            for flag in arg.flags:
                if flag not in used_flags:
                    yield Completion(flag, start_position=0)

        for dest, arg in parser._positional.items():
            if dest not in used_flags:
                yield Completion(arg.dest, start_position=0)

    def _complete_command(self, prefix: str) -> Iterable[Completion]:
        seen = set()
        for cmd in self.falyx.commands.values():
            for key in [cmd.key] + cmd.aliases:
                if key not in seen and key.upper().startswith(prefix.upper()):
                    yield Completion(key, start_position=-len(prefix))
                    seen.add(key)

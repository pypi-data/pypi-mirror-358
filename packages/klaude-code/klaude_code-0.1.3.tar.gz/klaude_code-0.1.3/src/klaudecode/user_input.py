from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Generator, Optional, Tuple

if TYPE_CHECKING:
    from .agent import Agent

from prompt_toolkit import PromptSession
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from pydantic import BaseModel
from rich.abc import RichRenderable
from rich.text import Text

from .message import UserMessage, register_user_msg_content_func, register_user_msg_renderer, register_user_msg_suffix_renderer
from .prompt.reminder import LANGUAGE_REMINDER
from .tui import ColorStyle, console, get_prompt_toolkit_color, get_prompt_toolkit_style, render_message
from .utils.file_searcher import FileSearcher

"""
Command: When users press /, it prompts slash command completion
InputModeCommand: When users press special characters like #, !, etc., they enter special input modes (memory mode, bash mode, etc.)
"""


class UserInput(BaseModel):
    command_name: str = 'normal'  # Input mode or slash command
    cleaned_input: str  # User input without slash command
    raw_input: str


class CommandHandleOutput(BaseModel):
    user_msg: Optional[UserMessage] = None
    need_agent_run: bool = False
    need_render_suffix: bool = True


# Command ABC
# ---------------------


class Command(ABC):
    @abstractmethod
    def get_name(self) -> str:
        """
        The name of the command.
        /{name}
        """
        raise NotImplementedError

    @abstractmethod
    def get_command_desc(self) -> str:
        """
        The description of the command.
        /{name} {desc}
        """
        raise NotImplementedError

    async def handle(self, agent: 'Agent', user_input: UserInput) -> CommandHandleOutput:
        """
        Handle slash command.
        Return True to indicate that the agent should run.
        """
        return CommandHandleOutput(
            user_msg=UserMessage(
                content=user_input.cleaned_input,
                user_msg_type=user_input.command_name,
                user_raw_input=user_input.raw_input,
            ),
            need_agent_run=False,
            need_render_suffix=True,
        )

    def render_user_msg(self, user_msg: UserMessage) -> Generator[RichRenderable, None, None]:
        yield render_message(Text(user_msg.user_raw_input), mark='>')

    def render_user_msg_suffix(self, user_msg: UserMessage) -> Generator[RichRenderable, None, None]:
        return
        yield  # Make sure to return a generator

    def get_content(self, user_msg: UserMessage) -> str:
        """Generate content for the user message - can be overridden by subclasses"""
        return user_msg.content

    @classmethod
    def is_slash_command(cls) -> bool:
        return True


class InputModeCommand(Command, ABC):
    @classmethod
    def is_slash_command(cls) -> bool:
        return False

    @abstractmethod
    def _get_prompt(self) -> str:
        """
        The mark of input line, default is '>'
        """
        raise NotImplementedError

    @abstractmethod
    @abstractmethod
    def _get_color(self) -> str:
        """
        The color of the input.
        """
        raise NotImplementedError

    @abstractmethod
    def _get_placeholder(self) -> str:
        """
        The placeholder of the input hint.
        """
        raise NotImplementedError

    def get_next_mode_name(self) -> str:
        """
        The name of the next input mode.
        """
        return NORMAL_MODE_NAME

    async def handle(self, agent: 'Agent', user_input: UserInput) -> CommandHandleOutput:
        return await super().handle(agent, user_input)

    def get_command_desc(self) -> str:
        return f'Input mode: {self.get_name()}'

    def get_prompt(self):
        if self._get_color():
            return HTML(f'<style fg="{self._get_color()}">{self._get_prompt()} </style>')
        return self._get_prompt() + ' '

    def get_placeholder(self):
        color = self._get_color() or get_prompt_toolkit_color(ColorStyle.INPUT_PLACEHOLDER)
        if color:
            return HTML(f'<style fg="{color}">{self._get_placeholder()} </style>')
        return self._get_placeholder() + ' '

    def binding_key(self) -> str:
        # ! DO NOT BIND `/` `enter` `backspace`
        raise NotImplementedError

    def get_style(self):
        style_dict = get_prompt_toolkit_style()
        if self._get_color():
            style_dict[''] = self._get_color()
        return Style.from_dict(style_dict)


class NormalMode(InputModeCommand):
    def get_name(self) -> str:
        return NORMAL_MODE_NAME

    def _get_prompt(self) -> str:
        return '>'

    def _get_color(self) -> str:
        return ''

    def _get_placeholder(self) -> str:
        return 'type you query... type exit to quit.'

    def get_next_mode_name(self) -> str:
        return NORMAL_MODE_NAME

    def binding_key(self) -> str:
        return ''

    async def handle(self, agent: 'Agent', user_input: UserInput) -> CommandHandleOutput:
        command_handle_output = await super().handle(agent, user_input)
        command_handle_output.need_agent_run = True
        return command_handle_output


# All Command Registry
# ---------------------

NORMAL_MODE_NAME = 'normal'
_INPUT_MODES = {
    NORMAL_MODE_NAME: NormalMode(),
}
_SLASH_COMMANDS = {}


def register_input_mode(input_mode: InputModeCommand):
    _INPUT_MODES[input_mode.get_name()] = input_mode
    register_user_msg_renderer(input_mode.get_name(), input_mode.render_user_msg)
    register_user_msg_suffix_renderer(input_mode.get_name(), input_mode.render_user_msg_suffix)
    register_user_msg_content_func(input_mode.get_name(), input_mode.get_content)


def register_slash_command(command: Command):
    _SLASH_COMMANDS[command.get_name()] = command
    register_user_msg_renderer(command.get_name(), command.render_user_msg)
    register_user_msg_suffix_renderer(command.get_name(), command.render_user_msg_suffix)
    register_user_msg_content_func(command.get_name(), command.get_content)


# User Input Handler
# ---------------------


class UserInputHandler:
    def __init__(self, agent: 'Agent'):
        self.agent = agent

    async def handle(self, user_input_text: str, print_msg: bool = True) -> bool:
        """
        Handle special mode and command input.
        """

        command_name, cleaned_input = self._parse_command(user_input_text)
        command = _INPUT_MODES.get(command_name, _SLASH_COMMANDS.get(command_name, NormalMode()))
        command_handle_output = await command.handle(
            self.agent,
            UserInput(
                command_name=command_name or NORMAL_MODE_NAME,
                cleaned_input=cleaned_input,
                raw_input=user_input_text,
            ),
        )
        user_msg = command_handle_output.user_msg

        if user_msg is not None:
            self._handle_language_reminder(user_msg)
            self.agent.append_message(user_msg)
            if print_msg:
                console.print(user_msg)
            elif command_handle_output.need_render_suffix:
                for item in user_msg.get_suffix_renderable():
                    console.print(item)

        return command_handle_output.need_agent_run

    def _parse_command(self, text: str) -> Tuple[str, str]:
        """Parse command from input text. Returns tuple of (command_enum, remaining_text)"""
        if not text.strip():
            return '', text

        stripped = text.strip()
        if stripped.startswith('/'):
            # Extract command and remaining text
            parts = stripped[1:].split(None, 1)  # Split into at most 2 parts
            if parts:
                command_part = parts[0]
                remaining_text = parts[1] if len(parts) > 1 else ''
                # Find matching command
                if command_part in _SLASH_COMMANDS:
                    return command_part, remaining_text
                if command_part in _INPUT_MODES:
                    return command_part, remaining_text
        return '', text

    def _handle_language_reminder(self, user_msg: UserMessage):
        if len(self.agent.session.messages) > 2:
            return
        user_msg.append_post_system_reminder(LANGUAGE_REMINDER)


# Prompt toolkit completer & key bindings
# ----------------------------------------


class UserInputCompleter(Completer):
    """Custom user input completer"""

    def __init__(self, input_session):
        self.commands: Dict[str, Command] = _SLASH_COMMANDS
        self.input_session = input_session

    def get_completions(self, document, _complete_event):
        # Only provide completion in normal mode
        text = document.text
        cursor_position = document.cursor_position

        # Check for @ file completion first
        at_match = self._find_at_file_pattern(text, cursor_position)
        if at_match:
            try:
                yield from self._get_file_completions(at_match)
            except Exception:
                # If file completion fails, fall back to normal behavior
                pass
            return

        # Only do slash command completion in normal mode
        if self.input_session.current_input_mode.get_name() != NORMAL_MODE_NAME:
            return

        # Original slash command completion - but only if text starts with /
        if not text.startswith('/') or cursor_position == 0:
            return

        # Get command part (content after /)
        command_part = text[1:cursor_position] if cursor_position > 1 else ''

        # If no space in the command part, we are still completing command name
        if ' ' not in command_part:
            for command_name, command in self.commands.items():
                if command_name.startswith(command_part):
                    yield Completion(
                        command_name,
                        start_position=-len(command_part),
                        display=f'/{command_name:15}',
                        display_meta=command.get_command_desc(),
                    )

    def _find_at_file_pattern(self, text, cursor_position):
        for i in range(cursor_position - 1, -1, -1):
            if text[i] == '@':
                file_prefix = text[i + 1 : cursor_position]
                # Avoid file completion for patterns that start with / or contain command characters
                if file_prefix.startswith('/') or any(c in file_prefix for c in ['/', '\\']):
                    return None
                return {'at_position': i, 'prefix': file_prefix, 'start_position': i + 1 - cursor_position}
            elif text[i].isspace():
                break
        return None

    def _get_file_completions(self, at_match):
        prefix = at_match['prefix']
        start_position = at_match['start_position']

        # Safety check - avoid searching problematic paths
        if not prefix or prefix.startswith('/') or any(c in prefix for c in ['/', '\\']):
            return

        workdir = self.input_session.workdir

        if prefix:
            prefix_path = Path(prefix)
            if prefix_path.is_absolute():
                # Don't allow absolute path completion for security
                return
            else:
                search_dir = workdir / prefix_path.parent if prefix_path.parent != Path('.') else workdir
                name_prefix = prefix_path.name
        else:
            search_dir = workdir
            name_prefix = ''

        if not search_dir.exists() or not search_dir.is_dir():
            return

        matches = []
        try:
            # Use fuzzy search for better user experience in @file completion
            files = FileSearcher.search_files_fuzzy(name_prefix or '', str(search_dir))

            for file_path in files:
                try:
                    relative_path = Path(file_path).relative_to(workdir)
                    path_str = str(relative_path)
                except ValueError:
                    relative_path = Path(file_path)
                    path_str = str(file_path)

                if name_prefix:
                    path_str_lower = path_str.lower()
                    name_prefix_lower = name_prefix.lower()

                    if name_prefix_lower not in path_str_lower:
                        continue

                matches.append({'path': relative_path, 'name': relative_path.name})
        except (OSError, PermissionError):
            return

        def sort_key(match):
            path_str = str(match['path']).lower()
            name = match['name'].lower()
            prefix_lower = name_prefix.lower() if name_prefix else ''

            if not prefix_lower:
                return (0, name)

            if name.startswith(prefix_lower):
                return (0, name)

            if prefix_lower in name:
                return (1, name)

            if path_str.startswith(prefix_lower):
                return (2, path_str)

            return (3, path_str)

        matches.sort(key=sort_key)

        matches = matches[:10]

        for match in matches:
            path_str = str(match['path'])

            yield Completion(
                path_str,
                start_position=start_position,
                display=path_str,
            )


class InputSession:
    def __init__(self, workdir: str = None):
        self.current_input_mode: InputModeCommand = _INPUT_MODES[NORMAL_MODE_NAME]
        self.workdir = Path(workdir) if workdir else Path.cwd()

        # Create history file path
        history_file = self.workdir / '.klaude' / 'input_history.txt'
        if not history_file.exists():
            history_file.parent.mkdir(parents=True, exist_ok=True)
            history_file.touch()
        self.history = FileHistory(str(history_file))
        self.user_input_completer = UserInputCompleter(self)

    def _dyn_prompt(self):
        return self.current_input_mode.get_prompt()

    def _dyn_placeholder(self):
        return self.current_input_mode.get_placeholder()

    def _switch_mode(self, event, mode_name: str):
        self.current_input_mode = _INPUT_MODES[mode_name]
        style = self.current_input_mode.get_style()
        if style:
            event.app.style = style
        else:
            event.app.style = None
        event.app.invalidate()

    def _setup_key_bindings(self, buf: Buffer, kb: KeyBindings):
        for mode in _INPUT_MODES.values():
            binding_keys = []
            if hasattr(mode, 'binding_keys'):
                binding_keys = mode.binding_keys()
            elif mode.binding_key():
                binding_keys = [mode.binding_key()]

            for key in binding_keys:
                if not key:  # Skip empty keys
                    continue

                # Create a proper closure with default arguments to avoid late binding
                def make_binding(current_mode=mode, bind_key=key):
                    @kb.add(bind_key)
                    def _(event):
                        document = buf.document
                        current_line_start_pos = document.cursor_position + document.get_start_of_line_position()
                        if buf.cursor_position == current_line_start_pos:
                            self._switch_mode(event, current_mode.get_name())
                            return
                        buf.insert_text(bind_key)

                    return _

                make_binding()

        @kb.add('backspace')
        def _(event):
            # Check if cursor is at the beginning of current line
            document = buf.document
            current_line_start_pos = document.cursor_position + document.get_start_of_line_position()
            if buf.cursor_position == current_line_start_pos:
                self._switch_mode(event, NORMAL_MODE_NAME)
                return
            buf.delete_before_cursor()

        @kb.add('c-u')
        def _(event):
            """Clear the entire buffer with ctrl+u (Unix standard)"""
            buf.text = ''
            buf.cursor_position = 0

        @kb.add('enter')
        def _(event):
            """
            Check if the current line ends with a backslash.
            - If yes, remove the backslash and insert a newline to continue editing.
            - If no, accept the line via `validate_and_handle()`, which triggers
              PromptToolkit's default accept‑line logic and persists the input
              into `FileHistory`.
            """
            buffer = event.current_buffer
            if buffer.text.endswith('\\'):
                # Remove trailing backslash (do **not** include it in history)
                buffer.delete_before_cursor()
                # Insert a real newline so the user can keep typing
                buffer.insert_text('\n')
            else:
                # Accept the line normally – this calls the buffer's
                # accept_action, which records the entry in FileHistory.
                buffer.validate_and_handle()

    def _get_session(self):
        kb = KeyBindings()
        session = PromptSession(
            message=self._dyn_prompt,
            key_bindings=kb,
            history=self.history,
            placeholder=self._dyn_placeholder,
            completer=self.user_input_completer,
            style=self.current_input_mode.get_style(),
        )
        self._setup_key_bindings(session.default_buffer, kb)
        return session

    def _switch_to_next_input_mode(self):
        next_mode_name = self.current_input_mode.get_next_mode_name()
        if next_mode_name not in _INPUT_MODES:
            return
        self.current_input_mode = _INPUT_MODES[next_mode_name]

    def prompt(self) -> UserInput:
        input_text = self._get_session().prompt()
        if self.current_input_mode.get_name() != NORMAL_MODE_NAME:
            input_text = f'/{self.current_input_mode.get_name()} {input_text}'
        self._switch_to_next_input_mode()
        return input_text

    async def prompt_async(self) -> UserInput:
        input_text = await self._get_session().prompt_async()
        if self.current_input_mode.get_name() != NORMAL_MODE_NAME:
            input_text = f'/{self.current_input_mode.get_name()} {input_text}'
        self._switch_to_next_input_mode()
        return input_text

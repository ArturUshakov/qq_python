from .command_registry import Command
from utils import print_colored

class PrintHelpCommand(Command):
    def __init__(self):
        super().__init__(["-h", "help"], "Выводит это сообщение")

    def execute(self, *args):
        width = 60
        border_char = "═"

        def center_text(text):
            return text.center(width)

        print(print_colored("bright_blue", f"\n{border_char * width}"))
        print(print_colored("bright_blue", center_text("Справка")))
        print(print_colored("bright_blue", f"{border_char * width}"))

        command_registry = self.registry
        max_name_length = max(
            len(', '.join(command.names)) for group in command_registry.groups for command in command_registry.get_group_commands(group).values()
        ) + 5

        for group, description in command_registry.groups.items():
            print(print_colored("bright_magenta", f"\n=== {description} ==="))
            for command in command_registry.get_group_commands(group).values():
                names = ', '.join(command.names)
                print(f"{print_colored('bright_green', f'  {names:<{max_name_length}}')} {print_colored('bright_yellow', command.description)}")

class BaseCommand:
    @staticmethod
    def register(registry):
        help_command = PrintHelpCommand()
        help_command.registry = registry
        registry.register_command(help_command)

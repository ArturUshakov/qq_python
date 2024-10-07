# commands/base_commands.py
from colorama import Fore, Style, init
from .command_registry import Command

init(autoreset=True)


class PrintHelpCommand(Command):
    def __init__(self):
        super().__init__(["-h", "help"], "Выводит это сообщение")

    def execute(self, *args):
        width = 80
        border_char = "─"
        title = "Справка по Командам"

        def center_text(text, width):
            return text.center(width)

        def print_header_footer():
            border = f"{border_char * width}"
            print(f"{Fore.CYAN}{border}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{center_text(title, width)}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{border}{Style.RESET_ALL}")

        def print_command_list():
            command_registry = self.registry
            max_name_length = max(
                len(', '.join(command.names)) for group in command_registry.groups for command in
                command_registry.get_group_commands(group).values()
            ) + 4

            for group, description in command_registry.groups.items():
                print(f"\n{Fore.MAGENTA}{border_char} {description} {border_char}{Style.RESET_ALL}")
                for command in command_registry.get_group_commands(group).values():
                    names = ', '.join(command.names)
                    formatted_names = f'  {names:<{max_name_length}}'
                    print(
                        f"{Fore.GREEN}{formatted_names}{Style.RESET_ALL} {Fore.WHITE}{command.description}{Style.RESET_ALL}")

        print_header_footer()
        print_command_list()


class BaseCommand:
    @staticmethod
    def register(registry):
        help_command = PrintHelpCommand()
        help_command.registry = registry
        registry.register_command(help_command)

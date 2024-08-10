from .command_registry import Command
from utils import print_colored

class PrintHelpCommand(Command):
    def __init__(self):
        super().__init__(["-h", "help"], "Выводит это сообщение")

    def execute(self, *args):
        print(print_colored("bright_blue", "\n==================== Справка ===================="))
        print_colored("bright_blue", "Доступные команды:")
        command_registry = self.registry
        for group, description in command_registry.groups.items():
            print(print_colored("bright_blue", f"\n===== {description} ====="))
            for command in command_registry.get_group_commands(group).values():
                names = ', '.join(command.names)
                print(f"  {print_colored('bright_green', f'{names:30}')}{print_colored('bright_yellow', command.description)}")
        print(print_colored("bright_blue", "================================================"))

class BaseCommand:
    @staticmethod
    def register(registry):
        help_command = PrintHelpCommand()
        help_command.registry = registry
        registry.register_command(help_command)

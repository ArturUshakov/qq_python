import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from colorama import Fore, Style
from commands.command_registry import CommandRegistry
from core.logger import safe_execute

def suggest_command(registry, input_cmd):
    import difflib
    commands = list(registry.commands.keys())
    matches = difflib.get_close_matches(input_cmd, commands, n=3, cutoff=0.3)
    if matches:
        print(f"{Fore.LIGHTBLUE_EX}✦ Похожие команды:{Style.RESET_ALL}")
        for cmd in matches:
            print(f"{Fore.LIGHTCYAN_EX}  • {cmd}{Style.RESET_ALL}")

def main():
    registry = CommandRegistry()
    registry.register_all_commands()

    if len(sys.argv) < 2:
        registry.print_help()
        return

    input_cmd = sys.argv[1]
    command = registry.get_command(input_cmd)

    if command:
        safe_execute(command, *sys.argv[2:])
    else:
        print(f"{Fore.LIGHTRED_EX}Неизвестная команда: {input_cmd}{Style.RESET_ALL}")
        suggest_command(registry, input_cmd)
        print(f"{Fore.LIGHTYELLOW_EX}ℹ️ Используйте '-h' или 'help' для списка команд.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()

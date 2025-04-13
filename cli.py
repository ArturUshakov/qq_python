import os
import sys
import logging
import importlib
import pkgutil
from colorama import Fore, Style
from commands.command_registry import CommandRegistry
from core.logger import safe_execute

logging.basicConfig(filename="errors.log", level=logging.ERROR, format="%(asctime)s %(levelname)s:%(message)s")

def suggest_command(registry, input_cmd):
    import difflib
    commands = list(registry.commands.keys())
    matches = difflib.get_close_matches(input_cmd, commands, n=3, cutoff=0.3)
    if matches:
        print(f"{Fore.LIGHTBLUE_EX}✦ Похожие команды:{Style.RESET_ALL}")
        for cmd in matches:
            print(f"{Fore.LIGHTCYAN_EX}  • {cmd}{Style.RESET_ALL}")

def autoimport_commands():
    import commands
    for _, module_name, _ in pkgutil.iter_modules(commands.__path__):
        importlib.import_module(f"commands.{module_name}")

def main():
    autoimport_commands()
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
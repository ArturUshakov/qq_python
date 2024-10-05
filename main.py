# main.py
import sys
from colorama import Fore, Style, init

init(autoreset=True)


def suggest_command(command_registry, command_input):
    import difflib

    commands = list(command_registry.commands.keys())
    similar_commands = difflib.get_close_matches(command_input, commands, n=3, cutoff=0.3)

    if similar_commands:
        print(f"{Fore.LIGHTBLUE_EX}✦ Возможно, вы имели в виду одну из этих команд:{Style.RESET_ALL}")
        for cmd in similar_commands:
            print(f"{Fore.LIGHTCYAN_EX}  • {cmd}{Style.RESET_ALL}")
    else:
        print(f"{Fore.LIGHTYELLOW_EX}✘ Нет похожих команд.{Style.RESET_ALL}")


def main():
    from commands import CommandRegistry
    from utils import check_for_updates

    command_registry = CommandRegistry()
    command_registry.register_all_commands()

    if len(sys.argv) < 2:
        command_registry.print_help()
        sys.exit(0)

    command_input = sys.argv[1]
    command = command_registry.get_command(command_input)

    if command:
        command.execute(*sys.argv[2:])
        check_for_updates()
        return

    print(f"{Fore.LIGHTRED_EX}Неизвестная команда: {command_input}{Style.RESET_ALL}")
    suggest_command(command_registry, command_input)
    print(
        f"{Fore.LIGHTYELLOW_EX}ℹ️ Используйте '-h' или 'help' для получения списка доступных команд.{Style.RESET_ALL}")
    sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}⚠️ Произошла ошибка: {e}{Style.RESET_ALL}")
        sys.exit(1)

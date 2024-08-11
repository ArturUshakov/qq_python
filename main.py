import sys
import difflib
from commands import CommandRegistry
from utils import check_for_updates
import threading

def suggest_command(command_registry, command_input):
    commands = list(command_registry.commands.keys())
    similar_commands = difflib.get_close_matches(command_input, commands, n=3, cutoff=0.3)

    if similar_commands:
        print("\033[94mВозможно, вы имели в виду одну из этих команд:\033[0m")
        for cmd in similar_commands:
            print(f"\033[96m  {cmd}\033[0m")

def main():
    command_registry = CommandRegistry()
    command_registry.register_all_commands()

    if len(sys.argv) < 2:
        print("\033[94mДоступные команды:\033[0m")
        command_registry.print_help()
        sys.exit(0)

    command_input = sys.argv[1]
    command = command_registry.get_command(command_input)

    if command:
        update_thread = threading.Thread(target=check_for_updates)
        update_thread.start()

        command.execute(*sys.argv[2:])

        update_thread.join()

        return

    print(f"\033[91mНеизвестная команда: {command_input}\033[0m")
    suggest_command(command_registry, command_input)
    print("\033[93mИспользуйте '-h' или 'help' для получения списка доступных команд.\033[0m")
    sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\033[91mПроизошла ошибка: {e}\033[0m")
        sys.exit(1)

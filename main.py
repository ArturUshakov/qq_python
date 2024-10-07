import subprocess
import sys
import logging
import traceback
from colorama import Fore, Style, init
from logging.handlers import RotatingFileHandler

init(autoreset=True)

log_handler = RotatingFileHandler(
    filename='app.log',
    mode='a',
    maxBytes=0,
    backupCount=0,
)


def clear_log_if_exceeds_limit(filename='app.log', limit=1000):
    try:
        with open(filename, 'r+') as f:
            lines = f.readlines()
            if len(lines) > limit:
                f.seek(0)
                f.truncate()
                logging.info("Лог файл был очищен, так как достиг предела в 1000 записей")
    except Exception as e:
        logging.error(f"Ошибка при проверке или очистке логов: {e}")


log_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(formatter)

logging.basicConfig(
    handlers=[log_handler],
    level=logging.DEBUG
)


def log_exception(e):
    logging.error("Произошла ошибка: %s", e)
    logging.error("Traceback: %s", traceback.format_exc())


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

    logging.info(f"Предложены похожие команды: {similar_commands}")


def safe_execute_command(command, *args):
    try:
        logging.debug(f"Выполнение команды: {command} с аргументами {args}")
        command.execute(*args)
    except subprocess.CalledProcessError as e:
        error_message = f"Ошибка при выполнении системной команды: {e}"
        print(Fore.LIGHTRED_EX + error_message + Style.RESET_ALL)
        log_exception(e)
    except Exception as e:
        error_message = f"Произошла ошибка при выполнении команды: {e}"
        print(Fore.LIGHTRED_EX + error_message + Style.RESET_ALL)
        log_exception(e)


def main():
    from commands import CommandRegistry
    from utils import check_for_updates

    logging.info("Программа запущена")

    command_registry = CommandRegistry()
    command_registry.register_all_commands()

    if len(sys.argv) < 2:
        logging.warning("Команда не указана")
        command_registry.print_help()
        sys.exit(0)

    command_input = sys.argv[1]
    command = command_registry.get_command(command_input)

    if command:
        safe_execute_command(command, *sys.argv[2:])
        check_for_updates()
        logging.info("Команда успешно выполнена")
        return

    logging.error(f"Неизвестная команда: {command_input}")
    print(f"{Fore.LIGHTRED_EX}Неизвестная команда: {command_input}{Style.RESET_ALL}")
    suggest_command(command_registry, command_input)
    print(
        f"{Fore.LIGHTYELLOW_EX}ℹ️ Используйте '-h' или 'help' для получения списка доступных команд.{Style.RESET_ALL}")
    sys.exit(1)


def global_exception_hook(exctype, value, tb):
    logging.critical("Необработанное исключение", exc_info=(exctype, value, tb))
    print(f"{Fore.LIGHTRED_EX}⚠️ Произошла глобальная ошибка: {value}{Style.RESET_ALL}")


if __name__ == "__main__":
    sys.excepthook = global_exception_hook
    try:
        clear_log_if_exceeds_limit()
        main()
    except Exception as e:
        log_exception(e)
        sys.exit(1)

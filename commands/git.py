# commands/git.py
import subprocess
from colorama import Fore, Style, init
from .command_registry import Command

init(autoreset=True)


class GitUndoLastCommitCommand(Command):
    def __init__(self):
        super().__init__(["-сlс", "clear-last-commit"], "Отменяет последний коммит, но оставляет изменения")

    def execute(self, *args):
        try:
            print(f"{Fore.YELLOW}Отмена последнего коммита...{Style.RESET_ALL}")
            subprocess.run(["git", "reset", "--soft", "HEAD~1"], check=True)
            print(f"{Fore.GREEN}Последний коммит отменен, изменения сохранены!{Style.RESET_ALL}")
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}Ошибка при отмене последнего коммита: {str(e)}{Style.RESET_ALL}")

class GitIgnoreFileModeCommand(Command):
    def __init__(self):
        super().__init__("-gi", "Отключает отслеживание изменений прав файлов в Git")

    def execute(self, *args):
        try:
            subprocess.run(["git", "config", "core.fileMode", "false"], check=True)
            print(
                f"{Fore.GREEN}{Style.BRIGHT}✔ Отслеживание изменений прав файлов в Git успешно отключено.{Style.RESET_ALL}")
        except subprocess.CalledProcessError:
            print(
                f"{Fore.RED}{Style.BRIGHT}✘ Ошибка: Не удалось отключить отслеживание изменений прав файлов в Git.{Style.RESET_ALL}")

class GitCommand:
    @staticmethod
    def register(registry):
        registry.register_command(GitUndoLastCommitCommand(), "git")
        registry.register_command(GitIgnoreFileModeCommand(), "git")

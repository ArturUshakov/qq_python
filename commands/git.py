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

class GitDiffCommand(Command):
    def __init__(self):
        super().__init__(["-gd", "git-diff"], "Показывает изменения, которые будут закоммичены")

    def execute(self, *args):
        try:
            # Выполняем команду git diff --staged
            result = subprocess.run(["git", "diff", "--staged"], capture_output=True, text=True, check=True)

            if not result.stdout.strip():
                print(f"{Fore.GREEN}Нет изменений для отображения.{Style.RESET_ALL}")
                return

            print(f"{Fore.YELLOW}Изменения перед коммитом:{Style.RESET_ALL}\n")

            # Разбираем вывод и применяем цветовое форматирование
            for line in result.stdout.splitlines():
                if line.startswith("diff --git"):
                    print(f"{Fore.CYAN}{line}{Style.RESET_ALL}")
                elif line.startswith("index"):
                    print(f"{Fore.MAGENTA}{line}{Style.RESET_ALL}")
                elif line.startswith("---"):
                    print(f"{Fore.RED}{line}{Style.RESET_ALL}")
                elif line.startswith("+++"):
                    print(f"{Fore.GREEN}{line}{Style.RESET_ALL}")
                elif line.startswith("@@"):
                    print(f"{Fore.BLUE}{line}{Style.RESET_ALL}")
                elif line.startswith("+"):
                    print(f"{Fore.GREEN}{line}{Style.RESET_ALL}")  # Добавленные строки
                elif line.startswith("-"):
                    print(f"{Fore.RED}{line}{Style.RESET_ALL}")  # Удалённые строки
                else:
                    print(line)

        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}Ошибка при выводе изменений: {str(e)}{Style.RESET_ALL}")

class GitCommand:
    @staticmethod
    def register(registry):
        registry.register_command(GitUndoLastCommitCommand(), "git")
        registry.register_command(GitDiffCommand(), "git")

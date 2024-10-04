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

class GitPruneMergedBranchesCommand(Command):
    def __init__(self):
        super().__init__(["-pmb", "git-prune-merged"], "Удаляет локальные ветки, которые уже слиты с master/main")

    def execute(self, *args):
        try:
            print(f"{Fore.YELLOW}Удаление локальных веток, которые были слиты с master/main...{Style.RESET_ALL}")
            subprocess.run(["git", "checkout", "master"], check=True)
            subprocess.run(["git", "fetch", "--prune"], check=True)
            subprocess.run(["git", "branch", "--merged", "master", "|", "grep", "-v", "'\\*'", "|", "xargs", "git", "branch", "-d"], shell=True, check=True)
            print(f"{Fore.GREEN}Локальные слитые ветки успешно удалены!{Style.RESET_ALL}")
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}Ошибка при удалении слитых веток: {str(e)}{Style.RESET_ALL}")

class GitCommand:
    @staticmethod
    def register(registry):
        registry.register_command(GitUndoLastCommitCommand(), "git")
        registry.register_command(GitPruneMergedBranchesCommand(), "git")

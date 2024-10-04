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
        super().__init__(["-pmb", "git-prune-merged"], "Удаляет локальные ветки, которые уже слиты с master")

    def execute(self, *args):
        try:
            print(f"{Fore.YELLOW}Удаление локальных веток, которые были слиты с master...{Style.RESET_ALL}")

            subprocess.run(["git", "checkout", "master"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

            merged_branches = subprocess.run(
                "git branch --merged | grep -v '\\*' | grep -v 'master'",
                shell=True, capture_output=True, text=True
            )

            branches_to_delete = merged_branches.stdout.strip().splitlines()

            if not branches_to_delete:
                print(f"{Fore.GREEN}Нет слитых веток для удаления.{Style.RESET_ALL}")
                return

            print(f"{Fore.YELLOW}Ветки, которые будут удалены:{Style.RESET_ALL}")
            for branch in branches_to_delete:
                print(f"{Fore.CYAN}{branch.strip()}{Style.RESET_ALL}")

            confirmation = input(f"{Fore.RED}Вы уверены, что хотите удалить эти ветки? (y/n): {Style.RESET_ALL}")
            if confirmation.lower() != 'y':
                print(f"{Fore.YELLOW}Удаление веток отменено.{Style.RESET_ALL}")
                return

            subprocess.run("git branch --merged | grep -v '\\*' | grep -v 'master' | xargs git branch -d",
                           shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

            print(f"{Fore.GREEN}Локальные слитые ветки успешно удалены!{Style.RESET_ALL}")
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}Ошибка при удалении слитых веток: {str(e)}{Style.RESET_ALL}")

class GitCommand:
    @staticmethod
    def register(registry):
        registry.register_command(GitUndoLastCommitCommand(), "git")
        registry.register_command(GitPruneMergedBranchesCommand(), "git")

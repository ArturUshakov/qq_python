# commands/system_commands.py
import os
import subprocess
import sys
from .command_registry import Command
from colorama import Fore, Style, init

init(autoreset=True)

class GitIgnoreFileModeCommand(Command):
    def __init__(self):
        super().__init__("-gi", "Отключает отслеживание изменений прав файлов в Git")

    def execute(self, *args):
        try:
            subprocess.run(["git", "config", "core.fileMode", "false"], check=True)
            print(f"{Fore.GREEN}{Style.BRIGHT}✔ Отслеживание изменений прав файлов в Git успешно отключено.{Style.RESET_ALL}")
        except subprocess.CalledProcessError:
            print(f"{Fore.RED}{Style.BRIGHT}✘ Ошибка: Не удалось отключить отслеживание изменений прав файлов в Git.{Style.RESET_ALL}")

class ChmodAllCommand(Command):
    def __init__(self):
        super().__init__("-ch", "Рекурсивно выставляет права 777 с директории выполнения")

    def execute(self, *args):
        try:
            print(f"{Fore.YELLOW}{Style.BRIGHT}⚙ Изменение прав доступа для всех файлов и директорий в текущей папке...{Style.RESET_ALL}")
            subprocess.run(["sudo", "chmod", "777", "-R", "."], check=True)
            print(f"{Fore.GREEN}{Style.BRIGHT}✔ Все файлы и директории в текущей папке успешно получили права 777.{Style.RESET_ALL}")
        except subprocess.CalledProcessError:
            print(f"{Fore.RED}{Style.BRIGHT}✘ Ошибка при изменении прав доступа.{Style.RESET_ALL}")

class GeneratePasswordHashCommand(Command):
    def __init__(self):
        super().__init__(["-gph", "generate-password-hash"], "Генерирует хэш пароля")

    def execute(self, *args):
        if not args:
            print(f"{Fore.RED}{Style.BRIGHT}✘ Ошибка: Пожалуйста, укажите пароль для генерации хеша.{Style.RESET_ALL}")
            return

        password = args[0]
        hash_value = None
        tools = [("htpasswd", ["htpasswd", "-bnBC", "10", "", password]),
                 ("php", ["php", "-r", f"echo password_hash('{password}', PASSWORD_DEFAULT);"]),
                 ("openssl", ["openssl", "passwd", "-6", password])]

        for tool, command in tools:
            if subprocess.run(["which", tool], capture_output=True).returncode == 0:
                try:
                    result = subprocess.run(command, capture_output=True, text=True, check=True)
                    hash_value = result.stdout.strip().split(":")[1] if tool == "htpasswd" else result.stdout.strip()
                    break
                except subprocess.CalledProcessError:
                    continue

        if hash_value:
            print(f"{Fore.GREEN}{Style.BRIGHT}Сгенерированный хеш:{Style.RESET_ALL} {Fore.CYAN}{hash_value}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}{Style.BRIGHT}✘ Ошибка: Команды htpasswd, PHP и OpenSSL не найдены. Установите одну из них для генерации хеша.{Style.RESET_ALL}")

class UpdateScriptCommand(Command):
    def __init__(self):
        super().__init__(["update", "upgrade"], "Обновляет скрипт до последней версии")

    def execute(self, *args):
        home_dir = os.path.expanduser("~")
        repo_dir = os.path.join(home_dir, "qq")

        if not os.path.exists(os.path.join(repo_dir, ".git")):
            print(f"{Fore.RED}{Style.BRIGHT}✘ Ошибка: Папка $HOME/qq не настроена как Git репозиторий.{Style.RESET_ALL}")
            sys.exit(1)

        try:
            os.chdir(repo_dir)

            print(f"{Fore.YELLOW}{Style.BRIGHT}⚙ Откат к чистой версии ветки master...{Style.RESET_ALL}")
            subprocess.run(["git", "checkout", "master"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["git", "reset", "--hard", "origin/master"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            print(f"{Fore.YELLOW}{Style.BRIGHT}🔄 Получение последних изменений из удаленного репозитория...{Style.RESET_ALL}")
            subprocess.run(["git", "pull", "origin", "master"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            print(f"{Fore.GREEN}{Style.BRIGHT}✔ Скрипт успешно обновлен до последней версии в ветке master!{Style.RESET_ALL}")
        except subprocess.CalledProcessError:
            print(f"{Fore.RED}{Style.BRIGHT}✘ Ошибка обновления скрипта.{Style.RESET_ALL}")
            sys.exit(1)

class GetExternalIpCommand(Command):
    def __init__(self):
        super().__init__(["-eip", "external-ip"], "Выводит IP для внешнего доступа")

    def execute(self, *args):
        try:
            result = subprocess.run(["ifconfig"], capture_output=True, text=True)
            ip_lines = result.stdout.split('\n')
            external_ip = None

            for line in ip_lines:
                if 'inet ' in line and not line.strip().startswith('127.'):
                    external_ip = line.split()[1]
                    break

            if external_ip:
                 print(f"{Fore.GREEN}{Style.BRIGHT}🌍 IP для внешнего доступа:{Style.RESET_ALL} {Fore.CYAN}{external_ip}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}{Style.BRIGHT}❌ Не удалось определить внешний IP-адрес.{Style.RESET_ALL}")

        except Exception as e:
            print(f"{Fore.RED}{Style.BRIGHT}⚠️ Ошибка при получении внешнего IP-адреса: {str(e)}{Style.RESET_ALL}")

class SystemCommand:
    @staticmethod
    def register(registry):
        registry.register_command(GeneratePasswordHashCommand(), "system")
        registry.register_command(GetExternalIpCommand(), "system")
        registry.register_command(GitIgnoreFileModeCommand(), "system")
        registry.register_command(ChmodAllCommand(), "system")
        registry.register_command(UpdateScriptCommand(), "system")

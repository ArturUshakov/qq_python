# commands/system.py
import os
import subprocess
import sys
import requests
import zipfile
import io
import shutil
from .command_registry import Command
from colorama import Fore, Style, init

init(autoreset=True)

class ChmodAllCommand(Command):
    def __init__(self):
        super().__init__(["-ch", "chmod"], "Рекурсивно выставляет права 777 с директории выполнения")

    def execute(self, *args):
        try:
            print(
                f"{Fore.YELLOW}{Style.BRIGHT}⚙ Изменение прав доступа для всех файлов и директорий в текущей папке...{Style.RESET_ALL}")
            subprocess.run(["sudo", "chmod", "777", "-R", "."], check=True)
            print(
                f"{Fore.GREEN}{Style.BRIGHT}✔ Все файлы и директории в текущей папке успешно получили права 777.{Style.RESET_ALL}")
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
            print(
                f"{Fore.GREEN}{Style.BRIGHT}Сгенерированный хеш:{Style.RESET_ALL} {Fore.CYAN}{hash_value}{Style.RESET_ALL}")
        else:
            print(
                f"{Fore.RED}{Style.BRIGHT}✘ Ошибка: Команды htpasswd, PHP и OpenSSL не найдены. Установите одну из них для генерации хеша.{Style.RESET_ALL}")

def change_ownership_with_sudo(repo_dir):
    try:
        subprocess.run(["sudo", "chmod", "777", "-R", repo_dir], check=True)
        print("✔ Права на папку успешно обновлены.")
    except subprocess.CalledProcessError as e:
        print(f"✘ Ошибка при изменении прав доступа: {e}")
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
                print(
                    f"{Fore.GREEN}{Style.BRIGHT}🌍 IP для внешнего доступа:{Style.RESET_ALL} {Fore.CYAN}{external_ip}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}{Style.BRIGHT}❌ Не удалось определить внешний IP-адрес.{Style.RESET_ALL}")

        except Exception as e:
            print(f"{Fore.RED}{Style.BRIGHT}⚠️ Ошибка при получении внешнего IP-адреса: {str(e)}{Style.RESET_ALL}")


class GitIgnorePermissionsCommand(Command):
    def __init__(self):
        super().__init__(
            ["-gi", "git-ignore"],
            "Управление отслеживанием прав доступа (chmod) в Git [--help для опций]"
        )

    def execute(self, *args):
        if not os.path.isdir(".git"):
            print(f"{Fore.RED}✘ Это не Git-репозиторий (папка .git не найдена).{Style.RESET_ALL}")
            return

        arg = args[0] if args else "--disable"

        if arg in ["-h", "--help", "help"]:
            self.print_help()
            return

        if arg == "--status":
            result = subprocess.run(["git", "config", "--get", "core.fileMode"], capture_output=True, text=True)
            value = result.stdout.strip()
            if value == "false":
                print(f"{Fore.GREEN}✔ Git не отслеживает изменения прав доступа (core.fileMode=false).{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⚠ Git отслеживает изменения прав доступа (core.fileMode={value or 'true'}).{Style.RESET_ALL}")

        elif arg == "--enable":
            subprocess.run(["git", "config", "core.fileMode", "true"])
            print(f"{Fore.CYAN}ℹ️ Git теперь будет отслеживать изменения прав доступа (core.fileMode=true).{Style.RESET_ALL}")

        elif arg == "--disable":
            subprocess.run(["git", "config", "core.fileMode", "false"])
            print(f"{Fore.GREEN}✔ Git больше не будет отслеживать chmod-изменения (core.fileMode=false).{Style.RESET_ALL}")

        else:
            print(f"{Fore.RED}✘ Неизвестный аргумент: {arg}{Style.RESET_ALL}")
            self.print_help()

    def print_help(self):
        print(f"""{Fore.CYAN}
Использование: qq -gi [флаг]

Флаги:
  --disable     Отключить отслеживание изменений прав доступа (по умолчанию)
  --enable      Включить отслеживание изменений прав
  --status      Показать текущее состояние core.fileMode
  -h, --help    Показать эту справку
{Style.RESET_ALL}""")

class SystemCommand:
    @staticmethod
    def register(registry):
        registry.register_command(GeneratePasswordHashCommand(), "system")
        registry.register_command(GetExternalIpCommand(), "system")
        registry.register_command(ChmodAllCommand(), "system")
        registry.register_command(GitIgnorePermissionsCommand(), "system")

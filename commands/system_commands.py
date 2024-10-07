# commands/system_commands.py
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
        super().__init__("-ch", "Рекурсивно выставляет права 777 с директории выполнения")

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


class UpdateScriptCommand(Command):
    def __init__(self):
        super().__init__(["update", "upgrade"], "Обновляет скрипт до последней версии")

    def execute(self, *args):
        home_dir = os.path.expanduser("~")
        repo_dir = os.path.join(home_dir, "qq")
        release_url = "https://api.github.com/repos/ArturUshakov/qq/releases/latest"

        if not os.path.exists(repo_dir):
            os.makedirs(repo_dir)

        try:
            print("🔄 Получение информации о последнем релизе...")
            response = requests.get(release_url)
            response.raise_for_status()
            release_data = response.json()
            zip_url = release_data["zipball_url"]

            print("⚙ Скачивание исходного кода последнего релиза...")
            zip_response = requests.get(zip_url)
            zip_response.raise_for_status()

            zip_path = os.path.join(repo_dir, "latest_release.zip")

            with open(zip_path, "wb") as f:
                f.write(zip_response.content)

            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(repo_dir)

            print("🗑 Удаление архива...")
            os.remove(zip_path)

            temp_dir = next(os.path.join(repo_dir, d) for d in os.listdir(repo_dir) if os.path.isdir(os.path.join(repo_dir, d)) and d.startswith("ArturUshakov-qq"))
            for file_name in os.listdir(temp_dir):
                shutil.move(os.path.join(temp_dir, file_name), repo_dir)

            shutil.rmtree(temp_dir)

            print("🗑 Удаление ненужных файлов...")
            files_to_remove = [".github", "README.md", ".gitignore"]
            for file_name in files_to_remove:
                file_path = os.path.join(repo_dir, file_name)
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                elif os.path.isfile(file_path):
                    os.remove(file_path)

            print("Выставление прав на папку...")
            shutil.chown(repo_dir, user=os.getenv("SUDO_USER", os.getenv("USER")), group=os.getenv("SUDO_USER", os.getenv("USER")))

            print("✔ Скрипт успешно обновлен до последней версии!")
        except requests.exceptions.RequestException as e:
            print(f"✘ Ошибка при скачивании исходного кода: {e}")
            sys.exit(1)
        except zipfile.BadZipFile:
            print("✘ Ошибка распаковки архива.")
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


class SystemCommand:
    @staticmethod
    def register(registry):
        registry.register_command(GeneratePasswordHashCommand(), "system")
        registry.register_command(GetExternalIpCommand(), "system")
        registry.register_command(ChmodAllCommand(), "system")
        registry.register_command(UpdateScriptCommand(), "system")

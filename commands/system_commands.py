import os
import subprocess
import sys
from .command_registry import Command
from utils import print_colored

class GitIgnoreFileModeCommand(Command):
    def __init__(self):
        super().__init__("-gi", "Отключает отслеживание изменений прав файлов в Git")

    def execute(self, *args):
        import subprocess
        subprocess.run(["git", "config", "core.fileMode", "false"])
        print("Отключено отслеживание изменений прав файлов в Git.")

class ChmodAllCommand(Command):
    def __init__(self):
        super().__init__("-ch", "Рекурсивно выставляет права 777 с директории выполнения")

    def execute(self, *args):
        try:
            subprocess.run(["sudo", "chmod", "777", "-R", "."], check=True)
            print(print_colored("bright_green", "Все файлы и директории в текущей папке получили права 777."))
        except subprocess.CalledProcessError:
            print(print_colored("bright_red", "Ошибка при изменении прав доступа."))

class GeneratePasswordHashCommand(Command):
    def __init__(self):
        super().__init__(["-gph", "generate-password-hash"], "Генерирует хэш пароля")

    def execute(self, *args):
        if not args:
            print(print_colored("bright_red", "Пожалуйста, укажите пароль для генерации хеша"))
            return

        password = args[0]
        hash_value = None

        if subprocess.run(["which", "htpasswd"], capture_output=True).returncode == 0:
            result = subprocess.run(["htpasswd", "-bnBC", "10", "", password], capture_output=True, text=True)
            hash_value = result.stdout.strip().split(":")[1]
        elif subprocess.run(["which", "php"], capture_output=True).returncode == 0:
            result = subprocess.run(["php", "-r", f"echo password_hash('{password}', PASSWORD_DEFAULT);"], capture_output=True, text=True)
            hash_value = result.stdout.strip()
        elif subprocess.run(["which", "openssl"], capture_output=True).returncode == 0:
            result = subprocess.run(["openssl", "passwd", "-6", password], capture_output=True, text=True)
            hash_value = result.stdout.strip()
        else:
            print(print_colored("bright_red", "Команды htpasswd, PHP и OpenSSL не найдены. Установите одну из них для генерации хеша."))
            return

        print(print_colored("bright_green", f"Сгенерированный хеш: {hash_value}"))

class RemoveImageCommand(Command):
    def __init__(self):
        super().__init__(["-ri", "remove-image"], "Удаляет image по указанному тегу")

    def execute(self, *args):
        if not args:
            print(print_colored("bright_red", "Ой! Пожалуйста, укажите версию для удаления."))
            return

        version = args[0]

        if version == "<none>":
            cleanup_docker_images()
            return

        images_to_remove = []

        try:
            result = subprocess.run(
                ["docker", "images", "--format", "{{.Repository}}\t{{.Tag}}\t{{.ID}}"],
                capture_output=True, text=True, check=True
            )
            images = result.stdout.strip().splitlines()

            for image in images:
                repository, tag, image_id = image.split('\t')
                if tag == version:
                    images_to_remove.append(image_id)

            if not images_to_remove:
                print(print_colored("bright_red", f"Образы с версией '{version}' не найдены."))
                return

            for image_id in images_to_remove:
                subprocess.run(["docker", "rmi", image_id], check=True)
                print(print_colored("bright_green", f"Удален образ с ID: {image_id}"))

        except subprocess.CalledProcessError:
            print(print_colored("bright_red", "Ошибка при удалении образов Docker."))

def cleanup_docker_images():
    try:
        result = subprocess.run(["docker", "images", "-f", "dangling=true", "-q"], capture_output=True, text=True)
        image_ids = result.stdout.strip().splitlines()

        if image_ids:
            subprocess.run(["docker", "rmi"] + image_ids, check=True)
            print(print_colored("bright_green", "Все images <none> очищены!"))
        else:
            print(print_colored("bright_green", "Нет images <none> для очистки."))

    except subprocess.CalledProcessError:
        print(print_colored("bright_red", "Ошибка при очистке images <none>."))

class UpdateScriptCommand(Command):
    def __init__(self):
        super().__init__(["update", "upgrade"], "Обновляет скрипт до последней версии")

    def execute(self, *args):
        home_dir = os.path.expanduser("~")
        repo_dir = os.path.join(home_dir, "qq")

        if not os.path.exists(os.path.join(repo_dir, ".git")):
            print_colored("bright_red", "Папка $HOME/qq не настроена как Git репозиторий.")
            sys.exit(1)

        try:
            # Переключение в директорию репозитория
            os.chdir(repo_dir)

            # Откат к чистой версии ветки master или другой целевой ветки
            print_colored("bright_yellow", "Откат к чистой версии ветки master...")
            subprocess.run(["git", "checkout", "master"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["git", "reset", "--hard", "origin/master"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Получение последних изменений с GitHub
            print_colored("bright_yellow", "Получение последних изменений из удаленного репозитория...")
            subprocess.run(["git", "pull", "origin", "master"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            print_colored("bright_green", "Скрипт успешно обновлен до последней версии в ветке master!")
        except subprocess.CalledProcessError as e:
            print_colored("bright_red", f"Ошибка обновления скрипта: {e}")
            sys.exit(1)

class SystemCommand:
    @staticmethod
    def register(registry):
        registry.register_command(GitIgnoreFileModeCommand(), "system")
        registry.register_command(ChmodAllCommand(), "system")
        registry.register_command(GeneratePasswordHashCommand(), "system")
        registry.register_command(RemoveImageCommand(), "system")
        registry.register_command(UpdateScriptCommand(), "system")
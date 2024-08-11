import subprocess
from utils import print_colored
from .command_registry import Command

class CleanupDockerImagesCommand(Command):
    def __init__(self):
        super().__init__(["-dni", "cleanup-docker-images"], "Удаляет <none> images")

    def execute(self, *args):
        try:
            print(print_colored("bright_yellow", "Поиск <none> images..."))
            result = subprocess.run(["docker", "images", "-f", "dangling=true", "-q"], capture_output=True, text=True)
            image_ids = result.stdout.strip().splitlines()

            if image_ids:
                print(print_colored("bright_yellow", f"Найдено {len(image_ids)} <none> images. Удаление..."))
                try:
                    subprocess.run(["docker", "rmi"] + image_ids, check=True)
                    print(print_colored("bright_green", "Все <none> images успешно удалены!"))
                except subprocess.CalledProcessError as e:
                    print(print_colored("bright_red", f"Ошибка при удалении <none> images: {str(e)}"))
                    # Попытка принудительного удаления
                    force_remove = input(print_colored("bright_yellow", "Хотите принудительно удалить эти images? (y/n): ")).lower()
                    if force_remove == 'y':
                        try:
                            subprocess.run(["docker", "rmi", "-f"] + image_ids, check=True)
                            print(print_colored("bright_green", "Все <none> images успешно удалены принудительно!"))
                        except subprocess.CalledProcessError as e:
                            print(print_colored("bright_red", f"Ошибка при принудительном удалении <none> images: {str(e)}"))
                    else:
                        print(print_colored("bright_yellow", "Принудительное удаление отменено."))
            else:
                print(print_colored("bright_green", "Нет <none> images для удаления."))

        except subprocess.CalledProcessError as e:
            print(print_colored("bright_red", f"Ошибка при поиске <none> images: {str(e)}"))

class PruneBuilderCommand(Command):
    def __init__(self):
        super().__init__(["-pb", "prune-builder"], "Удаляет неиспользуемые объекты сборки")

    def execute(self, *args):
        try:
            print(print_colored("bright_yellow", "Очистка неиспользуемых данных сборщика..."))
            result = subprocess.run(["docker", "builder", "prune", "-f"], check=True)
            if result.returncode == 0:
                print(print_colored("bright_green", "Все неиспользуемые данные сборщика успешно удалены!"))
            else:
                print(print_colored("bright_red", "Некоторые данные сборщика не удалось удалить."))

        except subprocess.CalledProcessError as e:
            print(print_colored("bright_red", f"Ошибка при очистке данных сборщика: {str(e)}"))

class CleanupCommand:
    @staticmethod
    def register(registry):
        registry.register_command(CleanupDockerImagesCommand(), "cleanup")
        registry.register_command(PruneBuilderCommand(), "cleanup")

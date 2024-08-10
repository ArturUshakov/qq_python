import subprocess
from utils import print_colored
from .command_registry import Command

class CleanupDockerImagesCommand(Command):
    def __init__(self):
        super().__init__(["-dni", "cleanup-docker-images"], "Удаляет <none> images")

    def execute(self, *args):
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

class PruneBuilderCommand(Command):
    def __init__(self):
        super().__init__(["-pb", "prune-builder"], "Удаляет неиспользуемые объекты сборки")

    def execute(self, *args):
        try:
            subprocess.run(["docker", "builder", "prune", "-f"], check=True)
            print(print_colored("bright_green", "Все неиспользуемые данные сборщика удалены!"))
        except subprocess.CalledProcessError:
            print(print_colored("bright_red", "Ошибка при очистке данных сборщика."))

class CleanupCommand:
    @staticmethod
    def register(registry):
        registry.register_command(CleanupDockerImagesCommand(), "cleanup")
        registry.register_command(PruneBuilderCommand(), "cleanup")

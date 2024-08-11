import subprocess
from colorama import Fore, Style, init
from .command_registry import Command

init(autoreset=True)

class CleanupDockerImagesCommand(Command):
    def __init__(self):
        super().__init__(["-dni", "cleanup-docker-images"], "Удаляет <none> images")

    def execute(self, *args):
        try:
            print(f"{Fore.YELLOW}Поиск <none> images...{Style.RESET_ALL}")
            result = subprocess.run(["docker", "images", "-f", "dangling=true", "-q"], capture_output=True, text=True)
            image_ids = result.stdout.strip().splitlines()

            if image_ids:
                print(f"{Fore.YELLOW}Найдено {len(image_ids)} <none> images. Удаление...{Style.RESET_ALL}")
                try:
                    subprocess.run(["docker", "rmi"] + image_ids, check=True)
                    print(f"{Fore.GREEN}Все <none> images успешно удалены!{Style.RESET_ALL}")
                except subprocess.CalledProcessError as e:
                    print(f"{Fore.RED}Ошибка при удалении <none> images: {str(e)}{Style.RESET_ALL}")
                    # Попытка принудительного удаления
                    force_remove = input(f"{Fore.YELLOW}Хотите принудительно удалить эти images? (y/n): {Style.RESET_ALL}").lower()
                    if force_remove == 'y':
                        try:
                            subprocess.run(["docker", "rmi", "-f"] + image_ids, check=True)
                            print(f"{Fore.GREEN}Все <none> images успешно удалены принудительно!{Style.RESET_ALL}")
                        except subprocess.CalledProcessError as e:
                            print(f"{Fore.RED}Ошибка при принудительном удалении <none> images: {str(e)}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}Принудительное удаление отменено.{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}Нет <none> images для удаления.{Style.RESET_ALL}")

        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}Ошибка при поиске <none> images: {str(e)}{Style.RESET_ALL}")

class PruneBuilderCommand(Command):
    def __init__(self):
        super().__init__(["-pb", "prune-builder"], "Удаляет неиспользуемые объекты сборки")

    def execute(self, *args):
        try:
            print(f"{Fore.YELLOW}Очистка неиспользуемых данных сборщика...{Style.RESET_ALL}")
            result = subprocess.run(["docker", "builder", "prune", "-f"], check=True)
            if result.returncode == 0:
                print(f"{Fore.GREEN}Все неиспользуемые данные сборщика успешно удалены!{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Некоторые данные сборщика не удалось удалить.{Style.RESET_ALL}")

        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}Ошибка при очистке данных сборщика: {str(e)}{Style.RESET_ALL}")

class CleanupCommand:
    @staticmethod
    def register(registry):
        registry.register_command(CleanupDockerImagesCommand(), "cleanup")
        registry.register_command(PruneBuilderCommand(), "cleanup")

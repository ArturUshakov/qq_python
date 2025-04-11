# commands/cleanup.py
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
                    force_remove = input(
                        f"{Fore.YELLOW}Хотите принудительно удалить эти images? (y/n): {Style.RESET_ALL}").lower()
                    if force_remove == 'y':
                        try:
                            subprocess.run(["docker", "rmi", "-f"] + image_ids, check=True)
                            print(f"{Fore.GREEN}Все <none> images успешно удалены принудительно!{Style.RESET_ALL}")
                        except subprocess.CalledProcessError as e:
                            print(
                                f"{Fore.RED}Ошибка при принудительном удалении <none> images: {str(e)}{Style.RESET_ALL}")
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


class ClearDockerCommand(Command):
    def __init__(self):
        super().__init__(
            ["-clr", "clear"],
            "Очистка Docker: образы <none>, builder cache, тома [--help для опций]"
        )

    def execute(self, *args):
        if "-h" in args or "--help" in args:
            self.print_help()
            return

        dry_run = "--dry-run" in args
        safe = "--safe" in args
        verbose = "--verbose" in args
        skip_confirm = "--yes" in args or "--force" in args

        if not dry_run and not skip_confirm:
            user_input = input(f"{Fore.YELLOW}❓ Уверены, что хотите продолжить очистку Docker? (y/n): {Style.RESET_ALL}").strip().lower()
            if user_input != "y":
                print(f"{Fore.RED}✘ Очистка отменена пользователем.{Style.RESET_ALL}")
                return

        print(f"{Fore.CYAN}📊 Объём Docker перед очисткой:{Style.RESET_ALL}")
        subprocess.run(["docker", "system", "df"])

        self.cleanup_docker_images(dry_run, safe, verbose)
        self.prune_builder(dry_run, verbose)
        self.cleanup_volumes(dry_run, verbose)

        print(f"{Fore.CYAN}\n📊 Объём Docker после очистки:{Style.RESET_ALL}")
        subprocess.run(["docker", "system", "df"])

    def cleanup_docker_images(self, dry_run=False, safe=False, verbose=False):
        print(f"{Fore.YELLOW}Поиск <none> images...{Style.RESET_ALL}")
        result = subprocess.run(["docker", "images", "-f", "dangling=true", "-q"], capture_output=True, text=True)
        image_ids = result.stdout.strip().splitlines()

        if not image_ids:
            print(f"{Fore.GREEN}✔ Нет dangling-образов для удаления.{Style.RESET_ALL}")
            return

        if dry_run:
            print(f"{Fore.CYAN}[dry-run] Нашлось {len(image_ids)} образов <none> для удаления:{Style.RESET_ALL}")
            for img in image_ids:
                print(f"  • {img}")
            return

        if safe:
            used_images = subprocess.run(["docker", "ps", "-a", "--format", "{{.Image}}"], capture_output=True, text=True).stdout.splitlines()
            safe_ids = [img for img in image_ids if img not in used_images]
        else:
            safe_ids = image_ids

        if not safe_ids:
            print(f"{Fore.YELLOW}⚠ Все найденные <none> образы используются. Пропуск удаления.{Style.RESET_ALL}")
            return

        try:
            subprocess.run(
                ["docker", "rmi"] + safe_ids,
                check=True,
                stdout=None if verbose else subprocess.DEVNULL,
                stderr=None if verbose else subprocess.DEVNULL
            )
            print(f"{Fore.GREEN}✔ Удалено {len(safe_ids)} <none> образов.{Style.RESET_ALL}")
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}✘ Ошибка при удалении образов: {e}{Style.RESET_ALL}")

    def prune_builder(self, dry_run=False, verbose=False):
        print(f"{Fore.YELLOW}Очистка builder cache...{Style.RESET_ALL}")
        if dry_run:
            print(f"{Fore.CYAN}[dry-run] Был бы выполнен: docker builder prune -f{Style.RESET_ALL}")
            return
        try:
            subprocess.run(
                ["docker", "builder", "prune", "-f"],
                check=True,
                stdout=None if verbose else subprocess.DEVNULL,
                stderr=None if verbose else subprocess.DEVNULL
            )
            print(f"{Fore.GREEN}✔ Кэш билдера успешно очищен.{Style.RESET_ALL}")
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}✘ Ошибка при очистке кэша билдера: {e}{Style.RESET_ALL}")

    def cleanup_volumes(self, dry_run=False, verbose=False):
        print(f"{Fore.YELLOW}Очистка неиспользуемых томов...{Style.RESET_ALL}")
        if dry_run:
            print(f"{Fore.CYAN}[dry-run] Был бы выполнен: docker volume prune -f{Style.RESET_ALL}")
            return
        try:
            subprocess.run(
                ["docker", "volume", "prune", "-f"],
                check=True,
                stdout=None if verbose else subprocess.DEVNULL,
                stderr=None if verbose else subprocess.DEVNULL
            )
            print(f"{Fore.GREEN}✔ Неиспользуемые тома успешно удалены.{Style.RESET_ALL}")
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}✘ Ошибка при удалении томов: {e}{Style.RESET_ALL}")

    def print_help(self):
        print(f"""{Fore.CYAN}
Очистка Docker-ресурсов: удаление dangling-образов, builder-кэша и неиспользуемых томов.

Использование:
  qq -clr [флаги]

Флаги:
  --dry-run     Показывает, что будет удалено, без выполнения
  --safe        Удаляет только явно неиспользуемые образы
  --verbose     Показывает подробный вывод Docker-команд
  --yes         Пропускает подтверждение (используйте осторожно)
  --force       То же, что и --yes
  -h, --help    Показать эту справку

По умолчанию:
  При каждом запуске требуется подтверждение для удаления.
  Безопасный режим (--safe) проверяет, не используются ли образы в контейнерах.
{Style.RESET_ALL}""")


class CleanupCommand:
    @staticmethod
    def register(registry):
        registry.register_command(CleanupDockerImagesCommand(), "cleanup")
        registry.register_command(PruneBuilderCommand(), "cleanup")
        registry.register_command(ClearDockerCommand(), "cleanup")

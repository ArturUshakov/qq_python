# commands/container_commands.py
import subprocess
import asyncio
import time
from colorama import Fore, Style, init
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
from tqdm import tqdm
from .command_registry import Command

init(autoreset=True)

class StopAllContainersCommand(Command):
    def __init__(self):
        super().__init__(["-d", "down"], "Останавливает все запущенные контейнеры по фильтру имени или проекта")

    async def stop_all_containers(self):
        start_time = time.time()

        process = await asyncio.create_subprocess_exec(
            "docker", "ps", "-q", stdout=asyncio.subprocess.PIPE
        )
        stdout, _ = await process.communicate()
        container_ids = stdout.decode().strip().splitlines()

        if not container_ids:
            print(Fore.RED + "🚫 Нет запущенных контейнеров для остановки.")
            return

        print(Fore.BLUE + "🔄 Остановка всех запущенных контейнеров:")

        try:
            await asyncio.create_subprocess_exec(
                "docker", "kill", *container_ids,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE
            )
            print(Fore.GREEN + f"✔ Все контейнеры остановлены.")
        except Exception as e:
            print(Fore.RED + f"✘ Ошибка при остановке контейнеров: {str(e)}")

        total_time = time.time() - start_time
        print(f"\n⏱ Время выполнения: {total_time:.2f} секунд")

    async def stop_filtered_containers(self, filter_option):
        start_time = time.time()

        process = await asyncio.create_subprocess_exec(
            "docker", "ps", "--format", "{{.ID}}\t{{.Names}}\t{{.Label \"com.docker.compose.project\"}}",
            stdout=asyncio.subprocess.PIPE
        )
        stdout, _ = await process.communicate()
        container_data = stdout.decode().strip().splitlines()

        matching_containers = [line for line in container_data if filter_option in line.split('\t')[2]]

        if not matching_containers:
            print(Fore.YELLOW + f"⚠ Проект, содержащий '{filter_option}', не найден. Пытаемся найти контейнеры по названию...")

            process = await asyncio.create_subprocess_exec(
                "docker", "ps", "--filter", f"name={filter_option}", "--format", "{{.ID}}\t{{.Names}}",
                stdout=asyncio.subprocess.PIPE
            )
            stdout, _ = await process.communicate()
            matching_containers = stdout.decode().strip().splitlines()

            if not matching_containers:
                print(Fore.RED + f"🚫 Контейнеры, содержащие '{filter_option}' в названии, не найдены.")
                return

        print(Fore.BLUE + f"🔍 Остановка контейнеров с частью имени/проекта {Fore.YELLOW}{filter_option}{Fore.BLUE}:")

        container_ids = [line.split('\t')[0] for line in matching_containers]

        try:
            await asyncio.create_subprocess_exec(
                "docker", "kill", *container_ids,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE
            )
            print(Fore.GREEN + f"✔ Все контейнеры остановлены.")
        except Exception as e:
            print(Fore.RED + f"✘ Ошибка при остановке контейнеров: {str(e)}")

        total_time = time.time() - start_time
        print(f"\n⏱ Время выполнения: {total_time:.2f} секунд")

    def execute(self, *args):
        filter_option = args[0] if args else ""
        if filter_option:
            asyncio.run(self.stop_filtered_containers(filter_option))
        else:
            asyncio.run(self.stop_all_containers())

class ListContainersCommand(Command):
    def __init__(self, names, filter_option, title, format_option):
        super().__init__(names, title)
        self.filter_option = filter_option
        self.title = title
        self.format_option = format_option

    def list_containers(self):
        compose_projects = {}

        result = subprocess.run(
            ["docker", "ps"] + self.filter_option.split() + ["--format", self.format_option],
            capture_output=True, text=True
        )
        containers = result.stdout.strip().splitlines()

        for container in containers:
            parts = container.split("\t")

            if len(parts) == 3:
                name, status, project = parts
            else:
                name, status = parts
                project = "N/A"

            if project in compose_projects:
                compose_projects[project].append((name, status))
            else:
                compose_projects[project] = [(name, status)]

        print(Fore.BLUE + self.title)
        for project, containers in compose_projects.items():
            print(Fore.YELLOW + f"\nПроект: {project}")
            for name, status in containers:
                print(f"{Fore.GREEN}{name.ljust(55)} {Fore.CYAN}{status}")

    def execute(self, *args):
        self.list_containers()


class ListRunningContainersCommand(ListContainersCommand):
    def __init__(self):
        super().__init__(["-l", "list"], "", "Запущенные контейнеры",
                         "{{.Names}}\t{{.Status}}\t{{.Label \"com.docker.compose.project\"}}")


class ListAllContainersCommand(ListContainersCommand):
    def __init__(self):
        super().__init__(["-la", "list-all"], "-a", "Все контейнеры",
                         "{{.Names}}\t{{.Status}}\t{{.Label \"com.docker.compose.project\"}}")


class ListImagesCommand(Command):
    def __init__(self):
        super().__init__(["-li", "list-images"], "Выводит список всех образов")

    def execute(self, *args):
        print(Fore.BLUE + "📦 Список образов:")
        print(f"{Fore.BLUE}{'ID':25} {Fore.BLUE}{'РЕПОЗИТОРИЙ':60} {Fore.BLUE}{'ТЕГ':27} {Fore.BLUE}{'РАЗМЕР':15}")

        try:
            result = subprocess.run(
                ["docker", "images", "--format", "{{.ID}}\t{{.Repository}}\t{{.Tag}}\t{{.Size}}"],
                capture_output=True, text=True, check=True
            )
            images = result.stdout.strip().splitlines()

            for image in images:
                id, repository, tag, size = image.split('\t')
                print(f"{Fore.GREEN}{id:25} {Fore.YELLOW}{repository:60} {Fore.CYAN}{tag:27} {Fore.RED}{size:15}")

        except subprocess.CalledProcessError:
            print(Fore.RED + "❌ Ошибка при получении списка образов Docker.")


class RemoveImageCommand(Command):
    def __init__(self):
        super().__init__(["-ri", "remove-image"], "Удаляет image по указанному тегу")

    def execute(self, *args):
        if not args:
            print(f"{Fore.RED}{Style.BRIGHT}✘ Ошибка: Пожалуйста, укажите тег версии для удаления.{Style.RESET_ALL}")
            return

        version = args[0]

        if version == "<none>":
            cleanup_docker_images()
            return

        try:
            result = subprocess.run(
                ["docker", "images", "--format", "{{.Repository}}\t{{.Tag}}\t{{.ID}}"],
                capture_output=True, text=True, check=True
            )
            images = result.stdout.strip().splitlines()
            images_to_remove = [image_id for repo, tag, image_id in (img.split('\t') for img in images) if
                                tag == version]

            if not images_to_remove:
                print(f"{Fore.YELLOW}{Style.BRIGHT}⚠ Образы с тегом '{version}' не найдены.{Style.RESET_ALL}")
                return

            for image_id in images_to_remove:
                subprocess.run(["docker", "rmi", image_id], check=True)
                print(f"{Fore.GREEN}{Style.BRIGHT}✔ Удален образ с ID: {image_id}{Style.RESET_ALL}")

        except subprocess.CalledProcessError:
            print(f"{Fore.RED}{Style.BRIGHT}✘ Ошибка при удалении образов Docker.{Style.RESET_ALL}")


def cleanup_docker_images():
    try:
        result = subprocess.run(["docker", "images", "-f", "dangling=true", "-q"], capture_output=True, text=True)
        image_ids = result.stdout.strip().splitlines()

        if image_ids:
            subprocess.run(["docker", "rmi"] + image_ids, check=True)
            print(f"{Fore.GREEN}{Style.BRIGHT}✔ Все images <none> успешно очищены!{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}{Style.BRIGHT}ℹ Нет images <none> для очистки.{Style.RESET_ALL}")

    except subprocess.CalledProcessError:
        print(f"{Fore.RED}{Style.BRIGHT}✘ Ошибка при очистке images <none>.{Style.RESET_ALL}")


class ContainerCommand:
    @staticmethod
    def register(registry):
        registry.register_command(StopAllContainersCommand(), "container")
        registry.register_command(ListRunningContainersCommand(), "container")
        registry.register_command(ListAllContainersCommand(), "container")
        registry.register_command(ListImagesCommand(), "container")
        registry.register_command(RemoveImageCommand(), "container")

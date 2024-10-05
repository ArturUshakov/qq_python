# commands/container_commands.py
import subprocess
from colorama import Fore, Style, init
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
from tqdm import tqdm
from .command_registry import Command

init(autoreset=True)


class StopAllContainersCommand(Command):
    def __init__(self):
        super().__init__(["-d", "down"], "Останавливает все запущенные контейнеры или контейнеры по фильтру имени")

    def stop_container(self, container_id, container_name):
        try:
            process = subprocess.Popen(["docker", "stop", container_id], stdout=subprocess.DEVNULL,
                                       stderr=subprocess.PIPE)
            _, stderr = process.communicate()
            if process.returncode == 0:
                return container_name, True
            return container_name, False, stderr.decode().strip()
        except Exception as e:
            return container_name, False, str(e)

    def execute(self, *args):
        filter_option = args[0] if args else ""
        if filter_option:
            self.stop_filtered_containers(filter_option)
        else:
            self.stop_all_containers()

    def stop_all_containers(self):
        result = subprocess.run(["docker", "ps", "--format", "{{.ID}}\t{{.Names}}"], capture_output=True, text=True)
        container_data = result.stdout.strip().splitlines()

        if not container_data:
            print(Fore.RED + "🚫 Нет запущенных контейнеров для остановки.")
            return

        print(Fore.BLUE + "🔄 Остановка всех запущенных контейнеров:")

        container_queue = Queue()
        max_name_length = 0

        for cid in container_data:
            container_id, container_name = cid.split('\t')
            container_queue.put((container_id, container_name))
            max_name_length = max(max_name_length, len(container_name))

        stopped_containers = []
        failed_containers = []

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(self.stop_container, container_id, container_name): container_name
                       for container_id, container_name in
                       [container_queue.get() for _ in range(container_queue.qsize())]}

            with tqdm(total=len(futures), desc="Остановка контейнеров", unit="container", ncols=100) as pbar:
                for future in as_completed(futures):
                    container_name, success, *error = future.result()
                    if success:
                        stopped_containers.append(container_name)
                    else:
                        failed_containers.append((container_name, error[0]))
                    pbar.update(1)

        status_msg = "остановлен"

        for name in stopped_containers:
            print(f"{Fore.GREEN}{name.ljust(max_name_length)} {Fore.RED}{status_msg}")

        if failed_containers:
            print(Fore.RED + "\n❗ Некоторые контейнеры не удалось остановить:")
            for name, error in failed_containers:
                print(f"{Fore.RED}{name.ljust(max_name_length)}: {Fore.YELLOW}{error}")

    def stop_filtered_containers(self, filter_option):
        result = subprocess.run(
            ["docker", "ps", "--filter", f"name={filter_option}", "--format", "{{.ID}}\t{{.Names}}"],
            capture_output=True, text=True)
        container_data = result.stdout.strip().splitlines()

        if not container_data:
            print(Fore.RED + f"🚫 Контейнеры, соответствующие фильтру '{filter_option}', не найдены.")
            return

        print(Fore.BLUE + f"🔍 Остановка контейнеров, соответствующих фильтру {Fore.YELLOW}{filter_option}{Fore.BLUE}:")

        container_queue = Queue()
        max_name_length = 0

        for cid in container_data:
            container_id, container_name = cid.split('\t')
            container_queue.put((container_id, container_name))
            max_name_length = max(max_name_length, len(container_name))

        stopped_containers = []
        failed_containers = []

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(self.stop_container, container_id, container_name): container_name
                       for container_id, container_name in
                       [container_queue.get() for _ in range(container_queue.qsize())]}

            with tqdm(total=len(futures), desc="Остановка контейнеров", unit="container", ncols=100) as pbar:
                for future in as_completed(futures):
                    container_name, success, *error = future.result()
                    if success:
                        stopped_containers.append(container_name)
                    else:
                        failed_containers.append((container_name, error[0]))
                    pbar.update(1)

        status_msg = "остановлен"

        for name in stopped_containers:
            print(f"{Fore.GREEN}{name.ljust(max_name_length)} {Fore.RED}{status_msg}")

        if failed_containers:
            print(Fore.RED + "\n❗ Некоторые контейнеры не удалось остановить:")
            for name, error in failed_containers:
                print(f"{Fore.RED}{name.ljust(max_name_length)}: {Fore.YELLOW}{error}")


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

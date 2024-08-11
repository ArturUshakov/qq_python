import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
from tqdm import tqdm
from utils import print_colored
from .command_registry import Command

class StopAllContainersCommand(Command):
    def __init__(self):
        super().__init__(["-d", "down"], "Останавливает все запущенные контейнеры или контейнеры по фильтру имени")

    def stop_container(self, container_id, container_name):
        try:
            process = subprocess.Popen(["docker", "stop", container_id], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if process.returncode == 0:
                return container_name, True
            else:
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
            print(print_colored("bright_red", "Нет запущенных контейнеров для остановки."))
            return

        print(print_colored("bright_blue", "Остановка всех запущенных контейнеров:"))

        container_queue = Queue()
        max_name_length = 0

        for cid in container_data:
            container_id, container_name = cid.split('\t')
            container_queue.put((container_id, container_name))
            max_name_length = max(max_name_length, len(container_name))

        stopped_containers = []
        failed_containers = []

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(self.stop_container, container_id, container_name): container_name for container_id, container_name in [container_queue.get() for _ in range(container_queue.qsize())]}

            for future in tqdm(as_completed(futures), total=len(futures), desc="Остановка контейнеров", unit="container"):
                container_name, success, *error = future.result()
                if success:
                    stopped_containers.append(container_name)
                else:
                    failed_containers.append((container_name, error[0]))

        status_msg = "остановлен"

        for name in stopped_containers:
            print(f"{print_colored('bright_green', name.ljust(max_name_length))} {print_colored('bright_red', status_msg)}")

        if failed_containers:
            print(print_colored("bright_red", "\nНекоторые контейнеры не удалось остановить:"))
            for name, error in failed_containers:
                print(f"{print_colored('bright_red', name.ljust(max_name_length))}: {print_colored('bright_yellow', error)}")

    def stop_filtered_containers(self, filter_option):
        result = subprocess.run(["docker", "ps", "--filter", f"name={filter_option}", "--format", "{{.ID}}\t{{.Names}}"], capture_output=True, text=True)
        container_data = result.stdout.strip().splitlines()

        if not container_data:
            print(print_colored("bright_red", f"Контейнеры, соответствующие фильтру '{filter_option}', не найдены."))
            return

        print(print_colored("bright_blue", f"Остановка контейнеров, соответствующих фильтру {print_colored('bright_yellow', filter_option)}:"))
        print(print_colored("bright_blue", "-----------------------------------------------------------"))

        container_queue = Queue()
        max_name_length = 0

        for cid in container_data:
            container_id, container_name = cid.split('\t')
            container_queue.put((container_id, container_name))
            max_name_length = max(max_name_length, len(container_name))

        stopped_containers = []
        failed_containers = []

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(self.stop_container, container_id, container_name): container_name for container_id, container_name in [container_queue.get() for _ in range(container_queue.qsize())]}

            with tqdm(total=len(futures), desc="Остановка контейнеров", unit="container") as pbar:
                for future in as_completed(futures):
                    container_name, success, *error = future.result()
                    if success:
                        stopped_containers.append(container_name)
                    else:
                        failed_containers.append((container_name, error[0]))
                    pbar.update(1)

        status_msg = "остановлен"

        for name in stopped_containers:
            print(f"{print_colored('bright_green', name.ljust(max_name_length))} {print_colored('bright_red', status_msg)}")

        if failed_containers:
            print(print_colored("bright_red", "\nНекоторые контейнеры не удалось остановить:"))
            for name, error in failed_containers:
                print(f"{print_colored('bright_red', name.ljust(max_name_length))}: {print_colored('bright_yellow', error)}")

        print(print_colored("bright_blue", "-----------------------------------------------------------"))

class GetExternalIpCommand(Command):
    def __init__(self):
        super().__init__(["-eip", "external-ip"], "Выводит ip для внешнего доступа")

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
                print(f"IP для внешнего доступа: {print_colored('bright_green', external_ip)}")
            else:
                print(print_colored("bright_red", "Не удалось определить внешний IP-адрес."))

        except Exception as e:
            print(print_colored("bright_red", f"Ошибка при получении внешнего IP-адреса: {str(e)}"))

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
            name, status, project = container.split("\t")
            if project in compose_projects:
                compose_projects[project].append((name, status))
            else:
                compose_projects[project] = [(name, status)]

        print(print_colored("bright_blue", self.title))
        for project, containers in compose_projects.items():
            print(print_colored("bright_yellow", f"\nПроект: {project}"))
            for name, status in containers:
                print(f"{print_colored('bright_green', name):55} {print_colored('bright_cyan', status)}")

    def execute(self, *args):
        self.list_containers()

class ListRunningContainersCommand(ListContainersCommand):
    def __init__(self):
        super().__init__(["-l", "list"], "", "Запущенные контейнеры", "{{.Names}}\t{{.Status}}\t{{.Label \"com.docker.compose.project\"}}")

class ListAllContainersCommand(ListContainersCommand):
    def __init__(self):
        super().__init__(["-la", "list-all"], "-a", "Все контейнеры", "{{.Names}}\t{{.Status}}\t{{.Label \"com.docker.compose.project\"}}")

class ListImagesCommand(Command):
    def __init__(self):
        super().__init__(["-li", "list-images"], "Выводит список всех образов")

    def execute(self, *args):
        print(print_colored("bright_blue", "Список образов:"))
        print(f"{print_colored('bright_blue', 'ID'):25} {print_colored('bright_blue', 'РЕПОЗИТОРИЙ'):60} {print_colored('bright_blue', 'ТЕГ'):27} {print_colored('bright_blue', 'РАЗМЕР'):15}")

        try:
            result = subprocess.run(
                ["docker", "images", "--format", "{{.ID}}\t{{.Repository}}\t{{.Tag}}\t{{.Size}}"],
                capture_output=True, text=True, check=True
            )
            images = result.stdout.strip().splitlines()

            for image in images:
                id, repository, tag, size = image.split('\t')
                print(f"{print_colored('bright_green', id):25} {print_colored('bright_yellow', repository):60} {print_colored('bright_cyan', tag):27} {print_colored('bright_red', size):15}")

        except subprocess.CalledProcessError:
            print(print_colored("bright_red", "Ошибка при получении списка образов Docker."))

class ContainerCommand:
    @staticmethod
    def register(registry):
        registry.register_command(GetExternalIpCommand(), "container")
        registry.register_command(ListRunningContainersCommand(), "container")
        registry.register_command(ListAllContainersCommand(), "container")
        registry.register_command(StopAllContainersCommand(), "container")
        registry.register_command(ListImagesCommand(), "container")

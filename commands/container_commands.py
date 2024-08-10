import subprocess
from .command_registry import Command
from concurrent.futures import ThreadPoolExecutor
from utils import print_colored

class StopAllContainersCommand(Command):
    def __init__(self):
        super().__init__(["-d", "down"], "Останавливает все запущенные контейнеры или контейнеры по фильтру имени")

    def stop_container(self, container_id):
        result = subprocess.run(
            ["docker", "ps", "--filter", f"id={container_id}", "--format", "{{.Names}}"],
            capture_output=True, text=True
        )
        container_name = result.stdout.strip()

        subprocess.run(["docker", "stop", container_id], stdout=subprocess.DEVNULL)

        return container_name

    def execute(self, *args):
        filter_option = args[0] if args else ""
        if filter_option:
            self.stop_filtered_containers(filter_option)
        else:
            self.stop_all_containers()

    def stop_all_containers(self):
        result = subprocess.run(["docker", "ps", "-q"], capture_output=True, text=True)
        container_ids = result.stdout.strip().splitlines()

        if not container_ids:
            print(print_colored("bright_red", "Нет запущенных контейнеров для остановки."))
            return

        print(print_colored("bright_blue", "Остановка всех запущенных контейнеров:"))

        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_container_id = {executor.submit(self.stop_container, cid): cid for cid in container_ids}

            for future in future_to_container_id:
                container_name = future.result()
                print(f"{print_colored('bright_green', container_name)} {print_colored('bright_red', 'остановлен')}")

    def stop_filtered_containers(self, filter_option):
        result = subprocess.run(["docker", "ps", "--filter", f"name={filter_option}", "-q"], capture_output=True, text=True)
        container_ids = result.stdout.strip().splitlines()

        if not container_ids:
            print(print_colored("bright_red", f"Контейнеры, соответствующие фильтру '{filter_option}', не найдены."))
            return

        print(print_colored("bright_blue", f"Остановка контейнеров, соответствующих фильтру {print_colored('bright_yellow', filter_option)}:"))
        print(print_colored("bright_blue", "-----------------------------------------------------------"))

        for container_id in container_ids:
            result = subprocess.run(
                ["docker", "ps", "--filter", f"id={container_id}", "--format", "{{.Names}}"],
                capture_output=True, text=True
            )
            container_name = result.stdout.strip()
            subprocess.run(["docker", "stop", container_id], stdout=subprocess.DEVNULL)
            print(f"{print_colored('bright_green', container_name)} {print_colored('bright_red', 'остановлен')}")

        print(print_colored("bright_blue", "-----------------------------------------------------------"))

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
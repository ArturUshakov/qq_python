# commands/container.py
import subprocess
import asyncio
import time
import re
from colorama import Fore, Style, init
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
        if container_ids:
            kill_process = await asyncio.create_subprocess_exec(
                "docker", "kill", *container_ids,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE
            )
            _, stderr = await kill_process.communicate()

            if kill_process.returncode == 0:
                print(Fore.GREEN + f"✔ Все контейнеры остановлены.")
            else:
                print(Fore.RED + f"✘ Ошибка при остановке контейнеров: {stderr.decode()}")

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
        if matching_containers:
            container_ids = [line.split('\t')[0] for line in matching_containers]
            kill_process = await asyncio.create_subprocess_exec(
                "docker", "kill", *container_ids,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE
            )
            _, stderr = await kill_process.communicate()

            if kill_process.returncode == 0:
                print(Fore.GREEN + f"✔ Все контейнеры остановлены.")
            else:
                print(Fore.RED + f"✘ Ошибка при остановке контейнеров: {stderr.decode()}")

        total_time = time.time() - start_time
        print(f"\n⏱ Время выполнения: {total_time:.2f} секунд")

    def execute(self, *args):
        filter_option = args[0] if args else ""
        asyncio.run(self.execute_async(filter_option))

    async def execute_async(self, filter_option):
        if filter_option:
            await self.stop_filtered_containers(filter_option)
        else:
            await self.stop_all_containers()

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
                         "{{.Names}}\t{{.Status}}\t{{.Label \"com.docker.compose.project\"}}\t{{.Image}}\t{{.Ports}}")

    def translate_status(self, status):
        if "Up" in status:
            return "Запущен"
        elif "Exited" in status:
            return "Остановлен"
        elif "Restarting" in status:
            return "Перезапускается"
        else:
            return status

    def list_containers(self):
        compose_projects = {}
        WEB_SERVICES = [
            "nginx", "apache", "node", "vite", "react", "flask",
            "laravel", "express", "next", "nuxt", "adminer", "grafana", "portainer"
        ]

        result = subprocess.run(
            ["docker", "ps", "--format", self.format_option],
            capture_output=True, text=True
        )
        containers = result.stdout.strip().splitlines()

        for container in containers:
            parts = container.split("\t")
            if len(parts) == 5:
                name, status, project, image, ports = parts
            else:
                name, status, project, image = parts
                ports = ""

            status_ru = self.translate_status(status)

            port_info = ""
            if status_ru == "Запущен" and "->" in ports:
                url_ports = []
                matches = re.findall(r"(?:0\.0\.0\.0|::|127\.0\.0\.1)?:(\d+)->", ports)
                for port in matches:
                    if any(service in image.lower() for service in WEB_SERVICES):
                        url_ports.append(f"http://localhost:{port}")
                    else:
                        url_ports.append(f"{port}/tcp")
                port_info = ", ".join(sorted(set(url_ports)))
            elif status_ru == "Запущен":
                port_info = ports

            if project in compose_projects:
                compose_projects[project].append((name, status_ru, image, port_info))
            else:
                compose_projects[project] = [(name, status_ru, image, port_info)]

        print(Fore.BLUE + self.title)
        for project, containers in compose_projects.items():
            print(Fore.YELLOW + f"\nПроект: {project}")
            for name, status, image, port_info in containers:
                print(f"{Fore.GREEN}{name.ljust(55)} {Fore.CYAN}{status.ljust(20)} {Fore.MAGENTA}{port_info}")

    def execute(self, *args):
        self.list_containers()


class ListAllContainersCommand(ListContainersCommand):
    def __init__(self):
        super().__init__(["-la", "list-all"], "-a", "Все контейнеры",
                         "{{.Names}}\t{{.Status}}\t{{.Label \"com.docker.compose.project\"}}")


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

class ExecInContainerCommand(Command):
    def __init__(self):
        super().__init__(["-e", "exec"], "Вход в контейнер (по части имени). Используйте -r для root-доступа.")

    def get_containers(self):
        try:
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip().splitlines()
        except subprocess.CalledProcessError as e:
            print(Fore.RED + f"✘ Ошибка при получении списка контейнеров: {str(e)}")
            return []

    def find_container(self, partial_name):
        containers = self.get_containers()
        partial_name_lower = partial_name.lower()

        matching_containers = [name for name in containers if partial_name_lower in name.lower()]

        if not matching_containers:
            print(Fore.RED + f"✘ Контейнер с частью имени '{partial_name}' не найден.")
            return None

        if len(matching_containers) > 1:
            print(Fore.YELLOW + "⚠ Найдено несколько контейнеров с похожими именами:")
            for idx, container in enumerate(matching_containers, 1):
                print(f"  {idx}. {container}")
            try:
                choice = int(input("Введите номер контейнера для подключения: "))
                if 1 <= choice <= len(matching_containers):
                    return matching_containers[choice - 1]
                else:
                    print(Fore.RED + "✘ Неверный выбор.")
                    return None
            except ValueError:
                print(Fore.RED + "✘ Некорректный ввод, необходимо ввести число.")
                return None

        return matching_containers[0]

    def check_container_running(self, container_name):
        try:
            result = subprocess.run(
                ["docker", "inspect", "-f", "{{.State.Running}}", container_name],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip() == "true"
        except subprocess.CalledProcessError:
            return False

    def exec_command(self, container_name, command, as_root=False):
        if not self.check_container_running(container_name):
            print(Fore.YELLOW + f"⚠ Контейнер '{container_name}' не запущен.")
            return

        # Определение доступного shell
        if command[0] == "bash":
            try:
                subprocess.run(["docker", "exec", container_name, "which", "bash"], check=True)
            except subprocess.CalledProcessError:
                command = ["sh"]

        exec_command = ["docker", "exec", "-it"]
        if as_root:
            exec_command += ["--user", "root"]

        exec_command += [container_name] + command

        try:
            print(Fore.GREEN + f"✔ Вход в контейнер: {container_name}")
            process = subprocess.Popen(exec_command)
            exit_code = process.wait()

            is_running = self.check_container_running(container_name)

            if exit_code == 0 and is_running:
                print(Fore.GREEN + f"✔ Выход из контейнера '{container_name}' завершён корректно.")
            elif exit_code == 0 and not is_running:
                print(Fore.YELLOW + f"⚠ Контейнер '{container_name}' завершился во время вашей сессии.")
            elif exit_code != 0 and not is_running:
                print(Fore.RED + f"✘ Контейнер '{container_name}' завершился аварийно (exit code {exit_code}).")
            else:
                print(Fore.RED + f"✘ Команда завершилась с ошибкой (код {exit_code}).")

        except KeyboardInterrupt:
            print(Fore.YELLOW + "\n⚠ Прерывание пользователем (Ctrl+C).")

        except subprocess.SubprocessError as e:
            print(Fore.RED + f"✘ Ошибка при выполнении команды в контейнере: {str(e)}")

        except Exception as e:
            print(Fore.RED + f"❌ Непредвиденная ошибка: {e}")

    def execute(self, *args):
        if not args:
            print(Fore.RED + "✘ Укажите часть имени контейнера.")
            return

        as_root = False
        partial_name = None
        command = []

        for arg in args:
            if arg == "-r":
                as_root = True
            elif partial_name is None:
                partial_name = arg
            else:
                command.append(arg)

        if partial_name is None:
            print(Fore.RED + "✘ Укажите часть имени контейнера.")
            return

        if not command:
            command = ["bash"]

        container_name = self.find_container(partial_name)
        if container_name:
            self.exec_command(container_name, command, as_root=as_root)

class ContainerCommand:
    @staticmethod
    def register(registry):
        registry.register_command(StopAllContainersCommand(), "container")
        registry.register_command(ListRunningContainersCommand(), "container")
        registry.register_command(ExecInContainerCommand(), "container")
        registry.register_command(ListAllContainersCommand(), "container")

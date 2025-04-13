from cвведённойolorama import Fore, Style
import subprocess
import asyncio
import time
import re
from ..command_registry import Command

class ListRunningContainersCommand(Command):
    def __init__(self):
        super().__init__(["-l", "list"], "Показать запущенные проекты")
        self.format_option = "{{.Names}}\t{{.Status}}\t{{.Label \"com.docker.compose.project\"}}\t{{.Image}}\t{{.Ports}}"


    def translate_status(self, status):
        if "Up" in status:
            return "Запущен"
        elif "Exited" in status:
            return "Остановлен"
        elif "Created" in status:
            return "Создан"
        elif "Restarting" in status:
            return "Перезапускается"
        else:
            return status

    def strip_ansi(self, text):
        return re.sub(r'\x1b\\[[0-9;]*m', '', text)

    def list_containers(self):
        all_projects = {}
        active_projects = {}
        WEB_SERVICES = [
            "nginx", "apache", "node", "vite", "react", "flask",
            "laravel", "express", "next", "nuxt", "adminer", "grafana", "portainer"
        ]

        result = subprocess.run(
            ["docker", "ps", "-a", "--format", self.format_option],
            capture_output=True, text=True
        )
        containers = result.stdout.strip().splitlines()

        if not containers:
            print(Fore.CYAN + "🔹 Нет контейнеров")
            return

        for container in containers:
            parts = container.split("\t")
            if len(parts) == 5:
                name, status, project, image, ports = parts
            else:
                name, status, project, image = parts
                ports = ""

            status_ru = self.translate_status(status)

            port_info = ""
            if "Up" in status:
                url_ports = []
                matches = re.findall(r'(?:[\d\.]+:)?(\d+)->|^(\d+)/tcp$', ports)
                for match in matches:
                    port = match[0] or match[1]
                    if not port:
                        continue
                    if any(service in image.lower() for service in WEB_SERVICES):
                        url_ports.append(f"http://localhost:{port}")
                    else:
                        url_ports.append(f"{port}/tcp")
                port_info = ", ".join(sorted(set(url_ports))) if url_ports else ports
            else:
                port_info = ports

            if project in all_projects:
                all_projects[project].append((name, status_ru, port_info))
            else:
                all_projects[project] = [(name, status_ru, port_info)]

            if "Up" in status:
                active_projects[project] = True

        if not active_projects:
            print(Fore.CYAN + "🔹 Нет активных проектов")
            return

        for project in active_projects:
            print(Fore.YELLOW + Style.BRIGHT + f"\n📦 Проект: {project}")
            print(Fore.WHITE + "─" * 80)
            for name, status, port_info in all_projects[project]:
                name_col = Fore.RED + f"{name}" + Style.RESET_ALL
                status_col = Fore.GREEN + f"{status}" + Style.RESET_ALL
                port_col = Fore.CYAN + f"{port_info}" + Style.RESET_ALL

                raw_name_len = len(name)
                raw_status_len = len(status)
                print(f"{name_col}{' ' * (32 - raw_name_len)}│ {status_col}{' ' * (12 - raw_status_len)}│ {port_col}")

    def execute(self, *args):
        self.list_containers()

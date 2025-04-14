from ..command_registry import Command
from colorama import Fore, Style
import socket
import subprocess
import re
import requests

class NetworkConnectCommand(Command):
    def __init__(self):
        super().__init__(["-net", "network"], "Показать локальный IP, проверить доступ к проектам по портам")

    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    def get_running_containers(self):
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}\t{{.Ports}}"],
            capture_output=True, text=True
        )
        return result.stdout.strip().splitlines()

    def extract_ports(self, ports_str):
        return re.findall(r'(?:0\.0\.0\.0|127\.0\.0\.1)?:(\d+)->', ports_str)

    def check_http(self, ip, port):
        try:
            resp = requests.get(f"http://{ip}:{port}", timeout=2)
            return resp.status_code in range(200, 400)
        except:
            return False

    def execute(self, *args):
        ip = self.get_local_ip()
        containers = self.get_running_containers()
        if not containers:
            print(Fore.YELLOW + "Нет активных контейнеров." + Style.RESET_ALL)
            return

        options = []
        print(f"{Fore.BLUE}Локальный IP вашей машины: {Fore.CYAN}{ip}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Выберите проект для проверки:{Style.RESET_ALL}\n")

        seen = set()
        for line in containers:
            parts = line.split("\t")
            if len(parts) != 2:
                continue
            name, ports = parts
            exposed_ports = self.extract_ports(ports)
            for port in exposed_ports:
                key = (name, port)
                if key not in seen:
                    seen.add(key)
                    options.append((name, port))

        if not options:
            print(Fore.RED + "Нет контейнеров с проброшенными портами." + Style.RESET_ALL)
            return

        for i, (name, port) in enumerate(options, 1):
            print(f"{i}. {name:<30} → http://{ip}:{port}")

        try:
            choice = int(input("\nВведите номер проекта: "))
            if not 1 <= choice <= len(options):
                raise ValueError
        except ValueError:
            print(Fore.RED + "Неверный ввод." + Style.RESET_ALL)
            return

        name, port = options[choice - 1]
        url = f"http://{ip}:{port}"

        print(f"\nПроверка подключения к {url}")
        if self.check_http(ip, port):
            print(Fore.GREEN + "\n✔ Соединение успешно! Можно подключаться по ссылке:" + Style.RESET_ALL)
            print(f"{Fore.LIGHTCYAN_EX}{url}{Style.RESET_ALL}")
        else:
            print(Fore.RED + "✘ Не удалось подключиться. Проверь, открыт ли порт и запущен ли сервис." + Style.RESET_ALL)
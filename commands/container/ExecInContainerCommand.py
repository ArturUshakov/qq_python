from colorama import Fore, Style
import subprocess
import asyncio
import time
import re
from ..command_registry import Command

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

from colorama import Fore, Style
import subprocess
import asyncio
import time
import re
from ..command_registry import Command

class StopAllContainersCommand(Command):
    def __init__(self):
        super().__init__(["-d", "down"], "Останавливает все запущенные контейнеры по имени или проекту")

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

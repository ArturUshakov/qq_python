import re
import os
import subprocess
import requests
import time
import json

COLORS = {
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "bright_black": "\033[90m",
    "bright_red": "\033[91m",
    "bright_green": "\033[92m",
    "bright_yellow": "\033[93m",
    "bright_blue": "\033[94m",
    "bright_magenta": "\033[95m",
    "bright_cyan": "\033[96m",
    "bright_white": "\033[97m",
    "bg_black": "\033[40m",
    "bg_red": "\033[41m",
    "bg_green": "\033[42m",
    "bg_yellow": "\033[43m",
    "bg_blue": "\033[44m",
    "bg_magenta": "\033[45m",
    "bg_cyan": "\033[46m",
    "bg_white": "\033[47m",
    "bg_bright_black": "\033[100m",
    "bg_bright_red": "\033[101m",
    "bg_bright_green": "\033[102m",
    "bg_bright_yellow": "\033[103m",
    "bg_bright_blue": "\033[104m",
    "bg_bright_magenta": "\033[105m",
    "bg_bright_cyan": "\033[106m",
    "bg_bright_white": "\033[107m"
}

CACHE_FILE = os.path.expanduser("~/qq/version_cache.json")
CACHE_DURATION = 300  # 5 минут

def print_colored(color, text):
    reset = "\033[0m"
    return f"{COLORS.get(color, '')}{text}{reset}"

def get_version():
    changelog_file = os.path.expanduser("~/qq/CHANGELOG.md")
    if not os.path.isfile(changelog_file):
        return "Файл CHANGELOG.md не найден."

    with open(changelog_file, "r") as file:
        content = file.read()
        match = re.search(r'## \[(\d+\.\d+\.\d+)\]', content)
        if match:
            return match.group(1)
    return "Не удалось определить версию."

def get_cached_version():
    if os.path.isfile(CACHE_FILE):
        with open(CACHE_FILE, "r") as file:
            cache_data = json.load(file)
            if time.time() - cache_data["timestamp"] < CACHE_DURATION:
                return cache_data["latest_version"]
    return None

def set_cached_version(version):
    with open(CACHE_FILE, "w") as file:
        json.dump({"latest_version": version, "timestamp": time.time()}, file)

def get_latest_version():
    cached_version = get_cached_version()
    if cached_version:
        return cached_version

    try:
        response = requests.get("https://api.github.com/repos/ArturUshakov/qq/tags", timeout=5)
        if response.status_code == 200:
            tags = response.json()
            if tags:
                latest_version = tags[0]['name'].strip('v')  # Убираем префикс 'v' если есть
                set_cached_version(latest_version)
                return latest_version
        return "Не удалось получить последнюю версию."
    except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
        return f"Ошибка при получении последней версии: {str(e)}"

def check_for_updates():
    installed_version = get_version()
    latest_version = get_latest_version()

    if installed_version == "Файл CHANGELOG.md не найден." or installed_version == "Не удалось определить версию.":
        print(print_colored("bright_red", installed_version))
        return

    if latest_version.startswith("Ошибка"):
        print(print_colored("bright_red", latest_version))
        return

    if installed_version != latest_version:
        print(print_colored("bright_red", "\nВнимание!"))
        print(print_colored("bright_yellow", f"Доступна новая версия qq: {latest_version}. Ваша версия: {installed_version}."))
        print(print_colored("bright_yellow", "Используйте 'qq update' для обновления до последней версии."))

def process_tag_line(line):
    match = re.match(r'^## \[([0-9]+\.[0-9]+\.[0-9]+)\] - ([0-9]{4}-[0-9]{2}-[0-9]{2})$', line)
    if match:
        print(f"{print_colored('bright_green', f'## [{match.group(1)}]')} - {print_colored('bright_yellow', match.group(2))}")
    elif line.startswith("- "):
        print(f"  {print_colored('bright_cyan', line)}")
    elif line.startswith("  - "):
        print(f"    {print_colored('bright_blue', line)}")
    else:
        print(line)
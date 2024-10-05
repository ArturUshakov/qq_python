# commands/info_commands.py
import os
from colorama import Fore, Style, init
from .command_registry import Command
from utils import get_version

init(autoreset=True)


class ScriptInfoCommand(Command):
    def __init__(self):
        super().__init__(["-i", "info"], "Информация о скрипте")

    def execute(self, *args):
        version = get_version()
        border_char = "─"
        width = 65

        def center_text(text, fill_char=" "):
            return text.center(width, fill_char)

        print(Fore.LIGHTBLUE_EX + center_text("🔍 Информация о скрипте", border_char) + Style.RESET_ALL)
        print(f"{Fore.WHITE}{'Repository:':>15} {Fore.CYAN}https://github.com/ArturUshakov/qq{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{'Creator:':>15} {Fore.CYAN}https://t.me/Mariores{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{'Version:':>15} {Fore.YELLOW}{version}{Style.RESET_ALL}")
        print(Fore.RED + "\n🛠️ Последние изменения:" + Style.RESET_ALL)
        TagInfo().get_latest_tag_info()
        print(Fore.LIGHTBLUE_EX + border_char * width + "\n" + Style.RESET_ALL)


class TagInfo:
    def get_latest_tag_info(self):
        changelog_file = os.path.expanduser("~/qq/CHANGELOG.md")
        if not os.path.isfile(changelog_file):
            print(Fore.RED + "🚫 Файл CHANGELOG.md не найден." + Style.RESET_ALL)
            return

        with open(changelog_file, "r") as f:
            lines = f.readlines()

        latest_tag_line = None
        latest_tag_index = None
        for i, line in enumerate(lines):
            if line.startswith("## ["):
                latest_tag_line = line.strip()
                latest_tag_index = i
                break

        if not latest_tag_line:
            print(Fore.RED + "🚫 Тэги не найдены в файле CHANGELOG.md." + Style.RESET_ALL)
            return

        changes = []
        current_section = None
        for line in lines[latest_tag_index + 1:]:
            if line.startswith("## ["):
                break

            line = line.strip()
            if not line:
                continue

            if line.startswith("- Реализовано"):
                current_section = "Реализовано"
                changes.append(f"\n{Fore.GREEN}{current_section}{Style.RESET_ALL}")
            elif line.startswith("- Удалено"):
                current_section = "Удалено"
                changes.append(f"\n{Fore.RED}{current_section}{Style.RESET_ALL}")
            elif line.startswith("- Исправлено"):
                current_section = "Исправлено"
                changes.append(f"\n{Fore.YELLOW}{current_section}{Style.RESET_ALL}")
            elif line.startswith("- Изменено"):
                current_section = "Изменено"
                changes.append(f"\n{Fore.BLUE}{current_section}{Style.RESET_ALL}")
            elif line.startswith("- "):
                if current_section:
                    changes.append(f"  {Fore.CYAN}•{Style.RESET_ALL} {Fore.BLUE}{line[2:].strip()}{Style.RESET_ALL}")
            else:
                if changes and not changes[-1].strip():
                    changes[-1] = changes[-1].strip()

        if latest_tag_line and changes:
            print(Fore.LIGHTMAGENTA_EX + "\n🔖 Тег: " + Style.RESET_ALL + latest_tag_line)
            for line in changes:
                print(line)
        else:
            print(Fore.RED + "🚫 Нет информации о последних изменениях." + Style.RESET_ALL)


class InfoCommand:
    @staticmethod
    def register(registry):
        registry.register_command(ScriptInfoCommand(), "info")

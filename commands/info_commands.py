import os
from .command_registry import Command
from utils import print_colored, get_version

class ScriptInfoCommand(Command):
    def __init__(self):
        super().__init__(["-i", "info"], "Информация о скрипте")

    def execute(self, *args):
        version = get_version()
        border_char = "═"
        width = 65

        def center_text(text, fill_char=" "):
            return text.center(width, fill_char)

        print(print_colored("bright_blue", border_char * width))
        print(print_colored("bright_blue", center_text("QQ Script Information", border_char)))
        print(print_colored("bright_blue", border_char * width))
        print(f"{print_colored('bright_white', 'Repository:'):>15} {print_colored('bright_green', 'https://github.com/ArturUshakov/qq')}")
        print(f"{print_colored('bright_white', 'Creator:'):>15} {print_colored('bright_green', 'https://t.me/Mariores')}")
        print(f"{print_colored('bright_white', 'Version:'):>15} {print_colored('bright_yellow', version)}")
        print(print_colored("bright_red", "\nLatest Changes:"))
        TagInfo().get_latest_tag_info()
        print(print_colored("bright_blue", border_char * width + "\n"))

class TagInfo:
    def get_latest_tag_info(self):
        changelog_file = os.path.expanduser("~/qq/CHANGELOG.md")
        if not os.path.isfile(changelog_file):
            print(print_colored("bright_red", "Файл CHANGELOG.md не найден."))
            return

        with open(changelog_file, "r") as f:
            lines = f.readlines()

        latest_tag_line = None
        latest_tag_index = None
        for i, line in enumerate(lines):
            if line.startswith("## ["):
                latest_tag_line = line
                latest_tag_index = i
                break

        if not latest_tag_line:
            print(print_colored("bright_red", "Тэги не найдены в файле CHANGELOG.md."))
            return

        output = []
        for line in lines[latest_tag_index:]:
            if line.startswith("## [") and output:
                break
            output.append(line.strip())

        for line in output:
            self.process_tag_line(line)

    def process_tag_line(self, line):
        if line.startswith("## ["):
            parts = line.split(" - ")
            if len(parts) == 2:
                tag, date = parts
                print(f"{print_colored('bright_green', tag)} {print_colored('bright_yellow', date)}")
        elif line.startswith("- "):
            print(f"  {print_colored('bright_cyan', '•')} {print_colored('bright_blue', line[2:])}")
        elif line.startswith("  - "):
            print(f"    {print_colored('bright_cyan', '›')} {print_colored('bright_blue', line[4:])}")
        else:
            print(line)

class InfoCommand:
    @staticmethod
    def register(registry):
        registry.register_command(ScriptInfoCommand(), "info")

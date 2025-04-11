# commands/command_registry.py
class Command:
    def __init__(self, names, description):
        if isinstance(names, str):
            self.names = [names]
        elif isinstance(names, list):
            self.names = names
        else:
            raise ValueError("Имена должны быть строкой или списком строк")
        self.description = description

    def execute(self, *args):
        raise NotImplementedError("Подклассы должны реализовать этот метод")


class CommandRegistry:
    def __init__(self):
        self.commands = {}
        self.groups = {
            "container": "Команды контейнеров",
            "system": "Системные команды",
            "cleanup": "Очистка",
        }
        self.command_groups = {
            "base": {},
            "container": {},
            "system": {},
            "cleanup": {},
        }

    def register_command(self, command, group="base"):
        for name in command.names:
            self.commands[name] = command
        self.command_groups[group][command.names[0]] = command

    def get_command(self, name):
        return self.commands.get(name)

    def get_group_commands(self, group):
        return self.command_groups.get(group, {})

    def register_all_commands(self):
        from .base import BaseCommand
        from .container import ContainerCommand
        from .system import SystemCommand
        from .cleanup import CleanupCommand

        BaseCommand.register(self)
        ContainerCommand.register(self)
        SystemCommand.register(self)
        CleanupCommand.register(self)

    def print_help(self):
        help_command = self.get_command("-h")
        if help_command:
            help_command.execute()

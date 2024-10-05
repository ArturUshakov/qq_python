# commands/command_registry.py
class Command:
    def __init__(self, names, description):
        if isinstance(names, str):
            self.names = [names]
        elif isinstance(names, list):
            self.names = names
        else:
            raise ValueError("names must be a string or a list of strings")
        self.description = description

    def execute(self, *args):
        raise NotImplementedError("Subclasses should implement this method")


class CommandRegistry:
    def __init__(self):
        self.commands = {}
        self.groups = {
            "container": "Команды контейнеров",
            "system": "Системные команды",
            "cleanup": "Очистка",
            "git": "GIT",
            "info": "Информационные команды"
        }
        self.command_groups = {
            "base": {},
            "container": {},
            "system": {},
            "cleanup": {},
            "info": {},
            "git": {},
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
        from .base_commands import BaseCommand
        from .container_commands import ContainerCommand
        from .system_commands import SystemCommand
        from .info_commands import InfoCommand
        from .cleanup_commands import CleanupCommand
        from .git import GitCommand

        BaseCommand.register(self)
        ContainerCommand.register(self)
        SystemCommand.register(self)
        InfoCommand.register(self)
        CleanupCommand.register(self)
        GitCommand.register(self)

    def print_help(self):
        help_command = self.get_command("-h")
        if help_command:
            help_command.execute()

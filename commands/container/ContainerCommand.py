from colorama import Fore, Style
import subprocess
import asyncio
import time
import re
from ..command_registry import Command
from .StopAllContainersCommand import StopAllContainersCommand
from .ListRunningContainersCommand import ListRunningContainersCommand
from .ExecInContainerCommand import ExecInContainerCommand

class ContainerCommand:
    @staticmethod
    def register(registry):
        registry.register_command(StopAllContainersCommand(), "container")
        registry.register_command(ListRunningContainersCommand(), "container")
        registry.register_command(ExecInContainerCommand(), "container")

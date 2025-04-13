import logging
import os
import traceback
from logging.handlers import RotatingFileHandler
from colorama import Fore, Style

log_file = os.path.expanduser("~/.qq/app.log")
log_dir = os.path.dirname(log_file)

os.makedirs(log_dir, exist_ok=True)

handler = RotatingFileHandler(log_file, mode='a', maxBytes=0, backupCount=0)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logging.basicConfig(handlers=[handler], level=logging.DEBUG)

def log_exception(e):
    logging.error("Произошла ошибка: %s", e)
    logging.error("Traceback: %s", traceback.format_exc())

def safe_execute(command, *args):
    try:
        logging.debug(f"Выполнение команды: {command} с аргументами {args}")
        command.execute(*args)
    except Exception as e:
        print(Fore.LIGHTRED_EX + f"⚠️ Ошибка: {e}" + Style.RESET_ALL)
        log_exception(e)

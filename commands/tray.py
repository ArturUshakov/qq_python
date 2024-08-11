import sys
import os
import subprocess
import logging
import fcntl
import socket
from PyQt5 import QtWidgets, QtGui, QtCore

logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("qq_app.log")]
)
logger = logging.getLogger(__name__)

AUTOSTART_FILE = os.path.expanduser("~/.config/autostart/qq.desktop")
ICON_PATH = os.path.expanduser("~/qq/icon.png")
LOCK_FILE = '/tmp/qq_tray.lock'
SOCKET_FILE = '/tmp/qq_tray.sock'

def send_close_signal():
    """Отправка сигнала на завершение существующего экземпляра."""
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(SOCKET_FILE)
            client_socket.sendall(b'close')
    except socket.error as e:
        logger.error(f"Не удалось отправить сигнал завершения: {e}")

def check_single_instance():
    if os.path.exists(SOCKET_FILE):
        send_close_signal()

    global lock_file
    lock_file = open(LOCK_FILE, 'w')

    try:
        fcntl.lockf(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        logger.error("Не удалось установить блокировку. Завершаем работу.")
        sys.exit(0)

def cleanup():
    try:
        if lock_file:
            lock_file.close()
        if os.path.exists(SOCKET_FILE):
            os.remove(SOCKET_FILE)
    except Exception as e:
        logger.error(f"Ошибка при очистке ресурсов: {e}")

def create_autostart_file():
    try:
        exec_path = os.path.expanduser("~/qq/qq")
        content = f"""
[Desktop Entry]
Type=Application
Exec={exec_path} tray
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=QQ app
Comment=Автоматический запуск qq
"""
        os.makedirs(os.path.dirname(AUTOSTART_FILE), exist_ok=True)
        with open(AUTOSTART_FILE, 'w') as f:
            f.write(content)
    except Exception as e:
        logger.error(f"Ошибка при создании файла автозапуска: {e}")
        raise

def remove_autostart_file():
    try:
        if os.path.exists(AUTOSTART_FILE):
            os.remove(AUTOSTART_FILE)
    except Exception as e:
        logger.error(f"Ошибка при удалении файла автозапуска: {e}")
        raise

class CommandRunner(QtCore.QThread):
    finished = QtCore.pyqtSignal(str, str)

    def __init__(self, args, success_message):
        super().__init__()
        self.args = args
        self.success_message = success_message

    def run(self):
        exec_path = os.path.expanduser("~/qq/qq")
        process = subprocess.Popen([exec_path] + self.args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        error_message = stderr.decode('utf-8') if stderr else None
        if process.returncode == 0:
            self.finished.emit(self.success_message, None)
        else:
            self.finished.emit(None, error_message)

class SettingsDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Настройки")
        self.setFixedSize(300, 100)

        layout = QtWidgets.QVBoxLayout()

        self.autostart_checkbox = QtWidgets.QCheckBox("Запускать qq при старте системы")
        self.autostart_checkbox.setChecked(os.path.exists(AUTOSTART_FILE))
        layout.addWidget(self.autostart_checkbox)

        save_button = QtWidgets.QPushButton("Сохранить")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def save_settings(self):
        try:
            if self.autostart_checkbox.isChecked():
                create_autostart_file()
            else:
                remove_autostart_file()
        except Exception as e:
            logger.error(f"Ошибка при сохранении настроек: {e}")
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить настройки: {e}")
        finally:
            self.close()

class SystemTrayApp(QtWidgets.QSystemTrayIcon):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.setIcon(QtGui.QIcon(ICON_PATH))
        self.setToolTip("QQ app")

        menu = QtWidgets.QMenu(parent)

        down_action = menu.addAction("Остановить контейнеры")
        down_action.triggered.connect(lambda: self.run_command(['-d'], "Остановка контейнеров завершена."))

        prune_action = menu.addAction("Запуск docker-prune")
        prune_action.triggered.connect(lambda: self.run_command(['-pb'], "Docker-prune завершён."))

        cleanup_action = menu.addAction("Удаление none images")
        cleanup_action.triggered.connect(lambda: self.run_command(['-dni'], "Удаление none images завершено."))

        settings_action = menu.addAction("Настройки")
        settings_action.triggered.connect(self.open_settings_dialog)

        menu.addSeparator()
        exit_action = menu.addAction("Выход")
        exit_action.triggered.connect(self.exit_app)

        self.setContextMenu(menu)
        self.show()

        self.server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            self.server_socket.bind(SOCKET_FILE)
            self.server_socket.listen(1)
            self.socket_thread = QtCore.QThread()
            self.socket_thread.run = self.listen_for_close_signal
            self.socket_thread.start()
        except socket.error as e:
            logger.error(f"Ошибка при создании серверного сокета: {e}")
            self.exit_app()

    def listen_for_close_signal(self):
        while True:
            connection, _ = self.server_socket.accept()
            with connection:
                data = connection.recv(1024)
                if data == b'close':
                    self.exit_app()

    def run_command(self, args, success_message):
        self.runner = CommandRunner(args, success_message)
        self.runner.finished.connect(self.on_command_finished)
        self.runner.start()

    def on_command_finished(self, success_message, error_message):
        if success_message:
            self.showMessage("Успех", success_message, QtWidgets.QSystemTrayIcon.Information)
        elif error_message:
            self.showMessage("Ошибка", error_message, QtWidgets.QSystemTrayIcon.Critical)

    def open_settings_dialog(self):
        dialog = SettingsDialog()
        dialog.exec_()

    def exit_app(self):
        QtWidgets.QApplication.quit()
        cleanup()

def start_tray_app():
    check_single_instance()

    if os.fork() > 0:
        sys.exit(0)

    os.setsid()
    if os.fork() > 0:
        sys.exit(0)

    sys.stdout.flush()
    sys.stderr.flush()

    with open('/dev/null', 'wb', 0) as devnull:
        os.dup2(devnull.fileno(), sys.stdin.fileno())
        os.dup2(devnull.fileno(), sys.stdout.fileno())
        os.dup2(devnull.fileno(), sys.stderr.fileno())

    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    tray_icon = SystemTrayApp(app)
    app.exec_()

if __name__ == "__main__":
    try:
        start_tray_app()
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
        cleanup()
        sys.exit(1)

# qq — Python CLI-компиляция в бинарники (Linux & macOS)

## Описание

Этот проект компилирует Python CLI-приложение (`cli.py`) в нативные бинарные файлы `qq` для Linux и macOS с помощью [Nuitka](https://nuitka.net/).

### 🚀 Возможности:
- Поддержка Linux (для ubuntu 20.04 и выше) и macOS (universal ARM64)

### 🛠 Требования:
- Python 3.8
- Nuitka, gcc/clang, build tools (автоматически устанавливаются через GitHub Actions)

### 🧪 Сборка вручную:

- Все зависимости описаны в Dockerfile

```bash
# Linux
sudo apt install python3 python3-pip gcc g++ clang patchelf zlib1g-dev
pip install nuitka
python3 -m nuitka cli.py --onefile --output-filename=qq

# macOS
brew install llvm zlib
pip install nuitka
python3 -m nuitka cli.py --onefile --output-filename=qq

Либо через докер для ubuntu 20.04 и выше использовать make all
```

### 📥 Скачать:

Актуальные бинарники доступны на [странице релизов](https://github.com/ArturUshakov/qq_python/releases).

---

## Overview

This project compiles a Python CLI tool (`cli.py`) into standalone native binaries `qq` for Linux and macOS using [Nuitka](https://nuitka.net/).

### 🚀 Features:
- Supports Linux (for Ubuntu 20.04 and above) and macOS (universal ARM64)

### 🛠 Requirements:
- Python 3.8
- Nuitka, gcc/clang, build tools (installed via GitHub Actions)

### 🧪 Manual build:

- All dependencies are registered in Dockerfile

```bash
# Linux
sudo apt install python3 python3-pip gcc g++ clang patchelf zlib1g-dev
pip install nuitka
python3 -m nuitka cli.py --onefile --output-filename=qq

# macOS
brew install llvm zlib
pip install nuitka
python3 -m nuitka cli.py --onefile --output-filename=qq

Or through the dock for Ubuntu 20.04 and above use Make All
```

### 📦 Release:

Binaries are built and uploaded automatically on push to the `master` branch.

### 📥 Download:

Visit the [releases page](https://github.com/ArturUshakov/qq_python/releases) to download the latest builds.


# qq — Python CLI Binaries for Linux & macOS

## ✨ Overview

**qq** is a Python-based CLI tool compiled into native binaries for **Linux** and **macOS** using [Nuitka](https://nuitka.net/).  
It provides fast, portable execution without needing to install Python or dependencies.

## 🚀 Features

- ✅ Cross-platform: runs on Ubuntu 20.04+ and macOS (ARM64 supported)
- ⚡ Compiled with Nuitka for native performance
- 🧠 Bash/Zsh autocomplete support
- 📁 Single binary distribution (`qq-linux`, `qq-macos`)
- 🛠 Easy to install via script

## 🔧 Requirements (for manual build)

- Python 3.8
- Nuitka
- Build tools: `gcc`, `clang`, `zlib`, etc.

## 🧪 Manual Build Instructions

You can manually build the `qq` binary using Nuitka:

### Linux

```bash
sudo apt install python3 python3-pip gcc g++ clang patchelf zlib1g-dev
pip install nuitka
python3 -m nuitka cli.py --onefile --output-filename=qq
```

### macOS

```bash
brew install llvm zlib
pip install nuitka
python3 -m nuitka cli.py --onefile --output-filename=qq
```

Or, if using Docker on Ubuntu 20.04+, run:

```bash
make all
```

## 📆 Automated Releases

Each push to the `master` branch triggers a GitHub Action that builds and publishes `qq` binaries for:

- `qq-linux`
- `qq-macos`

## 📅 Download & Install

1. Visit the [latest release](https://github.com/ArturUshakov/qq_python/releases)
2. Download the appropriate binary for your system:
    - `qq-linux` for Ubuntu/Linux
    - `qq-macos` for macOS
3. Download `qq-setup.sh` and `qq_completions.sh` from the release as well

### 🧰 Install:

In the folder with the downloaded files:

```bash
chmod +x install-linux.sh
./install-linux.sh
```

The script will:

- Copy the correct binary to `~/.qq/`
- Enable autocomplete
- Add the `qq` alias to your shell config
- Create a global `/usr/local/bin/qq` entry

Restart your terminal or run:

```bash
source ~/.bashrc   # or ~/.zshrc on zsh
```

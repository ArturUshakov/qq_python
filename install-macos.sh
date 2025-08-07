#!/bin/bash

set -e

QQ_INSTALL_DIR="$HOME/.qq"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
ZIP_PATH="$SCRIPT_DIR/qq-macos.zip"
TMP_DIR="$(mktemp -d)"

ZSH_COMPLETION_SRC="$TMP_DIR/qq_completions.zsh"
BASH_COMPLETION_SRC="$TMP_DIR/qq_completions.sh"
COMPLETION_SCRIPT_PATH="$QQ_INSTALL_DIR/qq_completions.sh"

if [[ ! -f "$ZIP_PATH" ]]; then
  echo "❌ Архив qq-macos.zip не найден в $SCRIPT_DIR"
  exit 1
fi

echo "📦 Распаковка архива..."
unzip -q "$ZIP_PATH" -d "$TMP_DIR"

if [[ ! -f "$TMP_DIR/qq-macos/cli" ]]; then
  echo "❌ Не найден cli-бинарь после распаковки"
  exit 1
fi

echo "📁 Установка в $QQ_INSTALL_DIR"
mkdir -p "$QQ_INSTALL_DIR"
rm -rf "$QQ_INSTALL_DIR/qq-macos"
cp -R "$TMP_DIR/qq-macos" "$QQ_INSTALL_DIR/"

BIN_WRAPPER="/usr/local/bin/qq"
echo "🛠 Создание запускаемого скрипта: $BIN_WRAPPER"
echo -e "#!/bin/bash\n\"$QQ_INSTALL_DIR/qq-macos/cli\" \"\$@\"" | sudo tee "$BIN_WRAPPER" > /dev/null
sudo chmod +x "$BIN_WRAPPER"

add_to_shell_config() {
  local shell_config="$1"
  local completion_line="$2"

  if [[ -f "$shell_config" ]]; then
    grep -q 'alias qq=' "$shell_config" || echo "alias qq=\"$QQ_INSTALL_DIR/qq-macos/cli\"" >> "$shell_config"
    grep -q "$completion_line" "$shell_config" || echo "source \"$completion_line\"" >> "$shell_config"
  fi
}

if [[ "$SHELL" == *zsh ]]; then
  if [[ -f "$ZSH_COMPLETION_SRC" ]]; then
    cp "$ZSH_COMPLETION_SRC" "$QQ_INSTALL_DIR/qq_completions.zsh"
    COMPLETION_SCRIPT_PATH="$QQ_INSTALL_DIR/qq_completions.zsh"
  fi
  add_to_shell_config "$HOME/.zshrc" "$COMPLETION_SCRIPT_PATH"
else
  if [[ -f "$BASH_COMPLETION_SRC" ]]; then
    cp "$BASH_COMPLETION_SRC" "$COMPLETION_SCRIPT_PATH"
  fi
  add_to_shell_config "$HOME/.bash_profile" "$COMPLETION_SCRIPT_PATH"
fi

echo "✅ Установка завершена!"
echo "🔁 Перезапусти терминал или выполни: source ~/.zshrc или source ~/.bash_profile"
echo "🚀 Теперь можешь запускать: qq"
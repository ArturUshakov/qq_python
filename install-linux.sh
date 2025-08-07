#!/bin/bash

set -e

QQ_INSTALL_DIR="$HOME/.qq"
COMPLETION_SCRIPT_PATH="$QQ_INSTALL_DIR/qq_completions.sh"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

QQ_BINARY_SOURCE="$SCRIPT_DIR/qq"

if [[ ! -f "$QQ_BINARY_SOURCE" ]]; then
  echo "❌ Бинарный файл 'qq' не найден в $SCRIPT_DIR"
  exit 1
fi

echo "📁 Установка в $QQ_INSTALL_DIR"
mkdir -p "$QQ_INSTALL_DIR"
cp "$QQ_BINARY_SOURCE" "$QQ_INSTALL_DIR/qq"
chmod +x "$QQ_INSTALL_DIR/qq"

if [[ -f "$SCRIPT_DIR/qq_completions.sh" ]]; then
  cp "$SCRIPT_DIR/qq_completions.sh" "$COMPLETION_SCRIPT_PATH"
fi

BIN_WRAPPER="/usr/local/bin/qq"
echo "🛠 Создание запускаемого скрипта: $BIN_WRAPPER"
echo -e "#!/bin/bash\n\"$QQ_INSTALL_DIR/qq\" \"\$@\"" | sudo tee "$BIN_WRAPPER" > /dev/null
sudo chmod +x "$BIN_WRAPPER"

add_to_shell_config() {
  local shell_config="$1"

  grep -q 'alias qq=' "$shell_config" 2>/dev/null || echo "alias qq=\"$QQ_INSTALL_DIR/qq\"" >> "$shell_config"
  grep -q "$COMPLETION_SCRIPT_PATH" "$shell_config" 2>/dev/null || echo "source \"$COMPLETION_SCRIPT_PATH\"" >> "$shell_config"
}

if [[ "$SHELL" == *zsh ]]; then
  add_to_shell_config "$HOME/.zshrc"
else
  add_to_shell_config "$HOME/.bashrc"
fi

echo "✅ Установка завершена!"
echo "🔁 Перезапусти терминал или выполни: source ~/.bashrc или source ~/.zshrc"
echo "🚀 Теперь можешь запускать: qq"
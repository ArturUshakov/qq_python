#!/bin/bash

QQ_INSTALL_DIR="$HOME/.qq"
COMPLETION_SCRIPT_PATH="$QQ_INSTALL_DIR/qq_completions.sh"

mkdir -p "$QQ_INSTALL_DIR"

OS_NAME="$(uname -s | tr '[:upper:]' '[:lower:]')"
case "$OS_NAME" in
  linux*) QQ_BINARY_NAME="qq-linux";;
  darwin*) QQ_BINARY_NAME="qq-macos";;
  *) echo "❌ Unsupported OS: $OS_NAME"; exit 1;;
esac

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
QQ_BINARY_SOURCE="$SCRIPT_DIR/$QQ_BINARY_NAME"

if [[ ! -f "$QQ_BINARY_SOURCE" ]]; then
  echo "❌ Required binary '$QQ_BINARY_NAME' not found in $SCRIPT_DIR."
  exit 1
fi

cp "$QQ_BINARY_SOURCE" "$QQ_INSTALL_DIR/qq"
chmod +x "$QQ_INSTALL_DIR/qq"

cp "$SCRIPT_DIR/qq_completions.sh" "$COMPLETION_SCRIPT_PATH"

QQ_SCRIPT_PATH="/usr/local/bin/qq"
echo -e "#!/bin/bash\n\"$QQ_INSTALL_DIR/qq\" \"$@\"" | sudo tee "$QQ_SCRIPT_PATH" > /dev/null
sudo chmod +x "$QQ_SCRIPT_PATH"

add_to_shell_config() {
  local shell_config="$1"

  if ! grep -q "alias qq=" "$shell_config" 2>/dev/null; then
    echo "alias qq=\"$QQ_INSTALL_DIR/qq\"" >> "$shell_config"
  fi

  if ! grep -q "$COMPLETION_SCRIPT_PATH" "$shell_config" 2>/dev/null; then
    echo "source \"$COMPLETION_SCRIPT_PATH\"" >> "$shell_config"
  fi
}

if [[ "$SHELL" == *zsh ]]; then
  add_to_shell_config "$HOME/.zshrc"
elif [[ "$OSTYPE" == "darwin"* ]]; then
  add_to_shell_config "$HOME/.bash_profile"
else
  add_to_shell_config "$HOME/.bashrc"
fi

echo "✅ Installation complete. Restart your terminal or run 'source ~/.bashrc' or 'source ~/.zshrc' to activate."
echo "🔧 Binary installed at: $QQ_INSTALL_DIR/qq"

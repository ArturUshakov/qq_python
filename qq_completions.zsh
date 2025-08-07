#compdef qq

_qq_completions() {
  local -a commands
  commands=(${(f)"$(qq 2>/dev/null | grep -Eo '^\s+-[a-z0-9]+(, [a-z0-9\-]+)?' | tr -d ',' | tr -s ' ')"})
  _describe 'command' commands
}

compdef _qq_completions qq
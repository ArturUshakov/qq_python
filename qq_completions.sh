#!/bin/bash

_qq_completions() {
    local cur prev commands
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD - 1]}"

    commands="-d -l -e -la -li -ri -gph -eip -ch -dni -pb -clr -clc -gi -i down list exec list-all list-images remove-image generate-password-hash external-ip update upgrade cleanup-docker-images prune-builder clear clear-last-commit info"

    COMPREPLY=($(compgen -W "${commands}" -- "${cur}"))
}

complete -F _qq_completions "python3 $HOME/qq/qq"

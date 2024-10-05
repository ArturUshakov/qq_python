#!/bin/bash

_qq_completions() {
    local cur prev commands
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD - 1]}"

    commands="-h -i -d -l -la -li -eip -ri -ch -gph -gi -dni -pb info down list list-all list-images external-ip remove-image chmod-all generate-password-hash upgrade update -c clear -clc clear-last-commit -pmb git-prune-merged"

    COMPREPLY=($(compgen -W "${commands}" -- "${cur}"))
}

complete -F _qq_completions "python3 $HOME/qq/qq.bin"

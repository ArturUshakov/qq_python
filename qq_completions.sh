#!/bin/bash

_qq_completions() {
    local cur prev commands
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD - 1]}"

    if type qq &>/dev/null; then
        commands=$(qq 2>/dev/null | grep -Eo '^\s+-[a-z0-9]+(, [a-z0-9\-]+)?' | tr -d ',' | tr -s ' ')
    else
        commands=""
    fi

    COMPREPLY=($(compgen -W "${commands}" -- "${cur}"))
}

complete -F _qq_completions qq


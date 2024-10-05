#!/bin/bash

docker build -t nuitka_project .

docker run --rm -v /home/artur/qq_test:/app/output -it nuitka_project /bin/bash -c "
    python3.8 -m nuitka --onefile --follow-imports --output-dir=output --output-filename=qq main.py
"

if [ -f /home/artur/qq_test/qq ]; then
    echo '✔ Файл успешно скомпилирован и сохранен в /home/artur/qq_test/qq'
else
    echo '✘ Ошибка: файл не был скомпилирован'
fi
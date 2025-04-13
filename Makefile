MAKEFLAGS += --no-print-directory --silent

PROJECT_NAME := nuitka_project
OUTPUT_DIR ?= $(CURDIR)/output
PYTHON ?= python3.10

.PHONY: help build up compile clean all

help:  ## Показать список доступных команд
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

build:  ## Собрать Docker-образ
	docker compose build

up:  ## Запустить контейнер в интерактивном режиме
	docker compose run --rm qq

compile: build ## Скомпилировать приложение через Nuitka
	docker compose run --rm qq \
		bash -c "export CC='gcc' && $(PYTHON) -m nuitka cli.py --onefile --output-dir=/app/output --output-filename=qq"

clean:  ## Удалить собранные файлы
	rm -rf $(OUTPUT_DIR)/qq

all: compile  ## Полная сборка

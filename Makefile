MAKEFLAGS += --no-print-directory --silent
PROJECT_NAME := nuitka_project
OUTPUT_DIR := /home/artur/qq_test
DOCKER_IMAGE := $(PROJECT_NAME)
CONTAINER_NAME := qq_nuitka_temp

.PHONY: build run compile extract clean all

build:
	docker build -t $(DOCKER_IMAGE) .

run:
	docker run --rm -v $(OUTPUT_DIR):/app/output -it $(DOCKER_IMAGE) /bin/bash

compile:
	docker rm -f $(CONTAINER_NAME) 2>/dev/null || true
	docker run --name $(CONTAINER_NAME) -v $(OUTPUT_DIR):/app/output -w /app $(DOCKER_IMAGE) \
		python3.8 -m nuitka cli.py --onefile --follow-imports --output-dir=output --output-filename=qq

extract:
	docker cp $(CONTAINER_NAME):/app/output/qq ./qq_test/qq
	docker rm $(CONTAINER_NAME)

clean:
	rm -rf ./qq_test/qq

all: build compile extract

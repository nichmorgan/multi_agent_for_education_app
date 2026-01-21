.PHONY: install migrate migrations run huey shell fmt

# Default workers for huey
workers ?= 1

PY = uv run python

install:
	uv sync

migrate:
	$(PY) manage.py migrate

migrations:
	$(PY) manage.py makemigrations

run:
	$(PY) manage.py runserver

huey:
	$(PY) manage.py djangohuey --workers $(workers)

shell:
	$(PY) manage.py shell

fmt:
	$(PY) -m isort .
	$(PY) -m black .

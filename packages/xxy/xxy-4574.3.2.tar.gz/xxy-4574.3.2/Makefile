.PHONY: help build format web host

ALL_PY := xxy
help:
	@LC_ALL=C $(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/(^|\n)# Files(\n|$$)/,/(^|\n)# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

build: format web
	-rm -rf dist out
	uv run stubgen $(ALL_PY)
	python3 -m build

format:
	uvx isort --profile black $(ALL_PY)
	uvx black $(ALL_PY)
	uv run mypy --strict $(ALL_PY)

test:
	uv run -m unittest discover

web:
	cp web.env.local web/.env.local
	cd web && npm run build
	rm -rf xxy/chatbot
	cp -r web/out xxy/chatbot

host:
	uv run uvicorn xxy.web:app --reload --port 5000
.PHONY: help build format web py clean host

ALL_PY := xxy

build: format web py clean

help:
	@LC_ALL=C $(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/(^|\n)# Files(\n|$$)/,/(^|\n)# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

clean:
	rm -rf dist out
	rm -rf xxy/chatbot

py:
	# uv run stubgen $(ALL_PY)
	uv build

format:
	uvx isort --profile black $(ALL_PY)
	uvx black $(ALL_PY)
	uv run mypy --strict $(ALL_PY)

test:
	uv run -m unittest discover

web/node_modules:
	cd web && npm install

web: web/node_modules
	cp web.env.local web/.env.local
	cp favicon.ico web/app/favicon.ico
	cd web && npm run build
	cp -r web/out xxy/chatbot

host:
	uv run uvicorn xxy.web:app --reload --port 5000
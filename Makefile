
QUARTO ?= $(if $(wildcard .tools/bin/quarto),.tools/bin/quarto,quarto)
PYTHON ?= python3
PORT ?= 8765

.PHONY: html rebuild preview serve check check-browser

html:
	$(QUARTO) render --to html

rebuild:
	$(QUARTO) render --to html --execute --cache-refresh

preview:
	$(QUARTO) preview --to html --host 127.0.0.1 --port $(PORT) --no-browser

serve:
	$(PYTHON) tools/serve.py --port $(PORT)

check:
	$(PYTHON) tools/check_site.py docs

check-browser:
	node tools/check_browser.cjs


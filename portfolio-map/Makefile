PY ?= python3

.PHONY: all check clean deps

all:            ## regenerate every view from model.yaml
	$(PY) render.py

check:          ## validate model.yaml without writing anything
	$(PY) render.py --check

deps:
	$(PY) -m pip install -r requirements.txt

clean:
	rm -rf out

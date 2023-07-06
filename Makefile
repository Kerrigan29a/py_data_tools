PY = $$(which python3 || which python)
URL = "https://github.com/kerrigan29a/py_data_tools/blob/main/{path}\#L{line}"

.PHONY: all clean distclean test

all: test README.md

clean:
	rm -f README.md data_tools.json

distclean: clean
	rm -f -r tools
	rm -rf __pycache__ .mypy_cache

test: data_tools.py
	$(PY) $^

README.md: data_tools.py tools/py2doc.py tools/doc2md.py
	$(PY) tools/py2doc.py $< | $(PY) tools/doc2md.py -u $(URL) -o README.md

tools/py2doc.py: tools
	curl https://raw.githubusercontent.com/Kerrigan29a/microdoc/main/py2doc.py -o $@

tools/doc2md.py: tools
	curl https://raw.githubusercontent.com/Kerrigan29a/microdoc/main/doc2md.py -o $@

tools:
	mkdir -p $@

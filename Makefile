PY = $$(which python3 || which python)
URL = "https://github.com/kerrigan29a/py_data_tools/blob/main/{path}\#L{line}"

.PHONY: all clean distclean test

all: test README.md

clean:
	rm -f README.md data_tools.json

distclean: clean
	rm -f doctest_utils.py
	rm -r -f tools
	rm -r -f __pycache__ .mypy_cache

test: data_tools.py doctest_utils.py
	$(PY) $<

README.md: data_tools.py tools/py2doc.py tools/doc2md.py
	$(PY) tools/py2doc.py $< | $(PY) tools/doc2md.py -u $(URL) -o README.md

doctest_utils.py:
	echo "# -*- coding: utf-8 -*-" > $@
	echo "" >> $@
	echo "################################################################################" >> $@
	echo "# DO NOT EDIT!!!" >> $@
	echo "# This file was downloaded from:" >> $@
	echo "# https://raw.githubusercontent.com/Kerrigan29a/microdoc/main/doctest_utils.py" >> $@
	echo "# and the Makefile will remove any change. " >> $@
	echo "###" >> $@
	echo "" >> $@
	curl https://raw.githubusercontent.com/Kerrigan29a/microdoc/main/doctest_utils.py >> $@

tools/py2doc.py: tools
	echo "# -*- coding: utf-8 -*-" > $@
	echo "" >> $@
	echo "################################################################################" >> $@
	echo "# DO NOT EDIT!!!" >> $@
	echo "# This file was downloaded from:" >> $@
	echo "# https://raw.githubusercontent.com/Kerrigan29a/microdoc/main/doctest_utils.py" >> $@
	echo "# and the Makefile will remove any change. " >> $@
	echo "###" >> $@
	echo "" >> $@
	curl https://raw.githubusercontent.com/Kerrigan29a/microdoc/main/py2doc.py >> $@

tools/doc2md.py: tools
	echo "# -*- coding: utf-8 -*-" > $@
	echo "" >> $@
	echo "################################################################################" >> $@
	echo "# DO NOT EDIT!!!" >> $@
	echo "# This file was downloaded from:" >> $@
	echo "# https://raw.githubusercontent.com/Kerrigan29a/microdoc/main/doctest_utils.py" >> $@
	echo "# and the Makefile will remove any change. " >> $@
	echo "###" >> $@
	echo "" >> $@
	curl https://raw.githubusercontent.com/Kerrigan29a/microdoc/main/doc2md.py >> $@

tools:
	mkdir -p $@

.PHONY: upload-release
upload-release:
	python setup.py release register sdist upload

PYREVERSE_OPTS = --output=pdf
.PHONY: view
view:
	-rm -Rf _pyreverse
	mkdir _pyreverse
	PYTHONPATH=src pyreverse ${PYREVERSE_OPTS} --project="pydevDAG" src/pydevDAG
	mv classes_pydevDAG.pdf _pyreverse
	mv packages_pydevDAG.pdf _pyreverse

.PHONY: archive
archive:
	git archive --output=./pydevDAG.tar.gz HEAD

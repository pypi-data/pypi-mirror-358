SPHINXOPTS    ?=
SOURCEDIR     = .
BUILDDIR      = _build
VENV_DIR      = .venv
PYTHON        = $(VENV_DIR)/bin/python3
SPHINXPROJ    = ORCA Python Interface tutorials
SPHINXBUILD   = $(PYTHON) -m sphinx
SPHINXAUTO    = $(PYTHON) -m sphinx_autobuild

clean_api:
	rm -rf "$(SOURCEDIR)/contents/api"
	rm -rf $(SOURCEDIR)/contents/scripts/*.sha256

clean:
	rm -rf "$(BUILDDIR)/html"

distclean: clean clean_api
	rm -rf "$(BUILDDIR)"
	rm -rf $(VENV_DIR)/

$(VENV_DIR)/bin/uv:
	@if [ ! -d "$(VENV_DIR)/bin/activate" ]; then \
		python3 -m venv $(VENV_DIR); \
		$(PYTHON) -m pip install --upgrade pip; \
	fi
	@if [ ! -f "$(VENV_DIR)/bin/uv" ]; then \
		$(PYTHON) -m pip install --upgrade uv; \
	fi

sphinx: $(VENV_DIR)/bin/uv
	$(PYTHON) -m uv sync --active --group docs --no-editable --locked --no-python-downloads

auto: sphinx
	@$(SPHINXAUTO) --re-ignore $(BUILDDIR) $(SOURCEDIR) $(BUILDDIR)/html

html: sphinx
	$(SPHINXBUILD) . $(BUILDDIR)/html

# > Phony targets
.PHONY: auto clean clean_generated distclean html sphinx

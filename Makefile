# =============================================================================
# sphinx-needs-template — top-level Makefile
#
# This file orchestrates the full pipeline:
#
#     LinkML data ─┐
#                  ├─► generate ─► sphinx-build (needs)  ─► pytest ─► sphinx-build (HTML/PDF)
#     LinkML schema┘                                       │
#                                                          └─► test_results.json (back into HTML)
#
# It also drives the secondary outputs (ReqIF export, JSON-LD export) and the
# multi-view HTML/PDF builds (six views).
# =============================================================================

# -----------------------------------------------------------------------------
# Paths and tools
# -----------------------------------------------------------------------------
SOURCE_DIR     := docs/public
BUILD_DIR      := docs/public/_build
GEN_DIR        := docs/public/_generated
SPHINX         := sphinx-build
SPHINX_OPTS    := --keep-going

LINKML_SCHEMA  := linkml/public/schema/needs.yaml
LINKML_DATA    := linkml/public/data
REQS_GEN_DIR   := docs/public/reqs_gen

VIEWS          := complete overview detail party_prep back_yard schema schedule
HTML_TARGETS   := $(addprefix html-,$(VIEWS))
PDF_TARGETS    := $(addprefix pdf-,$(VIEWS))

# -----------------------------------------------------------------------------
# Phony targets
# -----------------------------------------------------------------------------
.PHONY: help all generate validate needs test html pdf clean install \
        reqif-export jsonld-export $(HTML_TARGETS) $(PDF_TARGETS)

# -----------------------------------------------------------------------------
# Defaults
# -----------------------------------------------------------------------------
all: generate needs test html

help:
	@echo "Targets"
	@echo "  install         install Python dependencies (editable)"
	@echo ""
	@echo "  generate        regenerate reqs_gen/*.md from LinkML data + schema"
	@echo "  validate        validate LinkML data files against the schema"
	@echo ""
	@echo "  needs           build needs.json (used by pytest)"
	@echo "  test            run pytest with @satisfies validation + coverage"
	@echo ""
	@echo "  html            build all $(words $(VIEWS)) HTML views"
	@echo "  pdf             build all $(words $(VIEWS)) PDF views"
	@echo "  html-<view>     build a single HTML view"
	@echo "  pdf-<view>      build a single PDF view"
	@echo ""
	@echo "  reqif-export    export needs.json as ReqIF"
	@echo "  jsonld-export   export needs.json as JSON-LD"
	@echo ""
	@echo "  all             generate + needs + test + html"
	@echo "  clean           remove build outputs"
	@echo ""
	@echo "Available views: $(VIEWS)"

# -----------------------------------------------------------------------------
# Setup
# -----------------------------------------------------------------------------
install:
	pip install -e ".[dev]"

# -----------------------------------------------------------------------------
# Generation: LinkML data + schema → MyST under reqs_gen/
# -----------------------------------------------------------------------------
generate: validate
	@echo "==> Generating reqs_gen/ from LinkML"
	needs-from-linkml $(LINKML_DATA) -s $(LINKML_SCHEMA) -o $(REQS_GEN_DIR) -q
	schema-to-needs    $(LINKML_SCHEMA) -o $(REQS_GEN_DIR)/classes.md
	@echo "==> Done"

validate:
	@echo "==> Validating LinkML data"
	@for f in $(LINKML_DATA)/*.yaml; do \
	    echo "  $$f"; \
	    linkml-validate -s $(LINKML_SCHEMA) "$$f" || exit 1; \
	done

# -----------------------------------------------------------------------------
# needs.json — required input for pytest's @satisfies validation
# -----------------------------------------------------------------------------
needs: generate
	@echo "==> Building needs.json"
	$(SPHINX) -b needs -t view_complete -q $(SOURCE_DIR) $(BUILD_DIR)/needs

# -----------------------------------------------------------------------------
# pytest with @satisfies validation + coverage check
# -----------------------------------------------------------------------------
test: needs
	@echo "==> Running pytest"
	pytest -v tests/public

# -----------------------------------------------------------------------------
# HTML — one build per view via Sphinx tags
# -----------------------------------------------------------------------------
html: generate $(HTML_TARGETS)

$(HTML_TARGETS): html-%:
	@echo "==> HTML view: $*"
	$(SPHINX) -b html -t view_$* $(SPHINX_OPTS) $(SOURCE_DIR) $(BUILD_DIR)/html-$*
	@# Redirect index.html → the active view's master_doc for one-click viewing.
	@python3 docker/write_redirect.py $* $(BUILD_DIR)/html-$*

# -----------------------------------------------------------------------------
# PDF — sphinx-build → latex → latexmk
# -----------------------------------------------------------------------------
pdf: generate $(PDF_TARGETS)

$(PDF_TARGETS): pdf-%:
	@echo "==> PDF view: $*"
	$(SPHINX) -b latex -t view_$* $(SPHINX_OPTS) $(SOURCE_DIR) $(BUILD_DIR)/latex-$*
	$(MAKE) -C $(BUILD_DIR)/latex-$* LATEXMKOPTS="-xelatex -interaction=nonstopmode" all-pdf
	mkdir -p $(BUILD_DIR)/pdf-$*
	@# Copy only the report PDF; the latex/ directory may also contain
	@# image-conversion intermediates (e.g. garden_layout.pdf from rsvg-convert)
	@# which should not be exposed as deliverables.
	cp $(BUILD_DIR)/latex-$*/sphinx-needs-template-$*.pdf $(BUILD_DIR)/pdf-$*/

# -----------------------------------------------------------------------------
# Secondary outputs
# -----------------------------------------------------------------------------
reqif-export: needs
	@echo "==> Exporting needs.json → ReqIF"
	mkdir -p $(GEN_DIR)
	reqif-bridge export $(BUILD_DIR)/needs/needs.json -o $(GEN_DIR)/garden.reqif

jsonld-export: needs
	@echo "==> Exporting needs.json → JSON-LD"
	mkdir -p $(GEN_DIR)
	needs-to-jsonld $(BUILD_DIR)/needs/needs.json -s $(LINKML_SCHEMA) -o $(GEN_DIR)/garden.jsonld

# -----------------------------------------------------------------------------
# Clean
# -----------------------------------------------------------------------------
clean:
	rm -rf $(BUILD_DIR) $(GEN_DIR)
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache *.egg-info

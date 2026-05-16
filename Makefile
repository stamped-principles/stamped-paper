LU_MASTERS = main
FLAVORS = PDF

# https://gitlab.inria.fr/latex-utils/latex-make
# sudo apt install latex-make   on Debian systems
include /usr/include/LaTeX.mk

main.pdf: references.bib authors.tex author-contributions.tex

# Author byline and CRediT contributions are rendered from the
# .tributors{,.credit.yaml} single source of truth. Renderers are vendored
# under code/ so the build is self-contained (S in STAMPED). Upstream skill:
#   ~/.claude/skills/credit-contributions/
# Refresh vendored copies with:  make fetch-credit-renderer fetch-authors-renderer
CREDIT_RENDERER  := code/render_credit.py
AUTHORS_RENDERER := code/render_authors.py
SKILL_DIR        ?= $${HOME}/.claude/skills/credit-contributions

# --- Author byline + affiliations ------------------------------------------
authors.tex: .tributors.credit.yaml .tributors $(AUTHORS_RENDERER)
	python3 $(AUTHORS_RENDERER) .tributors.credit.yaml --tributors .tributors -o $@

# --- CRediT Author Contributions section + JATS XML ------------------------
author-contributions.tex: .tributors.credit.yaml .tributors $(CREDIT_RENDERER)
	python3 $(CREDIT_RENDERER) --format latex .tributors.credit.yaml -o $@

author-contributions.jats.xml: .tributors.credit.yaml .tributors $(CREDIT_RENDERER)
	python3 $(CREDIT_RENDERER) --format jats .tributors.credit.yaml -o $@

.PHONY: authors author-contributions author-contributions-jats credit-validate \
        fetch-credit-renderer fetch-authors-renderer
authors: authors.tex
author-contributions: author-contributions.tex
author-contributions-jats: author-contributions.jats.xml

credit-validate:
	python3 $(CREDIT_RENDERER) --validate-only .tributors.credit.yaml

# Refresh a vendored renderer from the user's installed skill.
# Compares first; only copies (and reports) when the upstream differs.
# $(1) = filename under code/ and under the skill dir.
define _fetch_renderer
	@if [ ! -f $(SKILL_DIR)/$(1) ]; then \
	  echo "ERROR: skill file not found at $(SKILL_DIR)/$(1)"; \
	  echo "Install the credit-contributions skill first."; \
	  exit 1; \
	fi
	@if cmp -s $(SKILL_DIR)/$(1) code/$(1); then \
	  echo "code/$(1) is up to date with skill."; \
	else \
	  echo "Updating code/$(1) from $(SKILL_DIR)/$(1)"; \
	  cp $(SKILL_DIR)/$(1) code/$(1); \
	  chmod +x code/$(1); \
	fi
endef

fetch-credit-renderer:
	$(call _fetch_renderer,render_credit.py)

fetch-authors-renderer:
	$(call _fetch_renderer,render_authors.py)

# Override default goal so bare "make" builds PDF then checks for problems
.DEFAULT_GOAL := default
.PHONY: default
default: pdf
	@if grep -sq -E 'There were undefined (citations|references)' main.log; then \
	  echo "ERROR: Undefined references remain after build:"; \
	  grep 'Citation.*undefined' main.log; \
	  false; \
	fi

# Mermaid diagrams — render .mmd to .svg and .pdf via mermaid-cli
MMD_SRCS := $(wildcard figures/*.mmd)
MMD_SVGS := $(MMD_SRCS:.mmd=.svg)
MMD_PDFS := $(MMD_SRCS:.mmd=.pdf)

.PHONY: diagrams
diagrams: $(MMD_SVGS) $(MMD_PDFS)

figures/%.svg: figures/%.mmd
	npx @mermaid-js/mermaid-cli -i $< -o $@ \
		$(if $(wildcard figures/$*.css),-C figures/$*.css)

figures/%.pdf: figures/%.mmd
	npx @mermaid-js/mermaid-cli -i $< -o $@ \
		$(if $(wildcard figures/$*.css),-C figures/$*.css)

# Zotero group library — public, no API key needed
ZOTERO_GROUP_ID = 6197458

references.bib:
	./code/fetch-zotero-bib.sh $(ZOTERO_GROUP_ID) $@

# REUSE specification compliance — https://reuse.software/
.PHONY: reuse-lint
reuse-lint:
	uvx --from reuse reuse lint

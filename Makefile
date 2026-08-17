LU_MASTERS = main
FLAVORS = PDF

AUTHOR_TARGETS := authors author-contributions author-contributions-jats \
                  credit-validate
CONTAINER_AUTHOR_TARGETS := $(addprefix container-,$(AUTHOR_TARGETS))
NON_LATEX_GOALS := $(AUTHOR_TARGETS) $(CONTAINER_AUTHOR_TARGETS) \
                   container-author-image container-pdf

# Author metadata targets do not need LaTeX.mk. Skipping the include lets
# their container-prefixed variants run on hosts without a LaTeX installation.
ifneq ($(strip $(MAKECMDGOALS)),)
ifeq ($(strip $(filter-out $(NON_LATEX_GOALS),$(MAKECMDGOALS))),)
SKIP_LATEX_MK := 1
endif
endif

ifndef SKIP_LATEX_MK
# https://gitlab.inria.fr/latex-utils/latex-make
# sudo apt install latex-make   on Debian systems
# Also provided by the build container (containers/build-latex.Dockerfile).
# When absent, the default target runs the same build there (container-pdf).
HAVE_LATEX_MK := $(wildcard /usr/include/LaTeX.mk)
ifneq ($(HAVE_LATEX_MK),)
include /usr/include/LaTeX.mk
endif
endif

main.pdf: references.bib authors.tex author-contributions.tex | author-contributions.jats.xml

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

# Lightweight, non-interactive Podman alternatives for the author metadata
# targets. The host needs Podman, but does not need Python, PyYAML, or LaTeX.
AUTHOR_CONTAINER_IMAGE ?= localhost/stamped-paper-author-metadata:latest
AUTHOR_CONTAINER_FILE  := containers/author-metadata.Dockerfile

.PHONY: container-author-image $(CONTAINER_AUTHOR_TARGETS)
container-author-image:
	@command -v podman >/dev/null 2>&1 || { \
	  echo "ERROR: Podman is required for container-* targets."; \
	  exit 1; \
	}
	podman build --file $(AUTHOR_CONTAINER_FILE) \
	  --tag $(AUTHOR_CONTAINER_IMAGE) containers

$(CONTAINER_AUTHOR_TARGETS): container-%: container-author-image
	podman run --rm --userns=keep-id \
	  --security-opt label=disable \
	  --env HOME=/tmp \
	  --volume "$(CURDIR):/work" \
	  --workdir /work \
	  $(AUTHOR_CONTAINER_IMAGE) $*

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

# Override default goal so bare "make" builds PDF then checks for problems.
# Without latex-make installed, delegate the build to the container instead.
.DEFAULT_GOAL := default
.PHONY: default
ifneq ($(HAVE_LATEX_MK),)
default: pdf
	@if grep -sq -E 'There were undefined (citations|references)' main.log; then \
	  echo "ERROR: Undefined references remain after build:"; \
	  grep 'Citation.*undefined' main.log; \
	  false; \
	fi
else
default: container-pdf
endif

# Containerized full PDF build: the same image CI uses (see the
# build-container workflow). Unlike the author metadata image, it is
# published to GHCR because building TeX Live locally is slow.
BUILD_CONTAINER_IMAGE ?= ghcr.io/stamped-principles/build-latex:latest

.PHONY: container-pdf
container-pdf:
	@command -v podman >/dev/null 2>&1 || { \
	  echo "ERROR: Podman is required for container-* targets."; \
	  exit 1; \
	}
	podman run --rm --userns=keep-id \
	  --security-opt label=disable \
	  --env HOME=/tmp \
	  --volume "$(CURDIR):/work" \
	  --workdir /work \
	  $(BUILD_CONTAINER_IMAGE) make

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
	npx @mermaid-js/mermaid-cli -i $< -o $@ --pdfFit \
		$(if $(wildcard figures/$*.css),-C figures/$*.css)

# Cover letter — render the submission cover letter to PDF via the
# official pandoc container (pandoc + minimal TeXLive; pinned version).
.PHONY: cover-letter
cover-letter: scidata-coverletter.pdf

scidata-coverletter.pdf: scidata-cover-letter.md
	podman run --rm -v "$$PWD:/work:z" -w /work docker.io/pandoc/latex:3.7 \
		$< -V geometry:margin=1in -V fontsize=11pt -o $@

# Zotero group library — public, no API key needed
ZOTERO_GROUP_ID = 6197458

references.bib:
	./code/fetch-zotero-bib.sh $(ZOTERO_GROUP_ID) $@

# REUSE specification compliance — https://reuse.software/
.PHONY: reuse-lint
reuse-lint:
	uvx --from reuse reuse lint

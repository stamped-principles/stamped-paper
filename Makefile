LU_MASTERS = main
FLAVORS = PDF

# https://gitlab.inria.fr/latex-utils/latex-make
# sudo apt install latex-make   on Debian systems
include /usr/include/LaTeX.mk

main.pdf: references.bib

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

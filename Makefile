LU_MASTERS = main
FLAVORS = PDF

# https://gitlab.inria.fr/latex-utils/latex-make
# sudo apt install latex-make   on Debian systems
include /usr/include/LaTeX.mk

main.pdf: references.bib

# Zotero group library — public, no API key needed
ZOTERO_GROUP_ID = 6197458

references.bib:
	./code/fetch-zotero-bib.sh $(ZOTERO_GROUP_ID) $@

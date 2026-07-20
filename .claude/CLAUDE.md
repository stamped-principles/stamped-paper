# STAMPED Paper (notes for AI agents)

A manuscript formalizing the STAMPED principles, Self-containment, Tracking, Actionability, Modularity, Portability, Ephemerality, and Distributability, for reproducible research objects.
Originating from the YODA Principles.

## Read this first

**All project conventions live in [`CONTRIBUTING.md`](../CONTRIBUTING.md).** @CONTRIBUTING.md
That file is the single source of truth for writing style, terminology, LaTeX/markup conventions, tables, the section pattern, authorship rendering, bibliography, licensing, build, version control, and commit co-authorship.
Read it in full and follow it.
This file holds only the few things specific to AI agents that do not belong in a human-facing contributing guide.
Do not duplicate convention text here; if a convention changes, change it in `CONTRIBUTING.md`.

## Agent-specific operating notes

- Read the relevant GitHub issues and PR discussion into context before acting, including inline review comments, which are easy to miss and often must be fetched explicitly; decisions are made in those threads, not only in the code.
- Changes land via pull requests only; never edit `main` in place (see `CONTRIBUTING.md` → Workflow).
- Commit co-authorship is **required** for AI-assisted commits.
  Discover your actual tool and model versions from the tool itself and do not guess them.
  Format and rationale are in `CONTRIBUTING.md` → Commit conventions.

## Venue and key reference material

- Target venue: Nature Scientific Data, Article format (not Data Descriptor).
- Format requirements: [research/SDATA-ARTICLE-REQUIREMENTS.md](../research/SDATA-ARTICLE-REQUIREMENTS.md)
- Style guide: [research/sdata-style-patterns.md](../research/sdata-style-patterns.md)
- Prior venue research (Nature Methods, no longer the target): [research/NMETH-ARTICLE-REQUIREMENTS.md](../research/NMETH-ARTICLE-REQUIREMENTS.md), [research/nmeth-style-patterns.md](../research/nmeth-style-patterns.md)

## Key files

- `main.tex` — manuscript source.
- `CONTRIBUTING.md` — all project conventions (start here).
- `.tributors`, `.tributors.credit.yaml` — single source of truth for byline and CRediT roles (rendered into `authors.tex` / `author-contributions.tex`).
- `references.bib` — generated from the Zotero group library; do not hand-edit.
- `research/` — background research, format requirements, and style guides.

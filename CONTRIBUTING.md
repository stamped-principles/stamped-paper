# Contributing to the STAMPED paper

This document is the single source of truth for how we write, build, and manage this repository.
It is written for everyone who contributes, humans and AI agents alike.
AI agents: this file is referenced from [`.claude/CLAUDE.md`](.claude/CLAUDE.md); read it in full and follow it.

This manuscript repository is itself meant to be a STAMPED research object.
The conventions below are not arbitrary house style: most of them exist to keep this repository Self-contained, Tracked, Actionable, Modular, Portable, Ephemeral, and Distributable.
Where a convention serves a STAMPED principle, we say so, so that the repository practices what the paper preaches.

## Contents

- [Workflow and collaboration](#workflow-and-collaboration)
- [Prose and writing style](#prose-and-writing-style)
- [STAMPED terminology and principle references](#stamped-terminology-and-principle-references)
- [LaTeX and manuscript conventions](#latex-and-manuscript-conventions)
- [Tables and the checklist](#tables-and-the-checklist)
- [Principle section pattern](#principle-section-pattern)
- [Authorship and contributions](#authorship-and-contributions)
- [Bibliography](#bibliography)
- [Licensing (REUSE)](#licensing-reuse)
- [Build](#build)
- [Version control and data](#version-control-and-data)
- [Commit conventions](#commit-conventions)

## Workflow and collaboration

- All editing and discussion happens on GitHub: <https://github.com/stamped-principles/stamped-paper>.
- Changes land through pull requests.
  Do not edit `main` in place.
- Use GitHub issues for discussion.
  Do not leave comments, suggestions, or edits on Overleaf; an Overleaf mirror may exist for convenience, but GitHub is authoritative.
- A PR triggers a CI build of the manuscript PDF and posts a diff preview comment.
  Check it before requesting review.
- Keep posts on GitHub (issues, PR descriptions, comments) concise: lead with the point.
  Wrap long contextual material (logs, large snippets, more than ~10 lines) in a `<details>` block with a `<summary>` label so the prose stays readable.
- If a PR is not yet ready to merge, add a TODO section at the bottom of its description; mark completed steps `- [x]` and pending steps `- [ ]`.

## Prose and writing style

These apply to the manuscript (`main.tex`) and, where sensible, to Markdown documentation in the repository.

- **One sentence per line.**
  Start each sentence on its own line and do not hard-wrap within a sentence.
  This keeps diffs sentence-scoped and reviewable.
- **American English spellings everywhere**: "behavior" not "behaviour", "serialize" not "serialise", "normalize" not "normalise", "organize" not "organise", "color" not "colour".
  This holds in prose, identifiers, comments, and commit messages.
- **No em dashes (—) or rhetorically-used en dashes (–).**
  Em-dash-heavy text reads as machine-generated.
  Replace an em dash with a comma, parentheses, a colon, a semicolon, or two sentences, whichever fits best.
  Hyphens in compound words and numeric ranges are fine.
- **Plain word choice.**
  Avoid inflated or trendy vocabulary when a plainer word is clearer.
  In particular, avoid "federated" unless it is technically precise; there is almost always a better choice.
- **Do not italicize Latin abbreviations** such as "e.g.", "i.e.", and "et al.".
- **Use "any" to disambiguate "state".**
  Prefer "any undocumented host state" over bare "state" where the scope is otherwise ambiguous.
- Keep terminology stable: see the terminology section below.

## STAMPED terminology and principle references

### Terminology

- **Principles, not properties.**
  We call the seven STAMPED items *principles*.
  A *principle* is the guidance ("make it Portable"); a *property* is the trait a research object exhibits ("it is Portable").
  Refer to "STAMPED principles" rather than "STAMPED properties".
  Untangling the two senses in specific sentences is an ongoing refinement (see issue #178).
- **Term hierarchy: Research Object > Module > Component.**
  - A **research object** is a collection of data, code, and metadata that together represent the research as a complete unit.
  - A **module** is a separately Distributable unit of a research object (a subdataset, a collection of scripts, an environment definition).
  - A **component** is a trackable element that is part of a module (a file, a script, a config).
- **Workflow** is defined externally by WCI-FW and cited, not redefined by us.
- **Provenance** is the recorded history of how components were produced or modified.
- **Tool-agnostic framing.**
  STAMPED does not depend on any particular tool.
  Avoid phrases like "STAMPED-compliant tools"; prefer "tools complementary to STAMPED".
  In tool tables and examples, treat tools as illustrative, not prescriptive.
- Avoid the phrase "research object's results"; refer to the research object or its components directly.

### How to write a principle reference

When referring to one of the seven principles in running prose, write the **capitalized name followed by its letter in parentheses**.
In LaTeX, join the two with a non-breaking space (`~`) so the name and its letter never split across a line break: `Tracking~(T)`, `Distributability~(D)`.

Exceptions (from the standardization in PR #158, tracked by issue #147):

- **Introduction**: do not use the parenthetical-letter form, to avoid distracting before the principles are introduced.
- **Within a principle's own section**: do not repeat the parenthetical letter, and leave the principle lowercase, so repeated in-section usage reads naturally.
- **Literature review / convergent-evolution**: apply the form only to *our* usage of the principles, not to usages quoted or paraphrased from other sources.
- **Non-principle senses**: a word like "distributed" used in its ordinary sense (not the Distributability principle) stays plain.

### RFC 2119 keywords

Normative requirements use the graded keywords of RFC 2119: **MUST**, **SHOULD**, **MAY**.
MUST marks the practical minimum; SHOULD and MAY mark progressively more aspirational practice.
Each principle is framed as a **spectrum** from a practical minimum (often what researchers already do) to an aspirational ideal.

## LaTeX and manuscript conventions

- **URLs go through the helper macros, not `\url`.**
  Use `\httpsurl{example.org/path}` for a general link and `\ghurl{org/repo}` for a GitHub link (both defined at the top of `main.tex`).
  These render via `\href`, drop the visual `https://` prefix, and remove the chance of swapping `\href`'s two arguments.
- **Anchored sections for stable deep links.**
  Use `\anchoredsection{anchor}{Title}`, `\anchoredsubsection{anchor}{Title}`, and `\anchoredsubsubsection{anchor}{Title}` instead of the plain `\section`/`\subsection`/`\subsubsection`.
  These attach a named PDF destination so a heading can be linked as `paper.stamped-principles.org/main.pdf#anchor`, which stays valid when sections are reordered (hyperref's default counter-based names do not).
  This is what makes the rendered manuscript Actionable and Distributable as a citable, deep-linkable artifact (resolves issue #124).
  Do not place a bare `\hypertarget` before or inside a heading; it lands at the wrong vertical position.
- **Code formatting: literal code only.**
  Wrap literal commands, CLI tool names, filenames, and code tokens in `\texttt{}` (for example `\texttt{git clone}`, `\texttt{datalad run}`, `\texttt{pyproject.toml}`).
  Leave proper software/product names in plain text when referring to the project rather than its command (for example git-annex, Docker, Node, Conda).
  In Markdown, the same rule maps to `code` spans.
- **No trailing periods in list items.**
  Bullets already separate items, and the next item starts lowercase, so a trailing period reads oddly.
- **Auto-generated date.**
  The title date uses `\monthyeardate\today`; never hardcode a month or year.
- **Hyperlink colors are intentional**: citations `darkblue`, internal links `darkgreen`, URLs `darkblue` (close to black so print stays legible).
  Do not change these per-link.
- **Title constraints (Nature Scientific Data).**
  Maximum 110 characters, no colons or parentheses, capitalize only the first word and proper nouns.

## Tables and the checklist

The manuscript carries three coordinated reference artifacts; keep their roles distinct.

- **Table 1 (principle definitions).**
  General, declarative definitions of each principle: the shorthand reference before the detailed sections.
- **Table 2 (normative properties).**
  Statements about a workflow that satisfies each principle, framed FAIR-table style, offering an evaluation-oriented re-framing rather than a restated definition.
- **Checklist (Figure 2 / the interactive checklist).**
  The collected imperative requirements from the individual sections, ordered by strength of requirement (MUST, SHOULD, MAY), as firm suggestions users apply to their own workflows.
  The checklist is backed by a versioned LinkML schema and served at <https://checklist.stamped-principles.org>.

Sharpening the distinct roles of these three is an active discussion (issues #176, #70); keep new edits consistent with the separation above.

## Principle section pattern

Nature Scientific Data Articles allow flexible structure (IMRaD recommended, not mandated).
Each STAMPED principle subsection follows this pattern:

1. **Motivation**: why the principle matters and what goes wrong without it.
2. **Definition**: reference the formal RFC 2119 requirements, then a brief prose restatement of the core idea.
3. **Spectrum** (minimum → ideal): practical floor to aspirational ceiling; foreshadow later principles rather than detailing them.
4. **Cross-references**: how this principle interacts with the others, briefly.

## Authorship and contributions

The byline and the Author Contributions section are **generated from a single source of truth**; do not hand-edit the rendered files.

- Edit `.tributors` (identity cache, con/tributors convention; ORCIDs sourced from <https://centerforopenneuroscience.org/whoweare>) and `.tributors.credit.yaml` (byline order, per-author CRediT roles from the 14 NISO Z39.104-2022 terms, affiliation links).
- Regenerate with `make authors` and `make author-contributions` (and `make author-contributions-jats`).
- `authors.tex`, `author-contributions.tex`, and `author-contributions.jats.xml` are build products: never edit them directly.
- The renderers `code/render_authors.py` and `code/render_credit.py` are vendored from the upstream `credit-contributions` skill so the build is Self-contained; refresh them with `make fetch-authors-renderer` / `make fetch-credit-renderer`.

## Bibliography

The bibliography is curated in the Center for Open Neuroscience public Zotero group library (group ID 6197458): <https://www.zotero.org/groups/6197458/centerforopenneuroscience/library>.

- `references.bib` is **generated** by `code/fetch-zotero-bib.sh`; add or fix references in the Zotero library, then regenerate, rather than hand-editing `references.bib`.
- `make` fails the build on undefined citations or references, so resolve those before opening a PR.

## Licensing (REUSE)

The project follows the [REUSE specification](https://reuse.software/) so copyright and licensing are machine-readable; this serves Distributability (each module carries a resolvable license).

- Manuscript text, bibliography, figures, and human-readable documentation are **CC-BY-4.0**.
- Code, tooling, and CI configuration are **Apache-2.0**.
- Vendored third-party helpers keep their own SPDX header (for example the MIT-licensed credit renderers).
- Every tracked file needs SPDX metadata.
  When you add a file, add an inline SPDX header where the format allows, or extend the matching `path` block in [`REUSE.toml`](REUSE.toml).
- Verify locally with `make reuse-lint` (or `uvx --from reuse reuse lint`).

## Build

- `make` (default) builds `main.pdf` and then fails if any citations or references are undefined.
- `make reuse-lint` checks licensing compliance.
- `make diagrams` renders Mermaid sources (`figures/*.mmd`) to SVG and PDF via `mermaid-cli`.
- `references.bib` is fetched from Zotero (see Bibliography).
- The PDF build, REUSE lint, and diff preview also run in CI on every PR.
  CI runs in disposable runners, exercising the repository's own Ephemerality and Portability.

## Version control and data

- The repository is a DataLad dataset with git-annex available for large or binary content.
  `.gitattributes` is configured so that `datalad save` / `git annex add` route binary content to the annex (content-addressed, MD5E backend); text and `.git*` files stay in Git.
- A plain `git add` bypasses that rule and commits a file directly to Git regardless of type, so use `datalad save` when adding large binaries you want annexed.
- Do not commit build artifacts; they are listed in `.gitignore` (for example `main.pdf`, `main.aux`, `main.log`).
- `local-notes/` is gitignored scratch space for non-committed notes.

## Commit conventions

When an AI tool (agent, coding assistant, IDE integration) materially contributes to a commit, the commit MUST include a `Co-Authored-By` trailer identifying both the **tool and its version** and the **model and its version**, so the git history is an inspectable provenance record (this is Tracking, applied to the manuscript's own authorship).

Format:

```
Co-Authored-By: <Tool> <tool-version> / <Model> <model-version> <noreply@<vendor-domain>>
```

Discover the tool and model versions from the tool itself; do not guess.
(Convention adopted from <https://github.com/con/catenate> `conboarding.md` § Commit Co-Authorship.)

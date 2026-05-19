# STAMPED Paper

A manuscript formalizing the STAMPED properties — Self-contained, Tracked, Actionable, Modular, Portable, Ephemeral, and Distributable — for reproducible research objects. Originating from the YODA Principles.

## Venue & Format

Target: Nature Scientific Data Article (not Data Descriptor).
- Format requirements: [research/SDATA-ARTICLE-REQUIREMENTS.md](research/SDATA-ARTICLE-REQUIREMENTS.md)
- Style guide: [research/sdata-style-patterns.md](research/sdata-style-patterns.md)
- Prior venue research (Nature Methods, no longer target): [research/NMETH-ARTICLE-REQUIREMENTS.md](research/NMETH-ARTICLE-REQUIREMENTS.md), [research/nmeth-style-patterns.md](research/nmeth-style-patterns.md)

## Project Style Conventions
- one sentence per line

## Key Files

- `main.tex` — manuscript source
- `proposals/stamped-acronym.md` — the STAMPED proposal (term definitions, acronym, normative properties, RFC 2119 rules)
- `REFERENCES-TODO.md` — references to incorporate
- `research/` — background research, format requirements, and style guide
- `local-notes/` is gitignored and available for non-committed scratch notes
- AI agents should load local-notes/CLAUDE.md into context immediately if available

## Term Hierarchy

- **Research Object** > **Module** > **Component**
- A research object is composed of modules (separately distributable collections of components)
- A component is a trackable element that is part of a module
- **Workflow**: defined by WCI-FW, cited not self-defined
- **Provenance**: recorded history of how components were produced or modified

## Key Decisions

- P = Portable (not Provenance). Provenance folds into Tracked (T).
- Actionability (A) is cross-cutting — applies to every other dimension
- Hierarchy: S = foundation, A = cross-cutting, T/M/P = core pillars, E/D = ideals
- STAMPED is tool-agnostic — avoid "STAMPED-compliant tools", prefer "tools complementary to STAMPED"
- Each property is a spectrum from practical minimums to aspirational ideals

## Section Pattern for Results

Scientific Data Articles allow flexible structure (IMRaD recommended, not mandated).
The current Results subsection pattern remains appropriate:
1. **Motivation**: Why this property matters. What goes wrong without it.
2. **Definition**: Reference the formal requirements in Table 1 using an imperative style using RFC 2119 specification. Brief prose restating the core idea.
3. **Spectrum** (minimum → ideal): Practical floor → aspirational ceiling. Foreshadow later properties rather than detail them.
4. **Cross-references**: How this property interacts with others (brief).


## Framing of Distinct Tables

- Table 1: General definitions of each principle. This is the shorthand reference prior to delving into deeper details in each section.
- Table 2: Descriptions of normative properties about a workflow that satisfies each principle. This offers a re-framed perspective on how to evaluate a workflow against the principle, rather than just defining the principle itself. This follows the style of the primary FAIR table.
- Table/Checklist 3: Collection of all imperative requirements from the individual sections, ordered by importance. This provides firm suggestions for users to apply to their own workflows.


## Writing Conventions

- Principles use RFC 2119 keywords (MUST, SHOULD, MAY)
- Refer to other properties by name with letter: e.g., "Tracking (T)", "Distributability (D)"
- Keep tool examples tool-agnostic in definitions, tool-specific in spectrum examples

## Workflow

- All editing and comments take place on GitHub https://github.com/stamped-principles/stamped-paper
- Changes occur via pull requests — do not edit in place
- Avoid comments on Overleaf; use GitHub issues instead

## Commit co-authorship

Every commit you author MUST include a `Co-Authored-By` trailer identifying both your tool name + version and your underlying model + version. Format:

```
Co-Authored-By: <Tool> <tool-version> / <Model> <model-version> <noreply@<vendor-domain>>
```

Use the actual versions reported by your tool. Don't guess.

(Convention adopted from https://github.com/con/catenate `conboarding.md` § Commit Co-Authorship.)

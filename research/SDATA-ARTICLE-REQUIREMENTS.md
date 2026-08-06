# Nature Scientific Data — Article Requirements

Source: https://www.nature.com/sdata/submission-guidelines and https://www.nature.com/sdata/aims-and-scope
Last verified against the live submission-guidelines page: 2026-08-06.

## Article Type: Article (not Data Descriptor)

Scientific Data publishes two article types:

1. **Data Descriptor** — describes new, open research datasets for reuse (the primary format)
2. **Article** — covers data policy, repositories, standards, ontologies, workflows, or any topic relating to the mechanics of data sharing. May also present commentaries or opinions on research data policy, workflows, or infrastructure. (Absorbed the former "Comment" type.)

**Scope**: Scientific Data does *not* publish traditional research articles using data to validate scientific hypotheses. Articles must relate to data sharing mechanics, infrastructure, or policy.

STAMPED fits the Article type: it formalizes properties for reproducible research objects — squarely about data management standards and workflows.

## Structure

Required sections for Articles:

1. **Title**
2. **Author list** (no heading needed)
3. **Abstract**
4. **Main sections** — IMRaD (Introduction, Methods, Results, Discussion) recommended but **not mandated**; more speculative or non-study works may use a different structure
5. **Data Availability**
6. **Code Availability**
7. **References**
8. **Author Contributions** (SNAPP-captured, see below)
9. **Competing Interests** (SNAPP-captured, see below)
10. **Acknowledgements** (optional; SNAPP-captured, see below)
11. **Funding**
12. **Ethics statement** (where relevant)

Compare to Data Descriptors which require rigid sections: Background & Summary, Methods, Data Records, Technical Validation, Usage Notes.

**SNAPP-captured statements**: for submissions via the current system (SNAPP), the Acknowledgements, Author Contributions, and Competing Interests statements are entered on the submission system, and the journal asks that they *not* appear in the manuscript file ("may be overwritten or excluded if the system information differs").
The **Funding** statement is the exception: it must appear as a sub-heading in the paper itself (system-side funding info is internal-only and not published).
Papers declaring no competing interests on SNAPP need no statement at all; the journal adds one during typesetting.

**Data Availability for Articles**: the statement should link any non-code outputs or platforms the paper describes, with a URL, a data-citation reference number, and a concrete description of what is shared (best practice: name specific files and folder structure).
If nothing is shared, say so explicitly ("No data is shared as part of this article").

**Introduction guidance for Articles**: explain why the work was performed and what value it adds, but "do not include subjective claims on novelty, impact, or utility".

## Limits

- **Main text**: No word limit. The journal is online-only and not printed.
- **Abstract**: 170 words — phrased as a recommendation ("We recommend the Abstract should not exceed 170 words"), not a hard cap; applies to both article types. Unstructured (no sub-headings), unreferenced. Should not make claims regarding new scientific findings. No URLs for data access.
- **Title**: Maximum 110 characters including spaces. No colons or parentheses. Capitalize only first word and proper nouns. Should avoid acronyms and abbreviations (except common ones like DNA), and explicitly: "Do not include dataset brand names in titles, self-constructed acronyms, or words used out of context for the scientific topic, as no user will be searching for them." Only real, technically descriptive words, aligned with how users search. No advertising claims ("novel"/"first"/"AI-ready"/"open"). Note: FAIR (2016) and TRUST (2020) were published in this journal with their self-constructed acronyms in the title, and coined acronyms still appear in current Data Descriptor titles, so enforcement is uneven.
- **Figures**: Recommended no more than 8 (not a hard limit).
- **Figure legends**: No more than 350 words total.
- **Tables**: Recommended no more than 10. Tables exceeding one A4 page go to Supplementary.
- **References**: No explicit limit.
- **Supplementary**: Should not extend paper by more than ~10 pages; journal discourages supplementary material and prefers content in main manuscript.

## LaTeX

- **No official template** — the journal explicitly discourages templates: "We do not provide, suggest or recommend the use of a LaTeX template so if you find a previous or legacy version of this via platforms such as Overleaf please do not use them."
- Use standard article class; Nature applies their own style at publication.
- For initial submission: a single PDF with embedded figures is sufficient.
- For revised manuscripts: a single standalone .TEX file required, compilable without .bib files, style sheets, or other dependencies.
- References MUST be embedded in the .TEX file (no separate .bib/.bbl).
- Recommended font: Computer Modern.
- Use graphicx.sty for figures.
- Do not use internal hyperlinks to sections, headers, figures, or tables (\cref or similar) — refer in free text ("see Fig. 1"); all internal linking is redone at typesetting. (Our `\anchoredsection` machinery falls under this for the revision-stage .tex.)
- The Springer Nature template (`sn-jnl` with `sn-nature` option) exists on Overleaf but is discouraged by the journal.

### Revised-manuscript uploads (round two)

- One machine-readable main article file (.docx or .tex only, no PDF); do not compile and upload your own PDF — the system generates it from the .tex.
- The .tex must be verified standalone: compile it with no read access to other files; the usual failure is a missing reference list from a .bib/.bbl dependency.
- Every figure as a separate file, one file per figure, panels merged into a single image with a/b/c labels embedded (typesetters will not arrange panels).
- A "Response to Reviewers" file (PDF) answering ALL reviewer and editor comments — uploaded under that category, not as a covering letter.
- Optionally a changes-highlighted PDF.
- Revision window: one month, flexible on request.

## References Format

- Standard Nature referencing style is *suggested*, not required: "Exact reference formats are not important as long as these contain all the key information (a name, a title, a journal, and - most importantly - a DOI)."
- DOIs are the priority field — append as `https://doi.org/<DOI>` to any reference that has one.
- Numbered sequentially, superscript in text. One publication per reference number.
- Only published/accepted papers or recognized preprints; preprints of accepted papers should be submitted with the manuscript.
- No grant details, acknowledgements, or other footnotes as numbered references.
- Titles required for cited articles.

Example:
> Schott, D. H., Collins, R. N. & Bretscher, A. Secretory vesicle transport velocity in living cells depends on the myosin V lever arm length. J. Cell Biol. 156, 35–39 (2002).

For 6+ authors: first author et al.

### Data Citations

Datasets must be cited in the reference list:
> Author(s). Title. Repository https://doi.org/XXXXX (Year).

## Figures

- Arabic numbering, in order of occurrence.
- Clear, sans-serif typeface (e.g., Helvetica).
- White background.
- Multi-panel: lowercase bold a, b, c labels.
- Scale bars preferred over magnification factors.
- SI units with single space between number and unit.
- Error bars with statistical treatment in legend.

## Cover Letter

- Uploading a covering letter file is a technical requirement of the submission system, but "there is no requirement to include any specific content and covering letters are not used to make editorial decisions" — even a blank file satisfies it.
- Statements about importance or why the work should be published "will not be checked or considered".
- Legitimate content: suggested reviewers or Editorial Board Members (optional — "neither are mandated"), non-preferred reviewers, and disclosure of live collaborations not discoverable from public records.
- Do NOT put data-access notes or instructions in the letter — reviewers never see it; access details must be in the article file.
- Prior publications are disclosed via a submission-system question, not the letter. Collection targeting, APC waiver requests, and author-detail notes likewise belong on the system, not in the letter.

## Peer Review

Process stages (each with an email notification):

1. Staff initial quality check — file availability, data/code availability, scope. Out-of-scope papers rejected here; everything else proceeds.
2. Editorial Board Member assignment — members are contacted until one accepts; can take several attempts.
3. Reviewer invitations — explicitly "the longest period of peer review"; invitations continue until the minimum two reviewers accept.
4. Review — reviewers typically get 10 days, extendable.
5. Decision — the Editorial Board Member recommends Accept, Revise, or Reject; communicated with data-policy check results.

- **Not assessed on perceived significance, importance, or impact** — all in-scope manuscripts meeting technical requirements are sent for review.
- The journal aims for a two-round process: round one surfaces issues, round two verifies they were addressed. Rejection at round two is rare but possible.
- Manuscripts are not subject to in-depth copy editing; authors responsible for language quality.

## Open Access

- Fully open access, online only.
- APC: ~$2,690 / GBP 2,150 / EUR 2,390 (waivers available for low-income countries).
- CC BY or CC BY-NC-ND license.

## Journal Info

- ISSN: 2052-4463 (online)
- Abbreviation: Sci. Data

#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Yaroslav Halchenko <yaroslav.o.halchenko@dartmouth.edu>
# SPDX-License-Identifier: MIT
#
# Generated with Claude Code 2.1.143 / Claude Opus 4.7
#
# Vendored from the credit-contributions skill:
#   ~/.claude/skills/credit-contributions/render_credit.py
# Vendored so the stamped-paper build is self-contained (S in STAMPED).
# To refresh from upstream:  make fetch-credit-renderer
# License is kept as MIT (matches upstream) so refresh is a clean copy.

"""Render CRediT contributor-role statements from a YAML overlay.

Reads `.tributors.credit.yaml` (CRediT roles + byline order) and, when
present, merges identity fields from a sibling `.tributors` JSON cache
(con/tributors convention). Emits one of:

  --format latex      LaTeX prose, initials- or fullname-style (default)
  --format markdown   Markdown prose
  --format jats       JATS V1.2 <contrib-group> per jats4r.niso.org
  --format text       Plain text prose
  --format matrix-md  Markdown contribution matrix (authors x 14 roles)
  --format matrix-tex LaTeX contribution matrix (authors x 14 roles)

`.tributors.credit.yaml` is the single source of truth. The same file
feeds all four output formats; never hand-edit the LaTeX / JATS that
this script emits.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape as xml_escape

try:
    import yaml
except ImportError:
    sys.stderr.write(
        "error: PyYAML is required. Install with: pip install pyyaml\n"
    )
    sys.exit(2)


# Canonical 14 CRediT roles, ordered as on credit.niso.org.
CREDIT_ROLES: list[tuple[str, str]] = [
    ("Conceptualization", "conceptualization"),
    ("Data curation", "data-curation"),
    ("Formal analysis", "formal-analysis"),
    ("Funding acquisition", "funding-acquisition"),
    ("Investigation", "investigation"),
    ("Methodology", "methodology"),
    ("Project administration", "project-administration"),
    ("Resources", "resources"),
    ("Software", "software"),
    ("Supervision", "supervision"),
    ("Validation", "validation"),
    ("Visualization", "visualization"),
    ("Writing – original draft", "writing-original-draft"),
    ("Writing – review & editing", "writing-review-editing"),
]
CANONICAL_NAMES = [r[0] for r in CREDIT_ROLES]
URI_BASE = "https://credit.niso.org/contributor-roles/"
VOCAB_IDENT = "https://credit.niso.org/"


def normalize_role(name: str) -> str:
    """Return canonical role name; raise ValueError on no match."""
    # Replace ASCII hyphens, em-dashes, etc. around "Writing" with en-dash
    # and " and " with " & "; collapse whitespace; case-fold for compare.
    norm = unicodedata.normalize("NFC", name).strip()
    norm = norm.replace("—", "–").replace("--", "–")
    norm = re.sub(r"\s*[-–]\s*", " – ", norm)
    norm = re.sub(r"\s+and\s+", " & ", norm, flags=re.IGNORECASE)
    norm = re.sub(r"\s+", " ", norm).strip()
    for canonical in CANONICAL_NAMES:
        if canonical.casefold() == norm.casefold():
            return canonical
    # Try a looser ASCII-only match
    ascii_input = norm.replace("–", "-").replace("&", "and").casefold()
    for canonical in CANONICAL_NAMES:
        ascii_canon = canonical.replace("–", "-").replace("&", "and").casefold()
        if ascii_canon == ascii_input:
            return canonical
    raise ValueError(
        f"unknown CRediT role: {name!r}. "
        f"Must be one of: {', '.join(CANONICAL_NAMES)}"
    )


def role_uri(canonical_name: str) -> str:
    for name, suffix in CREDIT_ROLES:
        if name == canonical_name:
            return f"{URI_BASE}{suffix}/"
    raise KeyError(canonical_name)


@dataclass
class Role:
    name: str  # canonical
    degree: str | None = None  # 'lead' | 'equal' | 'supporting' | None


@dataclass
class Contributor:
    handle: str
    name: str
    initials: str
    orcid: str | None = None
    affiliation: str | None = None
    roles: list[Role] = field(default_factory=list)


def derive_initials(full_name: str) -> str:
    """'Yaroslav O. Halchenko' -> 'Y.O.H.'  'Cody C. Baker' -> 'C.C.B.'"""
    tokens = [t for t in re.split(r"\s+", full_name.strip()) if t]
    if not tokens:
        return ""
    initials = []
    for t in tokens:
        # Strip trailing periods, take first letter (handle 'O.' -> 'O')
        t = t.strip(".")
        if t:
            initials.append(t[0].upper())
    return ".".join(initials) + "."


def load_tributors(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    with path.open() as fh:
        return json.load(fh)


def load_credit(path: Path) -> dict[str, Any]:
    with path.open() as fh:
        return yaml.safe_load(fh) or {}


def build_contributors(
    credit: dict[str, Any], tributors: dict[str, dict[str, Any]]
) -> list[Contributor]:
    """Resolve byline + per-contributor roles into Contributor objects."""
    byline: list[str] = list(credit.get("byline") or [])
    contribs_raw: dict[str, Any] = credit.get("contributors") or {}

    if not byline:
        # Fall back to insertion order of contributors map
        byline = list(contribs_raw.keys())

    out: list[Contributor] = []
    for handle in byline:
        entry = contribs_raw.get(handle, {}) or {}
        identity = tributors.get(handle, {})
        name = entry.get("name") or identity.get("name") or handle
        initials = entry.get("initials") or derive_initials(name)
        orcid = entry.get("orcid") or identity.get("orcid")
        affiliation = entry.get("affiliation") or identity.get("affiliation")

        roles_raw = entry.get("roles") or []
        roles: list[Role] = []
        for r in roles_raw:
            if isinstance(r, str):
                roles.append(Role(name=normalize_role(r)))
            elif isinstance(r, dict):
                rn = r.get("role") or r.get("name")
                if not rn:
                    raise ValueError(
                        f"contributor {handle!r} has role entry missing 'role': {r!r}"
                    )
                roles.append(Role(name=normalize_role(rn), degree=r.get("degree")))
            else:
                raise ValueError(
                    f"contributor {handle!r} has unsupported role entry: {r!r}"
                )
        out.append(
            Contributor(
                handle=handle,
                name=name,
                initials=initials,
                orcid=orcid,
                affiliation=affiliation,
                roles=roles,
            )
        )
    return out


# ---------------------------------------------------------------------------
# Renderers
# ---------------------------------------------------------------------------


def _apply_dash(text: str, mode: str) -> str:
    return text.replace("–", "-") if mode == "hyphen" else text


def _join_oxford(items: list[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + ", and " + items[-1]


def _label(c: Contributor, mode: str) -> str:
    return c.initials if mode == "initials" else c.name


def _role_with_degree(role: Role) -> str:
    if role.degree:
        return f"{role.name} ({role.degree})"
    return role.name


def render_prose(
    contribs: list[Contributor],
    style: dict[str, Any],
    output: str,  # 'latex' | 'markdown' | 'text'
) -> str:
    authors_as = style.get("authors_as", "initials")
    group_by = style.get("group_by", "byauthor")
    dash_mode = style.get("dash", "endash")

    def fmt(text: str) -> str:
        text = _apply_dash(text, dash_mode)
        if output == "latex":
            text = text.replace("&", r"\&")
            # En-dash stays as Unicode '–'; most LaTeX setups handle it.
            # If you need ASCII-only LaTeX, render with dash=hyphen.
        return text

    sentences: list[str] = []
    if group_by == "byauthor":
        for c in contribs:
            if not c.roles:
                continue
            label = _label(c, authors_as)
            role_strs = [fmt(_role_with_degree(r)) for r in c.roles]
            sentences.append(f"{label}: {_join_oxford(role_strs)}.")
    elif group_by == "byrole":
        per_role: dict[str, list[tuple[str, str | None]]] = {}
        for c in contribs:
            label = _label(c, authors_as)
            for r in c.roles:
                per_role.setdefault(r.name, []).append((label, r.degree))
        for role_name, _ in CREDIT_ROLES:
            assigned = per_role.get(role_name)
            if not assigned:
                continue
            parts = [
                f"{lbl}{f' ({deg})' if deg else ''}" for lbl, deg in assigned
            ]
            sentences.append(f"{fmt(role_name)}: {_join_oxford(parts)}.")
    else:
        raise ValueError(f"unknown style.group_by: {group_by!r}")

    return " ".join(sentences)


def render_latex_section(
    contribs: list[Contributor], style: dict[str, Any]
) -> str:
    prose = render_prose(contribs, style, "latex")
    return f"% AUTO-GENERATED from .tributors.credit.yaml by render_credit.py — do not hand-edit.\n{prose}\n"


def render_markdown_section(
    contribs: list[Contributor], style: dict[str, Any]
) -> str:
    prose = render_prose(contribs, style, "markdown")
    return f"<!-- AUTO-GENERATED from .tributors.credit.yaml by render_credit.py — do not hand-edit. -->\n{prose}\n"


def render_jats(contribs: list[Contributor]) -> str:
    """Emit a JATS V1.2 <contrib-group> per jats4r.niso.org/credit-taxonomy/."""
    lines: list[str] = []
    lines.append("<!-- AUTO-GENERATED from .tributors.credit.yaml by render_credit.py -->")
    lines.append("<contrib-group>")
    for c in contribs:
        lines.append("  <contrib contrib-type=\"author\">")
        # Decompose name into given/surname when possible.
        parts = c.name.rsplit(" ", 1)
        given, surname = (parts[0], parts[1]) if len(parts) == 2 else ("", c.name)
        lines.append("    <string-name>")
        if given:
            lines.append(f"      <given-names>{xml_escape(given)}</given-names>")
        lines.append(f"      <surname>{xml_escape(surname)}</surname>")
        lines.append("    </string-name>")
        if c.orcid:
            orcid_url = c.orcid if c.orcid.startswith("http") else f"https://orcid.org/{c.orcid}"
            lines.append(
                f"    <contrib-id contrib-id-type=\"orcid\">{xml_escape(orcid_url)}</contrib-id>"
            )
        for r in c.roles:
            attrs = (
                'vocab="credit" '
                f'vocab-identifier="{VOCAB_IDENT}" '
                f'vocab-term="{xml_escape(r.name)}" '
                f'vocab-term-identifier="{role_uri(r.name)}"'
            )
            if r.degree:
                attrs += f' specific-use="{xml_escape(r.degree)}"'
            lines.append(f"    <role {attrs}>{xml_escape(r.name)}</role>")
        lines.append("  </contrib>")
    lines.append("</contrib-group>")
    return "\n".join(lines) + "\n"


def render_matrix(contribs: list[Contributor], fmt: str) -> str:
    """Render an authors × 14-roles checkmark matrix."""
    headers = [name for name, _ in CREDIT_ROLES]
    rows: list[list[str]] = []
    for c in contribs:
        assigned = {r.name: (r.degree or "x") for r in c.roles}
        row = [c.initials or c.name]
        for h in headers:
            row.append(assigned.get(h, ""))
        rows.append(row)

    if fmt == "matrix-md":
        head = "| Author | " + " | ".join(headers) + " |"
        sep = "|" + "|".join(["---"] * (len(headers) + 1)) + "|"
        body = "\n".join("| " + " | ".join(r) + " |" for r in rows)
        return f"{head}\n{sep}\n{body}\n"
    # LaTeX matrix (compact, tabularx-friendly)
    cols = "l" + "c" * len(headers)
    lines = [f"\\begin{{tabular}}{{{cols}}}", "\\hline"]
    lines.append(" & ".join(["Author"] + [h.replace("&", r"\&") for h in headers]) + " \\\\")
    lines.append("\\hline")
    for r in rows:
        cells = [r[0]] + [
            ("$\\checkmark$" if v == "x" else (v if v else "")) for v in r[1:]
        ]
        lines.append(" & ".join(cells) + " \\\\")
    lines.append("\\hline")
    lines.append("\\end{tabular}")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="render_credit.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "credit_yaml",
        nargs="?",
        default=".tributors.credit.yaml",
        help="Path to the CRediT overlay YAML (default: .tributors.credit.yaml)",
    )
    p.add_argument(
        "--tributors",
        default=".tributors",
        help="Path to sibling .tributors JSON (default: .tributors). "
        "Ignored when absent.",
    )
    p.add_argument(
        "--format",
        choices=["latex", "markdown", "jats", "text", "matrix-md", "matrix-tex"],
        default="latex",
    )
    p.add_argument("-o", "--output", help="Write to file instead of stdout")
    p.add_argument(
        "--validate-only",
        action="store_true",
        help="Parse and validate; emit nothing. Exit non-zero on error.",
    )
    args = p.parse_args(argv)

    credit_path = Path(args.credit_yaml)
    if not credit_path.exists():
        sys.stderr.write(f"error: {credit_path} not found\n")
        return 2
    tributors_path = Path(args.tributors)

    try:
        credit = load_credit(credit_path)
        tributors = load_tributors(tributors_path)
        contribs = build_contributors(credit, tributors)
    except (ValueError, KeyError, yaml.YAMLError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 1

    if args.validate_only:
        sys.stderr.write(
            f"ok: validated {len(contribs)} contributor(s) with "
            f"{sum(len(c.roles) for c in contribs)} role assignment(s)\n"
        )
        return 0

    style = credit.get("style") or {}
    if args.format == "latex":
        out = render_latex_section(contribs, style)
    elif args.format == "markdown":
        out = render_markdown_section(contribs, style)
    elif args.format == "text":
        out = render_prose(contribs, style, "text") + "\n"
    elif args.format == "jats":
        out = render_jats(contribs)
    elif args.format in ("matrix-md", "matrix-tex"):
        out = render_matrix(contribs, args.format)
    else:  # pragma: no cover
        raise AssertionError(args.format)

    if args.output:
        Path(args.output).write_text(out)
    else:
        sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

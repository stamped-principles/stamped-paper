#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Yaroslav Halchenko <yaroslav.o.halchenko@dartmouth.edu>
# SPDX-License-Identifier: MIT
#
# Generated with Claude Code 2.1.143 / Claude Opus 4.7

"""Render the LaTeX ``\\author{}`` block (with affiliation references) from
``.tributors`` + ``.tributors.credit.yaml``.

Byline order is read from ``.tributors.credit.yaml`` (the ``byline:`` list),
because JSON object key order is not part of the JSON spec and so cannot be
the canonical source of byline order. Names and affiliations are read from
``.tributors``. Affiliations are deduplicated across the byline; each
distinct affiliation string gets the next integer id in first-appearance
order, and authors are tagged with ``\\textsuperscript{<ids>}``.

Per-author ``.tributors`` schema for affiliation:

  - ``affiliation: "Some place"``                # single string, OR
  - ``affiliation: ["Place A", "Place B"]``      # list of strings (multiple)

Authors without an ``affiliation`` field are rendered without a superscript;
no affiliation footer is emitted if no author has one.

Corresponding authors are declared in ``.tributors.credit.yaml`` with a
per-contributor ``corresponding: true`` flag:

  contributors:
    asmacdo:
      corresponding: true
      roles: [...]

Every flagged author gets ``*`` appended to their superscript markers, and a
``Corresponding author(s): <names>`` line, listing them in byline order, is
appended below the affiliations. When no author carries the flag, the first
byline author is treated as corresponding (the historical behaviour).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.stderr.write(
        "error: PyYAML is required. Install with: pip install pyyaml\n"
    )
    sys.exit(2)


def load_tributors(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def load_credit(path: Path) -> dict:
    return yaml.safe_load(path.read_text()) or {}


def _affiliations_of(entry: dict) -> list[str]:
    raw = entry.get("affiliation")
    if raw is None:
        return []
    if isinstance(raw, str):
        return [raw]
    if isinstance(raw, list):
        return [str(a) for a in raw]
    raise ValueError(f"unsupported affiliation type: {raw!r}")


_VALID_SIZES = {
    "tiny", "scriptsize", "footnotesize", "small",
    "normalsize", "large", "Large", "LARGE",
}

_VALID_ORCID_MARKERS = {"text-id", "orcidlink", "none"}


def _linkify(text: str, links: dict[str, str]) -> str:
    """Wrap each ``links`` key found in ``text`` with ``\\href{url}{key}``.

    Keys are tried longest-first so that overlapping keys (e.g.
    "Dartmouth College" vs "Dartmouth") link the more specific name.
    Each occurrence is wrapped, but a key inside an already-wrapped
    region is not re-wrapped (re.sub does a single left-to-right pass).
    """
    if not links:
        return text
    keys_sorted = sorted(links, key=len, reverse=True)
    pattern = re.compile("|".join(re.escape(k) for k in keys_sorted))

    def _sub(match: re.Match) -> str:
        key = match.group(0)
        url = links[key]
        return f"\\href{{{url}}}{{{key}}}"

    return pattern.sub(_sub, text)


def _corresponding_handles(credit: dict, byline: list[str]) -> list[str]:
    """Return the handles flagged ``corresponding: true``, in byline order.

    The flag lives in the ``contributors:`` map of the credit overlay, next
    to the CRediT roles, because being a corresponding author is a property
    of this manuscript rather than of the person's identity (``.tributors``).
    With no flag anywhere, the first byline author is returned so that
    projects predating the flag keep their previous rendering.
    """
    contributors = credit.get("contributors") or {}
    flagged = {
        handle
        for handle, entry in contributors.items()
        if (entry or {}).get("corresponding")
    }
    unknown = flagged - set(byline)
    if unknown:
        raise ValueError(
            "corresponding author(s) not in the byline: "
            + ", ".join(sorted(unknown))
        )
    ordered = [handle for handle in byline if handle in flagged]
    return ordered or byline[:1]


def _orcid_url(orcid: str) -> str:
    return orcid if orcid.startswith("http") else f"https://orcid.org/{orcid}"


def _orcid_id(orcid: str) -> str:
    """Return the bare 16-digit ORCID id (XXXX-XXXX-XXXX-XXXX), stripping
    any leading ``https://orcid.org/`` prefix."""
    return orcid.rsplit("/", 1)[-1] if "/" in orcid else orcid


def render(credit: dict, tributors: dict[str, dict]) -> str:
    byline: list[str] = list(credit.get("byline") or [])
    if not byline:
        byline = list(tributors.keys())
        sys.stderr.write(
            "warning: no 'byline' in credit YAML; falling back to "
            ".tributors insertion order (not guaranteed stable across "
            "JSON implementations)\n"
        )

    style = credit.get("style") or {}
    # Affiliation footer width as a fraction of \textwidth, and font size.
    # Wrapping the footer in a width-limited minipage prevents long
    # affiliation strings from forcing \maketitle to centre the entire
    # title block around an over-wide line.
    aff_width = float(style.get("affiliations_width", 0.85))
    if not 0 < aff_width <= 1:
        raise ValueError(
            f"style.affiliations_width must be in (0, 1]; got {aff_width}"
        )
    aff_size = str(style.get("affiliations_size", "small"))
    if aff_size not in _VALID_SIZES:
        raise ValueError(
            f"style.affiliations_size must be one of {sorted(_VALID_SIZES)}; "
            f"got {aff_size!r}"
        )
    orcid_marker = str(style.get("orcid_marker", "text-id"))
    if orcid_marker not in _VALID_ORCID_MARKERS:
        raise ValueError(
            f"style.orcid_marker must be one of {sorted(_VALID_ORCID_MARKERS)}; "
            f"got {orcid_marker!r}"
        )

    # Top-level: substring → URL replacements applied to every affiliation
    # via render_authors._linkify (longest-key-first).
    aff_links: dict[str, str] = dict(credit.get("affiliation_links") or {})

    corresponding = set(_corresponding_handles(credit, byline))

    aff_id: dict[str, int] = {}
    rendered_authors: list[str] = []
    corresponding_names: list[str] = []

    for handle in byline:
        entry = tributors.get(handle, {})
        name = entry.get("name") or handle
        ids: list[int] = []
        for aff in _affiliations_of(entry):
            if aff not in aff_id:
                aff_id[aff] = len(aff_id) + 1
            ids.append(aff_id[aff])

        # Build the marker(s) trailing the author name. ORCID marker form
        # depends on style.orcid_marker:
        #   text-id   — plain "iD" hyperlink, packed inside the affiliation
        #               superscript (no preamble change required).
        #   orcidlink — \orcidlink{<id>} from the orcidlink package, sits
        #               after the superscript (needs \usepackage{orcidlink}).
        #   none      — no ORCID marker rendered.
        orcid = entry.get("orcid")
        sup_parts: list[str] = [",".join(str(i) for i in ids)] if ids else []
        # Corresponding authors get "*" in the superscript; their names are
        # collected for the footer line below the affiliations.
        if handle in corresponding:
            sup_parts.append("*")
            corresponding_names.append(name)
        trailing = ""
        if orcid and orcid_marker == "text-id":
            sup_parts.append(f"\\href{{{_orcid_url(orcid)}}}{{iD}}")
        elif orcid and orcid_marker == "orcidlink":
            trailing = f"~\\orcidlink{{{_orcid_id(orcid)}}}"
        sup = f"\\textsuperscript{{{','.join(sup_parts)}}}" if sup_parts else ""
        rendered_authors.append(f"{name}{sup}{trailing}")

    corresponding_line: str | None = None
    if corresponding_names:
        label = "Corresponding author"
        if len(corresponding_names) > 1:
            label += "s"
        joined = ", ".join(corresponding_names)
        corresponding_line = f"\\textsuperscript{{*}}{label}: {joined}"

    lines: list[str] = [
        "% AUTO-GENERATED from .tributors{,.credit.yaml} by render_authors.py — do not hand-edit.",
        "\\author{%",
    ]
    # Comma-separate authors; one per line for readable source diff.
    for i, author in enumerate(rendered_authors):
        sep = "," if i < len(rendered_authors) - 1 else ""
        lines.append(f"  {author}{sep}")

    if aff_id or corresponding_line:
        lines.append("  \\\\[0.5ex]")
        lines.append(
            f"  \\begin{{minipage}}{{{aff_width}\\textwidth}}\\centering\\{aff_size}"
        )
        sorted_affs = sorted(aff_id.items(), key=lambda kv: kv[1])
        rows = [
            f"    \\textsuperscript{{{idx}}}{_linkify(aff, aff_links)}"
            for aff, idx in sorted_affs
        ]
        if corresponding_line:
            rows.append(f"    {corresponding_line}")
        for i, row in enumerate(rows):
            sep = " \\\\" if i < len(rows) - 1 else ""
            lines.append(f"{row}{sep}")
        lines.append("  \\end{minipage}")

    lines.append("}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="render_authors.py",
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
        help="Path to .tributors JSON (default: .tributors)",
    )
    p.add_argument("-o", "--output", help="Write to file instead of stdout")
    args = p.parse_args(argv)

    credit_path = Path(args.credit_yaml)
    tributors_path = Path(args.tributors)
    if not credit_path.exists():
        sys.stderr.write(f"error: {credit_path} not found\n")
        return 2
    if not tributors_path.exists():
        sys.stderr.write(
            f"error: {tributors_path} not found (need it for names "
            "and affiliations)\n"
        )
        return 2

    try:
        credit = load_credit(credit_path)
        tributors = load_tributors(tributors_path)
        out = render(credit, tributors)
    except (ValueError, yaml.YAMLError, json.JSONDecodeError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 1

    if args.output:
        Path(args.output).write_text(out)
    else:
        sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

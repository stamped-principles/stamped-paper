#!/usr/bin/env python3
#
# Migrate main.tex citation keys onto the keys Zotero now exports.
#
# Zotero's BibTeX export used to generate a citation key at export time from
# author, title and year (snake_case).  It now returns each item's stored
# citationKey field instead (camelCase), so regenerating references.bib renames
# nearly every entry and the manuscript's \cite commands stop resolving.
#
# Citation keys are therefore not a stable way to say "this work".  The
# migration is only verifiable against something that survives the rename:
#
#     DOI  ->  else URL  ->  else title
#
# Some cited entries carry no DOI (talks, specifications, repositories), which
# is why the chain has fallbacks rather than requiring one.
#
# Run with no arguments to audit: parse both files, resolve every citation site
# to an identity, and report.  Nothing is written.
#
# Run with --migrate to regenerate the bibliography, rewrite the keys, and
# verify that every citation site still resolves to the identity it had before.
# The verification is the point: "all keys resolve" would also pass if a
# citation were repointed at a different work.
#
# Keys that vanish from the library entirely cannot be mapped and must be named
# with --expect-missing; anything else disappearing is a hard failure.
#
# Where several library records share one DOI, the first candidate is taken
# deterministically.  That is safe -- same DOI, same work -- but it means the
# bibliography may render a less complete duplicate.  Deduplicating the library
# is the real fix and removes the choice entirely.
#
# Usage:
#   migrate-citation-keys.py
#   migrate-citation-keys.py --migrate [--dry-run] [--expect-missing K1,K2]

import argparse
import os
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict

# Citation commands to scan for.  main.tex uses \cite, but a stray \citep or
# \autocite must not be silently skipped -- a missed site is a missed rename.
CITE_COMMANDS = (
    "cite", "citep", "citet", "citeauthor", "citeyear",
    "autocite", "parencite", "textcite", "footcite",
)

CITE_RE = re.compile(
    r"\\(" + "|".join(CITE_COMMANDS) + r")\*?"   # command, optional star
    r"(?:\[[^\]]*\])*"                            # optional [pre][post] args
    r"\{([^}]*)\}"                                # the key list
)

ENTRY_RE = re.compile(r"^@(\w+)\s*\{\s*([^,\s]+)\s*,", re.MULTILINE)


def parse_bib(text):
    """Parse a .bib file into {key: {field: value}}.

    Brace-aware: values may span lines and contain nested braces.  This also
    means line-initial '@' inside an abstract (references.bib holds several
    GitHub @-mentions) is correctly ignored, which a line-based scan gets wrong.
    """
    entries = {}
    pos = 0
    while True:
        m = ENTRY_RE.search(text, pos)
        if not m:
            break
        key = m.group(2)
        body_start = text.index("{", m.start())
        body_end = _match_brace(text, body_start)
        if body_end is None:
            sys.exit(f"unbalanced braces in entry {key!r}")
        body = text[text.index(",", body_start) + 1 : body_end]
        entries[key] = _parse_fields(body)
        entries[key]["_type"] = m.group(1).lower()
        pos = body_end + 1
    return entries


def _match_brace(text, start):
    """Index of the '}' matching the '{' at start, or None."""
    depth = 0
    for i in range(start, len(text)):
        c = text[i]
        if c == "{" and (i == 0 or text[i - 1] != "\\"):
            depth += 1
        elif c == "}" and text[i - 1] != "\\":
            depth -= 1
            if depth == 0:
                return i
    return None


def _parse_fields(body):
    """Extract 'name = value' pairs from an entry body."""
    fields = {}
    i = 0
    while i < len(body):
        m = re.compile(r"\s*(\w+)\s*=\s*").match(body, i)
        if not m:
            i += 1
            continue
        name = m.group(1).lower()
        j = m.end()
        if j < len(body) and body[j] == "{":
            end = _match_brace(body, j)
            if end is None:
                break
            value, i = body[j + 1 : end], end + 1
        elif j < len(body) and body[j] == '"':
            end = body.index('"', j + 1)
            value, i = body[j + 1 : end], end + 1
        else:
            end = body.find(",", j)
            end = len(body) if end == -1 else end
            value, i = body[j:end], end
        fields[name] = value.strip()
    return fields


def norm_doi(v):
    v = re.sub(r"^\s*(https?://(dx\.)?doi\.org/|doi:)", "", v.strip(), flags=re.I)
    return re.sub(r"[{}\s]", "", v).lower()


def norm_url(v):
    v = re.sub(r"^\s*https?://", "", v.strip(), flags=re.I)
    return re.sub(r"[{}\s]", "", v).rstrip("/").lower()


def norm_title(v):
    return re.sub(r"[^a-z0-9]", "", v.lower())


def identity(entry):
    """(kind, value) that survives a key rename, or None if unidentifiable."""
    if entry.get("doi"):
        return ("doi", norm_doi(entry["doi"]))
    if entry.get("url"):
        return ("url", norm_url(entry["url"]))
    if entry.get("title"):
        return ("title", norm_title(entry["title"]))
    return None


def find_sites(tex):
    """Every cited key in document order: (n, key, command, label).

    A site is one key occurrence, so \\cite{a,b} is two sites.  n is the
    ordinal used as the migration's identity; label is for humans reading
    the report and carries no meaning to the tool.
    """
    sites = []
    for m in CITE_RE.finditer(tex):
        command, keylist = m.group(1), m.group(2)
        label = _preceding_words(tex, m.start())
        for key in (k.strip() for k in keylist.split(",")):
            if key:
                sites.append((len(sites) + 1, key, command, label))
    return sites


def _preceding_words(tex, pos, count=5):
    before = tex[max(0, pos - 400) : pos]
    before = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])*", " ", before)  # drop commands
    before = re.sub(r"[{}$%~\\]", " ", before)
    words = before.split()
    return " ".join(words[-count:]) if words else "(start of document)"


def site_identities(tex, entries):
    """{site ordinal: (identity, key, label)} -- the thing that must not change."""
    out = {}
    for n, key, _, label in find_sites(tex):
        entry = entries.get(key)
        out[n] = (identity(entry) if entry else None, key, label)
    return out


def build_key_map(cited, old_entries, new_entries):
    """old key -> new key, resolved by identity.  Also returns diagnostics."""
    index = defaultdict(list)
    for key, entry in new_entries.items():
        ident = identity(entry)
        if ident:
            index[ident].append(key)

    mapping, missing, ambiguous = {}, [], []
    for key in cited:
        candidates = sorted(index.get(identity(old_entries[key]), []))
        if not candidates:
            missing.append(key)
        elif len(candidates) > 1:
            # Candidates share an identity, so they are the same work and any
            # choice is correct; they differ only in metadata completeness.
            # Take the first deterministically and report it.  The real fix is
            # deduplicating the library, after which this branch stops firing.
            ambiguous.append((key, candidates))
            mapping[key] = candidates[0]
        else:
            mapping[key] = candidates[0]
    return mapping, missing, ambiguous


def rewrite_tex(tex, mapping):
    """Substitute keys inside citation commands only, preserving spacing.

    Keys are replaced span by span rather than by rejoining the key list, so
    the diff of a 59-key rename shows only the keys and no whitespace churn.
    """
    edits, renamed = [], 0
    for m in CITE_RE.finditer(tex):
        base, seg, cursor = m.start(2), m.group(2), 0
        for part in seg.split(","):
            stripped = part.strip()
            if stripped:
                start = base + cursor + part.index(stripped)
                new_key = mapping.get(stripped, stripped)
                if new_key != stripped:
                    edits.append((start, start + len(stripped), new_key))
                    renamed += 1
            cursor += len(part) + 1  # +1 for the comma
    out, last = [], 0
    for start, end, new_key in edits:
        out.append(tex[last:start])
        out.append(new_key)
        last = end
    out.append(tex[last:])
    return "".join(out), renamed


def verify(before, after, allow_broken):
    """Every site must still resolve to the identity it had before.

    Stronger than 'all keys resolve': a key that resolved to the wrong
    duplicate record would pass that check and fail this one.
    """
    problems = []
    for n, (ident, key, label) in sorted(before.items()):
        new_ident, new_key, _ = after.get(n, (None, None, None))
        if key in allow_broken:
            continue
        if new_ident is None:
            problems.append(f"site {n:3d}  {new_key}  no longer resolves  ...{label}")
        elif new_ident != ident:
            problems.append(
                f"site {n:3d}  {key} -> {new_key}  identity changed "
                f"{ident} -> {new_ident}  ...{label}"
            )
    if len(before) != len(after):
        problems.append(f"site count changed: {len(before)} -> {len(after)}")
    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tex", default="main.tex")
    ap.add_argument("--bib", default="references.bib")
    ap.add_argument("--verbose", action="store_true", help="list every site")
    ap.add_argument("--migrate", action="store_true",
                    help="regenerate the bibliography and rewrite the keys")
    ap.add_argument("--dry-run", action="store_true",
                    help="with --migrate: report the plan, write nothing")
    ap.add_argument("--new-bib", metavar="PATH",
                    help="use this file as the regenerated bibliography "
                         "instead of fetching (for testing)")
    # No --group here on purpose: the fetch script owns the group id and the
    # output path, so it stays in exactly one place.  We invoke it bare.
    ap.add_argument("--fetch-script", default="code/fetch-zotero-bib.sh")
    ap.add_argument("--expect-missing", default="", metavar="K1,K2",
                    help="cited keys allowed to vanish from the library; "
                         "anything else missing is a hard failure")
    args = ap.parse_args()

    allow_broken = {k for k in args.expect_missing.split(",") if k}

    with open(args.bib, encoding="utf-8") as f:
        entries = parse_bib(f.read())
    with open(args.tex, encoding="utf-8") as f:
        tex = f.read()
    sites = find_sites(tex)

    print(f"bib entries parsed : {len(entries)}")
    print(f"citation sites     : {len(sites)}")
    print(f"distinct keys cited: {len({s[1] for s in sites})}")
    print(f"commands seen      : {dict(Counter(s[2] for s in sites))}")

    # A cited key with no entry cannot be migrated -- it has no identity.
    undefined = sorted({key for _, key, _, _ in sites if key not in entries})
    print(f"\nundefined (cited, not in bib): {len(undefined)}")
    for key in undefined:
        print(f"  {key}")

    # Which link in the identity chain each cited key relies on.
    ids, unidentifiable = {}, []
    for key in sorted({s[1] for s in sites}):
        if key not in entries:
            continue
        ident = identity(entries[key])
        if ident is None:
            unidentifiable.append(key)
        else:
            ids[key] = ident
    print(f"\nidentity source: {dict(Counter(k for k, _ in ids.values()))}")
    if unidentifiable:
        print(f"UNIDENTIFIABLE (no doi, url or title): {len(unidentifiable)}")
        for key in unidentifiable:
            print(f"  {key}")

    # Two cited keys sharing an identity would later collapse into one key.
    collisions = defaultdict(list)
    for key, ident in ids.items():
        collisions[ident].append(key)
    shared = {i: ks for i, ks in collisions.items() if len(ks) > 1}
    print(f"\ncited keys sharing an identity: {len(shared)}")
    for ident, keys in shared.items():
        print(f"  {ident[0]}:{ident[1][:60]}")
        for key in keys:
            print(f"      {key}")

    if args.verbose:
        print("\nsites:")
        for n, key, _, label in sites:
            kind = ids.get(key, ("?", "unresolved"))[0]
            print(f"  {n:3d}  {kind:5s}  {key:46s}  ...{label}")

    ok = not undefined and not unidentifiable and not shared
    print("\nAUDIT OK" if ok else "\nAUDIT FOUND PROBLEMS (see above)")
    if not args.migrate:
        return 0 if ok else 1
    if not ok:
        sys.exit("refusing to migrate: resolve the audit problems first")

    # The snapshot must be taken before the bibliography is replaced -- it is
    # the only record of what each citation site pointed at beforehand.
    before = site_identities(tex, entries)

    backup = None
    if args.new_bib:
        new_path = args.new_bib
        print(f"\nusing supplied bibliography: {new_path} (bibliography not installed)")
    else:
        backup = args.bib + ".pre-migration"
        shutil.copyfile(args.bib, backup)
        print(f"\nregenerating via {args.fetch_script} (backup at {backup})")
        subprocess.run(["bash", args.fetch_script], check=True)
        new_path = args.bib
    with open(new_path, encoding="utf-8") as f:
        new_entries = parse_bib(f.read())
    print(f"regenerated entries: {len(new_entries)}")

    cited = sorted({s[1] for s in sites})
    mapping, missing, ambiguous = build_key_map(cited, entries, new_entries)

    unchanged = sorted(k for k, v in mapping.items() if k == v)
    print(f"\nmapped: {len(mapping)}   unchanged: {len(unchanged)}")
    for key in unchanged:
        print(f"      {key}")

    if ambiguous:
        print(f"\nambiguous -- several entries share one identity: {len(ambiguous)}")
        for key, candidates in ambiguous:
            print(f"  {key}")
            for cand in candidates:
                print(f"      {'-> ' if mapping[key] == cand else '   '}{cand}")

    print(f"\ngone from the library: {len(missing)}")
    for key in missing:
        print(f"      {key}")
    unexpected = sorted(set(missing) - allow_broken)
    if unexpected:
        _restore(backup, args.bib)
        sys.exit("refusing to migrate: unexpected keys vanished: "
                 + ", ".join(unexpected))
    stale = sorted(allow_broken - set(missing))
    if stale:
        print(f"note: --expect-missing names present keys: {', '.join(stale)}")

    # Two old keys collapsing onto one new key would silently merge distinct
    # citations -- the one failure mode the identity check cannot see.
    collapsed = defaultdict(list)
    for old_key, new_key in mapping.items():
        collapsed[new_key].append(old_key)
    merged = {n: o for n, o in collapsed.items() if len(o) > 1}
    if merged:
        for new_key, old_keys in merged.items():
            print(f"  MERGE {new_key} <- {', '.join(sorted(old_keys))}")
        _restore(backup, args.bib)
        sys.exit("refusing to migrate: distinct citations would collapse")

    new_tex, renamed = rewrite_tex(tex, mapping)
    print(f"\ncitation sites rewritten: {renamed} of {len(sites)}")

    problems = verify(before, site_identities(new_tex, new_entries), allow_broken)
    if problems:
        print("\nVERIFICATION FAILED:")
        for problem in problems:
            print("  " + problem)
        _restore(backup, args.bib)
        return 1
    checked = sum(1 for _, (_, key, _) in before.items() if key not in allow_broken)
    print(f"verification: {checked} sites keep their exact identity")

    if args.dry_run:
        _restore(backup, args.bib)
        print("\nDRY RUN -- nothing written")
        return 0

    with open(args.tex, "w", encoding="utf-8") as f:
        f.write(new_tex)
    if backup:
        os.remove(backup)
    print(f"\nwrote {args.tex}" + ("" if args.new_bib else f" and {args.bib}"))
    return 0


def _restore(backup, bib):
    """Put the original bibliography back after an abort or a dry run."""
    if backup and os.path.exists(backup):
        os.replace(backup, bib)


if __name__ == "__main__":
    sys.exit(main())

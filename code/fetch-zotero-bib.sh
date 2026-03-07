#!/bin/bash
#
# Fetch the full bibliography from a Zotero group library as BibTeX.
#
# Usage: fetch-zotero-bib.sh [GROUP_ID] [OUTPUT_FILE]
#
# Zotero API caps responses at 100 items, so this script paginates
# until all items are retrieved.  Results are sorted by title for
# deterministic output, and duplicate citation keys are removed.

set -euo pipefail

GROUP_ID="${1:-6197458}"
OUTPUT="${2:-references.bib}"
LIMIT=100
API="https://api.zotero.org/groups/${GROUP_ID}/items?format=bibtex&limit=${LIMIT}&sort=title&direction=asc"

curl -sf "${API}" -o "${OUTPUT}"
start="${LIMIT}"

while true; do
    tmp="${OUTPUT}.tmp"
    curl -sf "${API}&start=${start}" -o "${tmp}"
    if [ ! -s "${tmp}" ]; then
        rm -f "${tmp}"
        break
    fi
    cat "${tmp}" >> "${OUTPUT}"
    rm -f "${tmp}"
    start=$((start + LIMIT))
done

# Remove duplicate entries (keep first occurrence of each citation key)
dedup="${OUTPUT}.dedup"
awk '
    /^@[a-zA-Z]+\{/ {
        key = $0
        sub(/^@[a-zA-Z]+\{/, "", key)
        sub(/,.*/, "", key)
        if (key in seen) { skip = 1; next }
        seen[key] = 1
        skip = 0
    }
    !skip { print }
' "${OUTPUT}" > "${dedup}"
mv "${dedup}" "${OUTPUT}"

count=$(grep -c '^@' "${OUTPUT}")
echo "Fetched ${count} entries to ${OUTPUT}"

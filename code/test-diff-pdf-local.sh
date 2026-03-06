#!/bin/bash
#
# Local test for the diff-pdf container and diff pipeline.
#
# Usage: test-diff-pdf-local.sh [docker|podman]
#
# Requires: a built main.pdf in the repo root (run `make` first).
# Builds the container locally and runs a subset of the diff pipeline
# to verify that diff-pdf, pdftoppm, compare, and montage all work.

set -euo pipefail

RUNTIME="${1:-docker}"
IMAGE="local:diff-pdf-test"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [ ! -f "$REPO_ROOT/main.pdf" ]; then
    echo "ERROR: main.pdf not found in $REPO_ROOT — run 'make' first." >&2
    exit 1
fi

# Create a host-side tmpdir visible inside the container via the bind mount
TMPDIR="$REPO_ROOT/_test-tmp"
rm -rf "$TMPDIR"
mkdir -p "$TMPDIR"
cleanup() { rm -rf "$TMPDIR" "$REPO_ROOT/_test-diff.pdf" "$REPO_ROOT/pr-comment.md"; }
trap cleanup EXIT

echo "=== Building container with $RUNTIME (--no-cache) ==="
"$RUNTIME" build --no-cache \
    -t "$IMAGE" \
    -f "$REPO_ROOT/containers/diff-pdf.Dockerfile" \
    "$REPO_ROOT/containers/"

run() {
    "$RUNTIME" run --rm -v "$REPO_ROOT:$REPO_ROOT" -w "$REPO_ROOT" "$IMAGE" "$@"
}

passes=0
failures=0
pass() { echo "PASS"; passes=$((passes + 1)); }
fail() { echo "FAIL — $1"; failures=$((failures + 1)); }

echo ""
echo "=== Test 1: diff-pdf --help ==="
if run diff-pdf --help >/dev/null 2>&1; then
    pass
else
    fail "diff-pdf --help exited non-zero"
fi

echo ""
echo "=== Test 2: diff-pdf identical file (exit 0) ==="
if run diff-pdf main.pdf main.pdf; then
    pass
else
    fail "expected exit 0 for identical files"
fi

echo ""
echo "=== Test 3: diff-pdf output-diff ==="
run diff-pdf --output-diff=_test-diff.pdf main.pdf main.pdf || true
if [ -f "$REPO_ROOT/_test-diff.pdf" ]; then
    pass
else
    fail "no _test-diff.pdf produced"
fi

echo ""
echo "=== Test 4: pdftoppm ==="
# pdftoppm zero-pads page numbers based on total pages, so use a glob
run bash -c "pdftoppm -png -r 72 -f 1 -l 1 main.pdf $TMPDIR/test"
count=$(find "$TMPDIR" -name 'test-*.png' | wc -l)
if [ "$count" -eq 1 ]; then
    pass
else
    fail "expected 1 PNG, got $count"
fi

echo ""
echo "=== Test 5: compare (ImageMagick) ==="
img=$(find "$TMPDIR" -name 'test-*.png' | head -1)
cp "$img" "$TMPDIR/copy.png"
pixels=$(run compare -metric AE -fuzz 2% "$img" "$TMPDIR/copy.png" /dev/null 2>&1 || true)
echo "  pixel difference: $pixels"
if [ "$pixels" = "0" ]; then
    pass
else
    fail "expected 0 pixels different, got '$pixels'"
fi

echo ""
echo "=== Test 6: montage with labels (DejaVu-Sans font) ==="
if run montage -font DejaVu-Sans \
        -label "main" "$img" \
        -label "PR" "$img" \
        -label "changes" "$img" \
        -tile 3x1 -geometry '+4+4' "$TMPDIR/montage-labeled.png"; then
    if [ -f "$TMPDIR/montage-labeled.png" ]; then
        pass
    else
        fail "montage exited 0 but no output file"
    fi
else
    fail "montage with labels exited non-zero"
fi

echo ""
echo "=== Test 7: montage without labels (fallback) ==="
if run montage +label "$img" "$img" "$img" \
        -tile 3x1 -geometry '+4+4' "$TMPDIR/montage-plain.png"; then
    if [ -f "$TMPDIR/montage-plain.png" ]; then
        pass
    else
        fail "montage exited 0 but no output file"
    fi
else
    fail "montage without labels exited non-zero"
fi

echo ""
echo "=== Test 8: full diff script (dry run — 404 base URL) ==="
run ./code/gh-pages-diff-pdf.sh \
    main.pdf \
    "https://httpbin.org/status/404" \
    "test-branch" \
    "test/repo" \
    "https://github.com" \
    "abc1234"
if [ -f "$REPO_ROOT/pr-comment.md" ] && grep -q 'No main PDF deployed' "$REPO_ROOT/pr-comment.md"; then
    pass
else
    fail "pr-comment.md missing or unexpected content"
fi

echo ""
echo "==================================="
echo "Results: $passes passed, $failures failed"
if [ "$failures" -gt 0 ]; then
    exit 1
fi

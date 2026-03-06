#!/bin/bash
#
# Generate a PDF diff comment and assets for a PR preview branch.
#
# Usage: gh-pages-diff-pdf.sh <pr-pdf> <base-url> <preview-branch> <repo> <server> <head-sha>
#
# Inputs:
#   pr-pdf          — path to the PR-built PDF
#   base-url        — URL of the deployed main PDF (e.g. https://myyoda.github.io/principles-paper/main.pdf)
#   preview-branch  — name of the preview branch (e.g. gh-pages-pr-42)
#   repo            — GitHub repository (e.g. myyoda/principles-paper)
#   server          — GitHub server URL (e.g. https://github.com)
#   head-sha        — full SHA of the PR head commit
#
# Outputs (in current directory):
#   pr-comment.md       — markdown body for the PR comment
#   diff.pdf            — visual diff PDF (only if differences found)
#   diff-page-NN.png    — per-page diff images (only for changed pages)
#
# Exit codes:
#   0 — success (comment always generated)

set -euo pipefail

pr_pdf="$1"
base_url="$2"
preview_branch="$3"
repo="$4"
server="$5"
head_sha="$6"

raw_base="https://raw.githubusercontent.com/${repo}/${preview_branch}"
view_url="${server}/${repo}/blob/${preview_branch}/main.pdf"

# --- Build comment header ---
{
    echo "<!-- pdf-preview -->"
    echo "### Paper PDF"
    echo "Built from ${head_sha}."
    echo "**[View PDF](${view_url})** | **[Download](${raw_base}/main.pdf)**"
} > pr-comment.md

# --- Download the current main PDF for comparison ---
if ! curl -sfL "$base_url" -o main-base.pdf; then
    echo "" >> pr-comment.md
    echo "*No main PDF deployed yet — diff not available.*" >> pr-comment.md
    exit 0
fi

# --- Generate visual diff PDF ---
diff_view_url="${server}/${repo}/blob/${preview_branch}/diff.pdf"

if diff-pdf --output-diff=diff.pdf --dpi=300 --channel-tolerance=0 -g \
     main-base.pdf "$pr_pdf"; then
    echo "" >> pr-comment.md
    echo "No visual differences from main." >> pr-comment.md
    rm -f main-base.pdf
    exit 0
fi

# diff-pdf exits non-zero when differences exist — that's the normal path here

# --- Convert PDFs to per-page PNGs for comparison ---
mkdir -p diff-pages
pdftoppm -png -r 150 diff.pdf diff-pages/page
pdftoppm -png -r 150 main-base.pdf diff-pages/base
pdftoppm -png -r 150 "$pr_pdf" diff-pages/pr

mapfile -t diff_pngs < <(find diff-pages -name 'page-*.png' | sort -V)
mapfile -t base_pngs < <(find diff-pages -name 'base-*.png' | sort -V)
mapfile -t pr_pngs < <(find diff-pages -name 'pr-*.png' | sort -V)

base_count=${#base_pngs[@]}
pr_count=${#pr_pngs[@]}
diff_count=${#diff_pngs[@]}
max_count=$((base_count > pr_count ? base_count : pr_count))

changed=0
unchanged=0
added=0
removed=0
page_details=""

for ((i = 0; i < max_count; i++)); do
    page_num=$((i + 1))
    padded=$(printf '%02d' "$page_num")

    if [ "$i" -lt "$base_count" ] && [ "$i" -lt "$pr_count" ]; then
        if [ "$i" -lt "$diff_count" ]; then
            # Compare base vs PR page to detect per-page changes
            pixels=$(compare -metric AE -fuzz 2% \
                "${base_pngs[$i]}" "${pr_pngs[$i]}" /dev/null 2>&1 || true)

            if [ "$pixels" = "0" ] || ! [[ "$pixels" =~ ^[0-9]+$ ]]; then
                unchanged=$((unchanged + 1))
                page_details+="- Page ${page_num} — unchanged\n"
            else
                changed=$((changed + 1))
                # Generate side-by-side: main (left) | PR with red highlights (right)
                # compare -compose src overlays red on the second image where it differs
                compare -fuzz 2% -highlight-color '#FF000060' \
                    "${base_pngs[$i]}" "${pr_pngs[$i]}" \
                    -compose src "diff-pages/highlighted-${padded}.png" 2>/dev/null || true
                # Build 3-panel montage; try with labels, fall back to plain
                montage_args=(-tile 3x1 -geometry '+4+4')
                if ! montage \
                        -font DejaVu-Sans \
                        -label "main" "${base_pngs[$i]}" \
                        -label "PR" "${pr_pngs[$i]}" \
                        -label "changes" "diff-pages/highlighted-${padded}.png" \
                        "${montage_args[@]}" "diff-page-${padded}.png" 2>/dev/null; then
                    montage +label \
                        "${base_pngs[$i]}" "${pr_pngs[$i]}" \
                        "diff-pages/highlighted-${padded}.png" \
                        "${montage_args[@]}" "diff-page-${padded}.png"
                fi
                diff_img_url="${raw_base}/diff-page-${padded}.png"
                page_details+="<details><summary>Page ${page_num} — changed</summary>\n\n"
                page_details+="![page ${page_num} diff](${diff_img_url})\n\n"
                page_details+="</details>\n"
            fi
        fi
    elif [ "$i" -lt "$pr_count" ]; then
        added=$((added + 1))
        page_details+="- Page ${page_num} — **new**\n"
    else
        removed=$((removed + 1))
        page_details+="- Page ${page_num} — **removed**\n"
    fi
done

# --- Build summary ---
parts=()
[ "$changed" -gt 0 ]   && parts+=("${changed} changed")
[ "$unchanged" -gt 0 ] && parts+=("${unchanged} unchanged")
[ "$added" -gt 0 ]     && parts+=("${added} added")
[ "$removed" -gt 0 ]   && parts+=("${removed} removed")
summary="${pr_count} pages total: $(IFS=', '; echo "${parts[*]}")"
[ "$base_count" -ne "$pr_count" ] && summary+=" (was ${base_count})"

{
    echo ""
    echo "#### Diff vs main"
    echo "${summary}"
    echo "**[View full diff PDF](${diff_view_url})**"
    echo ""
    printf '%b' "$page_details"
} >> pr-comment.md

# Clean up temp directory
rm -rf diff-pages main-base.pdf

#!/usr/bin/env bash
set -euo pipefail

# Generate a simple inventory: SVG file -> referenced locations in docs/src
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SVG_DIR="$ROOT_DIR/docs/assets/images/diagrams"
SRC_DIR="$ROOT_DIR/docs/src"

echo "# Diagrams Inventory"
echo
echo "Generated on: $(date -Iseconds)"
echo

while IFS= read -r -d '' svg; do
  rel="${svg#$ROOT_DIR/}"
  echo "## $rel"
  # Find references
  hits=$(rg -n --fixed-strings "$rel" "$SRC_DIR" || true)
  if [[ -z "$hits" ]]; then
    # Try matching by file basename only
    base=$(basename "$rel")
    hits=$(rg -n "$base" "$SRC_DIR" || true)
  fi
  if [[ -z "$hits" ]]; then
    echo "- Referenced: not found"
  else
    echo "$hits" | awk '{print "- " $0}'
  fi
  echo
done < <(find "$SVG_DIR" -type f -name "*.svg" -print0 | sort -z)


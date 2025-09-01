#!/usr/bin/env bash
set -euo pipefail

DIR="docs/assets/images/diagrams"
missing=0

printf "SVG lint (title/desc/viewBox) in %s\n" "$DIR"

while IFS= read -r -d '' f; do
  has_title=$(rg -n "<title" -S "$f" >/dev/null && echo yes || echo no)
  has_desc=$(rg -n "<desc" -S "$f" >/dev/null && echo yes || echo no)
  has_viewbox=$(rg -n "viewBox" -S "$f" >/dev/null && echo yes || echo no)
  if [[ $has_title == no || $has_desc == no || $has_viewbox == no ]]; then
    printf "[WARN] %s: title=%s desc=%s viewBox=%s\n" "$f" "$has_title" "$has_desc" "$has_viewbox"
    missing=1
  fi
done < <(find "$DIR" -type f -name "*.svg" -print0)

if [[ $missing -eq 0 ]]; then
  echo "OK: all SVGs include title/desc/viewBox"
else
  echo "Done: Some SVGs are missing required elements." >&2
  exit 1
fi


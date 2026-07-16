#!/usr/bin/env bash
set -euo pipefail

DIR="docs/assets/images/diagrams"
warn=0

printf "SVG a11y lint (role/title[id]/desc/aria-labelledby) in %s\n" "$DIR"

while IFS= read -r -d '' f; do
  has_role=$(rg -n "role=\"img\"" -S "$f" >/dev/null && echo yes || echo no)
  has_title_id=$(rg -n '<title[^>]*id="[^"]+"' -S "$f" >/dev/null && echo yes || echo no)
  has_desc=$(rg -n "<desc" -S "$f" >/dev/null && echo yes || echo no)
  has_aria=$(rg -n 'aria-labelledby="[^"]+"' -S "$f" >/dev/null && echo yes || echo no)
  if [[ $has_role == no || $has_title_id == no || $has_desc == no || $has_aria == no ]]; then
    printf "[WARN] %s: role=%s title(id)=%s desc=%s aria-labelledby=%s\n" "$f" "$has_role" "$has_title_id" "$has_desc" "$has_aria"
    warn=1
  fi
done < <(find "$DIR" -type f -name "*.svg" -print0)

if [[ $warn -eq 0 ]]; then
  echo "OK: all SVGs include role/title[id]/desc/aria-labelledby"
else
  echo "Done: Some SVGs are missing recommended a11y attributes (non-fatal)" >&2
fi

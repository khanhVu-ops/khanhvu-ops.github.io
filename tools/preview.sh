#!/bin/sh
set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
exec python3 -m http.server "${1:-8765}" --bind 127.0.0.1 --directory "$repo_dir/website"

#!/bin/sh
# Copy the website (without tools, Code.gs and the claude.ai page) to
# docs/study2 at the top of the repository. GitHub Pages
# serves docs/ (Settings > Pages > main, /docs), so Study 2 is online at
# <Study 1 address>/study2/ after a commit and push.
#     sh tools/make_site_folder.sh
cd "$(dirname "$0")/.." || exit 1
OUT=../../docs/study2
mkdir -p "$OUT"
rsync -a --delete --exclude tools --exclude google_sheets --exclude claude_page.html \
      --exclude _headers --exclude .DS_Store --exclude .git --exclude .gitignore \
      --exclude .nojekyll ./ "$OUT/"
echo "Website copied to $OUT"

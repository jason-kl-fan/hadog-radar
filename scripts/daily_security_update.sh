#!/usr/bin/env bash
set -euo pipefail

cd /root/.openclaw/workspace-tg-group-5075638349/ai-news-site

python3 scripts/generate_site.py --fetch --mode security

git add .
if git diff --cached --quiet; then
  echo "No changes to commit"
  exit 0
fi

git -c user.name='OpenClaw Bot' -c user.email='openclaw@example.com' commit -m "chore: daily security news update $(TZ=America/Los_Angeles date +%F)"
git push origin main

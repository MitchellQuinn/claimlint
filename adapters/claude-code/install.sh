#!/usr/bin/env bash
set -euo pipefail

mkdir -p .claude/skills/clipboard-raccoon
cp -R skills/clipboard-raccoon/* .claude/skills/clipboard-raccoon/

echo "Installed ClaimLint skill to .claude/skills/clipboard-raccoon"


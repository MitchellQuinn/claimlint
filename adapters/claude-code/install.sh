#!/usr/bin/env bash
set -euo pipefail

mkdir -p .claude/skills/claimlint
cp -R skills/claimlint/* .claude/skills/claimlint/

echo "Installed ClaimLint skill to .claude/skills/claimlint"


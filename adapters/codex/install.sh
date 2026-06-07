#!/usr/bin/env bash
set -euo pipefail

mkdir -p .agents/skills/claimlint
cp -R skills/claimlint/* .agents/skills/claimlint/

echo "Installed ClaimLint skill to .agents/skills/claimlint"


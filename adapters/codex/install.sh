#!/usr/bin/env bash
set -euo pipefail

mkdir -p .agents/skills/clipboard-raccoon
cp -R skills/clipboard-raccoon/* .agents/skills/clipboard-raccoon/

echo "Installed ClaimLint skill to .agents/skills/clipboard-raccoon"


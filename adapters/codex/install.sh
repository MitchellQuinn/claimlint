#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/../.." && pwd)"
SOURCE_DIR="${REPO_ROOT}/skills/claimlint"
TARGET_DIR="${REPO_ROOT}/.agents/skills/claimlint"

mkdir -p "${TARGET_DIR}"
cp -R "${SOURCE_DIR}/." "${TARGET_DIR}/"

echo "Installed ClaimLint skill to ${TARGET_DIR}"

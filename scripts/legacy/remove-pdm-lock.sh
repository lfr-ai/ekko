#!/usr/bin/env bash
set -euo pipefail

if [ -f "pdm.lock" ]; then
  echo "Found pdm.lock — removing to avoid PDM/pip mismatch in this repo's new pip-based workflow."
  rm -v pdm.lock
  echo "Consider regenerating a pinned requirements.txt if you need reproducible installs."
else
  echo "No pdm.lock present. Nothing to do."
fi

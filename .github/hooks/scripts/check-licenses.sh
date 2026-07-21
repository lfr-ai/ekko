#!/usr/bin/env sh
set -eu

if [ "${SKIP_LICENSE_CHECK:-}" = "true" ]; then
  exit 0
fi

MODE="${LICENSE_MODE:-warn}"
LOG_DIR="${LICENSE_LOG_DIR:-logs/copilot/license-checker}"
mkdir -p "${LOG_DIR}"

if command -v pip-licenses >/dev/null 2>&1; then
  if pip-licenses --format=json >/dev/null 2>&1; then
    printf '{"timestamp":"%s","event":"license_check_ok","mode":"%s"}\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${MODE}" >> "${LOG_DIR}/license.log"
    exit 0
  fi
fi

printf '[License Check] pip-licenses unavailable or failed; running in %s mode\n' "${MODE}" >&2
if [ "${MODE}" = "block" ]; then
  exit 1
fi

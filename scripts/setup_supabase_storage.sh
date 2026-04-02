#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${SUPABASE_URL:-}" ]]; then
  echo "SUPABASE_URL is required"
  exit 1
fi

if [[ -z "${SUPABASE_SERVICE_ROLE_KEY:-}" ]]; then
  echo "SUPABASE_SERVICE_ROLE_KEY is required"
  exit 1
fi

BUCKET="${SUPABASE_STATE_BUCKET:-personal-ai-phone}"

curl -sS \
  -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
  "${SUPABASE_URL}/storage/v1/bucket" | rg "\"name\":\"${BUCKET}\"" >/dev/null 2>&1 && {
  echo "Bucket ${BUCKET} already exists"
  exit 0
}

curl -sS -X POST \
  -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "Content-Type: application/json" \
  "${SUPABASE_URL}/storage/v1/bucket" \
  -d "{\"name\":\"${BUCKET}\",\"public\":false}"

echo
echo "Bucket ${BUCKET} created"

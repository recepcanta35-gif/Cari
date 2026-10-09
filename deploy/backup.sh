#!/usr/bin/env bash
# Run inside a backend/backup operator container. External encrypted retention is mandatory.
set -Eeuo pipefail
: "${CARI_SITE:?Select site explicitly}"
cd /home/frappe/frappe-bench
bench --site "$CARI_SITE" backup --with-files --compress
# Frappe backups include DB/public/private files, but separately protect site_config.json
# with encryption_key. Do not copy backups/credentials to the source repository.
echo "Local backup generated. Copy DB/files and site configuration into the approved encrypted external repository; this is not a successful restore test."

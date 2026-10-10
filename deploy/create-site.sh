#!/usr/bin/env bash
# One-shot provisioning; run only after static preflight and infrastructure startup.
set -Eeuo pipefail
: "${CARI_SITE:?Set real site}"
: "${DB_ROOT_PASSWORD:?Inject database root secret}"
: "${INITIAL_ADMIN_PASSWORD:?Inject one-time administrator secret}"
if [[ "$CARI_SITE" == *.invalid || "$CARI_SITE" == *.local ]]; then
  echo "Refusing placeholder production site" >&2
  exit 1
fi
cd /home/frappe/frappe-bench
if [[ -d "sites/$CARI_SITE" ]]; then
  echo "Site already exists; no reset, overwrite or demo seed performed" >&2
  exit 1
fi
bench new-site "$CARI_SITE" --db-type mariadb --db-host db --db-port 3306 \
  --db-root-username root --db-root-password "$DB_ROOT_PASSWORD" \
  --admin-password "$INITIAL_ADMIN_PASSWORD" --install-app erpnext
bench --site "$CARI_SITE" install-app cari_custom
bench --site "$CARI_SITE" install-app uyumsoft_integration
bench --site "$CARI_SITE" set-config developer_mode 0
bench --site "$CARI_SITE" set-config host_name "https://$CARI_SITE"
bench --site "$CARI_SITE" enable-scheduler
# Legal entity/accounting data is entered by the real ERPNext setup workflow;
# never run the hard-coded Cari demo company/seed on production.
bench --site "$CARI_SITE" clear-cache
unset INITIAL_ADMIN_PASSWORD DB_ROOT_PASSWORD

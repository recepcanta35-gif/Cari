# The supported upstream runtime contains gunicorn, nginx, PDF libraries and assets.
ARG ERPNEXT_VERSION=v15.122.0
FROM frappe/erpnext:${ERPNEXT_VERSION}
USER root
COPY --chown=frappe:frappe apps/cari_custom /home/frappe/frappe-bench/apps/cari_custom
COPY --chown=frappe:frappe apps/uyumsoft_integration /home/frappe/frappe-bench/apps/uyumsoft_integration
USER frappe
WORKDIR /home/frappe/frappe-bench
RUN env/bin/pip install --no-deps -e apps/cari_custom -e apps/uyumsoft_integration \
    && printf '\ncari_custom\nuyumsoft_integration\n' >> sites/apps.txt \
    && mkdir -p sites/assets \
    && bench build --app cari_custom --app uyumsoft_integration \
    && cp -a sites/assets/. /home/frappe/frappe-bench/assets/ \
    && rm -rf sites/assets

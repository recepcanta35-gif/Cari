# ERPNext Kurulum Rehberi (Cari Projesi)

**Tarih:** 9 Ekim 2026
**Durum:** ✅ Çalışır durumda (geliştirme sunucusu: 0.0.0.0:8000)

## 1. Kurulu Bileşenler

| Bileşen | Sürüm | Not |
|---|---|---|
| Frappe Framework | 15.122.0 (branch version-15) | `/home/user/frappe-bench/apps/frappe` |
| ERPNext | 15.122.0 (branch version-15) | `apps/erpnext` |
| cari_custom | 0.0.1 | zimmet, görevlendirme, kargo alanları — `apps/` (symlink) |
| uyumsoft_integration | 0.0.1 | Uyumsoft kuyruğu + UBL-TR taslağı — `apps/` (symlink) |
| Python | 3.11.2 | bench env (uv venv) |
| Node.js | v22.22.3 | yarn 1.22.22 (global) |
| PostgreSQL | 16.2 | pgserver (pip) binary, TCP 127.0.0.1:5432, trust auth |
| Redis | 7.2.16 | GitHub'dan derlendi, 3 instance (13000 cache / 11000 queue / 12000 socketio) |
| frappe-bench CLI | 5.31.0 | `/usr/local/bin/bench` |

## 2. Site Bilgileri

- **Site adı:** `cari.local` (default site olarak ayarlı)
- **Veritabanı:** `cari` (PostgreSQL), kullanıcı `cari`, root `postgres` (trust)
- **Yönetici:** Administrator / admin (geliştirme ortamı için)
- **Erişim:** http://127.0.0.1:8000 (preview host üzerinden de default site olarak çözümlenir)

## 3. Sandbox'a Özel Workaround'lar (önemli — tekrar kurulumda gerekir)

Bu ortamda sadece github.com / npm registry / pypi erişilebilir; TLS intercept (e2b CA) ve apt erişimi YOK. Bu yüzden:

1. **yarn registry:** `yarn config set registry https://registry.npmjs.org --global` (~/.yarnrc) — yarn 1.x varsayılanı registry.yarnpkg.com erişilemez.
2. **yarn.lock host rewrite:** frappe ve erpnext klonlarında `sed -i 's|https://registry.yarnpkg.com|https://registry.npmjs.org|g' yarn.lock` ve **commit** (bench init local path'i git clone ile kopyalar — commit'siz değişiklik kaybolur).
3. **Node TLS CA:** `export NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt` — github.com/codeload TLS intercept nedeniyle Node bundled CA yetersiz.
4. **PostgreSQL:** `pip install pgserver` (bundled PG 16 binary). pgserver TCP dinlemez → manuel başlatma:
   `postgres -D /home/user/pgdata -c listen_addresses=127.0.0.1 -p 5432`
   Binary yolu: `/usr/local/lib/python3.11/dist-packages/pgserver/pginstall/bin`.
5. **psql/pg_dump PATH:** pginstall/bin altındaki tüm araçlar `/usr/local/bin`'e kopyalandı. `libpq` soname uyumu için symlink:
   `ln -s .../pginstall/lib/libpq.so.5.16 .../pginstall/lib/libpq-084d956f.so.5.16`
6. **LD_LIBRARY_PATH:** `export LD_LIBRARY_PATH=/usr/local/lib/python3.11/dist-packages/pgserver/pginstall/lib` (psql/pg_dump için; bench child process'lere taşınmalı).
7. **bench init --no-backups:** sistemde `crontab` binary yok (cron kurulamıyor).
8. **Redis:** `git clone --branch 7.2 https://github.com/redis/redis && make MALLOC=libc`, binary'ler `/usr/local/bin`.

## 4. Tekrarlanabilir Kurulum Komutları

```bash
# 0) Bağımlılıklar
sudo pip3 install --break-system-packages frappe-bench pgserver
sudo npm install -g yarn@1.22.22
yarn config set registry https://registry.npmjs.org --global
# redis derleme (bkz. yukarı)

# 1) frappe + erpnext klonları (yarn.lock sed + commit!)
git clone --depth 1 --branch version-15 https://github.com/frappe/frappe.git /tmp/frappe-fix
cd /tmp/frappe-fix && sed -i 's|https://registry.yarnpkg.com|https://registry.npmjs.org|g' yarn.lock \
  && git add yarn.lock && git -c user.name=fix -c user.email=fix@local commit -m "yarn registry"
# aynı işlem erpnext için /tmp/erpnext-fix

# 2) bench init
export NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt
bench init /home/user/frappe-bench --python /usr/bin/python3 --frappe-path /tmp/frappe-fix --no-backups

# 3) ERPNext app
cd /home/user/frappe-bench
bench get-app /tmp/erpnext-fix --branch version-15

# 4) PostgreSQL başlat (pgserver manuel, TCP)
# 5) Site + ERPNext kurulum
export LD_LIBRARY_PATH=/usr/local/lib/python3.11/dist-packages/pgserver/pginstall/lib
bench new-site cari.local --db-type postgres --db-root-username postgres \
  --db-root-password trustpw --db-host 127.0.0.1 --db-port 5432 --db-name cari \
  --admin-password admin --set-default --install-app erpnext

# 6) Custom app'ler (repo'dan symlink + editable install)
cd apps
ln -sf /home/user/Cari/apps/cari_custom cari_custom
ln -sf /home/user/Cari/apps/uyumsoft_integration uyumsoft_integration
printf 'frappe\nerpnext\ncari_custom\nuyumsoft_integration\n' > ../sites/apps.txt
cd ..
env/bin/pip install -e apps/cari_custom --no-deps
env/bin/pip install -e apps/uyumsoft_integration --no-deps
bench --site cari.local install-app cari_custom
bench --site cari.local install-app uyumsoft_integration
# (Module Def duplicate hatası alınırsa: psql ile "tabModule Def" kaydını silip tekrar dene)
bench --site cari.local migrate

# 7) Çalıştırma
bench start   # web: 0.0.0.0:8000, socketio: 0.0.0.0:9000
```

## 5. Bilinen Uyarılar / Sınırlamalar

- **PostgreSQL v15'te "limited support" uyarısı** — v16+ resmi destekler; v15 üzerinde çalışır (test edildi), ancak生产 öncesi v16'ya (Python 3.14 + Node 24 gerektirir) geçiş değerlendirilmeli.
- **wkhtmltopdf yok** (apt erişimi yok) — PDF için `weasyprint` kurulumu planlanmalı (Faz 1).
- **Otomatik yedekler kapalı** (--no-backups, crontab yok) — pg_dump manuel.
- **Geliştirme sunucusu** (werkzeug) — production için WSGI (gunicorn) + nginx gerekir.

## 6. Sonraki Adımlar (Faz 1 — Çekirdek Yapılandırma)

1. Şirket (Company) oluşturma + Türkiye hesap planı (Tekdüzen Hesap Planı) kurulumu
2. KDV oranları (%1, %10, %20) — Sales/Purchase Taxes and Charges Template
3. Para birimi TRY, dil Türkçe, bölge Türkiye ayarları
4. Depo (merkez/saha), birim (UOM), ürün grupları (Item Group) tanımları
5. Müşteri/tedarikçi grupları, ödeme şartları (vade günleri)
6. Roller/yetkiler (kapsam modülü 16 — Role Permission Manager)
7. E-posta (SMTP) ayarları + Email Alert/Auto Repeat hatırlatmaları (modül 15)
8. PDF: weasyprint kurulumu

## 7. Sonraki Adımlar (Faz 5 — Uyumsoft)

- Uyumsoft ürün/sürüm/erişim yetkisi onayı beklenecek (kapsam koşulu)
- `uyumsoft_integration` app'i: connector (REST/SOAP) + UBL-TR eşleme + kuyruk işleyici
- Test: ürün/cari/fatura aktarımı, e-Fatura gönderimi (GİB entegratör üzerinden)

## 8. Faz 1 — Türkiye Temel Yapılandırması (TAMAMLANDI — 9 Ekim 2026)

`bench --site cari.local console` içinde `cari_custom.setup_turkey.run()` çalıştırıldı (idempotent — tekrar çalıştırılabilir). Script: `apps/cari_custom/cari_custom/setup_turkey.py`.

- **Şirket:** Cari A.Ş. (CARI, Turkey, TRY) + jenerik chart of accounts (82 hesap) + varsayılan depolar (Stores/WIP/Finished Goods/Transit)
- **KDV:** KDV %20 (varsayılan) / %10 / %1 — Sales Taxes and Charges Template + Item Tax Template (KDV hesabı: company setup'ın "VAT 18% - CARI" — tekdüzen plana göre düzenlenecek)
- **Tanımlar:** UOM (Nos, Kg, m, Koli), Item Group (Genel), Customer Group (Bireysel/Kurumsal), Supplier Group (Yerli Tedarikçi), Territory (Türkiye + 7 bölge), Payment Terms (Peşin/30/60 gün), Mode of Payment (Nakit, Kredi Kartı, Havale/EFT, Çek, Senet), Banka - TRY hesabı, Saha Deposu
- **Roller (modül 16):** "Saha Personeli" — Sales Order/Quotation/Delivery Note CRUD; Customer/Item/Warehouse/Employee/Vehicle read; Stock Assignment + Daily Assignment CRUD (Custom DocPerm). Diğer roller: ERPNext hazır rolleri (Sales/Purchase/Accounts/Stock/HR User+Manager, System Manager).
- **Hatırlatma (modül 15):** Notification "Tahsilat Vadesi Yaklaşıyor" — Sales Invoice due_date, 7 gün önce, Email kanalı, Accounts Manager. SMTP (Email Account) ayarlanınca gönderim başlar.
- **Notlar:** developer_mode açık (site_config.json — DocType permission düzenleme için); v15'te Email Alert doctype yok → Notification kullanıldı; PDF (weasyprint/wkhtmltopdf) bu ortamda kurulamıyor (libpango/libXrender eksik) — production sunucuda apt ile kurulacak.

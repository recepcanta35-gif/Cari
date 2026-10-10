# Cari — GitHub Geliştirme ve Düzenleme Dökümü

**Hazırlanma:** 10 Ekim 2026 · **Saat dilimi:** Europe/Istanbul
**Depo:** https://github.com/recepcanta35-gif/Cari · **Dal:** `arena/c5b59147-cari`
**Döküm sınırı:** `614416291e1ae27dd79fd9fdab408ed2714b722e` (devir öncesi incelenen kod referansı).

> Bu döküm ilk 21 commit’i içerir (başlangıç + 20 geliştirme). Devir belgelerinin commit’i bunun üstüne eklenir; kaynak ZIP metadata’sı ve offline bundle teslim anındaki HEAD’i ayrıca verir. Commit başlığındaki “tamam” tarihî çalışma kapsamıdır, bütün modüllerin üretim son kabulü değildir.

## 1. Özet ve doğru dal

- İlk kaynak: `8cc37ee8cf632968ab19c539a69081f963ce5398`; yalnız README.
- İncelenen referans: 129 dosya; 21 commit; 9.928 eklenen / 1 silinen satır.
- Başlangıca göre **128 yeni (A)**, **1 düzenlenen (M)** dosya; silinen kaynak dosyası yok.
- [PR #1](https://github.com/recepcanta35-gif/Cari/pull/1) OPEN; base `main`, head çalışma dalı. `main` başlangıç commit'inde kalır.
- [Başarılı kaynak CI](https://github.com/recepcanta35-gif/Cari/actions/runs/37982049980); [PR CI](https://github.com/recepcanta35-gif/Cari/actions/runs/37982054831).
- Ayrıntılı başlangıç→kaynak dosya farkları: `degisen-dosyalar.tsv`.

## 2. Commit çizelgesi

| # | Commit | İstanbul zamanı | Dosya | + / − satır | Başlık |
|---|---|---|---|---|---|
| 1 | [`8cc37ee`](https://github.com/recepcanta35-gif/Cari/commit/8cc37ee8cf632968ab19c539a69081f963ce5398) | 2026-10-06 16:18:31 | 1 | +1 / −0 | Initial commit |
| 2 | [`35f55fa`](https://github.com/recepcanta35-gif/Cari/commit/35f55facd54828bbfacb5955be92ba4876fb62c7) | 2026-10-09 11:22:07 | 39 | +920 / −1 | ERPNext v15 kurulum tamamlandı + analiz raporları + custom app iskeletleri |
| 3 | [`568a882`](https://github.com/recepcanta35-gif/Cari/commit/568a882f800407fbaf50bd9f78a1bf3726f4f8f5) | 2026-10-09 11:50:14 | 7 | +334 / −4 | Faz 1 tamam: Turkiye temel yapilandirmasi (sirket, KDV, tanimlar, roller, hatirlatma) |
| 4 | [`4d36555`](https://github.com/recepcanta35-gif/Cari/commit/4d365552640f0acb13cdbd1990bcaf7f9b6b8b90) | 2026-10-09 14:08:03 | 19 | +3021 / −91 | Complete Faz 1.5 demo and end-to-end acceptance |
| 5 | [`fb51db1`](https://github.com/recepcanta35-gif/Cari/commit/fb51db144ebe6ebd17e35a4993c2f6e835a2d742) | 2026-10-09 15:47:15 | 39 | +2972 / −69 | Plan turnkey delivery and implement scoped users and field operations |
| 6 | [`be2955b`](https://github.com/recepcanta35-gif/Cari/commit/be2955b638c850c4575632c5dcb89e3c3fd24224) | 2026-10-09 15:55:37 | 4 | +36 / −0 | Add child controllers and inspectable CI failure diagnostics |
| 7 | [`11c606a`](https://github.com/recepcanta35-gif/Cari/commit/11c606a60477779993788eb827ee7678f58c9a22) | 2026-10-09 16:01:24 | 6 | +27 / −0 | Preserve Frappe controller exports and validate schema bindings |
| 8 | [`8e5810f`](https://github.com/recepcanta35-gif/Cari/commit/8e5810fc4d24a07fb5c641cff4c50bdbb91530fa) | 2026-10-09 16:08:21 | 28 | +1273 / −3 | Add business operations and supported deployment scaffold |
| 9 | [`6214ef4`](https://github.com/recepcanta35-gif/Cari/commit/6214ef439808acbaf56c6c4038627ace69836ca4) | 2026-10-09 16:13:16 | 5 | +269 / −2 | Prevent shared-document scope bypass and add guarded portal services |
| 10 | [`7391799`](https://github.com/recepcanta35-gif/Cari/commit/73917997c0f912beda0437c4a5d69dbfa6f49fa6) | 2026-10-09 16:22:00 | 15 | +518 / −1 | Add portal UI, scoped reminders and delivery acceptance cases |
| 11 | [`41e4a1b`](https://github.com/recepcanta35-gif/Cari/commit/41e4a1bfa71d1104d8f5895cbb4bad2b5e2c3095) | 2026-10-09 16:23:03 | 2 | +6 / −0 | Initialize the request-equivalent scope guard in CLI acceptance tests |
| 12 | [`c6f17bf`](https://github.com/recepcanta35-gif/Cari/commit/c6f17bf9b777327fc6b76542f542ce80992dfa2f) | 2026-10-09 16:29:59 | 4 | +22 / −0 | Give portal the minimum product permissions required by core pricing |
| 13 | [`071ca93`](https://github.com/recepcanta35-gif/Cari/commit/071ca93254daf2c6dd82fd89bfce74ae93a2771c) | 2026-10-09 16:35:39 | 4 | +12 / −0 | Allow scoped receivable selection without account read access |
| 14 | [`acee276`](https://github.com/recepcanta35-gif/Cari/commit/acee27665627626a26ba7c8ac50db49b8663f240) | 2026-10-09 16:41:49 | 7 | +385 / −1 | Record approved delivery program, passing MariaDB evidence and deployment boundaries |
| 15 | [`c240f4d`](https://github.com/recepcanta35-gif/Cari/commit/c240f4dd28842a532ea8322f68cb93c15bb556f9) | 2026-10-09 21:51:33 | 3 | +51 / −0 | Record production dependency statuses without secrets or false signoff |
| 16 | [`dc9f35e`](https://github.com/recepcanta35-gif/Cari/commit/dc9f35ed855ae3d56e39f2976a33cdb981f0ee28) | 2026-10-09 21:59:13 | 3 | +60 / −2 | Record FTP-only hosting evidence and preserve existing site |
| 17 | [`88f594a`](https://github.com/recepcanta35-gif/Cari/commit/88f594a301a5fc7355d925345a7c36507f64571b) | 2026-10-09 22:05:43 | 6 | +48 / −6 | Confirm PHP cloud with SSH and block incompatible Docker deployment |
| 18 | [`5abb517`](https://github.com/recepcanta35-gif/Cari/commit/5abb5171a65877a463dc397cb2d159025b9c654a) | 2026-10-09 22:12:50 | 2 | +37 / −0 | Add read-only hosting runtime inventory without secrets or changes |
| 19 | [`d544105`](https://github.com/recepcanta35-gif/Cari/commit/d544105ea3779c6af6b2ce76a495a8e3744e8833) | 2026-10-09 22:21:43 | 3 | +27 / −4 | Record reported ERP subdomain without claiming remote access or installation |
| 20 | [`5bc4e00`](https://github.com/recepcanta35-gif/Cari/commit/5bc4e0007f6e8ee69e103ac588b0c66780648be0) | 2026-10-09 22:31:47 | 2 | +22 / −2 | Record actual read-only transport checks without authentication |
| 21 | [`6144162`](https://github.com/recepcanta35-gif/Cari/commit/614416291e1ae27dd79fd9fdab408ed2714b722e) | 2026-10-09 22:42:25 | 3 | +73 / −0 | Assess PHP cloud replatforming while preserving ERP scope and decision gates |

## 3. Her commit’in anlamı ve düzenlenen dosyalar

### 01. `8cc37ee` — Initial commit

Başlangıç; README dışında kaynak yok.

| Dosya | Eklenen | Silinen |
|---|---:|---:|
| `README.md` | 1 | 0 |

### 02. `35f55fa` — ERPNext v15 kurulum tamamlandı + analiz raporları + custom app iskeletleri

Şartname/kapsam ve çözüm kıyası, ERPNext v15 sandbox raporu, iki Frappe app iskeleti; sandbox kurulumu kaynak arşivi değildir.

| Dosya | Eklenen | Silinen |
|---|---:|---:|
| `.gitignore` | 18 | 0 |
| `README.md` | 43 | 1 |
| `apps/cari_custom/README.md` | 9 | 0 |
| `apps/cari_custom/cari_custom/__init__.py` | 1 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/__init__.py` | 0 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/__init__.py` | 0 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/daily_assignment/__init__.py` | 0 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/daily_assignment/daily_assignment.json` | 31 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/daily_assignment/daily_assignment.py` | 13 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/stock_assignment/__init__.py` | 0 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/stock_assignment/stock_assignment.json` | 31 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/stock_assignment/stock_assignment.py` | 14 | 0 |
| `apps/cari_custom/cari_custom/fixtures/custom_fields.json` | 20 | 0 |
| `apps/cari_custom/cari_custom/hooks.py` | 17 | 0 |
| `apps/cari_custom/cari_custom/modules.txt` | 1 | 0 |
| `apps/cari_custom/cari_custom/patches.txt` | 0 | 0 |
| `apps/cari_custom/pyproject.toml` | 17 | 0 |
| `apps/uyumsoft_integration/README.md` | 12 | 0 |
| `apps/uyumsoft_integration/pyproject.toml` | 17 | 0 |
| `apps/uyumsoft_integration/uyumsoft_integration/__init__.py` | 1 | 0 |
| `apps/uyumsoft_integration/uyumsoft_integration/hooks.py` | 23 | 0 |
| `apps/uyumsoft_integration/uyumsoft_integration/modules.txt` | 1 | 0 |
| `apps/uyumsoft_integration/uyumsoft_integration/patches.txt` | 0 | 0 |
| `apps/uyumsoft_integration/uyumsoft_integration/uyumsoft/__init__.py` | 0 | 0 |
| `apps/uyumsoft_integration/uyumsoft_integration/uyumsoft/connector.py` | 25 | 0 |
| `apps/uyumsoft_integration/uyumsoft_integration/uyumsoft/sync.py` | 51 | 0 |
| `apps/uyumsoft_integration/uyumsoft_integration/uyumsoft/ubltr.py` | 15 | 0 |
| `apps/uyumsoft_integration/uyumsoft_integration/uyumsoft_integration/__init__.py` | 0 | 0 |
| `apps/uyumsoft_integration/uyumsoft_integration/uyumsoft_integration/doctype/__init__.py` | 0 | 0 |
| `apps/uyumsoft_integration/uyumsoft_integration/uyumsoft_integration/doctype/uyumsoft_settings/__init__.py` | 0 | 0 |
| `apps/uyumsoft_integration/uyumsoft_integration/uyumsoft_integration/doctype/uyumsoft_settings/uyumsoft_settings.json` | 31 | 0 |
| `apps/uyumsoft_integration/uyumsoft_integration/uyumsoft_integration/doctype/uyumsoft_settings/uyumsoft_settings.py` | 12 | 0 |
| `apps/uyumsoft_integration/uyumsoft_integration/uyumsoft_integration/doctype/uyumsoft_transfer_log/__init__.py` | 0 | 0 |
| `apps/uyumsoft_integration/uyumsoft_integration/uyumsoft_integration/doctype/uyumsoft_transfer_log/uyumsoft_transfer_log.json` | 29 | 0 |
| `apps/uyumsoft_integration/uyumsoft_integration/uyumsoft_integration/doctype/uyumsoft_transfer_log/uyumsoft_transfer_log.py` | 5 | 0 |
| `docs/cozum-secenekleri-karsilastirmasi.md` | 113 | 0 |
| `docs/erpnext-hazir-cozum-degerlendirmesi.md` | 104 | 0 |
| `docs/erpnext-kurulum-rehberi.md` | 112 | 0 |
| `docs/kapsam-analizi.md` | 154 | 0 |

### 03. `568a882` — Faz 1 tamam: Turkiye temel yapilandirmasi (sirket, KDV, tanimlar, roller, hatirlatma)

Türkiye demo şirketi/TRY/KDV ve master data bootstrap; field/autoname/dil/locale hataları ve rol/Notification uyumu.

| Dosya | Eklenen | Silinen |
|---|---:|---:|
| `README.md` | 6 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/daily_assignment/daily_assignment.json` | 1 | 1 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/stock_assignment/stock_assignment.json` | 1 | 1 |
| `apps/cari_custom/cari_custom/setup_turkey.py` | 313 | 0 |
| `apps/uyumsoft_integration/uyumsoft_integration/uyumsoft_integration/doctype/uyumsoft_settings/uyumsoft_settings.json` | 1 | 1 |
| `apps/uyumsoft_integration/uyumsoft_integration/uyumsoft_integration/doctype/uyumsoft_transfer_log/uyumsoft_transfer_log.json` | 1 | 1 |
| `docs/erpnext-kurulum-rehberi.md` | 11 | 0 |

### 04. `4d36555` — Complete Faz 1.5 demo and end-to-end acceptance

Gerçek PR/transfer/teklif/SO/DN/SI/PE demo, manifest/idempotency, GL/SLE/Bin/PLE kontrolü ve 13 DB regresyonu; PG dar adaptörler.

| Dosya | Eklenen | Silinen |
|---|---:|---:|
| `README.md` | 19 | 1 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/daily_assignment/daily_assignment.json` | 97 | 13 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/daily_assignment/daily_assignment.py` | 8 | 6 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/stock_assignment/stock_assignment.json` | 109 | 13 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/stock_assignment/stock_assignment.py` | 8 | 5 |
| `apps/cari_custom/cari_custom/compat_patches.py` | 86 | 0 |
| `apps/cari_custom/cari_custom/hooks.py` | 6 | 1 |
| `apps/cari_custom/cari_custom/postgres_queries.py` | 458 | 0 |
| `apps/cari_custom/cari_custom/sample_data.py` | 517 | 0 |
| `apps/cari_custom/cari_custom/sample_validation.py` | 292 | 0 |
| `apps/cari_custom/cari_custom/setup_turkey.py` | 84 | 50 |
| `apps/cari_custom/cari_custom/tests/__init__.py` | 0 | 0 |
| `apps/cari_custom/cari_custom/tests/test_faz15.py` | 320 | 0 |
| `apps/cari_custom/license.txt` | 674 | 0 |
| `apps/cari_custom/pyproject.toml` | 11 | 0 |
| `docs/erpnext-kapsam-mimari-kurumsal-uygunluk.md` | 97 | 0 |
| `docs/erpnext-kurulum-rehberi.md` | 19 | 2 |
| `docs/faz-1-5-test-sonuclari.md` | 166 | 0 |
| `scripts/run_faz15_tests.py` | 50 | 0 |

### 05. `fb51db1` — Plan turnkey delivery and implement scoped users and field operations

T0–T9/18 modül teslim planı; 9 persona scope/onboarding/audit, field operasyon otomasyonu, miktar API/dashboard, MariaDB CI.

| Dosya | Eklenen | Silinen |
|---|---:|---:|
| `.github/workflows/cari-ci.yml` | 101 | 0 |
| `apps/cari_custom/cari_custom/bootstrap.py` | 342 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/cari_scope_customer/__init__.py` | 0 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/cari_scope_customer/cari_scope_customer.json` | 30 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/cari_scope_warehouse/__init__.py` | 0 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/cari_scope_warehouse/cari_scope_warehouse.json` | 30 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/cari_security_event/__init__.py` | 0 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/cari_security_event/cari_security_event.json` | 67 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/cari_security_event/cari_security_event.py` | 11 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/cari_settings/__init__.py` | 0 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/cari_settings/cari_settings.json` | 120 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/cari_settings/cari_settings.py` | 0 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/cari_user_scope/__init__.py` | 0 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/cari_user_scope/cari_user_scope.json` | 89 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/cari_user_scope/cari_user_scope.py` | 0 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/daily_assignment/daily_assignment.json` | 66 | 15 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/daily_assignment/daily_assignment.py` | 0 | 15 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/stock_assignment/stock_assignment.json` | 89 | 17 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/stock_assignment/stock_assignment.py` | 0 | 17 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/stock_assignment_return/__init__.py` | 0 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/stock_assignment_return/stock_assignment_return.json` | 121 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/stock_assignment_return/stock_assignment_return.py` | 0 | 0 |
| `apps/cari_custom/cari_custom/delivery.py` | 76 | 0 |
| `apps/cari_custom/cari_custom/field_operations.py` | 443 | 0 |
| `apps/cari_custom/cari_custom/hooks.py` | 52 | 3 |
| `apps/cari_custom/cari_custom/permission_queries.py` | 109 | 0 |
| `apps/cari_custom/cari_custom/rules.py` | 150 | 0 |
| `apps/cari_custom/cari_custom/sample_data.py` | 10 | 0 |
| `apps/cari_custom/cari_custom/security.py` | 442 | 0 |
| `apps/cari_custom/cari_custom/setup_turkey.py` | 6 | 0 |
| `apps/cari_custom/cari_custom/tests/test_delivery.py` | 249 | 0 |
| `apps/cari_custom/cari_custom/user_management.py` | 140 | 0 |
| `apps/cari_custom/pyproject.toml` | 1 | 1 |
| `apps/uyumsoft_integration/pyproject.toml` | 1 | 1 |
| `docs/anahtar-teslim-plani.md` | 87 | 0 |
| `pytest.ini` | 3 | 0 |
| `scripts/run_delivery_tests.py` | 47 | 0 |
| `tests/conftest.py` | 6 | 0 |
| `tests/unit/test_rules.py` | 84 | 0 |

### 06. `be2955b` — Add child controllers and inspectable CI failure diagnostics

Eksik child DocType controller export ve CI failure annotation; bu ara durum son kabul değildir.

| Dosya | Eklenen | Silinen |
|---|---:|---:|
| `.github/workflows/cari-ci.yml` | 8 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/cari_scope_customer/cari_scope_customer.py` | 5 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/cari_scope_warehouse/cari_scope_warehouse.py` | 5 | 0 |
| `scripts/ci_annotation.py` | 18 | 0 |

### 07. `11c606a` — Preserve Frappe controller exports and validate schema bindings

Ruff F401 nedeniyle silinen controller imports: explicit alias re-export ve şema/controller AST binding testi.

| Dosya | Eklenen | Silinen |
|---|---:|---:|
| `apps/cari_custom/cari_custom/cari_custom/doctype/cari_settings/cari_settings.py` | 1 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/cari_user_scope/cari_user_scope.py` | 1 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/daily_assignment/daily_assignment.py` | 1 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/stock_assignment/stock_assignment.py` | 1 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/stock_assignment_return/stock_assignment_return.py` | 1 | 0 |
| `tests/unit/test_schema.py` | 22 | 0 |

### 08. `8e5810f` — Add business operations and supported deployment scaffold

Çek/senet, sevkiyat ve servis controller'ları; submit-sonrası guards; desteklenen sunucu için aday Docker/backup/TLS; her iki DB kronolojik SLE düzeltmesi.

| Dosya | Eklenen | Silinen |
|---|---:|---:|
| `.dockerignore` | 15 | 0 |
| `.gitignore` | 9 | 0 |
| `apps/cari_custom/cari_custom/api.py` | 154 | 0 |
| `apps/cari_custom/cari_custom/business_operations.py` | 316 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/cari_instrument_reference/__init__.py` | 0 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/cari_instrument_reference/cari_instrument_reference.json` | 28 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/cari_instrument_reference/cari_instrument_reference.py` | 5 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/cari_payment_instrument/__init__.py` | 0 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/cari_payment_instrument/cari_payment_instrument.json` | 169 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/cari_payment_instrument/cari_payment_instrument.py` | 1 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/cari_service_record/__init__.py` | 0 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/cari_service_record/cari_service_record.json` | 144 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/cari_service_record/cari_service_record.py` | 1 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/cari_shipment/__init__.py` | 0 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/cari_shipment/cari_shipment.json` | 145 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/cari_shipment/cari_shipment.py` | 1 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/page/cari_merkez/__init__.py` | 0 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/page/cari_merkez/cari_merkez.js` | 62 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/page/cari_merkez/cari_merkez.json` | 10 | 0 |
| `apps/cari_custom/cari_custom/compat_patches.py` | 8 | 3 |
| `apps/cari_custom/cari_custom/field_operations.py` | 11 | 0 |
| `apps/cari_custom/cari_custom/hooks.py` | 2 | 0 |
| `apps/cari_custom/cari_custom/public/js/operations.js` | 27 | 0 |
| `deploy/.env.example` | 13 | 0 |
| `deploy/Caddyfile` | 12 | 0 |
| `deploy/Dockerfile` | 14 | 0 |
| `deploy/compose.yml` | 122 | 0 |
| `deploy/mariadb.cnf` | 4 | 0 |

### 09. `6214ef4` — Prevent shared-document scope bypass and add guarded portal services

Frappe DocShare OR scope bypass: dış AND list guard + direct doc guard; portal server-price/idempotency ve cost redaction.

| Dosya | Eklenen | Silinen |
|---|---:|---:|
| `apps/cari_custom/cari_custom/bootstrap.py` | 3 | 0 |
| `apps/cari_custom/cari_custom/hooks.py` | 2 | 0 |
| `apps/cari_custom/cari_custom/portal.py` | 227 | 0 |
| `apps/cari_custom/cari_custom/security.py` | 35 | 0 |
| `scripts/ci_annotation.py` | 2 | 2 |

### 10. `7391799` — Add portal UI, scoped reminders and delivery acceptance cases

Portal WWW/JS sepet, scope/dedup vade-görev reminder ve ticari/saha DB kabul testleri.

| Dosya | Eklenen | Silinen |
|---|---:|---:|
| `apps/cari_custom/cari_custom/bootstrap.py` | 2 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/cari_reminder_log/__init__.py` | 0 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/cari_reminder_log/cari_reminder_log.json` | 62 | 0 |
| `apps/cari_custom/cari_custom/cari_custom/doctype/cari_reminder_log/cari_reminder_log.py` | 5 | 0 |
| `apps/cari_custom/cari_custom/hooks.py` | 6 | 1 |
| `apps/cari_custom/cari_custom/notifications.py` | 91 | 0 |
| `apps/cari_custom/cari_custom/public/js/portal.js` | 54 | 0 |
| `apps/cari_custom/cari_custom/tests/test_business.py` | 117 | 0 |
| `apps/cari_custom/cari_custom/www/cari-portal.html` | 15 | 0 |
| `apps/cari_custom/cari_custom/www/cari-portal.py` | 3 | 0 |
| `deploy/backup.sh` | 9 | 0 |
| `deploy/create-site.sh` | 27 | 0 |
| `scripts/deployment_preflight.py` | 85 | 0 |
| `scripts/run_delivery_tests.py` | 3 | 0 |
| `tests/unit/test_deployment.py` | 39 | 0 |

### 11. `41e4a1b` — Initialize the request-equivalent scope guard in CLI acceptance tests

CLI regresyon runner'ında HTTP request eşdeğeri scope query guard başlatma.

| Dosya | Eklenen | Silinen |
|---|---:|---:|
| `apps/cari_custom/cari_custom/tests/test_delivery.py` | 3 | 0 |
| `scripts/run_delivery_tests.py` | 3 | 0 |

### 12. `c6f17bf` — Give portal the minimum product permissions required by core pricing

Portal core fiyatlaması için minimum ürün okuma izinleri; maliyet/supplier/defaults koruması sürer.

| Dosya | Eklenen | Silinen |
|---|---:|---:|
| `apps/cari_custom/cari_custom/bootstrap.py` | 13 | 0 |
| `apps/cari_custom/cari_custom/hooks.py` | 1 | 0 |
| `apps/cari_custom/cari_custom/permission_queries.py` | 4 | 0 |
| `apps/cari_custom/cari_custom/security.py` | 4 | 0 |

### 13. `071ca93` — Allow scoped receivable selection without account read access

Portal/saha için kapsamlı receivable Account SELECT; geniş account read/GL erişimi verilmez. MariaDB CI başarılı hale geldi.

| Dosya | Eklenen | Silinen |
|---|---:|---:|
| `apps/cari_custom/cari_custom/bootstrap.py` | 2 | 0 |
| `apps/cari_custom/cari_custom/hooks.py` | 1 | 0 |
| `apps/cari_custom/cari_custom/permission_queries.py` | 4 | 0 |
| `apps/cari_custom/cari_custom/security.py` | 5 | 0 |

### 14. `acee276` — Record approved delivery program, passing MariaDB evidence and deployment boundaries

Başarılı MariaDB evidence, kullanıcı bütün faz onayı, lisans ve Docker/hosting son kabul sınırları kaydedildi.

| Dosya | Eklenen | Silinen |
|---|---:|---:|
| `README.md` | 12 | 1 |
| `apps/uyumsoft_integration/license.txt` | 21 | 0 |
| `apps/uyumsoft_integration/pyproject.toml` | 1 | 0 |
| `docs/anahtar-teslim-plani.md` | 13 | 0 |
| `docs/lisans-envanteri.md` | 22 | 0 |
| `docs/teslim-durumu.json` | 233 | 0 |
| `docs/uretim-isletim-kilavuzu.md` | 83 | 0 |

### 15. `c240f4d` — Record production dependency statuses without secrets or false signoff

Şirket/muhasebe daha sonra, SMTP hazır bildirimi, Uyumsoft API/ürün-sürüm eksikleri; secret-free production intake.

| Dosya | Eklenen | Silinen |
|---|---:|---:|
| `deploy/production-inputs.example.json` | 35 | 0 |
| `docs/anahtar-teslim-plani.md` | 10 | 0 |
| `docs/teslim-durumu.json` | 6 | 0 |

### 16. `dc9f35e` — Record FTP-only hosting evidence and preserve existing site

FTP hosting görüntüsü ve mevcut WordPress/dizinlerin korunması; erişim veya upload yapılmadı.

| Dosya | Eklenen | Silinen |
|---|---:|---:|
| `deploy/production-inputs.example.json` | 7 | 1 |
| `docs/hosting-uygunluk-kontrolu.md` | 39 | 0 |
| `docs/teslim-durumu.json` | 14 | 1 |

### 17. `88f594a` — Confirm PHP cloud with SSH and block incompatible Docker deployment

Kullanıcı düzeltmesi: VPS değil PHP/MySQL cloud + SSH. Uygunsuz Docker deployment preflight reddi eklendi.

| Dosya | Eklenen | Silinen |
|---|---:|---:|
| `deploy/.env.example` | 2 | 0 |
| `deploy/production-inputs.example.json` | 4 | 3 |
| `docs/hosting-uygunluk-kontrolu.md` | 15 | 0 |
| `docs/teslim-durumu.json` | 8 | 3 |
| `scripts/deployment_preflight.py` | 5 | 0 |
| `tests/unit/test_deployment.py` | 14 | 0 |

### 18. `5abb517` — Add read-only hosting runtime inventory without secrets or changes

Operatörün çalıştıracağı read-only runtime probe; sır veya site/servis konfigürasyonu değişikliği yok.

| Dosya | Eklenen | Silinen |
|---|---:|---:|
| `deploy/runtime-probe.sh` | 30 | 0 |
| `docs/hosting-uygunluk-kontrolu.md` | 7 | 0 |

### 19. `d544105` — Record reported ERP subdomain without claiming remote access or installation

Kullanıcının açtığı nexterp subdomain ve folder kaydı; DNS/TLS/DB oluşturma veya kurulum kanıtı değildir.

| Dosya | Eklenen | Silinen |
|---|---:|---:|
| `deploy/production-inputs.example.json` | 7 | 3 |
| `docs/hosting-uygunluk-kontrolu.md` | 9 | 0 |
| `docs/teslim-durumu.json` | 11 | 1 |

### 20. `5bc4e00` — Record actual read-only transport checks without authentication

Gerçek salt-okunur TCP/HEAD kontrolleri: greeting/HTTP/TLS EOF; kimlik doğrulama veya parola gönderimi olmadı.

| Dosya | Eklenen | Silinen |
|---|---:|---:|
| `docs/hosting-uygunluk-kontrolu.md` | 12 | 0 |
| `docs/teslim-durumu.json` | 10 | 2 |

### 21. `6144162` — Assess PHP cloud replatforming while preserving ERP scope and decision gates

PHP cloud uyumu/Dolibarr feasibility belgesi; replatform uygulanmadı. Son kullanıcı tercihi local Python; güncel karar devir commit'indedir.

| Dosya | Eklenen | Silinen |
|---|---:|---:|
| `README.md` | 4 | 0 |
| `docs/php-hosting-uyum-plani.md` | 59 | 0 |
| `docs/teslim-durumu.json` | 10 | 0 |

## 4. Local inceleme komutları

```bash
git log --reverse --date=iso-strict --format="%h %aI %s"
git diff --stat 8cc37ee8cf632968ab19c539a69081f963ce5398 614416291e1ae27dd79fd9fdab408ed2714b722e
git diff --name-status 8cc37ee8cf632968ab19c539a69081f963ce5398 614416291e1ae27dd79fd9fdab408ed2714b722e
git show 6214ef4 -- apps/cari_custom/cari_custom/security.py
git log -- apps/cari_custom/cari_custom/portal.py
```

Bundle SHA ve dalını teslim ZIP içindeki `DEVIR-METADATA.json` ile doğrulayın. Bundle clone GitHub erişimi olmadan dosya/geçmişi sağlar; upstream/vendor/runtime internet veya ayrı cache ister. GitHub kullanıcı credential/config, eski bench DB ve hosting sırları bundle içinde bulunmaz.

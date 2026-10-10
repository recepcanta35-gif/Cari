# Cari — Kapsam, Operasyon ve Local Python Devir Raporu

**Rapor tarihi:** 10 Ekim 2026

**Depo:** https://github.com/recepcanta35-gif/Cari

**Geliştirme dalı:** `arena/c5b59147-cari`

**İncelenen kod referansı:** `614416291e1ae27dd79fd9fdab408ed2714b722e`

**PR:** [#1 — OPEN](https://github.com/recepcanta35-gif/Cari/pull/1)

**Yön:** Kullanıcının son isteğiyle local **Python/Frappe/ERPNext** geliştirmesine devam; PHP geçişi yapılmadı.

> **Sonuç:** Kaynak ve testli geliştirme adayı mevcuttur; anahtar teslim/üretim kabulü tamamlanmamıştır (**NO-GO**). Eski demo sunucusunun halen çalıştığı veya Hostinger'e kurulum yapıldığı iddia edilmez. Raporda/ZIP'te kullanıcı parolası, SSH private key veya API sırrı bulunmaz.

## 1. Yönetici özeti

- İlk repo yalnız `README.md` içeren `8cc37ee` başlangıç commit'iydi.
- Şartname analiz edildi; sıfırdan geliştirme, ERPNext ve WP ERP karşılaştırıldı. Kullanıcı **ERPNext üzerine özel uygulama** seçti. WordPress/WooCommerce ERP altyapısı yapılmadı.
- 9 Ekim'de sandbox'da Frappe/ERPNext v15.122.0 + PostgreSQL/Redis demo kurulup test edildi. Sandbox kısıtları nedeniyle PostgreSQL deneysel çözüm kullanıldı; sonra resmî **MariaDB CI** doğrulaması eklendi.
- `cari_custom` ve `uyumsoft_integration` uygulamaları, Türkiye demo ayarları, güvenlik, stok/saha ve ticari özel kayıtlar, iş merkezi/portal ve teslim kapısı geliştirildi.
- İncelenen kaynakta **129 Git dosyası**, başlangıç dahil **21 commit** (20 geliştirme commit'i), **15 özel DocType** (13 Cari, 2 Uyumsoft) vardır. **Teslim kaynağı 6 yeni devir belgesiyle 135 dosyadır.** Devir commit'i incelenen kod referansının üstüne eklenir; teslim HEAD'i ZIP metadata'sı/bundle'da, bütün yollar `dosya-agaci.txt` ve envanterdedir.
- Kaynak referansı için [CI 37982049980](https://github.com/recepcanta35-gif/Cari/actions/runs/37982049980) **başarılı**; `unit` ve `mariadb` işleri ve sıfırdan site kurulumu geçti. Aynı kaynak PR CI [37982054831](https://github.com/recepcanta35-gif/Cari/actions/runs/37982054831) de başarılıdır.
- Bu rapor hazırlanırken saf Python testleri yeniden çalıştırıldı: **38/38**, Ruff başarılı. Mevcut MariaDB kabul senaryosu: **201 demo kontrolü + 13 temel + 18 ek DB regresyonu**.
- Üretim sunucusu/TLS, SMTP gerçek gönderim, PDF, bütün iş varyasyonları, tarayıcı/yük/güvenlik ve restore/UAT kabulü tamamlanmadı. Uyumsoft canlı istemci/UBL-TR eşleme henüz taslaktır.

## 2. Kapsam ve değiştirilmeyen kurallar

Amaç stok, saha satış, teklif, cari hesap, tahsilat, sevkiyat, servis ve online müşteri süreçlerini aynı web sisteminde yürütmektir. Kaynak şartname 8 Ekim 2026, sürüm 1; ana plan `docs/anahtar-teslim-plani.md`.

- **Barkod modülü yok.** Ürün adı/kodu/kategori/fotoğrafla seçim; çekirdek barkod alanları özelleştirmeyle gizlenir.
- **SMS yok.** Gönderim kanalı e-posta; SMS RPC çağrısı proje guard'ında reddedilir.
- Uyumsoft gerçek ürün/sürüm/API/sözleşme ve erişim onayı sonrası açılır; bunlar genel geliştirme onayından farklıdır.
- Online satış kapsamda; modüler mimari. Kart verisi depolama/ödeme sağlayıcısı uydurma yapılmadı.
- Onaylı finans/stok için iptal/iade/ters kayıt; form sayısını elle değiştirerek defter düzeltmesi yapılmaz.
- Rol/alan/kayıt izolasyonu yalnız UI gizlemesi değildir; list/direct ID/share/API/report/file senaryoları değerlendirilir.

## 3. 18 modülün gerçek mevcut durumu

“Core” = ayrı alınacak ERPNext çekirdeği; “özel kod” = bu repodaki Python/JS/DocType. Hiçbir satır tam üretim onayı anlamına gelmez.

| ID | Modül | Yapılmış işlem / kod | Açık son kabul |
|---|---|---|---|
| M01 | Dashboard | `api.dashboard`, miktar/finans persona ayrımı, Cari İş Merkezi | Tam finans rapor mutabakatı, filtre/yük/tarayıcı |
| M02 | Ürünler | Core Item/grup/UOM/fiyat; 4 demo ürün, 8 fiyat; maliyet alanı seviyesi | Gerçek ürün/fotoğraf/import/uzantı ve bütün yetki varyasyonları |
| M03 | Depolar ve stok | Core Warehouse/Stock Entry/SLE/Bin, satın alma girişi ve transfer | Sayım, serialized/batch, yarış, çoklu şirket ve tüm iptal/iade |
| M04 | Personel stok tahsisi | Stock Assignment → gerçek transfer; Return → kısmi/tam ters transfer; net satış/kalan hesaplama | Serialized/batch iade, paralel yarış, bütün satış iadesi varyasyonları |
| M05 | Satış/sipariş | Core teklif→SO→DN→SI; standart mapper, item zimmet bağlantısı | Kısmi sevk/fatura, iskonto/risk/kur ve gerçek iş kabulü |
| M06 | Satın alma | Core supplier/PO/PR/PI mevcut; demo PR giriş/maliyet defteri | Tam PO→PR→PI→supplier ödeme/iade kabulü henüz ayrı tamamlanmadı |
| M07 | Müşteri/cari | Core Customer/GL/Payment Ledger; TRY, vade ve scope; sıfır demo bakiye | Gerçek şirket/tax/hesap planı/risk, muhasebeci onayı |
| M08 | Tahsilat/evrak | Core PE, tam/kısmi; özel Çek/Senet alınma/bankada/tahsil ayrımı | Tüm evrak muhasebesi, farklı kur/banka, multi-tahsis/iptal/reject varyasyonları |
| M09 | Teklifler | Core Quotation, KDV ve sipariş dönüşümü testli | Gerçek PDF/e-posta ve iskonto onay kuralları |
| M10 | Araç/günlük görev | Daily Assignment; zaman çakışması, onay, start/finish, actual zamanlar | Mobil/tarayıcı, saat/dönem/çoklu kullanıcı yarış testleri |
| M11 | Sevkiyat/kargo | Cari Shipment, DN bağlantısı, firma/takip, dispatch/deliver, özel proof kontrolü | Gerçek kargo API'si yok; bütün istisna/iade/teslim kanıtı varyasyonları |
| M12 | İadeler | Core satış/alış iadesi yapı taşları; özel zimmet iade/iptal testli | Satış/alış credit note + stok/cari bütün zincirler |
| M13 | Garanti/servis | Core Warranty Claim/Serial No; özel servis başlat/tamamla, garanti tarihi kontrolleri | Serili ürün garanti gerçek veri kabulü, ücretli servis faturalaması |
| M14 | Raporlar | Miktar stock API/CSV ve kapsamlı dashboard; core finans raporları | Tüm rapor/export/print ve geniş veri mutabakatı/yük |
| M15 | E-posta | Scope'lu vade/görev reminder, dedup log; eski global-role reminder kapatıldı | SMTP gerçek gönderim; kritik stok/garanti bildirimleri ve hata teslim takibi tamam değil |
| M16 | Kullanıcı/yetki | 9 profil, User Scope, pasif oluştur/davet/deactivate, sessions clear, append-only audit, cost seviyeleri | Tam HTTP/tarayıcı/print/file bypass matrisi, MFA/operasyon güvenlik ve çoklu şirket UAT |
| M17 | Uyumsoft | Settings/Transfer Log/event kuyruğu; inactive guard | **Connector send/test ve UBL-TR `NotImplementedError`; canlı protokol geliştirilmedi** |
| M18 | Online/portal | WWW katalog/sepet, server price, UUID idempotency, own records, draft order | Gerçek tarayıcı/HTTPS/kargo adresi/ödeme sağlayıcısı; tam IDOR/dosya/katalog fiyat varyasyonları |

## 4. Bugüne kadarki operasyon çizelgesi

### 4.1 Analiz ve karar

Kapsam/bağımlılık/veri modeli/faz planı, ERPNext gap ve Türkiye/Uyumsoft değerlendirmesi, WP ERP ve sıfırdan çözüm kıyası oluşturuldu. ERPNext + özel app kararı alındı. Lisans çalışması: ERPNext GPL-3.0, Frappe MIT; `cari_custom` GPL-3.0, Uyumsoft özgün iskeleti MIT metniyle işaretli. Tam üçüncü taraf SBOM/dağıtım hukukî kabulü son kapıda açıktır.

### 4.2 Sandbox kurulumu (tarihî, 9 Ekim)

Bench 5.31, Python 3.11, Node 22/Yarn 1.22.22, Frappe/ERPNext v15.122.0 kuruldu. Apt/ağ kısıtı nedeniyle PG 16.2 ve derlenen Redis 7.2 kullanıldı. Site `cari.local`, dört app kurulumu, migrate ve login/preview-host HTTP kontrolleri yapıldı. Yarn registry/TLS/cron/psql/Redis/file-fixture/hook-path sorunları giderildi.

**Bu çalışma ortamı artık kaynak deposudur; eski bench, env, PostgreSQL data ve çalışan web süreçleri mevcut değildir.** Buradan `.venv` veya DB dump aktarılmış sayılmaz. PostgreSQL özel workaround'ları normal local kurulum önerisi değildir.

### 4.3 Türkiye demo ayarları

Cari A.Ş./CARI/Turkey/TRY, generic 82 hesaplık plan, KDV %1/%10/%20 satış/alış/item tax şablonları, birimler/gruplar/Türkiye+bölgeler, peşin/30/60 gün vade, ödeme yöntemleri, banka/saha deposu kuruldu. Dil `tr`, timezone `Europe/Istanbul`; yanlış INR default düzeltildi. Tekdüzen hesap planı ve ayrı alış-satış KDV hesabı gerçek muhasebe onayı **değil**.

### 4.4 Demo iş akışı

4 üründen 50'şer stok girişi; 10 mouse merkez→saha. 5 mouse × 250 + 10 USB kablo × 55 = **1.800 TL net**, **360 TL KDV**, **2.160 TL** fatura ve havale tahsilatı. Açık bakiye **0 TL**. Son stock: mouse merkez **35**, saha **10**; kablo **40**, monitör ve klavye **50'şer**. GL borç/alacak, Payment Ledger, Invoice outstanding, SLE/Bin karşılaştırıldı. Tekrar seed mükerrer belge/hareket üretmedi.

### 4.5 Genişletilmiş uygulama ve güvenlik

Gerçek zimmet onay/transfer/return/cancel, linked stock cancel guard, satış tüketimi; görev personel/araç çakışması ve whitelist edilmiş durum geçişleri; çek/senet gerçek tahsilat, sevkiyat ve servis lifecycle'ları eklendi. Role Profile/Custom DocPerm/Property Setter/custom field bootstrap; company/customer/warehouse/employee scope, controller guard ve scope'lu query/export/redaction geliştirildi. İş merkezi, portal, reminder ve NO-GO gate eklendi.

### 4.6 Hata düzeltmeleri (önemli local notları)

- Prompt autoname/root grup/Price List/Fiscal Year/field adları; `Email Alert` yerine v15 `Notification`.
- KDV şablonu title'a şirket suffix'ini iki kez ekleme ve idempotent lookup; legacy belgeler silinmedi.
- Role `add_permission` mevcut create/write'ı değiştirmediğinden property update; custom izinlerde System Manager erişimi.
- Sayısal `money_in_words` fallback kaldırıldı; asıl hata boş locale'dı.
- Broad `get_all/get_list` monkeypatch kaldırıldı; **9 SQL adaptörü PG-only**, kronolojik SLE tie-breaker v15 her iki DB'de. Genel query fonksiyonları değiştirilmez.
- Controller import'unu Ruff sildi; explicit class re-export + şema/controller AST testi eklendi.
- Frappe DocShare OR'unun scope aşması yakalandı; query dış AND guard ve direct-doc kapsam hatası eklendi. CLI runner da request eşdeğeri guard'ı kurar.
- Submit sonrası değişiklikler `before_update_after_submit` ve sunucu transition context ile sınırlandı.
- Portal core pricing Item ve receivable account selection bekliyordu; minimal Item read (cost/supplier/defaults korumalı) ve scope'lu **select-only** receivable eklendi; account read/GL hakkı verilmedi.
- CI log servisi ağ kapsamı dışındaydı; secret-redacted diagnostics Checks annotation üzerinden okunabilir yapıldı.

### 4.7 GitHub / CI

Pinned v15.122.0/Python3.11/Node22/MariaDB10.6 ve Redis ile taze site kuran GitHub Actions geliştirildi. İlk başarısız CI'ler controller binding, guard init ve portal izin eksiklerini gösterdi; düzeltildi, sonraki CI'ler başarılı. Push ve PR işleri ayrı evidence üretir; eski başarılı çalışma bütün son iş kapsamının kabulü değildir.

### 4.8 Hosting çalışması

Kullanıcı PHP/MySQL Hostinger cloud hosting (VPS değil), aktif SSH/FTP, `public_html/nexterp`, `nexterp.skysoftteknoloji.com.tr` ve DB oluşturma görüntülerini sağladı. Default PHP dosyası görülmüş, içeriği okunmamıştır. DB formu successful DB creation kanıtı değildir. **Kimlik doğrulama, dosya upload, DNS değişikliği veya DB/site değişikliği yapılmadı.**

Son read-only network check: SSH/FTP TCP kabulü sonrası greeting gelmeden kapanma; ERP HTTP `RemoteDisconnected`; phpMyAdmin TLS EOF. Parola gönderilmedi. Bu sonuç “yanlış parola/SSH kapalı” anlamına gelmez; kapanma nedeni kesinleşmedi. Paylaşılan parolalar rapora/Git'e alınmaz, değiştirilmesi önerilir.

PHP uyumu için Dolibarr veya özel PHP alternatif analizi dokümanı hazırlandı, **kod migration yapılmadı**. Son istek local Python olduğu için PHP seçeneği ertelendi; tarihi değerlendirme korunur.

## 5. Dosyalar ve ana iş mantığı

Tam, her dosyayı içeren ağaç: [dosya-agaci.txt](dosya-agaci.txt). Fonksiyon/şema/route ve göreviyle envanter: [dosya-envanteri.tsv](dosya-envanteri.tsv). GitHub commit bazlı düzenleme dökümü: [git-commit-dokumu.md](git-commit-dokumu.md), [değişen dosyalar](degisen-dosyalar.tsv).

| Dizin / dosya | Görev |
|---|---|
| `apps/cari_custom/cari_custom/bootstrap.py` | DB custom field/property/role/profile/izin kurulum ve migrate bootstrap |
| `security.py`, `permission_queries.py`, `user_management.py` | Kapsam/read/list/share/RPC, audit ve kullanıcı yaşam döngüsü |
| `rules.py` | Frappe'den bağımsız Decimal miktar, bakiye, transition, aralık ve redaction |
| `field_operations.py` | StockAssignment/Return ve DailyAssignment gerçek uygulama |
| `business_operations.py` | Çek/senet, shipment, service controller'ları |
| `api.py` | Kapsamlı dashboard, stok miktarı CSV, managed users |
| `portal.py`, `www/`, `public/js/`, `page/cari_merkez/` | Katalog/sepet/own records ve ERP iş merkezi/form aksiyonları |
| `setup_turkey.py`, `sample_data.py`, `sample_validation.py` | Demo ülke bootstrap, idempotent örnek veri, 201 kontrol |
| `compat_patches.py`, `postgres_queries.py` | v15 uyumluluk ve stok zaman sıralama adaptörleri |
| `notifications.py` | Scope/dedup SMTP reminder kuyruğu; teslim edilmiş anlamına gelmez |
| `delivery.py`, `Cari Settings`, `docs/teslim-durumu.json` | Üretim kabul kapısı **NO-GO**, gerçek proof şartları |
| `cari_custom/cari_custom/doctype/*` | JSON schema, controller export ve child DocType'lar |
| `apps/uyumsoft_integration/.../uyumsoft/*` | **Taslak** connector/UBL, event enqueue ve processing iskeleti |
| `.github/workflows/cari-ci.yml` | Unit + gerçek MariaDB/bench CI |
| `tests/unit/` | Çerçevesiz iş kuralı, schema, deploy config testleri |
| `apps/cari_custom/.../tests/` | Bağlı site üzerinde gerçek DB kabul testleri |
| `scripts/run_*tests.py` | Bench env/role/guard/rollback ve evidence runner'ları |
| `deploy/` | Üretim adayı Docker/TLS/backup/init/preflight; read-only hosting probe |
| `docs/` | Analiz, plan, kanıt, kısıt ve devir dokümanları |

`apps/cari_custom/cari_custom/cari_custom/` tekrarları hata değildir: app kaynak kökü → Python package → Frappe module. Controller küçük import dosyası, asıl class başka Python modülünde olabilir.

## 6. Local'e alma — hızlı başlangıç

```bash
git clone --branch arena/c5b59147-cari --single-branch https://github.com/recepcanta35-gif/Cari.git Cari
cd Cari
python3 -m venv .venv
.venv/bin/python -m pip install pytest pyyaml ruff
.venv/bin/python -m pytest -q
```

Windows komutları ve tam ERP/WSL/MariaDB/Redis/site/IDE/seed kabul adımları [Local Python kurulum kılavuzunda](local-python-kurulum.md). **Kaynağı clone etmek web uygulamasını çalıştırmaz.** Full development için ayrı bench kurulmalıdır.

Önerilen yerel düzen:

```text
~/projects/Cari/                         BU REPO / editlenen özel kod
~/cari-bench/
  apps/frappe/                          bench ile alınan pinned çekirdek
  apps/erpnext/                         bench ile alınan pinned çekirdek
  apps/cari_custom -> ~/projects/Cari/apps/cari_custom
  apps/uyumsoft_integration -> ~/projects/Cari/apps/uyumsoft_integration
  env/                                  bench Python interpreter
  sites/cari.local/                      yerelde yeniden oluşturulan site/DB config
  logs/                                 yalnız yerel evidence/log
```

Native Windows venv yalnız saf testler için; full Frappe için WSL2/Linux. Local'de VPS satın alma şartı yoktur. IDE'de full ERP yorumlayıcısı `~/cari-bench/env/bin/python` olmalıdır.

## 7. Arşiv kapsamı ve veri devri

Kaynak ZIP'i Git'teki proje dosyaları, devir raporları, dosya listeleri ve yardımcı metadata içerir; .git yerine ayrıca güvenli offline Git bundle hazırlanır. Bundle hiçbir `.git/config`/GitHub credential içermez. Kaynak ve geçmiş farklı teslim öğeleridir.

**Dahil olmayanlar:** eski bench/vendor kurulumları, env/node_modules, PostgreSQL/MariaDB data, Redis state, site_config/encryption_key, gerçek DB/backup, uploaded customer files, hostingin WordPress/diğer klasörleri, FTP/SSH/phpMyAdmin/SMTP/API/GitHub sırları. Bunlar kayıp veri varmış gibi uydurulmaz. İstenirse gerçek verilere ayrıca yetkili güvenli backup/restore gerekir.

Frappe/ERPNext çekirdek kodu bu repoya vendored olarak eklenmedi. Full local bench komutları aynı tag'leri GitHub'dan indirir; lisans metinleri ve version/policy şartları korunur. Demo kayıtlar seed'den yeniden oluşturulur; orijinal sandbox DB restore değildir.

## 8. Eksik işler ve local devam sırası

1. Kılavuzdaki full bench/MariaDB local kurulumunu kendi bilgisayarında doğrula; 38 saf test ve 201 + 13 + 18 kabulü tekrar çalıştır.
2. All-module/multi-company kayıt/field/print/file/SQL-RPC/tarayıcı güvenlik matrisi; CI parser/lint başarılarını tam güvenlik kabulü sanma.
3. Serialize/batch zimmet, net satış/iade/cancel, eşzamanlı yarış ve full PO/PI/iade/kur/evrak varyasyonları.
4. Tam mobile/browser, performans, gerçek şirket/Tekdüzen/KDV, PDF, SMTP delivery ve reminder kapsamı.
5. Uyumsoft gerçek ürün/sürüm/API/sandbox erişimi → connector/UBL/iptal/retry/idempotency; şu an eksik fonksiyonlar var.
6. Portal farklı payload-idempotency, file/IDOR ve gerçek ödeme/teslim senaryoları; draft order stok rezervasyonu değildir.
7. Backup/encryption_key/restore/upgrade rollback tatbikatı, SBOM/lisans review ve kullanıcı/muhasebe/GİB/sağlayıcı UAT.

“GitHub CI başarılı” = bu test seti geçti; “18 modül final kabul” değil. `delivery.readiness` henüz modül/entegrasyon kapılarını kapatmaz. Local devam tercihi bu açık işleri veya üretim NO-GO'yu değiştirmez.

## 9. GitHub devir referansları

- Repo: https://github.com/recepcanta35-gif/Cari
- Dal: https://github.com/recepcanta35-gif/Cari/tree/arena/c5b59147-cari
- PR #1: https://github.com/recepcanta35-gif/Cari/pull/1 — açık, `main` initial commit
- Kaynak CI: https://github.com/recepcanta35-gif/Cari/actions/runs/37982049980
- Genel CI: https://github.com/recepcanta35-gif/Cari/actions
- [Tam commit/işlem dökümü](git-commit-dokumu.md)

Bu rapor yalnız kaynak/dokümantasyon devridir; canlıya yükleme, üretim secret veya finansal kabul tutanağı değildir.

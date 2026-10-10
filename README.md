# Cari — Entegre İş Yönetim Sistemi

Stok, saha satış, teklif, cari hesap, tahsilat, sevkiyat ve online sipariş süreçlerini
tek web sistemi üzerinde yöneten **Frappe / ERPNext v15** tabanlı hibrit uyarlama.

## Güncel karar — 10 Ekim 2026

**Python/Frappe/ERPNext ile local geliştirmeye devam.** PHP/Dolibarr yalnız uygulanmamış
alternatif değerlendirmesidir; mimari değiştirilmedi, mevcut kod silinmedi.

**Üretim teslim durumu: NO-GO.** Kaynak ve testli geliştirme adayı vardır; 18 modülün
son kullanıcı/üretim kabulü tamamlanmış değildir. Eski demo bench/veritabanı ve çalışan
web sunucusu bu kaynak deposuna dahil değildir. Hostinger'e yükleme/login yapılmadı.

### Devir belgeleri

| Belge | İçerik |
|---|---|
| [Operasyon ve kapsam raporu](docs/devir/operasyon-ve-kapsam-raporu.md) | Bugüne kadarki işlemler, 18 modül matrisi, test kanıtları, eksikler ve kaynak devri |
| [Local Python kurulum kılavuzu](docs/devir/local-python-kurulum.md) | Windows saf testleri; WSL2/Linux bench, MariaDB/Redis, seed, DB testleri ve IDE yolları |
| [GitHub commit/düzenleme dökümü](docs/devir/git-commit-dokumu.md) | Başlangıçtan incelenen kod referansına her commit ve değişen dosyaları |
| [Tam dosya ağacı](docs/devir/dosya-agaci.txt) | Projedeki bütün kaynak ve dokümantasyon yolları |
| [Dosya envanteri](docs/devir/dosya-envanteri.tsv) | Her dosyanın türü/görevi, Python sembolleri ve DocType şema bilgileri |
| [Dosya bazlı değişiklik listesi](docs/devir/degisen-dosyalar.tsv) | İlk commit → incelenen kod referansı: ekleme/düzenleme, satır sayıları |

## Kaynakları bilgisayarınıza alın

Geliştirmeler **`arena/c5b59147-cari`** dalındadır. [PR #1](https://github.com/recepcanta35-gif/Cari/pull/1)
açıktır; `main` yalnız ilk commit'i içerir. Sadece `main` clone etmek geliştirmeleri getirmez.

```bash
git clone --branch arena/c5b59147-cari --single-branch https://github.com/recepcanta35-gif/Cari.git Cari
cd Cari
```

Yalnız saf Python testleri (Linux/WSL):

```bash
python3 -m venv .venv
.venv/bin/python -m pip install pytest pyyaml ruff
.venv/bin/python -m pytest -q
.venv/bin/ruff check --config apps/cari_custom/pyproject.toml apps/cari_custom/cari_custom scripts tests
```

**Full ERP `python main.py` ile çalışmaz.** Ayrı bench + MariaDB + Redis kurun;
[Windows/WSL2 ve tam kurulum adımları](docs/devir/local-python-kurulum.md).
Yerel kurulumda yeni güçlü parolalar kullanın; tarihî demo/hosting parolalarını yeniden kullanmayın.

## Depo yapısı

```text
apps/
  cari_custom/             Python iş kuralları, güvenlik, zimmet/görev/ticari DocType'lar,
                           iş merkezi, müşteri portalı, Türkiye demo setup/seed/test
  uyumsoft_integration/    Settings/log/kuyruk iskeleti; connector ve UBL-TR eksik
.github/workflows/        Saf test + pinned v15.122.0 / MariaDB taze site CI
scripts/                  Bağlı-site test runner'ları, deploy preflight, CI diagnostic
tests/unit/              Frappe gerektirmeyen kural/şema/deploy testleri
deploy/                   Üretim adayı Docker/TLS/backup ve read-only runtime probe
docs/                     Analiz, plan, kanıt, işletim ve devir raporları
```

Önerilen local dizinler: kaynak `~/projects/Cari`, runtime `~/cari-bench`.
Core Frappe/ERPNext, bench env, Node bağımlılıkları ve site/DB bench altında yeniden kurulur;
repo bunları vendor/backup olarak içermez. Tam ağaç için devir dosyası kullanılmalıdır.

## Test kanıtı ve kabul sınırı

İncelenen kod referansı: **`614416291e1ae27dd79fd9fdab408ed2714b722e`**.
10 Ekim'de saf Python testleri **38/38**, Ruff başarılı.
[Kaynak CI 37982049980](https://github.com/recepcanta35-gif/Cari/actions/runs/37982049980)
ve [PR CI 37982054831](https://github.com/recepcanta35-gif/Cari/actions/runs/37982054831)
başarılı: unit + gerçek MariaDB/bench fresh site; **201 demo kontrolü,
13 temel + 18 ek DB regresyonu**. Kaynak CI sabit Frappe/ERPNext v15.122.0,
Python 3.11, Node 22/Yarn 1.22.22 ve MariaDB 10.6 kullanır.

Bu başarı bütün modüllerin güvenlik/tarayıcı/yük/UAT/üretim onayı değildir.
Docker build, gerçek SMTP/PDF/TLS, backup-restore tatbikatı, gerçek muhasebe ve
Uyumsoft/GİB/sağlayıcı kabulü açıktır. Güncel işler [Actions](https://github.com/recepcanta35-gif/Cari/actions)
üzerinden görülür; eski başarı başka commit'in yerine geçmez.

## Geliştirilmiş alanlar

9 kullanıcı profili; şirket/müşteri/depo/personel scope, pasif hesap → SMTP daveti,
deactivate/session invalidation, audit ve maliyet koruması; gerçek zimmet stok transferi,
kısmi/tam iade ve iptal; görev çakışması/başlat/tamamla; çek/senet gerçek tahsilatı,
sevkiyat ve servis lifecycle; scope'lu miktar/CSV/dashboard; portal katalog/sepet ve
server-price/idempotent **draft** sipariş adayları.

İş merkezi `/app/cari-merkez`, müşteri portalı `/cari-portal`.
Portal/e-posta `Cari Settings` üzerinden varsayılan kapalıdır. Uyumsoft
`connector.test_connection`, `send_payload` ve `invoice_to_ubltr` henüz
**`NotImplementedError`** verir; log/kuyruk varlığı canlı entegrasyon değildir.

## Kapsam notları

- **Barkod ve SMS yoktur.** Ürün seçimi ad, ürün kodu, kategori ve fotoğraf üzerinden.
- Uyumsoft gerçek ürün/sürüm/API sözleşmesi ve erişim onayına bağlıdır.
- Online satış kapsamda, modüler ve ayrı kabul gerektirir.
- Mevcut WordPress ve hosting klasörleri korunur; ERP bunların üzerine dönüştürülmez.

## Plan ve tarihî belgeler

| Belge | İçerik |
|---|---|
| [Tam teslim planı](docs/anahtar-teslim-plani.md) | Kullanıcının bütün faz onayı, T0–T9 ve 18 modül kabulü |
| [Teslim durumu](docs/teslim-durumu.json) | Makinece okunur NO-GO, dış bağımlılıklar ve local devam kararı |
| [Üretim işletim kılavuzu](docs/uretim-isletim-kilavuzu.md) | Üretim adayının işletim/backup ve açık kapıları |
| [Kapsam analizi](docs/kapsam-analizi.md) | İlk şartname/veri modeli/bağımlılık analizi |
| [ERPNext değerlendirmesi](docs/erpnext-hazir-cozum-degerlendirmesi.md) | Core/özel modül gap ve Türkiye/Uyumsoft |
| [Çözüm kıyası](docs/cozum-secenekleri-karsilastirmasi.md) | Sıfırdan / ERPNext / WP ERP |
| [Ek mimari analiz](docs/erpnext-kapsam-mimari-kurumsal-uygunluk.md) | Teknik/lisans doğrulama notları |
| [Tarihî sandbox kurulum rehberi](docs/erpnext-kurulum-rehberi.md) | 9 Ekim PG sandbox workaround'ları; normal local kurulum önerisi değil |
| [Faz 1.5 demo raporu](docs/faz-1-5-test-sonuclari.md) | Demo kimlikleri, GL/stok/cari, ana PG 199 / fresh 201 kontrol |
| [Hosting uygunluğu](docs/hosting-uygunluk-kontrolu.md) | PHP cloud/SSH, salt-okunur transport check; kurulum yapılmadı |
| [PHP uyum analizi](docs/php-hosting-uyum-plani.md) | Uygulanmamış alternatif; local Python tercihiyle ertelendi |
| [Lisans envanteri](docs/lisans-envanteri.md) | Lisans kapsamı ve açık SBOM/dağıtım kontrolü |

9 Ekim demo Türkiye setup: Cari A.Ş./TRY, generic hesap planı, KDV %1/%10/%20,
temel tanımlar/rol/saha deposu; 4 ürün ve gerçek teklif → sipariş → irsaliye →
fatura → banka tahsilatı. **1.800 TL net + 360 TL KDV = 2.160 TL**, bakiye 0.
Bu demo gerçek Tekdüzen hesap planı/muhasebe/üretim kabulü değildir.
Eski runtime/DB mevcut değildir; seed local'de yeniden üretir, orijinal DB restore etmez.

## Lisans

ERPNext **GPL-3.0**, Frappe Framework **MIT** lisanslıdır. `cari_custom`, ERPNext'ten
uyarlanan sorgu kodu içerdiğinden GPL-3.0 işaretlidir ve lisans metni eklenmiştir.
`uyumsoft_integration` mevcut bağımsız iskeleti MIT işaretlidir; tamamlanan entegrasyonun
dağıtım şekli/lisans değerlendirmesi ayrıca yapılmalıdır. İç kullanım ve üçüncü kişilere
dağıtım koşulları aynı değildir; bu not hukukî görüş değildir.

# Cari — Local Python/ERPNext Geliştirme Kurulumu

**Tarih:** 10 Ekim 2026

**Hedef:** PHP'ye geçmeden Python/Frappe/ERPNext v15 üzerinde kendi bilgisayarında devam etmek.

## 1. Önce doğru kaynak dalını alın

Geliştirmeler `main` üzerinde değil, `arena/c5b59147-cari` dalındadır. PR #1 açık; merge yapılmış sayılmaz.

```bash
git clone --branch arena/c5b59147-cari --single-branch https://github.com/recepcanta35-gif/Cari.git Cari
cd Cari
git branch --show-current
git log --oneline -10
```

İlk kod inceleme referansı: `614416291e1ae27dd79fd9fdab408ed2714b722e`. Devir raporları bu referansın üstüne eklenir. Aynı dal üzerinde devam edin; düzeltmeleri kaybetmek için reset/force/overwrite kullanmayın.

### ZIP ve çevrimdışı Git geçmişi

- **`Cari-Kaynak-ve-Raporlar-2026-10-10.zip`** içinde proje dizini `Cari/` ve 135 kaynak/rapor dosyası bulunur. `.git` yoktur; ZIP açmak Git geçmişini kurmaz. Paket kökündeki `DEVIR-METADATA.json`, `KAYNAK-SHA256.tsv` ve `OKU-ONCE.txt` kaynak dışı teslim metadata'sıdır.
- **`Cari-Devir-2026-10-10.sha256`** iki indirilebilir paketin bütünlük özetini verir. Linux/WSL'de aynı klasörde `sha256sum -c Cari-Devir-2026-10-10.sha256`; PowerShell'de `Get-FileHash -Algorithm SHA256 .\Cari-Kaynak-ve-Raporlar-2026-10-10.zip` ile karşılaştırın. SHA-256 bütünlük kontrolüdür, imzalı kimlik kanıtı değildir.
- Ayrı **`Cari-Git-Gecmisi.bundle`** ile çevrimdışı clone:

```bash
git clone --branch arena/c5b59147-cari ./Cari-Git-Gecmisi.bundle Cari
cd Cari
git remote set-url origin https://github.com/recepcanta35-gif/Cari.git
```

Bundle ile clone veya ZIP ile açma **alternatiflerdir**; ikisini aynı dolu dizin üzerine yapmayın. GitHub erişimi varsa normal clone önerilir.

## 2. İki farklı çalışma seviyesi

| Seviye | Gereken | Ne sağlar? |
|---|---|---|
| Kaynak inceleme / saf Python testleri | Python 3.11+, pytest, PyYAML, ruff | İş kuralları, şema ve konfigürasyon testleri. ERP web sunucusu çalışmaz. |
| Tam ERP geliştirmesi | Linux/WSL2, Frappe bench, Python, Node/Yarn, MariaDB, Redis | DocType'lar, stok/muhasebe motoru, web, worker, scheduler, socketio, gerçek DB kabul testleri. |

`python main.py` ile çalışan bağımsız bir program değildir; Frappe uygulamalarıdır. `frappe` PyPI paketini tek başına yüklemek tam kurulumun yerine geçmez.

Windows üzerinde tam Frappe/bench için **WSL2 Ubuntu** veya Linux VM kullanın. Windows sanal ortamı saf testler için yeterlidir. Linux çalışması için VPS satın almak gerekmez; WSL2 kendi bilgisayarınızdadır.

## 3. Yalnız kaynak ve birim testleri — Windows veya Linux

Python 3.11 ile:

```powershell
# Windows PowerShell — Cari kök dizininde
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install pytest pyyaml ruff
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\ruff.exe check --config apps/cari_custom/pyproject.toml apps/cari_custom/cari_custom scripts tests
```

```bash
# Linux / WSL — Cari kök dizininde
python3 -m venv .venv
.venv/bin/python -m pip install pytest pyyaml ruff
.venv/bin/python -m pytest -q
.venv/bin/ruff check --config apps/cari_custom/pyproject.toml apps/cari_custom/cari_custom scripts tests
```

Rapor hazırlanırken **38 test geçti**, Ruff geçti. Bu saf test sayısıdır; DB/web/GUI/SMTP/Uyumsoft kabulü değildir. Yeni test veya dosya eklenirse sayı değişebilir. Frappe entegrasyon testleri `pytest.ini` içindeki bu saf test yoluna dahil değildir.

## 4. Tam ERP — Linux / Windows WSL2

### 4.1 Windows WSL2

PowerShell (Windows yöneticisi) ile WSL kurulu değilse:

```powershell
wsl --install -d Ubuntu-24.04
```

Gerekirse yeniden başlatın. Devamındaki komutlar **Ubuntu terminalinde** çalışır. Projeyi Linux dosya sistemi altında tutun (`~/projects/Cari`); `/mnt/c` altında bench/env/node_modules çalıştırmak izin ve watcher sorunlarına yol açabilir. VS Code Remote WSL ile bu dizini açabilirsiniz.

### 4.2 Sürümler

- Frappe: **v15.122.0**
- ERPNext: **v15.122.0**
- CI Python: **3.11**; yerel Python 3.12 tercih edilirse sabit upstream tag ve bütün testler ayrıca doğrulanmalı.
- Node.js: **22**, Yarn: **1.22.22**
- CI DB: **MariaDB 10.6**. Ubuntu 24.04 varsayılanı farklı olabilir; kullanılan sürümü kaydedin ve testleri yeniden çalıştırın.
- Redis: geliştirme instance'ları **13000 cache / 11000 queue**.

Ubuntu/WSL2'daki gerekli paketler:

```bash
sudo apt-get update
sudo apt-get install -y git python3 python3-dev python3-venv build-essential pkg-config \
  mariadb-server mariadb-client libmariadb-dev redis-server \
  libpango-1.0-0 libpangoft2-1.0-0 libpangocairo-1.0-0 libharfbuzz0b \
  libldap2-dev libsasl2-dev
python3 --version
mariadb --version
```

Node 22'yi Linux için güvenilir/resmî yöntemiyle kurun; Windows node.exe'yi WSL'de kullanmayın. NVM hazırsa:

```bash
nvm install 22
nvm use 22
npm install -g yarn@1.22.22
node --version
yarn --version
```

Bench CLI'ı sistem Python'unu bozmayacak ayrı ortamda kurun:

```bash
python3 -m venv "$HOME/.venvs/frappe-bench-cli"
"$HOME/.venvs/frappe-bench-cli/bin/pip" install frappe-bench
export PATH="$HOME/.venvs/frappe-bench-cli/bin:$PATH"
bench --version
```

Bu PATH'i sonraki Ubuntu terminalinde de kullanın. Node/NVM kurulumu ve MariaDB auth ayarı bilgisayarınızın durumuna bağlıdır; burada yerel makinenizde yapılmış/test edilmiş sayılmaz.

### 4.3 Ayrı bench dizini oluşturun

Aşağıdaki örnek `~/projects/Cari` kaynak deposunu varsayar. Repo başka yerdeyse **yalnız `CARI_REPO`** değerini değiştirin. Bench dizini kaynak repo dışında olsun; var olan dizini silmeyin/overwrite etmeyin.

```bash
export CARI_REPO="$HOME/projects/Cari"
export CARI_BENCH="$HOME/cari-bench"

# Var olan bench varsa bu init adımını tekrarlamayın.
bench init --python "$(command -v python3)" --frappe-branch v15.122.0 --no-backups "$CARI_BENCH"
cd "$CARI_BENCH"
bench get-app erpnext --branch v15.122.0

ln -s "$CARI_REPO/apps/cari_custom" apps/cari_custom
ln -s "$CARI_REPO/apps/uyumsoft_integration" apps/uyumsoft_integration
printf '\ncari_custom\nuyumsoft_integration\n' >> sites/apps.txt
env/bin/pip install --no-deps -e apps/cari_custom -e apps/uyumsoft_integration
```

Symlink zaten varsa yeniden oluşturmayın. `sites/apps.txt` içinde dört isim **ayrı satırda ve birer kez** yer almalı: frappe, erpnext, cari_custom, uyumsoft_integration. Windows ZIP açmada executable izinleri kaybolabilir; shell scriptler `bash script.sh` ile çalıştırılabilir.

### 4.4 Yerel MariaDB ve Redis

```bash
sudo service mariadb start
```

DB yöneticisi **yerel yeni/dedicated geliştirme instance'ında** kullanıcı/veritabanı oluşturma yetkisine sahip olmalı. Ubuntu root socket auth ile Python/TCP auth aynı şey değildir. Gerekirse yerel bootstrap kullanıcısını operatör oluşturur:

```bash
# SQL geçmişine sır yazmamak için:
sudo env MYSQL_HISTFILE=/dev/null mariadb
```

Bu client içinde, `<YENI_YALNIZ_LOCAL_DB_PAROLASI>` değerini yeni güçlü bir sırla değiştirin:

```sql
CREATE USER 'cari_local_admin'@'127.0.0.1' IDENTIFIED BY '<YENI_YALNIZ_LOCAL_DB_PAROLASI>';
GRANT ALL PRIVILEGES ON *.* TO 'cari_local_admin'@'127.0.0.1' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EXIT;
```

Bu geniş yetki **yalnız ayrı local bootstrap instance'ı** içindir, uygulamanın çalışma DB kullanıcısı değildir. Mevcut ortak/üretim DB veya Hostinger üzerinde uygulanmaz. Zaten uygun yerel DB yöneticiniz varsa bu kullanıcı oluşturma adımını yapmayın.

MariaDB charset/collation için `deploy/mariadb.cnf` içindeki utf8mb4 ayarlarını bu dedicated geliştirme instance'ına uygulayıp servis restart'ını operatör planlar. Site kurulumu uyarı verirse charset sürümünü kontrol edin; para/stok tabloları InnoDB olmalıdır.

İlk app install ve CLI kabulü sırasında Redis gerekir. **Bu portları başka bench kullanmıyorsa** geçici instance'lar:

```bash
redis-server --port 13000 --daemonize yes --save '' --appendonly no
redis-server --port 11000 --daemonize yes --save '' --appendonly no
cd "$CARI_BENCH"
bench set-config -g redis_cache redis://127.0.0.1:13000
bench set-config -g redis_queue redis://127.0.0.1:11000
bench set-config -g redis_socketio redis://127.0.0.1:11000
```

Instance'lar size ait değilse başlatmayın/durdurmayın; farklı bench portları planlayın. Port çakışmasını iki kez aynı sunucuyu açarak çözmeye çalışmayın.

### 4.5 Yeni demo site

Sırları repo veya sohbete yazmayın; yerel terminalde gizli giriş kullanın:

```bash
cd "$CARI_BENCH"
read -rsp 'Yerel DB bootstrap parolası: ' CARI_DB_PASSWORD; printf '\n'
read -rsp 'Yeni local Administrator parolası: ' CARI_ADMIN_PASSWORD; printf '\n'
bench new-site cari.local --db-type mariadb --db-host 127.0.0.1 --db-port 3306 \
  --db-root-username cari_local_admin --db-root-password "$CARI_DB_PASSWORD" \
  --admin-password "$CARI_ADMIN_PASSWORD" --set-default --install-app erpnext
unset CARI_DB_PASSWORD CARI_ADMIN_PASSWORD

bench --site cari.local install-app cari_custom
bench --site cari.local install-app uyumsoft_integration
bench --site cari.local set-config developer_mode 1
bench --site cari.local migrate
bench --site cari.local execute cari_custom.setup_turkey.run
bench --site cari.local execute cari_custom.sample_data.run --kwargs '{"allow_demo": True}'
bench build
```

**Mevcut siteyi `--force` ile sıfırlamayın.** `cari.local` varsa önce var olan yedek ve durumu inceleyin. Bu scriptler demo şirketi (Cari A.Ş.)/örnek belgeler oluşturur; gerçek ticari veya üretim ortamında çalıştırılmaz. Hostinger'de paylaşılan parolayı local için yeniden kullanmayın.

### 4.6 Kabul testleri

```bash
cd "$CARI_BENCH"
bench --site cari.local execute cari_custom.sample_validation.verify
env/bin/python "$CARI_REPO/scripts/run_faz15_tests.py" \
  --bench "$CARI_BENCH" --site cari.local --report "$CARI_BENCH/logs/local-demo-evidence.json"
env/bin/python "$CARI_REPO/scripts/run_delivery_tests.py" \
  --bench "$CARI_BENCH" --site cari.local --report "$CARI_BENCH/logs/local-delivery-evidence.json"
```

Taze site: 201 demo kontrolü; 13 temel + 18 kapsam/saha/ticari regresyon testi. Bu sayılar mevcut senaryo setine aittir; tüm üretim, yük, serialized item, e-posta, PDF ve tarayıcı kabulü tamamlanmış değildir. Regresyonların geçici DB kayıtları rollback edilir; seed kalıcı demo oluşturur.

### 4.7 İsteğe bağlı local portal görüntüleme

`Cari Settings` varsayılan olarak portal/e-posta gönderimini kapalı tutar. Portalı
test etmek için yalnız yeni demo sitede System Manager olarak **Cari Settings** açın;
şirket, selling price list ve portal warehouse alanlarını demo kayıtlarla eşleştirin.
Ardından portalı açın; gerekiyorsa public catalog'u ayrıca etkinleştirin. Müşteriye
bağlı Portal profili ve scope olmadan sipariş verilemez. Bu adım SMTP/Uyumsoft'u
açmaz ve sipariş finans/stok onayı yerine geçmez. Bir web sayfasının açılması API
kabulü değildir; sonraki DB/tarayıcı testleri ayrıca yapılır.

### 4.8 Web geliştirme sunucusu

Yalnız kendinizin başlattığı geçici Redis instance'larını kapatın; bench start kendi Redis süreçlerini açacaktır:

```bash
redis-cli -p 13000 shutdown nosave
redis-cli -p 11000 shutdown nosave
cd "$CARI_BENCH"
bench start
```

Tarayıcı: `http://localhost:8000`. Kullanıcı **Administrator**, parola kurulumda sizin verdiğiniz yeni local paroladır. İş merkezi `/app/cari-merkez`, portal `/cari-portal`.

Terminal açık kalır; `Ctrl+C` bench geliştirme süreçlerini durdurur. Yeni terminalde bench'in `env/bin/python` yorumlayıcısını kullanın. Global Python ortamındaki modüller bench env'ine otomatik gelmez.

## 5. Local IDE ve kaynak yolları

- Kaynak: `~/projects/Cari/apps/cari_custom/cari_custom/`.
- Yorumlayıcı (tam ERP): `~/cari-bench/env/bin/python`.
- DocType controller dosyaları aynı isimli class'ları başka modülden dışa aktarır; `as ClassName` re-export'u kaldırmayın. Asıl iş mantığı `field_operations.py`, `business_operations.py`, `security.py` vb. içindedir.
- Python değişikliği sonrası ilgili süreç restart gerekebilir; DocType JSON/Custom Field değişikliği sonrası `bench --site cari.local migrate`.
- JS/CSS/bundle değişikliği sonrası `bench build --app cari_custom`, cache temizliği ve tarayıcı yenileme.
- Kaynak symlink sayesinde düzenlemeler depoda kalır; Frappe/ERPNext vendor dosyalarını gelişi güzel değiştirmeyin.

## 6. Nelerin yeniden alınması/kurulması gerekiyor?

Git/ZIP **şunları içermez**: önceki `/home/user/frappe-bench`, Python env, Node node_modules, PostgreSQL/MariaDB data dizini, `sites/cari.local/site_config.json`, encryption_key, Redis state, demo DB dump, kullanıcının hosting dosyaları.

Çekirdekler bench ile GitHub'dan sabit tag'lerle alınır. Demo seed kaynakta olduğu için örnek veri yeniden üretilebilir; eski canlı DB'nin birebir kopyası değildir. Gerçek kayıtlar varsa ayrıca güvenli backup/restore ve encryption_key gerekir.

`docs/erpnext-kurulum-rehberi.md` geçmiş sandbox workaround'larını anlatır; onun PostgreSQL/trust/LD_LIBRARY_PATH/yarn rewrite komutlarını normal local ortama körlemesine taşımayın. Yeni local tercih MariaDB'dir. Üretim `deploy/compose.yml` TLS/gerçek domain ister; tek başına local geliştirme compose dosyası değildir.

## 7. Güvenlik ve eksik işleri unutmayın

SMTP ve portal `Cari Settings` üzerinde default kapalıdır. Uyumsoft ürün/sürüm/API/erişim teyidi gelmeden kapalı; connector ve UBL eşleme taslaktır. PDF/SMTP/gerçek muhasebe/uygulamalı restore/UAT ve tam güvenlik/yük kabulü açık. Yerel geliştirme **NO-GO** üretim kapısını kapatmaz.

Bu kılavuz CI'de geçen backend akışını yerel geliştirme için düzenler. WSL/native kurulum, Docker build ve sizin bilgisayarınızdaki servis/auth/portlar bu raporu hazırlarken kurulmadı; hazır çalışan local ortam arşivi diye sunulmaz.

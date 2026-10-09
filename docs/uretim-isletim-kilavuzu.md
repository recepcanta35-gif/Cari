# Cari — Üretim ve İşletim Kılavuzu (Aday Paket)

Bu belge **yayın adayı hazırlığıdır**; doğrulanmış canlı kurulum yerine geçmez. Gerçek şirket, muhasebe, sunucu/DNS, SMTP, Uyumsoft sözleşmesi ve kabul kanıtları sağlanmadan NO-GO geçerlidir.

## 1. Sürüm ve lisans

- Çekirdek: Frappe/ERPNext **v15.122.0**. Üretim DB: **MariaDB 10.6** ailesi; yama/digest operasyon sırasında sabitlenmeli ve yeniden test edilmelidir.
- Üretim imajı yalnız resmi çekirdek + `cari_custom` + `uyumsoft_integration` içermelidir. `deploy/Dockerfile` özel kodu imaja alır; yalın ERPNext imajı özel DocType'ları içermez.
- GPL-3.0 kaynak ve atıfları, Frappe MIT ve bağımlılık lisansları pakette korunur. Kullanıcı başına aktivasyon/lisans anahtarı eklenmez. Sırları kaynak paketine eklemeyin.
- Değişiklikler `arena/c5b59147-cari` çalışma dalında; yayın sürümü ancak test/UAT kapıları kapanınca etiketlenir. `0.1.0` imaj etiketi şu an örnek aday etikettir.

## 2. Ön koşullar

Docker Engine ve güncel Compose v2, gerçek domain/DNS erişimi, güvenlik duvarı, yeterli depolama ve dışarıdaki şifreli yedek hedefi gerekir. Donanım boyutu gerçek veri/kullanıcı yük testiyle kesinleşir; CI sonucu yük kapasitesi kanıtı değildir.

`deploy/.env.example` dosyasını **Git dışındaki** bir sır dosyasına kopyalayın, gerçek değerlerle doldurun ve `chmod 600` uygulayın. Parola veya API anahtarı sohbete/yaml'a/loga konmaz. İlk admin parolası yalnız tek seferlik oluşturma sürecine verilir.

```bash
python3 scripts/deployment_preflight.py --env-file /secure/cari-production.env
# PASS = yalnız statik konfigürasyon geçerli; üretim kabulü değildir.
docker build -f deploy/Dockerfile --build-arg ERPNEXT_VERSION=v15.122.0 -t cari/erpnext:0.1.0 .
docker compose --env-file /secure/cari-production.env -f deploy/compose.yml config --quiet
docker compose --env-file /secure/cari-production.env -f deploy/compose.yml up -d
```

Ön kontrol ve imaj oluşturma **bu sandbox'da Docker olmadığı için yerel olarak çalıştırılmadı**. MariaDB backend doğrulaması GitHub CI'de yapılır; Docker build/TLS/PDF/restore için ayrıca staging kabulü gerekir. `docker compose config` çıktısını sır değerleri içerebileceği için paylaşmayın; `--quiet` kullanın.

## 3. Site oluşturma

`deploy/create-site.sh` yalnız yeni, açıkça seçilmiş gerçek sitede çalışır. Var olan siteyi overwrite/force/reset etmez. Çalıştırıcıya `CARI_SITE`, `DB_ROOT_PASSWORD`, `INITIAL_ADMIN_PASSWORD` **secret/env** olarak, backend konteyneri içinde sağlanır. Sonra:

```bash
# Konteyner içindeki güvenli operatör kabuğunda:
bash /operator/create-site.sh
```

Operatör dosyasını salt okunur bağlayın veya STDIN ile çalıştırın; sırları komut satırına yazmayın. Normal backend/worker servisinde ilk admin veya DB root parolası ENV olarak tutulmaz.

Gerçek şirketi ERPNext ilk kurulum akışından oluşturun. **`sample_data.run` veya sabit demo şirketini yaratan `setup_turkey.run` üretimde çalıştırılmaz.** Üretim yerelleştirmesi gerçek şirkete, onaylı Tekdüzen/KDV eşlemesine ve gerçek banka/depo yapısına uygulanır.

Kontroller:

- Developer mode ve test/demo seed kapalı; CSRF açık; wildcard CORS yok.
- Uygulama/DB ayrı kullanıcı ve parolalar; encryption_key güvenli saklanıyor.
- Caddy gerçek domain üzerinde TLS; HTTP→HTTPS, websocket ve dosya yükleme boyutu doğrulandı.
- Backend/worker/scheduler/websocket ve cache/queue ayrı süreçler; yalnız Caddy 80/443 dışarı açık.
- Backend/worker egress ağı SMTP/entegrasyon için vardır; DB/Redis yalnız özel ağda, dış port yok.
- Admin parolası değiştirildi; OTP App MFA teknik/finans yönetiminde uygulanıp kurtarma tatbikatı yapıldı. SMS kullanılmaz.
- SMTP/domain/DKIM/SPF/DMARC, gönderim kuyruğu ve PDF gerçek belgeden doğrulandı.

## 4. Kullanıcı yönetimi

Kullanıcı tipi ve profilinden bağımsız olarak gerçek `Cari User Scope` gerekir. Saha kullanıcıları Employee.user_id ve şirketle; portal kullanıcıları tam bir müşteriyle eşleşir. Depo/saha depoları açıkça atanır. Boş müşteri listesi “tüm müşteriler” değildir.

Kullanıcı oluşturma servisi yeni hesabı pasif tutar; SMTP daveti/parola kurulumu yapılmadan hazır hesap/parola göstermez. İşletme kullanıcı yöneticisi teknik yönetici/finans/İK yükseltmesi yapamaz. Pasifleştirme kullanıcıyı, kapsamı ve aktif oturumları kapatır. Denetim kaydı parola/token içermez.

- İş merkezi: `/app/cari-merkez`
- Özel DocType'lar: `Stock Assignment`, `Stock Assignment Return`, `Daily Assignment`, `Cari Payment Instrument`, `Cari Shipment`, `Cari Service Record`.
- Portal: `/cari-portal`; `Cari Settings.portal_enabled` ve müşteri profili kurulmadan veri/sipariş erişimi kapalıdır.

## 5. Stok/finans işlemleri

Onaylı zimmet gerçek Stock Entry üretir; tekrar çağrı çift transfer üretmez. Kısmi iade ayrı onaylı belge, satış tüketimi zimmete bağlı kalemler üzerinden hesaplanır. Stok miktarı formdaki sayıları değiştirmekle düzenlenmez. Bağlı transfer doğrudan iptal edilmez. Önce satış/iadelerin uygun iptal/ters kayıt zinciri tamamlanır.

Çek/senet **alındı/bankada** durumları para tahsilatı değildir. Gerçek banka kabul referansı ile tahsil edilince Payment Entry oluşturulur. Birden çok fatura tahsisi ve tahsis edilmeyen cari avans ayrı takip edilir; muhasebe kur/tahsis validasyonları atlanmaz. Evrak muhasebesinin 101/121/127 vb. yerel hesap eşlemesi muhasebeci tarafından belirlenir; aday kod statutory kabul yerine geçmez.

Görevler personel ve araç zaman çakışmasını denetler. Tamamlanmış görev/servis geçmişi keyfi iptal yerine düzeltme süreciyle korunur. Sevk/teslim durumları fiziksel stok çıkışı yerine geçmez; çıkış normal irsaliyededir.

## 6. Yedek ve geri yükleme

`deploy/backup.sh` DB + public/private dosya yedeği üretir. Site konfigürasyonu/encryption_key, şifreli dış depoya ayrıca alınır. Konteyner/volume/sunucu üzerinde tek kopya yedek sayılmaz. Yerel yedek üretmek geri yükleme testinin başarılı olduğu anlamına gelmez.

Politika işletme tarafından onaylanır: sıklık, şifreleme, saklama süresi, RPO/RTO, operatör, dış hedef ve alarm. Restore **ayrı staging sitesi** üzerinde uygulanır; DB, dosyalar, özel app sürümleri ve encryption_key aynı yedek noktasından geri yüklenir. Belge adedi, stok/Bin/GL/cari, özel dosyalar, SMTP şifre çözümü, rol/portal izolasyonu test edilir. Tutanak ve süre kaydedilir. Üretim üzerine `--force` ile otomatik restore yoktur.

## 7. Upgrade / rollback

Önce yedek ve staging kopyası → sabit imaj/dep sürümü → `bench --site ... migrate` → kabul/testler → bakım penceresinde yayın. Onaylı finans/stok verisi eski şemaya rastgele döndürülmez. İmaj rollback'i ile DB rollback'i aynı şey değildir; migrate öncesi test edilmiş geri dönüş noktası gerekir. Sürüm numarası yükseltildi diye kabul tamamlanmaz.

## 8. İzleme ve teslim kapısı

Ping yalnız web canlılığını gösterir; DB, job kuyruğu, scheduler, websocket, disk, yedek yaşı, SMTP hata kuyruğu ve entegrasyon durumları ayrıca izlenir. Kişisel/mali veri ve secret loglanmaz. İzleme alıcıları şirket/rol kapsamıyla sınırlandırılır.

`cari_custom.delivery.readiness` şu an **NO-GO** döndürür. Modüllerin tam testleri, güvenlik/yük/tarayıcı kabulü, muhasebe/UAT/restore ve gerçek Uyumsoft sözleşmesi henüz kapanmamıştır. Bu kapı tamamlanmadan pakete “teslime hazır” veya “GİB uyumlu” denmez.

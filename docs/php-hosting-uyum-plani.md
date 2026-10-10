# PHP/MySQL Cloud Hosting Uyum Seçeneği

> **10 Ekim 2026 güncellemesi:** Kullanıcı şimdilik local Python/Frappe/ERPNext ile devam etmeyi seçti. Bu belge tarihî, uygulanmamış PHP alternatifidir; replatform yapılmadı. Güncel devir: [local kurulum](devir/local-python-kurulum.md), [operasyon raporu](devir/operasyon-ve-kapsam-raporu.md).

**Tarih:** 9 Ekim 2026
**Durum:** Mimari değişiklik önerisi; ERPNext kararı henüz değiştirilmedi, PHP uygulaması kurulmadı.

## Kısa cevap

Aynı 18 modüllük Cari iş kapsamı mevcut PHP/MySQL bulut hosting için geliştirilebilir. **ERPNext'in Python/Frappe kodu PHP'ye bir ayarla dönüştürülemez.** Bu yol çekirdek ERP platformunu değiştirme ve özel modülleri PHP tarafına yeniden uygulama işidir; FTP ile mevcut Frappe uygulamasını yüklemek değildir.

## Öncelikli yaklaşım: hazır PHP ERP + özel modüller

Önceki “sıfırdan ERP ve WordPress/WooCommerce istemiyoruz” kararı nedeniyle, ilk incelenecek aday bağımsız **Dolibarr ERP/CRM** çekirdeğidir. Upstream README; PHP web uygulaması olduğunu, teklif/fatura/sipariş/stok/agenda modüllerini ve MySQL/MariaDB desteğini açıklar. GPL-3+ kaynak/lisans şartları korunur.

Kaynak: https://github.com/Dolibarr/dolibarr — develop README bu ön uygunluk incelemesinde okunmuştur. **Develop dalı üretim sürümü olarak seçilmez.** Sabit desteklenen release ve PHP/eklenti matrisi ayrı doğrulanmalıdır; hazır modül bulunması son iş kabulü demek değildir.

Dolibarr 18 modülün tamamının veya Türkiye muhasebe/Uyumsoft/portal/yetki gereksinimlerinin hazır karşılandığı iddiası değildir. Alan/kayıt bazlı maliyet gizleme, zimmet, araç/görev, servis geçmişi, kargo, e-posta kapsamı ve portal için ayrı gap/kabul analizi gerekir.

**Alternatif:** PHP sürümüyle uyumlu Laravel + MySQL özel uygulama. Bu hosting uyumlu olabilir ancak Laravel tek başına ERP/muhasebe çekirdeği sağlamaz; stok/finans/iptal/iadeler, rol ve bütün ticari süreçler yeniden geliştirilir. Önceki sıfırdan geliştirmeme kararı değiştirilmeden bu yola girilmez.

## Hosting uyumlu teknik düzen

- PHP uygulama sunucusu + MySQL/MariaDB InnoDB; Docker, sistem Redis veya kalıcı Python daemon zorunluluğu yok.
- Günlük işlemler HTTP/PHP request içinde kısa ve transaction'lı; para için DECIMAL, stok için satır kilidi, onaylı işlem/ters kayıt ve audit korunur.
- Arka plan işlerinin barındırmanın izin verdiği cron ile sınırlı batch'ler halinde çalışması; kalıcı `queue:work` daemon'una bağımlılık yok. İş tekilleştirme, retry, zaman aşımı ve çakışma kontrolü yine gerekir.
- Canlı ekran güncellemesi için gerekirse AJAX polling; ayrı websocket sunucusu zorunlu tutulmaz.
- PDF için çekirdek/PHP kütüphanesi yolu; sistem wkhtmltopdf kurulumuna bağlı olmayacak şekilde değerlendirme.
- CSS/JS build geliştirici/CI ortamında yapılır; sunucuda Node build zorunluluğu yok.
- Kod/config/belge yükleri korunur; yalnız public dosyalar domain document root'ta. DB parolası, yedek ve uygulama sırları web kökünde tutulmaz. Hazır ERP'nin installer lock/config erişim kuralları ayrıca test edilir.
- `nexterp.skysoftteknoloji.com.tr` ve `public_html/nexterp` hedefi kullanılabilir; gerçek document root, PHP sürümü/uzantıları, DB sürümü, HTTPS, cron, writable dizinler ve dosya erişimi kurulmadan doğrulanmış sayılmaz.
- Mevcut WordPress/diğer siteler silinmez veya ERP'ye dönüştürülmez; ERP bağımsız uygulamadır. Barkod/SMS kapsam dışında kalır.

## Mevcut çalışmadan korunanlar

| Korunacak | Yeniden uygulanacak / doğrulanacak |
|---|---|
| 18 modül kapsamı ve iş kuralları | Python/Frappe controller/DocType/permission hook kodu PHP'de çalışmaz |
| Rol/şirket/müşteri/depo sınırları ve saldırı senaryoları | Yeni çekirdeğin gerçek REST/list/export/print/dosya izolasyonu |
| Zimmet/iade/satış/iptal kuralları, decimal ve idempotency yaklaşımı | Yeni stok/finans defteri, GL/cari/stok mutabakatı ve yarış testleri |
| Örnek veri tasarımı ve iş kabul senaryoları | Python testleri PHP doğrulama kanıtı sayılmaz; eşdeğer testler yeniden yazılır |
| UI fikirleri, Türkçe içerik ve metadata | Frappe UI çağrıları yeni backend/form altyapısına uyarlanır |
| Uyumsoft koşullu onay ve sağlayıcı sözleşmesi gereksinimi | PHP konektörü ve kuyruk adaptasyonu; canlı hâlâ ürün/sürüm/erişim onayı sonrası |

Varsa gerçek kayıtlar sessizce SQL kopyalanmaz; aktarım kuru koşusu, kimlik/hesap eşleme, defter mutabakatı, yedek ve geri dönüş gerekir. Eski kod silinmeden saklanır. GPL/üçüncü taraf kaynaklardan uyarlanan kodun lisans/atıf şartları korunur.

## Geçiş fazları

1. Yeni çekirdek kararı: hazır PHP ERP ön uygunluk ve 18 modül gap analizi, desteklenen PHP/release sabitleme.
2. Kurulabilir paket, sunucu sağlık/cron/HTTPS/DB/config erişim testleri ve güvenli installer.
3. Kullanıcı/rol/kayıt/alan izolasyonu ve maliyet gizleme.
4. Ürün/depo/cari, ticari akış, stok/GL, zimmet/iade/görev, evrak tahsilatı.
5. Rapor/servis/sevkiyat/e-posta ve portal.
6. Uyumsoft ürün/sürüm/API erişimi doğrulandıktan sonra sandbox/canlı sağlayıcı kabulü.
7. Yeni platformun tam UAT/güvenlik/yedek-restore/yük/tarayıcı kabulü ve kaynak devir paketi.

Bu küçük bir “hosting ayarı” değildir. Önceki MariaDB/Frappe CI başarısı yeni PHP sürümünün kabulü olarak aktarılmaz. Bütün geliştirme fazlarının genel onayı korunur, ancak seçilmiş ERPNext platformunu değiştirme kararı netleştirilmeden proje sessizce replatform edilmez.

## Ayrı kalan erişim sınırı

PHP uyumuna geçmek hostingte çalıştırma imkânını değiştirir; bu oturumdan yapılan FTP/SSH/HTTPS denemelerinde protokol karşılamasından önce bağlantıların kapanmasını tek başına çözmez. Kurulabilir paket hazırlanabilir, fakat canlı yükleme erişebilen yetkili operatör/dağıtım ortamından yapılır. Şifreler Git veya sohbette tekrar paylaşılmaz.

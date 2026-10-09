# Cari — Anahtar Teslim Geliştirme ve Kabul Planı

**Plan tarihi:** 9 Ekim 2026
**Yetki:** Kullanıcı bütün geliştirme fazlarını onayladı; faz geçişlerinde yeniden geliştirme onayı istenmez.
**Mimari:** Frappe/ERPNext v15 üzerine modüler özel uygulamalar; üretimde MariaDB.
**Dışarıda:** Barkod ve SMS. İş kuralları değiştirilmez.

## Teslime hazır ne demek?

Çalışan demo, bitmiş/teslime hazır ürün değildir. Teslim ancak kapsamın 18 modülünün kabulü, rol/alan/kayıt güvenliği, gerçek ortam yedek-geri yüklemesi, SMTP/PDF, gerçek şirket/muhasebe doğrulaması, müşteri portalı izolasyonu ve koşullu canlı entegrasyon kabulü tamamlandığında yapılır. Otomatik kontrol `GO` vermeden “anahtar teslim tamam” denmez.

Onay; lisans anahtarı icat etme, barkod/SMS ekleme, GİB onayı varsayma, gerçek müşteri verisini demo ile karıştırma veya bilinmeyen sağlayıcıya canlı istek gönderme yetkisi değildir. Kullanıcı sayısını/yazılım kullanımını sınırlayan ücretli lisans modeli eklenmez. ERPNext GPL-3.0, Frappe MIT; kod dağıtımı/atfı, üçüncü taraf lisans envanteri ve kaynak teslimi korunur.

## Fazlar ve kapılar

| Faz | Teslim paketi | Kabul / bitiş kapısı |
|---|---|---|
| **T0 — Kapsam ve lisans** | 18 modül izlenebilirliği, lisans/NOTICE/SBOM, veri sorumluluğu, kapsam dışı arayüzler | İş kuralları ve lisans envanteri kodla tutarlı; lisans/dağıtım istisnaları kayda alınmış |
| **T1 — Üretim altyapısı** | Sabit sürüm özel Docker imajı, MariaDB/Redis/worker/scheduler/websocket, TLS, sır yönetimi, CI, sağlık kontrolü, yedekleme | Sıfırdan kurulum + upgrade/migrate; staging yedeğinden dosyalar ve encryption_key dahil geri yükleme; debug kapalı |
| **T2 — Kullanıcı ve yetki** | Yönetici, kullanıcı yöneticisi, satış, saha, depo, muhasebe, servis, portal profilleri; kullanıcı oluşturma/davet/pasifleştirme; kapsam ve denetim izi | Eksik kapsam varsayılan olarak reddedilir; kayıtlar doğrudan URL/API/export/print/link sorgusu üzerinden sızmaz; maliyet alanları korunur; yükseltme saldırısı reddedilir |
| **T3 — Stok ve saha** | Ürün/fotoğraf/birim/kategori, depo hareketleri, onaylı zimmet transferi, kısmi/tam iade, iptal/ters kayıt; personel/araç planı | Defter/Bin/zimmet bakiye eşitliği; negatif stok/çift transfer/fazla iade engeli; eşzamanlı yarış testi; görev/araç çakışması engeli |
| **T4 — Ticari ve cari** | Teklif → sipariş → irsaliye → fatura → tahsilat; satın alma, KDV, vade/risk, nakit/havale/kart/çek/senet takibi, iadeler | Kısmi sevk/fatura/tahsilat ve iade/iptal; GL ve cari eşitliği; çek/senet banka tahsilatı sayılmadan bekleyen evrak olarak takip; muhasebeci onayı |
| **T5 — Lojistik, servis, raporlar** | Kargo/sevkiyat durumları, teslim kanıtı; garanti/servis geçmişi; rol-kapsamlı dashboard/raporlar; e-posta bildirimleri | Yetkisiz durum/kanal engeli; garanti/servis ve seri no bağlantısı; rapor ile defter mutabakatı; sadece açık/ilgili kayıt için mükerrersiz bildirim |
| **T6 — Uyumsoft** | Olay/idempotency kuyruğu, tekrar deneme/kalıcı hata/manual yeniden deneme, canonical veri ve UBL-TR, sağlayıcı adaptörü, izleme | **Ürün + sürüm + API sözleşmesi + erişim onayı + test hesabı** olmadan canlı kapalı; sandbox eşleme/iptal/timeout/çift gönderim testleri; sağlayıcı/GİB kabulü |
| **T7 — Online satış ve portal** | Responsive katalog/fotoğraf/arama, sepet, sunucu fiyatlı sipariş, müşteri teklif/sipariş/fatura/ödeme/sevkiyat/servis takibi | Müşteriler arası IDOR yok; istemci fiyatı güvenilmez; CSRF/limit/idempotency; sipariş ve stok/cari aynı ERP'de; ödeme sağlayıcısı varsa ayrı sandbox kabulü |
| **T8 — Kalite ve UAT** | Birim/entegrasyon/HTTP/tarayıcı/rol matrisi testleri, örnek ve gerçek veri ayrımı, yük/güvenlik testi, operatör kılavuzu | Sıfır açık kritik/yüksek güvenlik veya finans/stok hatası; tüm senaryolar kanıtlı; kullanıcı kabul senaryoları ve muhasebe onayı |
| **T9 — Yayın ve devir** | Sürüm/CHANGELOG, kurulum ve kaynak paketi, yedek/rollback, eğitim, yetki listesi, destek/izleme | Gerçek sunucu/DNS/TLS/SMTP/PDF doğrulandı; geri yükleme tatbikatı; kullanıcı ve muhasebe/entegrasyon kabul tutanakları; GO |

T0–T2 altyapı ve güvenlik önceliklidir. T3–T5 ve T7 modüler yürür. T6 teknik hazırlığı diğer fazlarla paralel yürür; bilinmeyen sağlayıcı protokolü varsayılmaz. T8 her fazda test olarak başlar, T9 sonunda tek teslim kapısı olarak kapanır.

## 18 modülün son kabulü

| ID | Modül | Teslimde aranacak somut sonuç |
|---|---|---|
| M01 | Dashboard | Kullanıcının kapsamındaki satış, stok, tahsilat ve görev toplamları; muhasebe ve stok raporlarıyla aynı sonuç |
| M02 | Ürünler | Kod/ad/kategori/fotoğraf/birim/fiyat/kritik stok; barkodsuz seçim; depocuya maliyet sızmaz |
| M03 | Depolar / hareketler | Çoklu depo giriş/çıkış/transfer, stok defteri, sayım, negatif stok ve şirket sınırı kontrolü |
| M04 | Personel stok tahsisi | Onay = gerçek transfer; kısmi/tam iade = ters transfer; satış/iade/cancel ile hesaplanan kalan; tam denetim izi |
| M05 | Satış / sipariş | Tekliften dönüşüm, kısmi sevk/fatura, durumlar, uygun depo/zimmet, fiyat/risk kontrolü |
| M06 | Satın alma | Tedarikçi → PO → PR → PI → ödeme; kısmi giriş/iade, alış KDV ve stok/muhasebe mutabakatı |
| M07 | Müşteri / cari | Doğru şirket/müşteri erişimi; vade/risk, ekstre, borç/alacak, kişisel bilgilerin korunması |
| M08 | Tahsilat | Nakit/havale/kart ile gerçek ödeme, çek/senet için evrak-vade-durum; kısmi tahsis/iptal/geri ödeme; banka/cari mutabakatı |
| M09 | Teklif | Geçerlilik, fiyat/iskonto, PDF/e-posta ve sipariş dönüşümü; müşteri/saha izolasyonu |
| M10 | Araç / görev | Personel/araç/rota/müşteri, zaman aralığı, başlat/bitir/iptal, çakışma kontrolü, mobil erişim |
| M11 | Sevkiyat / kargo | Sipariş/irsaliye bağlı sevk, firma/takip numarası, teslim/istisna/iade durumları ve yetkili güncelleme |
| M12 | İadeler | Satış/alış/zimmet iadelerinin kendi aslına bağlantısı, miktar sınırı ve stok/cari ters hareketleri |
| M13 | Garanti / servis | Ürün/seri no/müşteri geçmişi, garanti tarihi ve hizmet sonucu, özel ekler/ücretli servis ayrımı |
| M14 | Raporlar | Miktar bazlı depo ve zimmet raporları; finans rolleri için cari/tahsilat/satış/maliyet; filtre ve export izolasyonu |
| M15 | E-posta | SMTP/TLS, şablonlar, vade/kritik stok/görev/garanti olayları, mükerrer önleme, hata kuyruğu; SMS yok |
| M16 | Yetkiler / kullanıcılar | En az ayrı teknik ve işletme yönetimi; kontrollü davet/profil/kapsam, oturum iptali, denetim kaydı, alan/kayıt düzeyi test |
| M17 | Uyumsoft | Onay kapısı, olay kuyruğu, doğru belge eşleme, idempotency, tekrar deneme/iptal, canlı sağlayıcı kabulü |
| M18 | Online / portal | Katalog/sepet/sipariş + müşterinin kendi kayıtları; sunucu fiyatı ve güvenli dosyalar; gerekirse ödeme sağlayıcısının sandbox kabulü |

## Değiştirilemeyen güvenlik ve işlem kuralları

- Ön yüz gizleme tek başına yetkilendirme sayılmaz; doğrudan API ve referans sorguları da denetlenir.
- Kapsamı olmayan saha/portal/depo kullanıcılarında boş filtre “her şeyi gör” anlamına gelmez.
- Onaylı stok/finans belgeleri üzerinde sessiz SQL değişikliği yapılmaz; ERPNext iptal/iade/ters kayıt sistemi kullanılır.
- Aynı belge tekrar işlendiğinde ikinci stok/tahsilat/entegrasyon hareketi oluşmaz.
- Aynı zimmet üzerinde satış/iade işlemlerinde kilitleme ve güncel miktar denetimi gerekir.
- Üretimde demo seed, developer_mode, varsayılan admin parolası, wildcard CORS ve CSRF kapatma yasaktır.
- Parola/API anahtarı sohbette, Git'te, logda veya test artefaktında tutulmaz; sırlar sunucu secret/env yönetimiyle sağlanır.
- Müşteri portalı kendi müşteri bağını sunucudan alır; istemciden gelen customer/company/fiyat kabul edilmez.
- Çek/senet kaydı bankaya gerçekleşmiş para girişi sayılmaz; vade ve tahsil edilme aşamaları ayrıdır.

## Dış bağımlılıklar — geliştirme onayından farklıdır

Aşağıdaki bilgileri/kanıtları kullanıcı veya yetkili işletme sağlar. Bunlar olmadan kod geliştirme sürer; gerçek üretim/canlı kabul kapısı açık kalır.

| Bağımlılık | Gerekli bilgi/kanıt | Neden |
|---|---|---|
| Gerçek şirket | Unvan, VKN/TCKN, vergi dairesi, adres, gerçek banka/depo/personel ve muhasebeci | Demo şirketi mali belge için kullanılamaz |
| Üretim | VPS/altyapı, alan adı ve DNS kontrolü, TLS, erişim yöntemi ve onaylı maliyet | Sunucu veya alan adı varmış/ücret onaylanmış varsayılmaz |
| SMTP | Sağlayıcı, gönderen/domain, TLS ayarları, secret erişimi, test alıcısı | E-posta gönderiminin uçtan uca kabulü |
| Muhasebe | Tekdüzen eşleme, KDV/tevkifat/istisna ihtiyacı, fiş ve evrak kuralları; yetkili imzalı inceleme | Yazılım demo testi hukuki muhasebe onayı değildir |
| Uyumsoft | Ürün/sürüm, API dokümanı/test ve canlı endpoint, sözleşme/erişim yetkisi, sandbox hesabı | Koşullu kapsam; keyfî REST/SOAP protokolü uydurulmaz |
| Portal ödeme | Hesaba sipariş / ödeme yöntemi; gerekiyorsa sağlayıcı ve sandbox | Kart verisi saklanmaz; bilinmeyen sağlayıcıya bağlanılmaz |
| Kabul | Gerçek kullanıcı/rol listesi, iş süreçlerini doğrulayan yetkililer, geri yükleme tatbikatı ve UAT | Teslimi kullanıcı ve mali yetkililer doğrular |

Parola/secret değerlerini bu belgeye veya sohbete yazmayın. Sırların güvenli sunucu/secret yönetimiyle sağlanması gerekir.

## Çalışma ve durum kaydı

- `docs/teslim-durumu.json` modül/faz/bağımlılık durumunun makinece okunur kaydıdır.
- Test kanıtı olmadan tamamlanma işaretlenmez; eski PostgreSQL demo raporları tarihi kanıt olarak saklanır, yeni MariaDB kabulü yerine geçmez.
- Teslim paketi sürümlenecek; release/checklist, lisans metinleri, veri sözlüğü, kullanıcı ve operatör kılavuzları, bilinen kısıtlar ve geri dönüş planı aynı kaynak deposunda tutulur.
- Kullanıcı tüm fazları onayladığı için geliştirme sırasında yeniden “devam edelim mi?” sorulmaz; yalnız gerçekten eksik dış bilgi veya iş kuralı çatışması için soru sorulur.

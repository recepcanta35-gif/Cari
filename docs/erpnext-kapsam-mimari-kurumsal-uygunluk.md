# ERPNext Kapsam, Mimari ve Kurumsal Uygunluk Analizi

> Ek bilgi dokümanı — 9 Ekim 2026 (kullanıcı tarafından sağlandı)

Bu analiz dokümanı; 8 Ekim 2026 tarihli yazılımcı kapsam şartnamesinde yer alan stok, saha satış, teklif, cari hesap, tahsilat, sevkiyat, servis/garanti geçmişi ve müşteri portalı süreçlerinin **ERPNext** açık kaynak çözümü üzerinden karşılanabilirliğini, kurumsal olgunluğunu ve lisanslama şartlarını incelemektedir.

---

## 1. İlgili GitHub Depoları

* **ERPNext Ana Deposu (ERP Modülleri):**
  [https://github.com/frappe/erpnext](https://github.com/frappe/erpnext)
* **Frappe Framework (Çekirdek Web Framework & Admin Altyapısı):**
  [https://github.com/frappe/frappe](https://github.com/frappe/frappe)
* **Frappe Docker (Resmi Konteyner Kurulum Aracı):**
  [https://github.com/frappe/frappe_docker](https://github.com/frappe/frappe_docker)

---

## 2. Şartname Modülleri ile ERPNext Karşılaştırması

| Şartname Modülü | ERPNext Karşılığı | Yerleşik Durum |
| :--- | :--- | :--- |
| **Ürünler & Depolar & Stok Hareketleri** | Stock Module (Warehouse, Stock Entry, Delivery Note) | **Hazır:** Çoklu depo, transferler, rezerve stok desteği tam. |
| **Personel Stok Tahsisi (Saha)** | User Permission + Sub-warehouse / Transit Warehouse | **Hazır:** Saha personeline özel sanal/araç deposu atanabilir. |
| **Satış, Sipariş & Teklifler** | Selling Module (Quotation, Sales Order) | **Hazır:** Tekliften siparişe ve irsaliyeye doğrudan dönüşüm. |
| **Müşteriler & Cari Hesap & Tahsilat** | Accounts Module (Customer, Payment Entry, Ledger) | **Hazır:** Detaylı ekstre, vadesi geçmiş bakiye, çoklu para birimi. |
| **Araç & Günlük Görevlendirme** | Projects / Maintenance / Delivery Trip | **Kısmen Hazır:** Ufak iş akışı veya form özelleştirmesi gerekir. |
| **Garanti ve Servis Geçmişi** | Support & Maintenance Module (Warranty Claim, Maintenance Visit) | **Hazır:** Seri no/ürün bazında garanti ve arıza kayıtları. |
| **Online Satış & Müşteri Portalı** | Portal & E-Commerce Module | **Hazır:** Müşterilerin cari, teklif ve siparişlerini gördüğü web portalı. |
| **Yetkiler & E-Posta Tetikleyicileri** | Role-Based Access Control (RBAC) & Email Alerts | **Hazır:** Alan (field) ve belge bazlı yetkilendirme, otomatik bildirimler. |
| **Uyumsoft Veri Aktarımı** | REST API & Webhooks | **Özel Geliştirme:** Dış servis/entegrasyon katmanı kodlanmalıdır. |

---

## 3. Çalışma Mimarisi ve Lisans Durumu

* **Web Tabanlı Mimari:**
  ERPNext %100 web tabanlıdır. İstemci (client) tarafında ek program gerektirmez; masaüstü ve mobil tarayıcılar üzerinden responsive olarak çalışır.
* **Lisans Modeli (GNU GPL v3.0):**
  * ERPNext tamamen ücretsiz ve açık kaynak kodludur.
  * Kullanıcı sayısı, şube veya işlem hacmi kısıtlaması yoktur; lisans bedeli ödenmez.
  * **Şirket İçi Kullanım Serbestliği:** Şirket içi kullanımda, sahada ve müşteri portalında ticari olarak özgürce kullanılabilir. Çekirdek kod dışarıya kapalı lisansla satılmadıkça şirketinizin Uyumsoft gibi entegrasyon kodlarını kamuya açma zorunluluğu bulunmaz.
* **Maliyet Odakları:**
  Yazılım ücretsiz olsa da bulut sunucu kiralama (VPS) ve Uyumsoft entegrasyonu için ayrılacak geliştirici iş gücü ana maliyet kalemleridir.

---

## 4. KOBİ Ölçeğinde Kurumsal Olgunluk Değerlendirmesi

ERPNext, küçük ve orta ölçekli işletmeler (KOBİ) için **fazlasıyla kurumsal kalitededir**:

1. **Denetim İzi (Audit Trail) & Veri Bütünlüğü:**
   Onaylanmış (Submitted) finans ve stok belgeleri veritabanından doğrudan silinemez; ters kayıt (Cancellation/Amendment) zorunludur. Hangi kullanıcının hangi alanı değiştirdiği kayıt altına alınır.
2. **Rol ve Alan Seviyesinde Güvenlik:**
   Saha satıcısının sadece kendi müşterilerini/tekliflerini görmesi, depo personelinin maliyetleri görmeden sadece miktar görmesi gibi katı kurallar yerleşiktir.
3. **Çoklu Şube ve Çoklu Para Birimi:**
   Dövizli cari takibi, otomatik kur değerlemeleri ve birden fazla tüzel kişilik/şube yapısına uygundur.
4. **Disiplinli Süreç Yönetimi:**
   Klasik kontrolsüz iş akışlarının önüne geçerek teklif -> sipariş -> irsaliye -> fatura -> tahsilat zincirini kurumsal disiplinle yürütür.

---

## 5. Uygulama ve Geliştirme Yol Haritası Önerisi

1. **Test Kurulumu:** Ubuntu/Debian sunucu üzerinde Frappe Docker ile ERPNext kurulumu yapılması.
2. **Kapsam Daraltma:** Şartnamede istenmeyen SMS ve Barkod gibi bileşenlerin arayüzden gizlenmesi.
3. **Form ve Roller:** Saha satış personeli, depo yöneticisi ve muhasebe rolleri için form ve yetki alanlarının düzenlenmesi.
4. **Uyumsoft Entegrasyonu:** ERPNext'in REST API ve Webhook mekanizmaları kullanılarak cari, sipariş ve stok hareketlerinin Uyumsoft sistemine asenkron aktarımı için bir mikro servis veya Frappe Custom App yazılması.

---

## 6. Bu Projede Durum (9 Ekim 2026 güncellemesi)

| Öneri | Durum |
|---|---|
| Test kurulumu (Frappe Docker) | Self-hosted kurulum yapıldı (daha fazla kontrol): bench 5.31 + PostgreSQL 16 + Redis 7.2 — bkz. [erpnext-kurulum-rehberi.md](erpnext-kurulum-rehberi.md) |
| Kapsam daraltma (SMS/barkod gizleme) | SMS zaten yok; barkod alanları (Item Barcode) mevcut ama kullanılmayacak — arayüzden gizleme Faz 2'de (Customize Form) |
| Form ve Roller | Faz 1'de rol matrisi kuruldu (Saha Personeli + hazır ERPNext rolleri); form/alan bazlı ince ayarlar devam ediyor |
| Uyumsoft Entegrasyonu | `uyumsoft_integration` custom app iskeleti hazır (REST connector + UBL-TR taslağı + kuyruk); ürün/sürüm/yetki onayı sonrası detaylandırılacak |
| Personel stok tahsisi | `Stock Assignment` kaydı gerçek demo saha transferine bağlandı; otomatik transfer/iade ve yetki ayrıntıları henüz tamamlanmadı |


## 7. Teknik Doğrulama ve Nüanslar

Yukarıdaki bölümler kullanıcı tarafından verilen değerlendirmeyi korur. Aşağıdaki noktalar, mevcut kurulumla değerlendirme metni arasındaki önemli farklardır:

- **Saha tahsisi:** personel/araç deposu yerleşik yapı taşlarıyla kurulabilir; zimmetin stokla tutarlı aktarımı, kısmi iade, onay ve personel bazlı erişim kendiliğinden tamamlanmış sayılmaz. Bu fazda gerçek transfer + bağlantılı kayıt test edildi; otomasyon sonraki fazdır.
- **Yetkiler:** RBAC/User Permission altyapısı hazırdır; yalnız kendi müşterilerini görme veya maliyeti gizleme kuralları yapılandırılmadan otomatik uygulanmaz. Faz 1.5 testi rol haklarının bir bölümünü doğrular, tam güvenlik kabulü değildir.
- **Denetim izi:** onaylı belgelerde iptal/düzeltme disiplini uygulama seviyesinde geçerlidir. Bu, yüksek yetkili bir veritabanı yöneticisinin SQL ile veri değiştiremeyeceği anlamına gelmez. Change tracking, erişim kısıtları ve yedek/denetim politikası ayrıca önemlidir.
- **Portal / online satış:** müşteri portalı altyapısı ile tam katalog/sepet/online ödeme aynı şey değildir. Bu v15 kurulumunda `webshop` app'i kurulu değildir; online satış ayrı kurulum/yapılandırma ve kabul ister. Dört kurulu app: frappe, erpnext, cari_custom, uyumsoft_integration.
- **E-posta / SMS / barkod:** bildirim için bu sürümde `Notification` kullanılır. SMTP gönderimi bu aşamada test edilmedi. SMS ve barkod geliştirilmez; çekirdekte bulunabilecek arayüz/alanların saha rollerinden gizlenmesi ayrı uyarlama işidir.
- **Lisans:** ERPNext GPL-3.0, Frappe Framework MIT lisanslıdır. Şirket içi işletme/hosting ile yazılım kopyasının üçüncü kişilere dağıtılması ayrılmalıdır. GPL kaynak sağlama yükümlülükleri yalnız “çekirdeği kapalı lisansla satma” koşuluna bağlı değildir; dağıtılan türev kod ve lisans birleştirme durumu da değerlendirilir. Kamuya genel yayın ile kopya alıcılarına kaynak sağlama aynı yükümlülük değildir. Uyumsoft kodunun bağımsızlığı/dağıtımı için hukukî değerlendirme gerekir; burada koşulsuz gizlilik veya yayın zorunluluğu garantisi verilmez.
- **Bu repodaki lisans bilgisi:** ERPNext kaynaklarından adapte edilen sorgular nedeniyle `cari_custom` GPL-3.0 olarak işaretlendi, kaynak atfı ve lisans metni eklendi. Uyumsoft iskeleti mevcut özgün koduyla MIT olarak işaretlidir.
- **Üretim mimarisi:** buradaki v15/PostgreSQL sınırlı destekli demo, üretim tercihi değildir. Desteklenen v15/MariaDB kurulumuna geçiş, güvenlik, yedek/geri yükleme ve Türkiye muhasebe/e-belge onayı ayrı üretim kabulü gerektirir.

Güncel uygulama kanıtı: [Faz 1.5 test sonuçları](faz-1-5-test-sonuclari.md) — ana sitede 199 kontrol, sıfırdan test sitesinde 201 kontrol ve her iki ortamda 13/13 regresyon testi.

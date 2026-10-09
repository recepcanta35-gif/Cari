# Hazır Çözüm Değerlendirmesi: Frappe ERPNext

**Tarih:** 9 Ekim 2026
**Kaynak:** [github.com/frappe/erpnext](https://github.com/frappe/erpnext) (incelendi: yerel shallow clone, branch `develop` HEAD)
**Karşılaştırma temeli:** `docs/kapsam-analizi.md` içindeki 18 modüllük kapsam

---

## 1. ERPNext Nedir?

| Özellik | Değer |
|---|---|
| Lisans | **GPL-3.0** (ücretsiz, açık kaynak) |
| GitHub stars | ~39.900 |
| Forks | ~13.000 |
| Geliştirme | Çok aktif (son push: 9 Ekim 2026) |
| Teknoloji | Python + Frappe Framework, MariaDB/PostgreSQL, JS |
| Modüller | Accounts, Stock, Selling, Buying, CRM, Assets, Support, Manufacturing, POS, HR, Projects, Webshop, Portal, EDI, Regional |

## 2. Kapsam Modüllerinin ERPNext Karşılığı (Gap Analizi)

| # | Kapsam Modülü | ERPNext Karşılığı | Durum |
|---|---|---|---|
| 1 | Dashboard | Desk dashboard + özelleştirilebilir widget'lar | ✅ Hazır |
| 2 | Ürünler | **Item** (kod, ad, kategori/item_group, fotoğraf `image`, barkod alanı, KDV şablonu) | ✅ Hazır |
| 3 | Depolar ve stok hareketleri | **Warehouse**, **Stock Entry**, Stock Ledger, **Serial No**, **Batch**, stok raporları | ✅ Hazır |
| 4 | Personel stok tahsisi | Stock Entry (transfer) + Warehouse Type; personel zimmet ekranı | ⚠️ Kısmen — custom alan/doctype gerekir |
| 5 | Satış ve sipariş | **Sales Order**, **POS Invoice** (pos_profile, pos_opening/closing), Kundenauftrag akışları | ✅ Hazır |
| 6 | Satın alma | **Purchase Order**, Purchase Receipt, Supplier, Supplier Quotation | ✅ Hazır |
| 7 | Müşteriler ve cari hesap | **Customer**, Cari ekstresi (Payment Ledger), Accounts Receivable/Payable, risk/vade alanları | ✅ Hazır |
| 8 | Tahsilat | **Payment Entry** (nakit/çek/havale = Mode of Payment), Bank Reconciliation, çek/senet takibi (sınırlı, muhasebe fişiyle) | ✅ Hazır |
| 9 | Teklifler | **Quotation** (geçerlilik tarihi `valid_till`, siparişe dönüşüm) | ✅ Hazır |
| 10 | Araç ve günlük görevlendirme | **Delivery Trip** (driver, vehicle, departure_time, delivery_stops, rota optimizasyonu); günlük saha görev planı | ⚠️ Kısmen — Delivery Trip temel var, personel görev planı custom |
| 11 | Sevkiyat ve kargo | **Delivery Note** + Delivery Trip; kargo takip no/entegrasyon | ⚠️ Kısmen — kargo takip no custom alan |
| 12 | İadeler | Sales Invoice iade/Debit Note, Purchase Return, stok geri giriş | ✅ Hazır |
| 13 | Garanti ve servis geçmişi | **Warranty Claim** (seri no, `warranty_expiry_date`, complaint, çözüm), **Serial No** üzerinde `warranty_expiry_date`, Asset Maintenance, Issue + SLA | ✅ Hazır |
| 14 | Raporlar | Query Report, Script Report, Report Builder, modüllere yayılı 70+ hazır rapor | ✅ Hazır |
| 15 | E-posta hatırlatmaları | Frappe **Email Alert**, **Auto Repeat**, **Email Digest** (vade, stok, görev vb. için) | ✅ Hazır |
| 16 | Yetkiler | **Role Permission Manager** (modül + alan bazlı, çok güçlü) | ✅ Hazır |
| 17 | Uyumsoft veri aktarımı | **YOK** — custom entegrasyon gerekir (REST/SOAP/XML) | ❌ Custom geliştirme |
| 18 | Online satış ve müşteri portalı | **Webshop** (shopping_cart, all-products, shop-by-category) + **Customer Portal** (sipariş/fatura/teklif/dubleks sayfaları) | ✅ Hazır |

**Özet:** 18 modülün **13'ü hazır**, **3'ü kısmen hazır (küçük özelleştirme)**, **1'i (Uyumsoft) özel entegrasyon**, personel zimmet ekranı dahil toplam özelleştirme ihtiyacı makul düzeydedir.

### Kapsam dışı maddeler (barkod / SMS)

- ERPNext'te barkod desteği (Item Barcode, barkodlu stok hareketleri) **vardır** — kapsam dışı olduğu için kapatılır/önemsizdir, geliştirme maliyeti sıfırdır.
- SMS modülü yoktur — kapsam gereği doğru.

## 3. Türkiye / Uyumsoft Durumu (Kritik Bölüm)

- ERPNext içinde `erpnext/regional/turkey/` klasörü vardır ama **`setup.py` içeriği boştur (`pass`)** — Türkiye'ye özel muhasebe planı, vergi şablonu veya e-belge desteği **yoktur**.
- Sadece adres şablonu ve sınırlı belgeler (örn. `lower_deduction_certificate` — tevkifat bağlantılı) vardır.
- **KDV** oranları ERPNext'te yapılandırılabilir (Sales/Purchase Taxes and Charges Template) — bu genel mekanizma ile çözülür.
- **e-Fatura / e-Arşiv / e-İrsaliye (UBL-TR, GİB)**: ERPNext'te yoktur. Uyumsoft (özel entegratör) üzerinden **custom entegrasyon** şart. Bu, kapsam dokümanının "ürün, sürüm ve erişim yetkilerine bağlı" dediği koşulla birebir örtüşür.
- Türkiye'de ERPNext danışmanlığı pazarı vardır (örn. **Logedosoft** — Türkiye yetkili danışmanı; kurulum, yerelleştirme, e-Fatura entegrasyonu hizmetleri veriyor). Yerel destek bulunabilir.
- Uyumsoft tarafında hazır konektörler vardır (örn. GitHub'da `Uyumsoft-E-fatura-Entegrasyon` PHP REST örnekleri) — protokol tarafı nettir, geliştirme tahmin edilebilir iş yüküdür.

## 4. Maliyet ve Süre Karşılaştırması (Tahmini, 2 kişilik ekip varsayımıyla)

| Senaryo | Süre | Not |
|---|---|---|
| **Sıfırdan geliştirme** (kapsam dokümanındaki 18 modül) | 12–18+ ay | Yüksek risk, sıfırdan altyapı (yetki, log, rapor, e-posta, muhasebe mantığı) |
| **ERPNext üzerine uyarlama** | 3–5 ay | Kurulum 1–2 hf; çekirdek uyarlama 2–4 hf; özelleştirmeler (zimmet, görevlendirme, kargo takip, garanti ekranları) 4–8 hf; Uyumsoft entegrasyonu 4–8 hf (ayrı iş kalemi); webshop/portal 2–4 hf |
| Lisans maliyeti (ERPNext) | 0 TL | GPL-3.0 |
| Barındırma (self-hosted VPS) | ~20–100 $/ay | veya Frappe Cloud (ücretli, ~10–50 $/ay/site) |
| Danışmanlık (opsiyonel) | Logedosoft vb. | Türkiye'de mevcut |

## 5. ERPNext Kullanmanın Riskleri

1. **GPL-3.0 lisansı:** Kaynak kodu dağıtırsanız açma yükümlülüğü doğar. Self-hosted kullanımda sorun yoktur; SaaS olarak servis verirseniz (kullanıcıların kaynakla doğrudan etkileşimi olmadan) GPL tetiklenmez — yine de hukuki danışmanlık önerilir.
2. **Frappe Framework öğrenme eğrisi:** Doctype-tabanlı geliştirme, sıfırdan web geliştirmeden farklı bir paradigmedir.
3. **Özelleştirme maliyeti:** Çok spesifik iş kuralları (örn. saha personel zimmet mantığı) custom app gerektirir; bu ERPNext "ücretsiz" demek değildir — uyarlama ücreti ödenir.
4. **Operasyon:** Self-hosted ise güncelleme, yedekleme, güvenlik yamaları Betrieb yükü size aittir.
5. **Uyumsoft entegrasyonu her iki senaryoda da custom iştir** — bu kalemde ERPNext avantaj sağlamaz, aksine hazır muhasebe (Accounts) modülü veri aktarımını kolaylaştırır.

## 6. Öneri

**Hibrit yaklaşım tavsiye edilir:** ERPNext'i temel alıp, üzerine:

1. `cari_custom` (Frappe custom app): personel stok zimmeti, günlük görevlendirme/görev planı, kargo takip no alanları, Türkiye'ye özel cari/tahsilat düzenlemeleri (çek/senet detayı).
2. `uyumsoft_integration` (custom app): ürün/cari/fatura verilerinin Uyumsoft'a aktarımı + e-Fatura UBL-TR üretimi (Uyumsoft özel entegratör üzerinden GİB'e).
3. Webshop + Customer Portal'u kapsam dokümanındaki sıraya göre (geliştirme sırası sonradan kesinleşir) devreye alma.

Bu yaklaşım, sıfırdan geliştirmeye kıyasla **~3–4 kat daha hızlı** ve çok daha düşük riskle hedefe ulaşır; hazır muhasebe, stok, rapor ve yetki altyapısından免费 yararlanır.

## 7. Karar Noktaları

1. ERPNext üzerine devam mı, sıfırdan geliştirme mi?
2. Barındırma: self-hosted (VPS) mu, Frappe Cloud mu?
3. Uyumsoft entegrasyonu: ürün/sürüm/yetki onayı alındıktan sonra ayrı faz olarak mı başlasın?
4. Türkiye danışmanlığı (Logedosoft vb.) alınacak mı, yoksa iç kaynakla mı ilerlenecek?
5. Online satış geliştirme sırası: çekirdek ticari modüllerden sonra mı?

## 8. WP ERP (wperp.com) ile Kıyas

Aynı kapsam için [WP ERP](https://wperp.com) (WordPress eklentisi, weDevs; core GPLv2 ücretsiz, Pro/extension ücretli) de incelendi. Özet farklar:

- **Kapsam kapsama:** ERPNext 18 modülün 13'ünü hazır sunar; WP ERP çekirdeği (HRM, CRM, Accounting) kapsamın ancak ~%30–40'ını karşılar — **stok/depo hareketleri, zimmet, araç/görevlendirme, dahili garanti/servis ve derin cari hesap WP ERP'de yoktur**.
- WP ERP'nin güçlü yönü **WooCommerce/online satış** (ERPNext webshop'ine denk); zayıf yönü stok, lojistik ve Türkiye muhasebe derinliğidir (hesap planı jenerik, tevkifat/e-belge yok).
- **Uyumsoft entegrasyonu her iki seçenekte de custom iştir** — bu kalemde fark yoktur.
- Maliyet: ERPNext uyarlaması (~3–5 ay) WP ERP üzerinde aynı kapsamı karşılamak için gereken custom geliştirmeye (~8–12 ay) göre düşüktür.

Üç seçeneğin (sıfırdan / ERPNext / WP ERP) tam karşılaştırması: [`docs/cozum-secenekleri-karsilastirmasi.md`](cozum-secenekleri-karsilastirmasi.md)

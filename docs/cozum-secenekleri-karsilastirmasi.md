# Çözüm Seçenekleri Karşılaştırması
## Sıfırdan Geliştirme vs Frappe ERPNext vs WP ERP (wperp.com)

**Tarih:** 9 Ekim 2026
**Karşılaştırma temeli:** `docs/kapsam-analizi.md` (18 modül kapsamı)
**İncelenen kaynaklar:** github.com/frappe/erpnext (HEAD, 9 Ekim 2026), github.com/wp-erp/wp-erp (v1.17.10, 8 Ekim 2026), wperp.com ve kamuya açık inceleme kaynakları

---

## 1. Seçeneklerin Özeti

| Özellik | **Sıfırdan geliştirme** | **Frappe ERPNext** | **WP ERP (weDevs)** |
|---|---|---|---|
| Tür | Özel yazılım | Açık kaynak ERP platformu | WordPress eklentisi (ERP) |
| Lisans | — (sizin) | GPL-3.0, ücretsiz | Core GPLv2+ ücretsiz; Pro + 20+ extension ücretli (~$9,99–12,99/kullanıcı/ay + extension'lar) |
| Teknoloji | Serbest seçim | Python, Frappe Framework, MariaDB/PostgreSQL | PHP, WordPress, MySQL |
| Topluluk | — | ~40.000 stars, çok aktif | ~700 stars (core), aktif (v1.17.10, dün güncellendi) |
| Hazır çekirdek modüller | Yok | Muhasebe, stok, satış, alım, CRM, varlık, destek, İK, POS, üretim, webshop, portal | HRM, CRM, Accounting (üç çekirdek modül, ücretsiz) |
| Hedef ölçek | Sınırsız (tasarıma bağlı) | Enterprise (binlerce kullanıcı, çok şirket) | KOBİ (onlarca kullanıcı; WordPress tavanı) |
| Türkiye lokalizasyonu | İhtiyaca göre sıfırdan | **Boş** (`regional/turkey/setup.py` = `pass`); KDV yapılandırılabilir | Sadece dil/il desteği; hesap planı ve vergiler jenerik |
| Uyumsoft entegrasyonu | Custom | Custom | Custom |
| Online satış | Custom | Webshop + Müşteri Portalı (hazır) | **WooCommerce** (en güçlü yönü; sync extension ücretli) |

## 2. Kapsam Matrisi (18 modül × 3 seçenek)

✅ hazır/kapsam dahil · ◐ kısmen hazır (özelleştirme gerekir) · ❌ yok (custom geliştirme gerekir)

| # | Kapsam Modülü | Sıfırdan | ERPNext | WP ERP |
|---|---|---|---|---|
| 1 | Dashboard | ❌ | ✅ | ◐ (muhasebe/CRM özet ekranları temel) |
| 2 | Ürünler | ❌ | ✅ Item (kod, ad, kategori, fotoğraf) | ◐ Accounting "products" (katalog, maliyet fiyatı; WooCommerce sync ücretli ext.) |
| 3 | Depolar ve stok hareketleri | ❌ | ✅ Warehouse, Stock Entry, Serial No, Batch | ❌ (ürün var; depo/stok hareketi/miktar takibi yok) |
| 4 | Personel stok tahsisi (zimmet) | ❌ | ◐ (transfer + custom zimmet) | ❌ |
| 5 | Satış ve sipariş | ❌ | ✅ Sales Order + POS Invoice | ◐ WooCommerce siparişleri (sync ile CRM/muhasebe) |
| 6 | Satın alma | ❌ | ✅ Purchase Order + Receipt | ◐ Purchases (fatura/ödeme bazlı temel alım) |
| 7 | Müşteriler ve cari hesap | ❌ | ✅ Customer + cari ekstresi (Payment Ledger) | ◐ CRM Contact + Accounting People; temel cari ekstresi |
| 8 | Tahsilat | ❌ | ✅ Payment Entry (nakit/çek/havale), banka mutabakatı | ◐ Payments, Bank Accounts, pay-bills/rec-payments |
| 9 | Teklifler | ❌ | ✅ Quotation (geçerlilik tarihi, siparişe dönüşüm) | ◐ **Estimate** (tahmini fatura/teklif temel olarak var) |
| 10 | Araç ve günlük görevlendirme | ❌ | ◐ Delivery Trip (şoför, araç, durak, rota) | ❌ |
| 11 | Sevkiyat ve kargo | ❌ | ◐ Delivery Note + kargo takip no (custom alan) | ◐ WooCommerce kargo takibi (temel) |
| 12 | İadeler | ❌ | ✅ Satış/alım iadたいesi, stok geri giriş | ◐ WooCommerce iadeler (temel) |
| 13 | Garanti ve servis geçmişi | ❌ | ✅ Warranty Claim + Serial No garanti tarihi | ◐ Zendesk/Help Scout destek entegrasyonu; dahili servis yok |
| 14 | Raporlar | ❌ | ✅ 70+ hazır rapor + Report Builder | ◐ Muhasebe raporları (ledger, bilanço, gelir tablosu, KDV raporu, trial balance) + CRM/HR raporları |
| 15 | E-posta hatırlatmaları | ❌ | ✅ Email Alert + Auto Repeat + Email Digest | ◐ İşlemsel e-postalar (fatura/ödeme/teklif); otomatik hatırlatma sınırlı |
| 16 | Yetkiler | ❌ | ✅ Role Permission Manager (modül+alan bazlı) | ◐ WordPress rol/capability sistemi (temel) |
| 17 | Uyumsoft veri aktarımı | ❌ | ❌ custom entegrasyon | ❌ custom entegrasyon |
| 18 | Online satış ve müşteri portalı | ❌ | ✅ Webshop + Customer Portal | ✅ **WooCommerce** + müşteri hesabı (en güçlü yönü) |

**Skor (hazır / kısmi / yok):**

| Seçenek | ✅ | ◐ | ❌ |
|---|---|---|---|
| ERPNext | **13** | **3** (zimmet, araç/görev, kargo takip) | **1–2** (Uyumsoft + ince ayarlar) |
| WP ERP | **1** (online satış/WooCommerce) | **~8** | **~8–9** (stok/depo, zimmet, araç/görev, alım derinliği, cari derinliği, garanti dahili, gelişmiş raporlama, hatırlatma) |
| Sıfırdan | 0 | 0 | 18 (ama tam iş-kuralı uyumu) |

**Kritik çıkarım:** WP ERP'nin hazır gelenleri (CRM, HRM, temel muhasebe, WooCommerce) kapsamınızın **~%30–40'ını** karşılar. Kapsamın ağır bölümü — **stok/depo hareketleri, personel zimmet, saha görevlendirme, kargo, dahili garanti/servis, derin cari hesap** — WP ERP'de yoktur ve WordPress üzerinde custom geliştirme gerektirir; bu noktada pratikte "WordPress üzerinde sıfırdan geliştirme" senaryosuna yaklaşır.

## 3. WP ERP Teknik İnceleme Özeti (kaynak: wp-erp/wp-erp v1.17.10)

- **Çekirdek modüller (ücretsiz):** HRM, CRM, Accounting.
- **Accounting (74 PHP dosyası):** ledger hesapları (açılış/kapanış bakiyesi), journal entry, satış faturası (**Estimate/teklif tipi dahil**), alış faturası (purchases), çek/bills, expenses, banka hesapları, tahsilat/ödeme (rec-payments/pay-bills/pay-purchases), people (customer/vendor), ürün kataloğu (cost_price; **stok miktarı/depo yok**), KDV/tax rate yönetimi (oran, daire, kategori), raporlar: **ledger, trial balance, bilanço, gelir tablosu, KDV raporu, kâr/zarar**.
- **CRM:** Contact/şirket, contact group, aktivite log, Gmail sync, e-posta gönderimi, raporlar (aktivite, müşteri, büyüme). Deals/Workflow/Custom Field Builder extension'ları **ücretli**.
- **HRM:** Çalışan, departman, pozisyon, izin politikası/talep/tatil, duyurular, İK raporları. Bordro (payroll) **ücretli extension**.
- **WooCommerce:** Entegrasyon **ücretli extension** (~$5,99/ay); ürün/müşteri/sipariş senkronizasyonu CRM + accounting'e.
- **Lisans:** Core GPLv2+ (ücretsiz). Pro ve extension'lar ücretli; kaynak kodunun tamamı GitHub'da (sadece core).
- **Türkiye:** Sadece dil desteği (i18n, TR il kodları). **Tekdüzen hesap planı, tevkifat, e-Fatura/e-Arşiv/e-İrsaliye (UBL-TR/GİB) desteği YOK.** Uyumsoft entegrasyonu custom geliştirme gerektirir — ERPNext ve sıfırdan seçenekle aynı durumdadır.

## 4. Maliyet ve Süre Tahmini (order-of-magnitude)

Varsayımlar: 2 kişilik geliştirme ekibi, ~6.000 $/kişi/ay (Türkiye yazılımcı piyasası ortalama kabulu), 3 yıllık toplam sahip olma maliyeti (TCO).

| Kalem | Sıfırdan | ERPNext | WP ERP |
|---|---|---|---|
| Lisans | 0 | 0 (GPL-3.0) | Core 0; Pro+ext. ~500–1.000 $/yıl |
| Geliştirme/uyarlama süresi | 12–18 ay | 3–5 ay | Kapsamın ~%60'ı custom: 8–12 ay |
| Geliştirme maliyeti | ~144.000–216.000 $ | ~36.000–60.000 $ | ~96.000–144.000 $ |
| Uyumsoft entegrasyonu | dahili (yukarıda) | ayrı kalem, ürün/sürüm/yetki onayı sonrası | dahili (yukarıda) |
| Barındırma (3 yıl) | ~4.000–15.000 $ | ~4.000 $ (self-hosted VPS) | ~1.000–2.000 $ (WP hosting) |
| Bakım/yıl (3 yıl) | ~90.000 $ (yüksek) | ~12.000–24.000 $ (düşük) | ~60.000–90.000 $ (custom geliştirme birikimi) |
| **3 yıl TCO (tahmini)** | **~250.000–350.000 $** | **~60.000–90.000 $** | **~160.000–240.000 $** |

*Not: WP ERP düşük lisans maliyetine rağmen, kapsamın büyük bölümünü custom geliştirme gerektirdiği için toplam maliyette sıfırdan geliştirmeye yaklaşır; üstelik WordPress ölçek tavanı düşüktür.*

## 5. Riskler

| Risk | Sıfırdan | ERPNext | WP ERP |
|---|---|---|---|
| Teslim süresi/gecikme | Yüksek | Düşük-orta | Orta (custom kapsam nedeniyle) |
| Ölçeklenebilirlik | Tasarıma bağlı | Yüksek (enterprise) | Düşük-orta (WordPress/MySQL tavanı) |
| Türkiye mevzuat uyumu (KDV, tevkifat, e-belge) | Sıfırdan inşa | Yapılandırılabilir muhasebe motoru; e-belge custom | Jenerik vergi; e-belge custom; hesap planı Türk standartlarında değil |
| Uyumsoft entegrasyonu | Custom | Custom (güçlü muhasebe motoru kolaylaştırır) | Custom (zayıf muhasebe motoru zorlaştırır) |
| Lisans | — | GPL-3.0 (dağıtımda kaynak açma; SaaS'ta tetiklenmez, hukuki danışman önerilir) | GPLv2 core; Pro/extension ücretli ve kısmen kapalı kaynak |
| Yetenek/danışman bulunabilirliği | Her zaman | Türkiye'de danışman var (örn. Logedosoft) | WordPress ekosistemi geniş |
| Bağımlılık (vendor lock-in) | Yok | Frappe topluluğu, düşük | weDevs'e bağımlılık (ücretli extension'lar) |

## 6. Öneri

**Birincil öneri: ERPNext üzerine hibrit uyarlama.** Kapsamınız stok, saha lojistiği, zimmet, cari hesap ve muhasebe derinliği içeriyor — bu alanlarda ERPNext hazır; WP ERP bu derinlikte değildir. ERPNext ile 3–5 ayda hedefe ulaşılır, maliyet ve risk düşüktür.

**WP ERP şu senaryoda mantıklı:** Halihazırda WooCommerce/WordPress altyapınız varsa **ve kapsam daraltılırsa** (sadece CRM + temel muhasebe + online satış; stok/saha/lojistik süreçleri kapsam dışı bırakılır veya başka sistemde tutulursa). Bu senaryoda maliyet en düşük, başlangıç en hızlıdır.

**Sıfırdan geliştirme:** Ancak çok spesifik iş kuralları, özel entegrasyon zorunluluğu veya lisanslama kısıtları (GPL) kabul edilemiyorsa düşünülmelidir — maliyet ve süre en yüksek seçenektir.

**Uyumsoft entegrasyonu her üç seçenekte de custom iştir** — bu kalem karar kriteri değildir; ERPNext'te güçlü hazır muhasebe motoru bu entegrasyonu en kolaylaştıran seçenektir.

## 7. Karar Noktaları

1. Hangi seçenek: **ERPNext / WP ERP / sıfırdan**?
2. Varsa mevcut **WooCommerce/WordPress** altyapısı var mı? (WP ERP senaryosu için belirleyici)
3. Kapsam daraltılabilir mi? (stok/saha süreçleri zorunlu mu?)
4. Barındırma tercihi (self-hosted / Frappe Cloud / WP hosting)?
5. Uyumsoft ürün/sürüm/yetki onayı durumu — entegrasyon takvimi?

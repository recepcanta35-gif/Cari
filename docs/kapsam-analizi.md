# Cari — Kapsam ve İş Kuralları Analizi

**Tarih:** 9 Ekim 2026
**Kaynak doküman:** "Yazılımcı için kapsam ve iş kuralları — 8 Ekim 2026, Sürüm 1"
**Depo durumu:** Boş iskelet (yalnızca `README.md`)

---

## 1. Mevcut Durum

- Depo `recepcanta35-gif/Cari` boş bir başlangıç deposu: tek dosya `README.md` (içerik: `# Cari`).
- Henüz kod, bağımlılık, veri modeli veya klasör yapısı yok.
- Bu therefore analiz, kapsam dokümanından hareketle **proje planı ve teknik çerçeve önerisi** sunar.

## 2. Kapsam Özeti (Dokümandan Çıkarımlar)

Amaç: stok, saha satış, teklif, cari hesap, tahsilat, sevkiyat ve online sipariş süreçlerini **tek bir web sistemi** üzerinde yönetmek.

### 2.1 Temel Modüller (18 adet)

| # | Modül | Temel İşlev |
|---|-------|-------------|
| 1 | Dashboard | Tüm modüllerden özet veri (satış, stok, tahsilat, görevler) |
| 2 | Ürünler | Ürün kartı: ad, ürün kodu, kategori, fotoğraf, birim, fiyat, kritik stok |
| 3 | Depolar ve stok hareketleri | Giriş/çıkış/transer hareketleri, depo bazlı stok |
| 4 | Personel stok tahsisi | Personelin zimmetindeki stok (saha/depo/araç) |
| 5 | Satış ve sipariş | Sipariş oluşturma, depo çıkışı, durum takibi |
| 6 | Satın alma | Tedarikçi siparişi, stok girişi |
| 7 | Müşteriler ve cari hesap | Cari kart, risk limiti, vade, borç/alacak hareketleri |
| 8 | Tahsilat | Nakit/çek/senet/havale, cari harekete eşleştirme |
| 9 | Teklifler | Teklif hazırlama, geçerlilik tarihi, siparişe dönüşüm |
| 10 | Araç ve günlük görevlendirme | Personel-araç-görev planlama (saha satış) |
| 11 | Sevkiyat ve kargo | Kargo firması, takip no, teslimat durumu |
| 12 | İadeler | Satış/alış iadesi, stok geri giriş/çıkış |
| 13 | Garanti ve servis geçmişi | Seri no bazlı garanti, servis kayıtları |
| 14 | Raporlar | Stok, satış, cari, tahsilat raporları |
| 15 | E-posta hatırlatmaları | Vade, kritik stok, görev, garanti bitişi vb. |
| 16 | Yetkiler | Rol bazlı modül erişim matrisi |
| 17 | Uyumsoft veri aktarımı | Muhasebe entegrasyonu (ürün/sürüm/yetkiye bağlı) |
| 18 | Online satış ve müşteri portalı | Web katalog, sepet, online sipariş, müşteri takibi |

### 2.2 Kapsam Dışı (Kritik — kodlamada atlanacak)

- ❌ **Barkod modülü yok.** Ürün seçimi; **ad, ürün kodu, kategori ve fotoğraf** üzerinden yapılır. (Yani barkod okuyucu/label yazdırma geliştirilmeyecek.)
- ❌ **SMS modülü yok.** Bildirimler yalnızca e-posta ile.

### 2.3 Koşullu / Esnek Noktalar

- **Uyumsoft bağlantısı; ürün, sürüm ve erişim yetkilerine bağlıdır** → entegrasyon, ancak ilgili Uyumsoft ürün/sürümü acquired edildiğinde ve yetki onaylandığında başlar. Öncesinde arayüz/altyapı hazır ama canlı bağlantı kapalı.
- **Online satış kapsamda ama geliştirme sırası kesin değil** → modüler mimari şart; portal sonradan eklenebilir şekilde tasarlanmalı.
- Doküman bir **şartname taslağıdır**; teknik uygulama önerileri ve kararsız ayrıntılar değişebilir, **iş kuralları değişmez**. Yazılımcı teknik boşlukları varsayarak iş kuralını değiştirmemelidir.

## 3. Modül Bağımlılık Zinciri

```
Yetkiler (16) ────────────────► TÜM MODÜLLER (erişim kontrolü)
Ürünler (2) ─► Depolar/Stok (3) ─► Personel stok tahsisi (4)
                    ▲                    │
Satın alma (6) ─────┘                    ▼
Müşteriler/Cari (7) ─► Teklifler (9) ─► Satış/Sipariş (5) ─► Sevkiyat/Kargo (11)
                              │                    │                      │
                              │                    ▼                      ▼
                              │              Tahsilat (8)            İadeler (12)
                              │                    ▲                      │
                              └────────────────────┘──────────────────────┘
Ürünler (2) ─► Garanti/Servis (13)
Dashboard (1) + Raporlar (14) ◄── TÜM MODÜLLERDEN veri çeker
E-posta hatırlatmaları (15) ◄── Tahsilat vadesi, kritik stok, görev, garanti bitişi
Uyumsoft (17) ◄── Ürün, cari, fatura verisi (ürün/sürüm/yetki koşullu)
Online satış/portal (18) ◄── Ürünler, Müşteriler, Sipariş (son faz, sırası esnek)
```

**Önemli çıkarım:** Yetkiler en temel katmandır; ürün–stok–cari çekirdeği olmadan ticari modüller anlamsızdır.

## 4. Önerilen Veri Modeli (Varlıklar)

| Varlık | Öne Çıkan Alanlar |
|--------|-------------------|
| `Kullanici` / `Rol` / `Yetki` | Rol bazlı modül CRUD matrisi |
| `Urun` | urun_kodu, ad, kategori_id, fotograf, birim, alis_fiyat, satis_fiyat, kdv, kritik_stok, garanti_suresi |
| `Kategori` | ad, ust_kategori (ağaç yapı) |
| `Depo` | ad, adres, tip (merkez/saha/araç) |
| `StokHareket` | depo, urun, miktar, birim_fiyat, hareket_tipi (giriş/çıkış/transfer), belge_no, kaynak_modul, tarih |
| `Personel` | kullanici, bolge, arac_id |
| `StokTahsis` | personel, depo/arac, urun, zimmet_miktar |
| `Musteri` (Cari) | unvan, vergi_no/TC, adres, telefon, e-posta, risk_limiti, vade_gunu, bakiye |
| `CariHareket` | musteri, tip (borç/alacak), tutar, belge, vade_tarihi, kapama_durumu |
| `Teklif` / `TeklifKalem` | teklif_no, musteri, gecerlilik_tarihi, durum, siparis_id |
| `SatisSiparis` / `SiparisKalem` | siparis_no, musteri, depo, durum, sevkiyat_id |
| `SatinAlma` / `AlimKalem` | tedarikçi, depo, stok girisi bağlantısı |
| `Tahsilat` | tahsilat_tipi (nakit/çek/senet/havale), tutar, cari_hareket_eslestirme |
| `Arac` | plaka, kapasite, tip |
| `Gorevlendirme` | tarih, personel, arac, bolge/rota, görev_notu |
| `Sevkiyat` | siparis, kargo_firma, takip_no, durum, teslim_tarihi |
| `Iade` | tip (satis/alis), siparis/alim, urun, miktar, stok_geri_giris |
| `GarantiServis` | urun, seri_no, garanti_baslangic/bitis, servis_kayitlari |
| `UyumsoftAktarimLog` | aktarim_tipi, kayit, durum, hata_mesaji, tarih |
| `OnlineSiparis` / `Sepet` / `PortalMusteri` | katalog, sepet, online siparis, kargo takibi |

## 5. Önerilen Teknoloji Yığını

Doküman teknoloji dayatmadığı için öneri (değiştirilebilir):

- **Backend:** Django (Python) + Django REST Framework — auth/rol yönetimi, ORM, admin ve hızlı geliştirme avantajı. Alternatif: NestJS (Node.js) veya Laravel (PHP).
- **Veritabanı:** PostgreSQL (cari hareketler ve stok için ACID raport zorunlu).
- **Frontend:** Django template + Vue.js/React (veya saf server-side rendering ile başlama).
- **E-posta:** SMTP (kurumsal mail) + arka plan görev kuyruğu (Celery/RQ) ile hatırlatmalar.
- **Uyumsoft:** REST/SOAP entegrasyonu (protokolü ürün/sürüm onayından sonra netleşir).
- **Online portal:** aynı backend, ayrı customer-facing frontend (faz 5).

## 6. Önerilen Geliştirme Fazları

| Faz | İçerik | Bağımlılık |
|-----|--------|-----------|
| **Faz 0 — Altyapı** | Kullanıcı/rol/yetki (16), log, e-posta servisi, temel UI iskeleti, boş Dashboard | — |
| **Faz 1 — Çekirdek** | Ürünler (2), Depolar/Stok hareketleri (3), Müşteriler/Cari (7) | Faz 0 |
| **Faz 2 — Ticari süreç** | Satın alma (6), Teklifler (9), Satış/Sipariş (5), Tahsilat (8) | Faz 1 |
| **Faz 3 — Saha lojistiği** | Personel stok tahsisi (4), Araç & görevlendirme (10), Sevkiyat/Kargo (11), İadeler (12) | Faz 1–2 |
| **Faz 4 — Raporlama & servis** | Garanti/Servis (13), Raporlar (14), Dashboard içerikleri (1), E-posta hatırlatmaları (15) | Faz 1–3 |
| **Faz 5 — Entegrasyon & portal** | Uyumsoft aktarımı (17), Online satış + müşteri portalı (18) | Faz 1–2; Uyumsoft ürün/sürüm/yetki onayı; portal sırası sonradan kesinleşir |

## 7. Açık Karar Noktaları (Kullanıcı/Doküman Sahibiyle Netleştirilecek)

1. **Teknoloji yığını** (Django / NestJS / Laravel?)
2. **Uyumsoft entegrasyon protokolü** — API mi, dosya aktarımı mı? Hangi belgeler (e-fatura, e-arşiv, stok)?
3. **Online satış geliştirme sırası** — hangi fazda?
4. **Faturalama kapsamda mı?** Dokümanda tahsilat var, fatura modülü açıkça yok — faturalar Uyumsoft üzerinden mi kesilecek?
5. **Lot/seri no takibi** stokta gerekli mi? (Garanti modülü seri no gerektirir.)
6. **Çok para birimi** desteği var mı?
7. **Saha satışında mobil uygulama** mi, mobil web mi?
8. **Depo sayısız mı, çoklu depo/şube desteği** ilk aşamada gerekli mi?

## 8. İş Kuralları Notları (Değiştirilemez)

- Tüm süreçler **aynı web sistemi** içinde yönetilecek — modüller arası entegre veri akışı şart.
- Ürün seçimi **barkod olmadan**: ad, ürün kodu, kategori, fotoğraf.
- Bildirimler **yalnızca e-posta** (SMS yok).
- Uyumsoft bağlantısı **ürün + sürüm + erişim yetkisi** ön koşuluna bağlı.
- Teknik ayrıntılardaki boşluklar iş kuralını değiştirmez.

## 9. Hazır Çözüm Seçenekleri (Frappe ERPNext ve WP ERP)

Ayrıca [WP ERP](https://wperp.com) (WordPress eklentisi, weDevs; core ücretsiz GPLv2, Pro/extension ücretli) incelendi. WP ERP çekirdeği (HRM, CRM, Accounting — teklif/Estimate dahil) kapsamın ancak ~%30–40'ını karşılar; **stok/depo hareketleri, personel zimmet, araç/görevlendirme, dahili garanti/servis ve derin cari hesap yoktur**. Online satışta (WooCommerce) en güçlü seçenektir. Uyumsoft entegrasyonu her iki seçenekte de custom iştir. Üç seçeneğin tam kıyası için [karşılaştırma raporuna](cozum-secenekleri-karsilastirmasi.md) bakınız.

Kapsamdaki 18 modülün **ücretsiz ve açık kaynak** bir çözümü olan [Frappe ERPNext](https://github.com/frappe/erpnext) (GPL-3.0, ~40k stars, aktif geliştirme) incelendi. Özet:

- **13 modül hazır** (ürün, stok, satış/sipariş, satın alma, cari, tahsilat, teklif, iadeler, garanti/servis — `Warranty Claim` + seri no üzerinde `warranty_expiry_date`, raporlar, e-posta hatırlatmaları, yetkiler, online webshop + müşteri portalı).
- **3 modül kısmen hazır** (personel stok tahsisi/zimmet, araç & günlük görevlendirme — `Delivery Trip` temel var, sevkiyat/kargo takip no) — küçük custom geliştirme gerekir.
- **Uyumsoft veri aktarımı her senaryoda custom iştir**: ERPNext Türkiye lokalizasyonu fiilen boştur (`regional/turkey/setup.py` = `pass`); KDV yapılandırılabilir, ancak e-Fatura/UBL-TR entegrasyonu özel geliştirme ister (Uyumsoft özel entegratör üzerinden). Türkiye'de danışmanlık pazarı vardır (örn. Logedosoft).
- Barkod desteği ERPNext'te vardır ama kapsam dışı olduğu için kapatılır; SMS yoktur (kapsama uygun).

**Öneri:** ERPNext üzerine hibrit uyarlama (custom app: zimmet/görevlendirme/kargo + Uyumsoft entegrasyonu). Tahmini 3–5 ay vs sıfırdan 12–18+ ay.

Detaylar: [`docs/erpnext-hazir-cozum-degerlendirmesi.md`](erpnext-hazir-cozum-degerlendirmesi.md)

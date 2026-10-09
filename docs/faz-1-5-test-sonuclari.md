# Faz 1.5 — Örnek Veri ve Uçtan Uca Test Sonuçları

**Tarih:** 9 Ekim 2026
**Sonuç:** GEÇTİ — demo verisi oluşturuldu ve doğrulandı.
**Ortam:** Frappe/ERPNext v15.122.0, PostgreSQL 16.2; ana site `cari.local`.

> Bu çalışma geliştirme/demo kabulüdür; üretim veya GİB/e-Fatura uygunluk onayı değildir. Örnek kayıtlar gerçek ticari işlem olarak kullanılmamalıdır.

## 1. Oluşturulan veri seti

- 4 stok ürünü ve TRY cinsinden 8 alış/satış fiyatı
- 2 müşteri: ABC Teknoloji Ltd. ve Ahmet Yılmaz
- 1 tedarikçi: Tedarikçi A.Ş.
- 2 personel: Ayşe Demir (satış), Mehmet Kaya (depo)
- 1 araç: 34 ABC 123, Ford Transit
- 2026 mali yılı, TRY fiyat listeleri ve Türkiye varsayılanları
- Her üründen 50 adet stok girişi
- 10 adet mouse için gerçek merkez → saha depo transferi ve buna bağlı zimmet
- Ayşe Demir + araç + Marmara + ABC Teknoloji müşterisine bağlı günlük görev
- Teklif → sipariş → irsaliye → fatura → havale tahsilatı

| Ürün kodu | Ürün | Alış fiyatı (net) | Satış fiyatı (net) |
|---|---|---:|---:|
| ITEM-001 | Kablosuz Mouse | 150 TL | 250 TL |
| ITEM-002 | USB-C Kablo 2m | 30 TL | 55 TL |
| ITEM-003 | 27 inç Monitör | 2.500 TL | 4.200 TL |
| ITEM-004 | Mekanik Klavye | 400 TL | 700 TL |

## 2. Ana sitedeki kayıtlar

ERPNext'in arama çubuğundan belge türünü açıp aşağıdaki kimliklerle kayıtları bulabilirsiniz.

| İşlem | Belge türü | Belge kimliği |
|---|---|---|
| Stok girişi | Purchase Receipt | `MAT-PRE-2026-00001` |
| Merkez → saha transferi | Stock Entry | `CARI-DEMO-15-TRANSFER` |
| Personel zimmeti | Stock Assignment | `e9s55f7cs8` |
| Günlük görevlendirme | Daily Assignment | `e9sc52dhdl` |
| Teklif | Quotation | `SAL-QTN-2026-00001` |
| Satış siparişi | Sales Order | `SAL-ORD-2026-00001` |
| İrsaliye | Delivery Note | `MAT-DN-2026-00001` |
| Satış faturası | Sales Invoice | `ACC-SINV-2026-00001` |
| Tahsilat | Payment Entry | `ACC-PAY-2026-00001` |

Ana sitede önceki demo kayıtları açıkça benimsenmiş, onaylı finans belgeleri yeniden oluşturulmamış/silinmemiştir. İlk iki özel kaydın eski hash kimlikleri korunmuştur; yeni zimmet/görev kayıtlarında `SA-` / `DA-` adlandırması aktiftir.

Ana sitedeki eski fatura sipariş kalemlerine bağlıdır. Yeni seed ve regresyon senaryosu standart ERPNext mapper'larıyla **tekliften siparişe, siparişten irsaliyeye, irsaliyeden faturaya** dönüşür; fatura kalemlerinde hem irsaliye hem sipariş bağlantısı doğrulanmıştır.

## 3. Satış ve cari sonuçları

| Kalem | Miktar | Net birim fiyat | Net tutar |
|---|---:|---:|---:|
| Mouse | 5 | 250 TL | 1.250 TL |
| USB-C kablo | 10 | 55 TL | 550 TL |
| **Net toplam** | | | **1.800 TL** |
| **KDV %20** | | | **360 TL** |
| **Fatura toplamı** | | | **2.160 TL** |
| **Havale tahsilatı** | | | **2.160 TL** |
| **Açık bakiye** | | | **0 TL** |

- Sipariş durumu: **Completed**; sevkiyat ve faturalama oranları **%100**.
- Fatura durumu: **Paid**.
- Fatura bakiyesi; Payment Ledger, GL cari borç/alacak toplamı ve ERPNext cari sorgusu üzerinden ayrı ayrı kontrol edildi.
- Stok irsaliyede düşer; fatura `update_stock=0` olduğundan ikinci kez stok düşmez.
- Satılan ürünlerin maliyeti: **1.050 TL**; irsaliyenin stok/maliyet muhasebe fişi dengeli.
- Fatura, tahsilat, stok girişi ve irsaliye fişlerinde **borç toplamı = alacak toplamı**.
- KDV oranı, başlık alanından değil ürün bazındaki **etkin vergi oranı ve tutarından** da kontrol edildi. ERPNext ürün vergi şablonu, başlık oranını override edebilir.

## 4. Son stok durumu

| Ürün | Merkez depo | Saha deposu | Toplam |
|---|---:|---:|---:|
| Mouse | **35** | **10** | **45** |
| USB-C kablo | **40** | 0 | **40** |
| Monitör | **50** | 0 | **50** |
| Klavye | **50** | 0 | **50** |

Stock Ledger hareketleri ve Bin bakiyeleri birbiriyle karşılaştırıldı. Zimmet kaydındaki `stok_hareketi` alanı, onaylı transfer belgesine bağlıdır.

**Önemli sınır:** Zimmet formu henüz otomatik transfer/iade üretmez. Bu fazda transfer seed tarafından standart Stock Entry ile yapılır ve zimmete bağlanır. Otomatik zimmet/iade iş akışı Faz 2'de geliştirilecektir.

## 5. Otomatik kabul ve regresyon

| Çalıştırma | Sonuç |
|---|---|
| Ana site `cari.local` | **199 kabul kontrolü geçti** |
| Sıfırdan kurulan izole site `cari-faz15-test.local` | **201 kabul kontrolü geçti** |
| Regresyon testleri (her iki site) | **13/13 geçti**, hata/başarısızlık yok |
| Tekrar seed çalıştırma | Yeni ürün, belge, stok veya muhasebe hareketi üretmedi |
| Regresyon sonrası temizlik | Geçici `CARI-TEST-*` işlem kayıtları rollback edildi |
| Ruff + Python derleme kontrolü | Geçti |

Yeni sitedeki iki ek kabul kontrolü, fatura kalemlerinin doğrudan irsaliye bağlantılarıdır. Test sitesinin kurulumu önizlemenin varsayılan sitesini değiştirmedi; ana site hâlâ `cari.local`.

**13 regresyon testi:**

1. Kaydedilmiş demo veri setinin kabulü
2. Seed idempotency: belge/defter mükerrerliği yok
3. Demo için açık `allow_demo=True` onayı zorunlu
4. Üretim modunda seed çalıştırma engeli
5. Zimmette sıfır/negatif miktar ve geçmiş iade tarihi engeli
6. Görevde başlangıçtan önce bitiş zamanı engeli
7. Standart mapper zinciri ve **1.080 TL kısmi + 1.080 TL tamamlayıcı tahsilat**
8. Fatura bakiyesinden fazla tahsis edilen ödeme engeli
9. Yetersiz stok çıkışı engeli (negatif stok açılmadı)
10. Farklı maliyet merkezlerine ait ek maliyetlerin tamamının toplanması
11. Stok kayıt zamanında doğru sıralama; creation yalnızca eşit posting zamanı için kullanılır
12. System Manager erişiminin korunması ve saha rolünün tanımlı oluşturma/yazma hakları
13. PostgreSQL adaptörlerinin siteye göre çalışması ve çift sarılmaması

Bu liste tam alan/şahıs bazlı yetki kabulü değildir. Saha personelinin yalnız kendi müşterilerini görmesi ve depo rolünün maliyetleri görmemesi ayrıca tasarlanıp test edilmelidir.

## 6. HTTP / önizleme kontrolü

Güncel kodla sunucu yeniden başlatıldı. `Host: 8000-demo.e2b.app` başlığıyla önizleme-host yönlendirmesi test edildi:

- Login sayfası ve giriş: **HTTP 200**
- Desk/boot sayfası: **HTTP 200**, kurulum sihirbazı yerine demo Desk erişimi
- Fatura, zimmet ve günlük görev API'ları: **HTTP 200**, beklenen veri doğrulandı
- PostgreSQL inventory-dimension whitelist endpoint'i: **HTTP 200**
- Oturum açmamış kullanıcının fatura listesine erişimi: **HTTP 403**

Bu HTTP ve sunucu/DB testidir; tam tarayıcı otomasyonu, mobil görüntü ve canlı socket davranışı bu kabulün parçası değildir.

## 7. Tekrar çalıştırma

```bash
cd /home/user/frappe-bench
export NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt
export LD_LIBRARY_PATH=/usr/local/lib/python3.11/dist-packages/pgserver/pginstall/lib

# Önce Türkiye temel yapılandırması
bench --site cari.local execute cari_custom.setup_turkey.run

# Açık demo onayı gerekir (v15 CLI kwargs bir Python dict ifadesidir)
bench --site cari.local execute cari_custom.sample_data.run \
  --kwargs '{"allow_demo": True}'

# Veri yaratmadan kabul kontrolü
bench --site cari.local execute cari_custom.sample_validation.verify

# Regresyon (rapor Git dışında bench/logs altında)
env/bin/python /home/user/Cari/scripts/run_faz15_tests.py \
  --report /home/user/frappe-bench/logs/faz15-acceptance.json
```

Seed `developer_mode=1` ve System Manager/Administrator yetkisi ister. Kamuya açık API olarak whitelist edilmemiştir. Belge kimlikleri `sites/cari.local/private/files/cari-faz15-demo.json` içinde tutulur. Manifest silinmemelidir; kayıtlar işletilirse kabul kontrollerinin güncel değerlerden dolayı başarısız olması normaldir. Script var olan farklı bir ürünü/fiyatı/cari belgesini sessizce değiştirmez.

Hatalar saklanmaz; rollback ve başarısız komut sonucu üretilir. E-posta gönderimi seed/test sırasında susturulur. SMTP kurulmadı, Uyumsoft `aktif=0`; canlı entegrasyon denemesi yapılmadı. Barkod ve SMS geliştirilmedi.

## 8. PostgreSQL uyumluluk notu ve üretim sınırı

Frappe/ERPNext v15 + PostgreSQL sınırlı/deneysel bir kombinasyondur. Bu ortamın ağ/paket sınırlamaları nedeniyle demo bu kombinasyonda çalışır; **üretim için v15 + MariaDB ve desteklenen resmi kurulum önerilir**.

`compat_patches.py` / `postgres_queries.py` içinde **10 hedefli adaptör** vardır: DISTINCT sıralama, GROUP BY/CTE, MySQL IF ifadesi, ödeme isteği eşleştirmesi ve stok zaman sıralaması. Request/job/migrate hook'larında ve test girişinde uygulanırlar. Genel `frappe.get_all`, `get_list`, `sql` fonksiyonları veya stok/muhasebe validasyonları değiştirilmez. MariaDB yolu orijinal fonksiyonlara yönlenir; v16+ üzerinde adaptör kurulmaz. ERPNext çekirdek checkout'u değiştirilmemiştir.

Önceki sayısal `money_in_words` fallback'i kaldırıldı: asıl hata konsolun dil ayarının boş olmasıydı. Dil `tr`, saat dilimi `Europe/Istanbul`, Global Defaults/varsayılan para birimi TRY olarak düzenlendi; hesaplama hataları gizlenmez.

**Üretim öncesinde açık işler:**

- Desteklenen DB/kurulum ve yükseltme/yedekleme geri-dönüş planı
- Gerçek şirket bilgileri, adres/vergi numarası ve muhasebeci onaylı Tekdüzen Hesap Planı
- Demo hesap adının `VAT 18% - CARI` olması tarihî kurulum kalıntısıdır; **hesaplanan oran %20'dir**, ancak nötr/ayrı alış-satış KDV hesap eşlemesi üretimde düzeltilmelidir
- SMTP, PDF, güvenli kimlik bilgileri, HTTPS ve üretim sunucu yapılandırması
- Kendi kayıtlarına erişim/alan bazlı maliyet gizleme ve zimmet/iade onay kuralları
- Uyumsoft ürün/sürüm/erişim onayı; GİB/e-belge kabulü ayrı faz

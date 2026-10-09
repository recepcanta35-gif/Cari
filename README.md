# Cari — Entegre İş Yönetim Sistemi

Stok, saha satış, teklif, cari hesap, tahsilat, sevkiyat ve online sipariş süreçlerini
tek web sistemi üzerinde yöneten proje. **Frappe ERPNext** (ücretsiz, açık kaynak, GPL-3.0)
tabanlı hibrit uyarlama.

## Belgeler

| Belge | İçerik |
|---|---|
| [docs/kapsam-analizi.md](docs/kapsam-analizi.md) | Kapsam ve iş kuralları analizi (18 modül, bağımlılıklar, veri modeli, faz planı) |
| [docs/erpnext-hazir-cozum-degerlendirmesi.md](docs/erpnext-hazir-cozum-degerlendirmesi.md) | ERPNext gap analizi (modül eşleştirmesi, Türkiye/Uyumsoft durumu, maliyet) |
| [docs/cozum-secenekleri-karsilastirmasi.md](docs/cozum-secenekleri-karsilastirmasi.md) | Sıfırdan / ERPNext / WP ERP üçlü kıyası |
| [docs/erpnext-kurulum-rehberi.md](docs/erpnext-kurulum-rehberi.md) | Kurulum rehberi (bu ortam için özel adımlar) |
| [docs/faz-1-5-test-sonuclari.md](docs/faz-1-5-test-sonuclari.md) | Demo belge kimlikleri, stok/cari sonuçları, tekrar çalıştırma ve test raporu |
| [docs/erpnext-kapsam-mimari-kurumsal-uygunluk.md](docs/erpnext-kapsam-mimari-kurumsal-uygunluk.md) | Kullanıcının ek analizi ve teknik/lisans doğrulama notları |

## Depo yapısı

```
docs/                 analiz ve kıyas raporları
apps/
  cari_custom/        zimmet (Stock Assignment), günlük görevlendirme (Daily Assignment),
                      Delivery Note kargo takip alanları (fixture)
  uyumsoft_integration/  Uyumsoft aktarım kuyruğu + UBL-TR taslağı (ürün/sürüm/yetki onayı bekliyor)
frappe-bench/         yerel ERPNext kurulumu (git'e alınmaz — .gitignore)
```

## Hızlı başlangıç

**Kurulum tamamlandı** (9 Ekim 2026) — ERPNext v15.122.0 + PostgreSQL 16 + Redis 7.2.

```bash
cd /home/user/frappe-bench
bench start          # geliştirme sunucusu (0.0.0.0:8000)
# Site: cari.local — yönetici: Administrator / admin
```

Kurulum detayları ve sandbox workaround'ları: [docs/erpnext-kurulum-rehberi.md](docs/erpnext-kurulum-rehberi.md)

## Durum (9 Ekim 2026)

- ✅ **Faz 0–1 tamamlandı:** ERPNext v15 + PostgreSQL + site `cari.local` yayında (0.0.0.0:8000)
- ✅ **Faz 1 — Türkiye yapılandırması:** şirket (Cari A.Ş., TRY), KDV %1/%10/%20, temel tanımlar (birim, grup, bölge, vade, ödeme tipleri, saha deposu), rol matrisi (Saha Personeli), e-posta hatırlatması
- ✅ **Faz 1.5 — demo ve uçtan uca kabul:** 4 ürün, stok girişi, gerçek saha transferi, müşteri, teklif/sipariş/irsaliye/fatura/tahsilat, zimmet ve görev. Ana sitede **199**, sıfırdan test sitesinde **201** kabul kontrolü; iki sitede de **13/13** regresyon testi geçti.
- 🔲 **Sonraki:** zimmet/iade otomasyonu ve kayıt/alan bazlı yetki ayrıntıları (Faz 2); Uyumsoft (ürün/sürüm/yetki onayı sonrası); webshop/portal yapılandırması (ayrı faz).

## Kapsam notları (değiştirilemez)

- Barkod ve SMS modülü yoktur; ürün seçimi ad, ürün kodu, kategori ve fotoğraf üzerinden.
- Uyumsoft bağlantısı; ürün, sürüm ve erişim yetkilerine bağlıdır.
- Online satış kapsamda; geliştirme sırası çekirdek ticari modüllerden sonra.

## Demo kabulünü tekrar çalıştırma

```bash
cd /home/user/frappe-bench
export LD_LIBRARY_PATH=/usr/local/lib/python3.11/dist-packages/pgserver/pginstall/lib
bench --site cari.local execute cari_custom.sample_data.run --kwargs '{"allow_demo": True}'
env/bin/python /home/user/Cari/scripts/run_faz15_tests.py
```

**Yalnızca geliştirme/demo ortamıdır.** Seed için `developer_mode=1` ve yönetici yetkisi gerekir; e-posta gönderilmez ve canlı Uyumsoft bağlantısı açılmaz. Frappe/ERPNext v15 + PostgreSQL sınırlı destekli olduğundan özel sorgu adaptörleri demo içindir. Üretim için desteklenen v15 + MariaDB kurulumu, güvenli kimlik bilgileri, yedekleme ve muhasebeci onayı gereklidir. Ayrıntılar [test raporunda](docs/faz-1-5-test-sonuclari.md).

## Lisans

ERPNext **GPL-3.0**, Frappe Framework **MIT** lisanslıdır. `cari_custom`, ERPNext'ten uyarlanan sorgu kodu içerdiğinden GPL-3.0 olarak işaretlenmiş ve lisans metni eklenmiştir. `uyumsoft_integration` mevcut bağımsız iskeleti MIT olarak işaretlidir; tamamlanan entegrasyonun dağıtım şekli/lisans değerlendirmesi ayrıca yapılmalıdır. İç kullanım ve yazılımı üçüncü kişilere dağıtma koşulları aynı değildir; bu not hukukî görüş değildir.

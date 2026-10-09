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
- 🔲 **Sonraki:** örnek veri + uçtan uca test (ürün → stok → cari → sipariş → fatura → tahsilat); Uyumsoft entegrasyonu (ürün/sürüm/yetki onayı sonrası); online webshop/portal (Faz 5)

## Kapsam notları (değiştirilemez)

- Barkod ve SMS modülü yoktur; ürün seçimi ad, ürün kodu, kategori ve fotoğraf üzerinden.
- Uyumsoft bağlantısı; ürün, sürüm ve erişim yetkilerine bağlıdır.
- Online satış kapsamda; geliştirme sırası çekirdek ticari modüllerden sonra.

# uyumsoft_integration — Uyumsoft Veri Aktarımı (Kapsam Modülü 17)

Kapsam dokümanı koşulu: **Uyumsoft bağlantısı; ürün, sürüm ve erişim yetkilerine bağlıdır.**
Bu uygulama, o koşullar sağlanana kadar entegrasyon iskeletini ve aktarım kuyruğunu hazır tutar.

- `Uyumsoft Settings` (Singleton): bağlantı ayarları, aktarım tercihleri
- `Uyumsoft Transfer Log`: her aktarımın durum kaydı
- `uyumsoft/connector.py`: Uyumsoft REST/SOAP istemcisi (taslak)
- `uyumsoft/ubltr.py`: UBL-TR (e-Fatura/e-Arşiv/e-İrsaliye) eşleme taslağı
- `uyumsoft/sync.py`: Sales Invoice submit/cancel olaylarıyla kuyruk tetikleme

Kurulum: `bench --site <site> install-app uyumsoft_integration`

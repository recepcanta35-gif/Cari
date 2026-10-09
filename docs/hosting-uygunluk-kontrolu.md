# Hostinger Ortamı — ERPNext Kurulum Uygunluk Kontrolü

**Tarih:** 9 Ekim 2026
**Kanıt:** Kullanıcının sağladığı FTP hesapları ve web dosya yöneticisi görüntüleri.

## Görünenler ve görünmeyenler

- Mevcut web sitesi alan adı: `skysoftteknoloji.com.tr`.
- Web kök dizini `public_html`; ERP için `nexterp` adlı bir klasör oluşturulmuş.
- Mevcut sitede WordPress dizinleri ve başka uygulama klasörleri var. Bunlar **silinmez, taşınmaz veya üzerine yazılmaz**. ERP çözümü WordPress/WooCommerce üzerine değiştirilmez.
- Görüntüler FTP/web dosya erişimini gösterir; VPS, root/sudo SSH, Docker, sistem servisleri, Redis veya desteklenen veritabanı çalıştırma yetkisini **kanıtlamaz**.
- Paketin yalnız web/cloud hosting mi yoksa ayrıca VPS de içerip içermediği teyit edilmelidir. Sağlayıcının adı tek başına uygunluk/uygunsuzluk kanıtı değildir.

## Neden FTP klasörü yeterli değil?

ERPNext bir PHP sitesi veya dosyaları `public_html` içine açınca çalışan statik paket değildir. Python/Frappe, MariaDB, Redis, web/worker/scheduler/websocket servisleri, dosya izinleri, kalıcı depolama, ters proxy ve TLS birlikte kurulmalıdır. FTP tek başına bu servisleri kurup yönetemez.

- **Yalnız web/cloud hosting + FTP varsa:** bu klasöre ERPNext yüklenmez. Ayrı bir VPS/dedicated ortam veya Frappe uygulamalarını destekleyen yönetilen ERP barındırma gerekir.
- **Ayrıca VPS varsa:** işletim sistemi, root/sudo erişimi, Docker/Compose, kaynaklar, güvenlik duvarı ve yedekleme teyit edilerek üretim adayı paket uygulanabilir.
- **Yönetilen Frappe hosting varsa:** sağlayıcının özel uygulama, sürüm, worker, scheduler, PDF ve yedek desteği doğrulanır; Docker paketinin aynı şekilde kullanılacağı varsayılmaz.

## Önerilen ayrım

Mevcut site olduğu gibi kalır. ERP için örneğin `erp.skysoftteknoloji.com.tr` veya `nexterp.skysoftteknoloji.com.tr` ayrı sunucu/site olarak yapılandırılır. Subdomain DNS kaydı ancak gerçek hedef IP, kullanıcı tercihi, TLS ve erişim doğrulandıktan sonra değiştirilir.

`skysoftteknoloji.com.tr/nexterp` alt dizininde çalışacağı varsayılmaz; Frappe site/asset/oturum ve proxy yolları için ayrı hostname tercih edilir. PHP yönlendirme dosyası, şifre dosyası veya ERP kaynak arşivi web köküne konmaz.

## Güvenli erişim

- Sohbette paylaşılan parola değiştirilmelidir. Parola burada tekrar edilmez; Git'e, env örneğine, loga veya dokümana kaydedilmez.
- Sunucu yönetimi için tercihen sınırlı operatör hesabı, SSH anahtarı ve doğrulanmış host fingerprint kullanılır. Web FTP parolası root/sudo SSH veya VPS erişimi sayılmaz.
- Parola/SSH private key/API anahtarı sohbete yazılmaz. Operatör/sunucu secret yönetimiyle sağlanır.
- Hostinger paneli bu oturumda doğrudan yönetilebilen bir connector değildir. Mevcut bağlantı yetenekleriyle FTP oturumu açılmadı, dosya yüklenmedi ve DNS/hosting üzerinde değişiklik yapılmadı.

## Sonraki teyit

Hostinger **VPS → Genel Bakış / işletim sistemi** ekranının veya **Hosting Planı** ekranının, parolalar ve anahtarlar görünmeden paylaşılması yeterlidir. Amaç yalnız ortam türünü ve yetkilerini belirlemektir; geliştirme fazlarının onayı tekrar istenmez.

Uygun çalışma ortamı doğrulanmadan üretim teslim kapısı **NO-GO** kalır. Sunucu seçimi/ücretli kaynak oluşturma veya mevcut siteyi değiştirme otomatik yapılmaz.

## Kullanıcının netleştirmesi — SSH açık, ortam VPS değil

Kullanıcı ortamı açıkça **PHP/MySQL bulut hosting, VPS değil** olarak teyit etti. Yeni görüntüde SSH aktif ve bağlantı noktası 65002. Ortam türü tekrar sorulmayacak; FTP/SSH bilgileri yeniden istenmeyecek.

SSH bir erişim yöntemidir; Python web trafiği yönlendirmesi, Redis, kalıcı worker/scheduler/websocket yönetimi veya Docker yetkisi demek değildir. PHP/MySQL'nin bulunması da ERPNext'in Python uygulama katmanının karşılığı değildir. Gerçek sunucuda bu servis yetkileri test edilmedi; yokmuş gibi test sonucu uydurulmaz. Mevcut Docker paketinin VPS/dedicated hedef ön kontrolü, `php_cloud` değerini açıkça reddeder.

**İki ayrı konu vardır:**

1. Seçilen ERPNext mimarisinin uygun bir çalışma ortamına ihtiyacı vardır. Mevcut web sitesini bu hostingte tutup ERP'yi ayrı Frappe destekli yönetilen barındırma veya VPS/dedicated ortamında aynı domainin bir subdomain'i ile sunmak mümkündür. Yeni kaynak/ücret kendiliğinden oluşturulmaz.
2. Bu asistan çalışma ortamından sağlanan IP'ye doğrudan FTP/SSH ağ bağlantısı kurulamıyor. Parolanın paylaşılmış olması bu bağlantı yeteneğini açmaz. Hiçbir oturum, yükleme, DNS değişikliği veya mevcut site değişikliği yapılmadı.

ERP'nin **yalnız bu PHP cloud hesabında** çalışması kesin şart haline gelirse, ERPNext yerine PHP uyumlu farklı bir uygulama/mimari gerekir. Bu önceki ERPNext kararı ve geliştirme kapsamı değişikliğidir; sessizce başka sisteme geçilmez. Mevcut ERPNext geliştirmenin onayı ve bağımsız modül işleri korunur.

Sohbette paylaşılmış parola tekrar edilmez/kaydedilmez; değiştirilmesi önerilir. Bu not veya ön kontrol gerçek hostingte yapılmış servis testi, canlı kurulum ya da anahtar teslim kabulü değildir.


## Salt-okunur runtime envanteri

`deploy/runtime-probe.sh` operatörün mevcut SSH oturumunda çalıştırabileceği bir envanterdir. Sudo kullanmaz, yapılandırma/secret okumaz, dosya yazmaz, servis başlatmaz ve paket kurmaz. Program varlığı; kalıcı servis çalıştırma, Python web yönlendirmesi veya üretim uygunluğu kanıtı değildir. Sunucunuzda bu script çalıştırılmadı; yalnız shell sözdizimi bu çalışma ortamında kontrol edildi.

Operatör SSH terminaline script içeriğini yapıştırabilir veya web kökü dışında kendi home dizinine alıp `bash runtime-probe.sh` çalıştırabilir. Çıktı paylaşılabilir; parola, private key, env/site_config veya phpMyAdmin bağlantı sırları paylaşılmaz. Host key fingerprint'i yeni bağlantıda sağlayıcıyla doğrulanmalıdır.


## Yeni ERP alan adı ve veritabanı görüntüsü

Kullanıcı `nexterp.skysoftteknoloji.com.tr` subdomain'inin açıldığını bildirdi. Hedef site/alan adı hazırlık şablonunda bu değerle güncellendi; DNS/TLS bu oturumdan doğrulanmadı. Klasör görüntüsünde yalnız `default.php` görülüyor; içeriği okunmadı ve dosya değiştirilmedi. Bu dosya ERPNext kurulum kanıtı değildir.

MySQL görüntüsü veritabanı/kullanıcı oluşturma formunu gösterir; başarılı oluşturma/listede görünme veya DB erişimi teyit edilmedi. phpMyAdmin adresi alınmıştır ancak oturum açılmamıştır. Parola/SSH/FTP/DB sırları bu dokümana, örnek dosyaya veya Git'e alınmaz; parola yeniden paylaşılmaz.

Bu çalışma ortamının dış ağ kapsamı verilen IP/SSH/FTP ve Hostinger HTTPS hedeflerini içermez. Hiçbir ağ kısıtı dolanılmadı, başka servise parola aktarılmadı, bağlantı denendi ya da oturum açıldı iddiasında bulunulmadı. Mevcut site, klasör ve DB üzerinde değişiklik yapılmadı. Operatör tarafında güvenli erişimle çalışma veya bu hedeflere erişebilen yetkili dağıtım ortamı gerekir. PHP cloud ortamına ERPNext runtime hizmetleri mevcutmuş gibi yükleme yapılmaz.

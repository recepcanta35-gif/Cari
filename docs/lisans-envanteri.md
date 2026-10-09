# Lisans ve Kaynak Devir Envanteri

## Birincil uygulamalar

| Bileşen | Lisans | Kaynak / sürüm |
|---|---|---|
| Frappe Framework | MIT | frappe/frappe, v15.122.0; CI sabit tag |
| ERPNext | GPL-3.0 | frappe/erpnext, v15.122.0; resmî imaj ve kaynak |
| cari_custom | GPL-3.0 | `apps/cari_custom/license.txt`; ERPNext kaynak adaptasyonlarında atıf |
| uyumsoft_integration iskeleti | MIT olarak işaretli | Bağımsız prototip; tamamlanmış adaptör/dağıtım ilişkisi ayrıca incelenir |
| MariaDB / Redis / Caddy / Python / Node / işletim sistemi ve Python/npm bağımlılıkları | Kendi sürüm lisansları | Kullanılan tam imaj digest ve lock/dependency envanterinde ayrı toplanmalı |

ERP lisans anahtarı, kullanıcı başına ücret veya sunucu/şube sayısına özel yapay kullanım sınırı eklenmez. Lisanssız üçüncü taraf ticari bileşen dahil edilmez. Yazılımın ücretsiz lisansı; sunucu, alan adı, e-posta, bakım ve özel entegratör maliyetlerini ortadan kaldırmaz.

## Son teslimde gerekli kayıtlar

- Kaynak dalı ve release SHA/tag, imaj digest, Python/npm bağımlılık sürümleri ve makinece okunur SBOM
- GNU GPL metni, Frappe MIT metni, kaynak atıfları ve diğer dağıtılan bileşenlerin NOTICE/lisans metinleri
- Uyumsoft/SMTP/ödeme sağlayıcısı sözleşme ve kullanım yetkisi (secret içermeden)
- Kodun şirket içinde işletilmesi, barındırılması, kopyasının dağıtılması veya türevlerinin üçüncü kişilere verilmesi için uygun lisans değerlendirmesi

Bu dosya **tam bağımlılık SBOM'u veya hukukî onay değildir**. İmaj build/SBOM/tarama ve lisans/dağıtım incelemesi T0/T8/T9 kapılarında tamamlanır. “Çekirdeği satmıyoruz” ifadesi bütün GPL dağıtım yükümlülüklerini ortadan kaldırmaz; genel kamuya yayın ve kopya alıcılarına kaynak sağlama aynı yükümlülük değildir. Lisans ve sözleşme incelemesinde yetkili danışman gerekir.

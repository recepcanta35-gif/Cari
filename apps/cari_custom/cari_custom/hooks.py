app_name = "cari_custom"
app_title = "Cari Custom"
app_publisher = "Cari"
app_description = "Personel stok zimmeti, gunluk gorevlendirme ve kargo takibi ozel gelistirmeleri"
app_email = "info@cari.local"
app_license = "GPL-3.0"

# Kapsam disi: barkod ve SMS modulu yoktur (is kuralı)

fixtures = [
	{
		"dt": "Custom Field",
		"filters": [
			["name", "in", ["Delivery Note-kargo_firma", "Delivery Note-kargo_takip_no"]]
		],
	}
]

# Geliştirme sitelerinde v15/PostgreSQL adaptörleri (MariaDB/v16 çekirdeğe yönlenir).
before_request = ["cari_custom.compat_patches.install"]
before_job = ["cari_custom.compat_patches.install"]
before_migrate = ["cari_custom.compat_patches.install"]

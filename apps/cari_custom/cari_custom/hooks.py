app_name = "cari_custom"
app_title = "Cari Custom"
app_publisher = "Cari"
app_description = "Personel stok zimmeti, gunluk gorevlendirme ve kargo takibi ozel gelistirmeleri"
app_email = "info@cari.local"
app_license = "MIT"

# Kapsam disi: barkod ve SMS modulu yoktur (is kuralı)

fixtures = [
	{
		"dt": "Custom Field",
		"filters": [
			["name", "in", ["Delivery Note-kargo_firma", "Delivery Note-kargo_takip_no"]]
		],
	}
]

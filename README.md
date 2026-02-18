# MF v5.1 Prosedürel Mimari Motoru (Blender 5.0.1)

MF v5.1, Blender 5.0.1 ve Godot Engine için tasarlanmış, **mühendislik standartlarında** bir prosedürel varlık üretim ve yönetim sistemidir. Geleneksel mesh üretiminin ötesine geçerek, deterministik matematiksel kurallar, slot tabanlı yerleştirme ve JSON komut sistemi ile çalışır.

## 🚀 Yeni Nesil Mimari
Bu proje, aşağıdaki mühendislik prensipleri üzerine inşa edilmiştir:
- **Deterministik RNG Zinciri:** Alt-sistem bazlı bağımsız seed yönetimi.
- **Altın Oran (Golden Ratio):** Estetik ve işlevsel BSP bölünmeleri.
- **Euler Manifold Kontrolü:** Matematiksel olarak doğrulanmış kusursuz geometri.
- **Slot Sistemi:** Varlıklar arası akıllı bağlantı noktaları.

## 📖 Dokümantasyon
- [Dönüşüm Planı](docs/PLAN.md)
- [Görev Takibi](docs/TODO.md)


## Özellikler

- **Deterministik Üretim:** Aynı `seed` değeri her zaman aynı binayı üretir.
- **Blender 5.0.1 Entegrasyonu:** En yeni `bpy` ve `bmesh` API'leri ile tam uyumlu.
- **Manifold Geometri:** İç yüzeylerden (internal faces) arındırılmış, oyun motoru dostu mesh yapısı.
- **Godot Hazır:** Otomatik collider (`-col` suffix) ve manifest üretimi.
- **Gelişmiş Çatı Tipleri:** Hip, Gabled, Shed ve Flat çatı desteği.

## Kurulum

1. **Blender 5.0.1+** yüklü olduğundan emin olun.
2. Bağımlılıkları yükleyin (Blender dışı testler için):
   ```bash
   pip install -r requirements.txt
   ```

## Kullanım Örneği (API)

```python
from pathlib import Path
from mf_v5 import BuildingSpec, RoofType, generate

# Bina özelliklerini tanımlayın
spec = BuildingSpec(
    width=20.0,      # Genişlik (metre)
    depth=16.0,      # Derinlik (metre)
    floors=3,        # Kat sayısı
    seed=12345,      # Deterministik üretim için anahtar
    roof_type=RoofType.GABLED
)

# Üretimi başlatın (Blender içinde çalıştırılmalıdır)
output_dir = Path("./output")
result = generate(spec, output_dir)

print(f"Bina üretildi: {result.glb_path}")
print(f"Kat planı detayları: {result.floors}")
```

## Seed Parametresi ve Determinizm

`BuildingSpec` içindeki `seed` parametresi, binanın tüm rastgele süreçlerini (oda bölünmeleri, kapı konumları) kontrol eder. 
- Aynı `seed` değeri, farklı zamanlarda veya farklı makinelerde çalıştırılsa bile **birebir aynı** kat planını ve geometriyi üretir.
- Kat planı çeşitliliği için farklı tamsayılar (integer) kullanın.

## Hata Yönetimi ve Logging

Sistem, hataları yakalamak için özel istisnalar (`exceptions.py`) ve detaylı bir logging mekanizması kullanır.

- **Debug Modu:** `MF_DEBUG=1` ortam değişkenini ayarlayarak detaylı üretim loglarını görebilirsiniz.
- **Exceptions:** `GenerationError`, `GeometryError`, `ExportError` gibi spesifik hata tipleri ile süreçleri kontrol edebilirsiniz.

## Testler

Unit testleri çalıştırmak için:
```bash
pytest tests/
```

## Klasör Yapısı

- `mf_v5/`: Ana motor modülleri.
- `tests/`: Kapsamlı unit testleri.
- `output/`: Üretilen GLB ve manifest dosyaları.
- `requirements.txt`: Bağımlılık listesi.

## Lisans

MIT License.

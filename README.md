# 🏗️ BlenPC v5.1.1 (Optimized)

BlenPC, **Blender 5.0.1+** ve **Godot Engine** için tasarlanmış, mühendislik standartlarında bir prosedürel bina ve varlık üretim motorudur. Deterministik matematiksel kurallar, akıllı slot yerleştirme ve JSON komut sistemi ile çalışır.

---

## 🏛️ Mimari Yapı

Proje, katmanlı ve modüler bir yapıda organize edilmiştir:

### 📂 Klasör Organizasyonu
| Dizin / Dosya | Sorumluluk Alanı |
| :--- | :--- |
| `src/blenpc/` | Ana Paket (Source) |
| `├── atoms/` | Temel Yapı Taşları (Wall, Window, Door) |
| `├── engine/` | Envanter ve Slot Yerleştirme Motoru |
| `├── mf_v5/` | Prosedürel Bina Üretim Mantığı |
| `├── config.py` | Merkezi Ayarlar ve Path Yönetimi |
| `├── cli.py` | Komut Satırı Arayüzü (CLI) |
| `└── run_command.py` | Blender Bridge Script |
| `_library/` | Üretilen `.blend` Varlık Kütüphanesi |
| `_registry/` | JSON Tabanlı Varlık Envanteri (Inventory) |
| `output/` | Final Çıktılar (GLB, Manifest) |

---

## 🚀 Temel Özellikler

- **Deterministik Üretim:** Aynı `seed` değeri ile her zaman aynı binayı üretir.
- **Slot Sistemi:** Varlıklar üzerinde matematiksel olarak hesaplanmış bağlantı noktaları.
- **Godot Uyumluluğu:** Otomatik collider ve manifest üretimi.
- **Manifold Geometri:** Euler formülü (**V - E + F = 2**) ile geometri doğrulaması.
- **Windows 11 Desteği:** Blender yolu otomatik keşfi ve path optimizasyonu.

---

## 💻 CLI Kullanımı

BlenPC, JSON komut sistemi üzerinden kontrol edilir.

### 🏢 Bina Üretimi
```bash
# JSON parametreleri ile üretim
python src/blenpc/cli.py generate --width 20 --depth 16 --floors 3 --seed 42 --roof gabled
```

### 📦 Varlık Kaydı ve Denetleme
```bash
python src/blenpc/cli.py registry list
python src/blenpc/cli.py inspect output/Building.glb
```

---

## 🔧 Kurulum

1. **Blender 5.0.1+** yüklü olduğundan emin olun.
2. Repoyu klonlayın ve bağımlılıkları yükleyin:
   ```bash
   git clone https://github.com/ozyorionlast-cloud/blenpc-5.0-optimized
   pip install -r requirements.txt
   ```

---

## 📄 Lisans
MIT License.

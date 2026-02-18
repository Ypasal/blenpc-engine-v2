# 📚 BlenPC v5.1.1 API Teknik Referansı

Bu doküman, **BlenPC v5.1.1 (Expert Edition)** paketinin modüler yapısını, sınıflarını ve fonksiyonlarını teknik düzeyde açıklar.

---

## 🏗️ 1. Paket Yapısı (Package Hierarchy)

BlenPC, modern `src/blenpc` hiyerarşisini kullanır. Tüm modüller `blenpc` ana paketi altında toplanmıştır.

| Modül | Dosya Yolu | Sorumluluk |
| :--- | :--- | :--- |
| **Config** | `blenpc.config` | Merkezi ayarlar, path yönetimi ve i18n. |
| **Atoms** | `blenpc.atoms.wall` | Temel geometri üretimi ve manifold kontrolü. |
| **Inventory** | `blenpc.engine.inventory_manager` | Varlık kaydı, kilitleme ve arama. |
| **Slots** | `blenpc.engine.slot_engine` | Akıllı yerleştirme ve AABB hesaplama. |
| **Core** | `blenpc.mf_v5.engine` | Bina üretim boru hattı (pipeline). |
| **Models** | `blenpc.mf_v5.datamodel` | Veri modelleri ve tip tanımlamaları. |

---

## ⚙️ 2. Yapılandırma (`blenpc.config`)

Merkezi ayarlar bu modülde toplanmıştır.

### Önemli Sabitler
- **`GRID_UNIT`**: `0.25` (Metre cinsinden modüler ızgara birimi).
- **`STORY_HEIGHT`**: `3.0` (Standart kat yüksekliği).
- **`PHI`**: `1.618...` ( BSP bölmeleri için Altın Oran sabiti).
- **`EXPORT_PRECISION`**: `4` (Koordinat yuvarlama hassasiyeti).
- **`AUTO_BACKUP_REGISTRY`**: `True` (Her asset kaydında otomatik yedekleme).

### Fonksiyonlar
- **`get_blender_path()`**: Windows/Linux/MacOS için Blender yolunu otomatik keşfeder.
- **`get_settings()`**: Tüm aktif ayarları bir `dict` olarak döndürür.

---

## 🧱 3. Geometri Motoru (`blenpc.atoms.wall`)

Temel mesh üretim fonksiyonlarını barındırır.

### Fonksiyonlar
- **`create_engineered_wall(name, length, seed)`**:
  - `name`: Varlık adı.
  - `length`: Duvar uzunluğu (metre).
  - `seed`: Deterministik üretim için anahtar.
  - **Döndürür**: `(bpy_object, slots_list)`.
- **`check_manifold(bm)`**: Euler formülü (**V - E + F = 2**) ile geometri doğruluğunu denetler.
- **`golden_split(length, rng)`**: Uzunluğu Altın Oran'a göre böler ve ızgaraya (`GRID_UNIT`) sabitler.

---

## 🗃️ 4. Varlık Yönetimi (`blenpc.engine.inventory_manager`)

JSON tabanlı envanter sistemini yönetir.

### `InventoryManager` Sınıfı
- **`register_asset(asset_data)`**: Yeni bir varlığı `inventory.json` dosyasına güvenli bir şekilde kaydeder.
- **`acquire_lock()`**: Dosya çakışmalarını önlemek için güvenli bir dosya kilidi (lock) oluşturur.
- **`find_asset(tags)`**: Belirtilen etiketlere (tags) sahip ilk varlığı bulur.

---

## 🏠 5. Bina Üretimi (`blenpc.mf_v5.engine`)

En üst seviye üretim mantığını yönetir.

### Fonksiyonlar
- **`generate(spec, output_dir)`**:
  - `spec`: `BuildingSpec` nesnesi.
  - `output_dir`: Çıktı dizini.
  - **Döndürür**: `GenerationOutput` nesnesi (GLB yolu ve manifest bilgisi ile).

---

## 📊 6. Veri Modelleri (`blenpc.mf_v5.datamodel`)

### `BuildingSpec` (Dataclass)
Bina üretim parametrelerini tanımlar:
- `width`: Genişlik.
- `depth`: Derinlik.
- `floors`: Kat sayısı.
- `seed`: Üretim anahtarı.
- `roof_type`: `RoofType` (FLAT, GABLED, HIP, SHED).

---

*Teknik sorularınız için lütfen [GitHub Issues](https://github.com/ozyorionlast-cloud/blenpc-5.0-optimized/issues) üzerinden iletişime geçin.*

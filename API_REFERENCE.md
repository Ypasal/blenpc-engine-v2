# MF v5.1 API Referansı

Bu doküman, MF v5.1 motorundaki ana sınıfları, fonksiyonları ve parametreleri detaylandırır.

## 1. Veri Yapıları (`datamodel.py`)

### `BuildingSpec`
Bina üretim parametrelerini tanımlayan ana sınıftır.

| Parametre | Tip | Varsayılan | Açıklama |
|-----------|-----|------------|----------|
| `width` | `float` | - | Binanın X eksenindeki genişliği (metre, min: 5m). |
| `depth` | `float` | - | Binanın Y eksenindeki derinliği (metre, min: 5m). |
| `floors` | `int` | `1` | Kat sayısı (1-100). |
| `seed` | `int` | `0` | Deterministik üretim için rastgelelik anahtarı. |
| `roof_type` | `RoofType` | `RoofType.FLAT` | Çatı tipi (Enum). |

### `RoofType` (Enum)
Desteklenen çatı tipleri:
- `RoofType.FLAT`: Düz çatı.
- `RoofType.HIP`: Kırma çatı.
- `RoofType.GABLED`: Beşik çatı.
- `RoofType.SHED`: Tek yöne eğimli çatı.

## 2. Ana Motor (`mf_v5/engine.py`)

### `generate(spec: BuildingSpec, output_dir: Path) -> GenerationOutput`
Binayı belirtilen özelliklere göre üretir ve GLB olarak dışa aktarır.

- **Parametreler:**
  - `spec`: `BuildingSpec` nesnesi.
  - `output_dir`: Çıktıların kaydedileceği dizin.
- **Dönüş Değeri (`GenerationOutput`):**
  - `floors`: Kat istatistikleri listesi (`FloorOutput`).
  - `glb_path`: Üretilen GLB dosyasının yolu.
  - `export_manifest`: Üretim detaylarını içeren JSON dosyasının yolu.

## 3. Temel Bileşenler (`atoms/wall.py`)

### `create_engineered_wall(name: str, length: float, seed: int = 0)`
Matematiksel olarak yerleştirilmiş slotlara sahip bir duvar nesnesi oluşturur.

- **Parametreler:**
  - `name`: Varlık adı.
  - `length`: Duvar uzunluğu (metre).
  - `seed`: Slot yerleşimi için seed.

## 4. Varlık Yönetimi (`engine/inventory_manager.py`)

### `InventoryManager.find_asset(tags: List[str]) -> Optional[Dict]`
Belirtilen etiketlerin tamamına sahip bir varlığı envanterde arar.

### `InventoryManager.register_asset(asset_data: Dict)`
Yeni bir varlığı envantere kaydeder (Dosya kilidi kullanarak).

## 5. Konfigürasyon Sabitleri (`config.py`)

Global ayarlar ve limitler:
- `GRID_UNIT`: Modüler ızgara birimi (0.25m).
- `STORY_HEIGHT`: Kat yüksekliği (3.0m).
- `WALL_THICKNESS_BASE`: Temel duvar kalınlığı (0.2m).
- `GOLDEN_RATIO_VARIATION`: Altın oran sapma payı (0.04).
- `INVENTORY_LOCK_TIMEOUT`: Envanter kilit zaman aşımı (5s).

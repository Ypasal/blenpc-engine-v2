# 📚 BlenPC v5.2.0 API Teknik Referansı

Bu doküman, **BlenPC v5.2.0 (Modular Grid System)** paketinin modüler yapısını, sınıflarını ve fonksiyonlarını teknik düzeyde açıklar.

---

## 🏗️ 1. Paket Yapısı (Package Hierarchy)

BlenPC, modern `src/blenpc` hiyerarşisini kullanır. Tüm modüller `blenpc` ana paketi altında toplanmıştır.

| Modül | Dosya Yolu | Sorumluluk |
| :--- | :--- | :--- |
| **Config** | `blenpc.config` | Merkezi ayarlar, path yönetimi, grid standartları ve i18n. |
| **Engine** | `blenpc.engine.*` | Grid sistemi, obje yönetimi ve oda tespiti. |
| **Atoms** | `blenpc.atoms.*` | Temel modüler geometri üretimi (duvar, kapı, pencere). |
| **Inventory** | `blenpc.engine.inventory_manager` | Varlık kaydı, kilitleme ve arama. |
| **Core** | `blenpc.mf_v5.engine` | Bina üretim boru hattı (pipeline). |
| **Models** | `blenpc.mf_v5.datamodel` | Veri modelleri ve tip tanımlamaları. |

---

## ⚙️ 2. Yapılandırma (`blenpc.config`)

Merkezi ayarlar ve mimari standartlar bu modülde toplanmıştır.

### Önemli Sabitler
- **`MICRO_UNIT`**: `0.025` (Metre cinsinden en küçük grid birimi, 2.5 cm).
- **`SNAP_MODES`**: Grid snap modları (`micro`, `meso` (0.25m), `macro` (1.0m)).
- **`GRID_UNIT`**: `0.25` (Eski sistemle uyumluluk için korunan modüler ızgara birimi).
- **`STORY_HEIGHT`**: `3.0` (Standart kat yüksekliği).
- **`WALL_THICKNESS_BASE`**: `0.2` (Standart duvar kalınlığı).
- **`DOOR_STANDARDS`**: Farklı kapı stilleri için genişlik ve yükseklik standartları (`single`, `double`, `garage`).
- **`WINDOW_STANDARDS`**: Farklı pencere stilleri için genişlik, yükseklik ve denizlik yüksekliği standartları (`small`, `standard`, `large`, `panoramic`).
- **`PHI`**: `1.618...` (BSP bölmeleri için Altın Oran sabiti).
- **`EXPORT_PRECISION`**: `4` (Koordinat yuvarlama hassasiyeti).
- **`AUTO_BACKUP_REGISTRY`**: `True` (Her asset kaydında otomatik yedekleme).

### Fonksiyonlar
- **`get_blender_path()`**: Windows/Linux/MacOS için Blender yolunu otomatik keşfeder.
- **`get_settings()`**: Tüm aktif ayarları bir `dict` olarak döndürür.

---

## 🚀 3. Grid ve Obje Yönetimi (`blenpc.engine`)

Yeni tamsayı grid sistemi ve obje yönetimini içerir.

### `blenpc.engine.grid_pos`
- **`GridPos(x, y, z)`**: Tamsayı koordinatları temsil eden sınıf. Metre ve birim dönüşümleri sağlar.
  - **`from_meters(x, y, z, snap)`**: Metre cinsinden koordinatları `GridPos`'a dönüştürür ve belirtilen snap moduna göre hizalar.
  - **`to_meters()`**: `GridPos`'u metre cinsinden koordinatlara dönüştürür.

### `blenpc.engine.grid_object`
- **`IGridObject`**: Grid sistemine entegre olacak objeler için arayüz (Protocol).
  - `name`, `grid_pos`, `grid_size`, `snap_mode`, `slots`, `tags` gibi temel özellikleri tanımlar.
- **`GridObjectMixin`**: `IGridObject` arayüzünü uygulayan sınıflar için yardımcı mixin.
  - **`get_footprint()`**: Objenin grid üzerindeki kapladığı hücreleri döndürür.
  - **`get_aabb()`**: Objenin Axis-Aligned Bounding Box (AABB) değerlerini döndürür.
  - **`get_center()`**: Objenin merkez `GridPos`'unu döndürür.

### `blenpc.engine.grid_manager`
- **`SceneGrid()`**: Tüm objeleri yöneten ve çakışma kontrolü yapan sparse hashmap tabanlı grid yöneticisi.
  - **`place(obj: IGridObject)`**: Bir objeyi grid'e yerleştirir. Çakışma varsa `False` döndürür.
  - **`remove(obj_name)`**: Bir objeyi grid'den kaldırır.
  - **`get_at(pos: GridPos)`**: Belirtilen `GridPos`'taki objenin adını döndürür.
  - **`get_stats()`**: Grid'deki obje sayısı, dolu hücre sayısı gibi istatistikleri döndürür.

### `blenpc.engine.room_detector`
- **`RoomData`**: Tespit edilen oda verilerini tutan dataclass.
- **`RoomDetector(grid: SceneGrid)`**: `SceneGrid` üzerindeki duvarlardan odaları tespit eder.
- **`auto_complete_room(walls: List[WallData))`**: Verilen duvar listesinden otomatik olarak bir oda objesi oluşturur, alan hesaplar ve zemin/tavan metadata üretir.

---

## 🧱 4. Modüler Atomlar (`blenpc.atoms`)

Temel modüler geometri üretim fonksiyonlarını barındırır.

### `blenpc.atoms.wall_modular`
- **`WallSegment`**: Duvarın 0.25m'lik bir segmentini temsil eder.
- **`Opening`**: Kapı veya pencere açıklığını tanımlar.
- **`WallData`**: Duvarın tüm verilerini (segmentler, slotlar, metadata) içeren dataclass.
- **`build_wall(length, height, thickness, openings, name, seed)`**: Segment tabanlı, pre-cut mimariye sahip bir duvar oluşturur.
- **`build_wall_composed(wall_spec, opening_specs, name, seed)`**: Duvar, kapı ve pencereleri tek bir komutla entegre bir şekilde oluşturur. Kapı ve pencereler duvarın child objeleri olarak yönetilir (Hierarchical Placement).
- **`generate_wall_mesh(wall_data)`**: `WallData`'dan Blender mesh objesi üretir (sadece engellenmemiş segmentler).
- **`wall_to_json(wall_data)`**: Duvar verilerini JSON formatına serileştirir.
- **`create_engineered_wall(name, length, seed)`**: Eski API ile uyumluluk için basit bir duvar oluşturur (dahili olarak yeni sistemi kullanır).

### `blenpc.atoms.door`
- **`DoorData`**: Kapının tüm verilerini (parçalar, slotlar, metadata) içeren dataclass.
- **`build_door(style, material, swing, name, position)`**: 4 parçalı anatomiye sahip modüler bir kapı oluşturur (`frame_jamb_left`, `frame_jamb_right`, `frame_head`, `door_leaf`).
- **`generate_door_mesh(door_data)`**: `DoorData`'dan Blender mesh objesi üretir (her parça için ayrı obje, ana objeye parent edilir).
- **`door_to_json(door_data)`**: Kapı verilerini JSON formatına serileştirir.
- **`DOOR_MATERIALS`**: Farklı kapı malzemeleri için Blender shader özellikleri.

### `blenpc.atoms.window`
- **`WindowData`**: Pencerenin tüm verilerini (parçalar, slotlar, metadata) içeren dataclass.
- **`build_window(style, frame_material, frame_color, glass_inner, glass_outer, has_sill, name, position)`**: 3 parçalı anatomiye sahip modüler bir pencere oluşturur (`frame_outer`, `frame_inner`, `glass_pane`).
- **`generate_window_mesh(window_data)`**: `WindowData`'dan Blender mesh objesi üretir (her parça için ayrı obje, ana objeye parent edilir).
- **`window_to_json(window_data)`**: Pencere verilerini JSON formatına serileştirir.
- **`GLASS_MATERIALS`**: Farklı cam malzemeleri için Blender shader özellikleri.

---

## 🗃️ 5. Varlık Yönetimi (`blenpc.engine.inventory_manager`)

JSON tabanlı envanter sistemini yönetir.

### `InventoryManager` Sınıfı
- **`register_asset(asset_data)`**: Yeni bir varlığı `inventory.json` dosyasına güvenli bir şekilde kaydeder.
- **`acquire_lock()`**: Dosya çakışmalarını önlemek için güvenli bir dosya kilidi (lock) oluşturur.
- **`find_asset(tags)`**: Belirtilen etiketlere (tags) sahip ilk varlığı bulur.

---

## 🏠 6. Bina Üretimi (`blenpc.mf_v5.engine`)

En üst seviye üretim mantığını yönetir.

### Fonksiyonlar
- **`generate(spec, output_dir)`**:
  - `spec`: `BuildingSpec` nesnesi.
  - `output_dir`: Çıktı dizini.
  - **Döndürür**: `GenerationOutput` nesnesi (GLB yolu ve manifest bilgisi ile).

---

## 📊 7. Veri Modelleri (`blenpc.mf_v5.datamodel`)

### `BuildingSpec` (Dataclass)
Bina üretim parametrelerini tanımlar:
- `width`: Genişlik.
- `depth`: Derinlik.
- `floors`: Kat sayısı.
- `seed`: Üretim anahtarı.
- `roof_type`: `RoofType` (FLAT, GABLED, HIP, SHED).

---

## 📝 8. Ek Dokümantasyon

- **`COLLISION_PROBLEM_ANALYSIS.md`**: Composed Wall entegrasyonundaki collision probleminin detaylı analizi ve **hierarchical placement** ile çözümü. Archimesh, Archipack ve Geometry Nodes gibi araçların bu tür collision problemlerini çözemediği vurgulanmıştır.
- **`PROGRESS_SUMMARY.md`**: Projenin genel ilerlemesi ve tamamlanan fazların özeti.
- **`CHANGELOG.md`**: Tüm sürüm değişikliklerinin kronolojik listesi.

---

*Teknik sorularınız için lütfen [GitHub Issues](https://github.com/altlastozorion-crypto/blenpc-5.0-optimized/issues) üzerinden iletişime geçin.*

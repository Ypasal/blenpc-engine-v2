# BlenPC 5.0 - Modüler Duvar/Kapı/Pencere Sistemi Geliştirme Planı

## Proje Özeti

Bu doküman, BlenPC 5.0 için modüler slot-based duvar, kapı ve pencere sisteminin tam geliştirme planını içermektedir. Sistem, Sims 4 build mode'undan esinlenerek grid-based snap sistemi, otomatik oda algılama ve modüler assembly pipeline'ı sunacaktır.

---

## Mevcut Durum Analizi

### Güçlü Yönler
- ✅ Deterministik üretim sistemi (seed-based)
- ✅ Manifold geometri kontrolü (Euler formülü: V - E + F = 2)
- ✅ JSON komut pipeline'ı
- ✅ Slot sistemi temel altyapısı
- ✅ Godot uyumlu GLB export
- ✅ Registry ve inventory sistemi

### Geliştirme Gerektiren Alanlar
- ❌ Duvar segment sistemi yok (tek mesh olarak üretiliyor)
- ❌ Pre-cut opening sistemi yok (boolean operations kullanılıyor)
- ❌ Modüler kapı/pencere anatomisi eksik
- ❌ Sims-tarzı grid snap sistemi yok
- ❌ Otomatik oda algılama yok
- ❌ MCP entegrasyonu yok

---

## Teknik Gereksinimler

### 1. Grid Sistemi (Sims-Inspired)
```python
SNAP_MODES = {
    "full":    1.00,  # 1m
    "half":    0.50,  # 50cm
    "quarter": 0.25,  # 25cm (mevcut GRID_UNIT)
    "free":    None   # sadece collision kontrolü
}
```

### 2. Standart Boyutlar (ISO 2848 + Oyun Standardı)
```python
WALL_STANDARDS = {
    "height":    {"min": 2.4, "default": 3.0,  "max": 4.5,  "step": 0.25},
    "thickness": {"thin": 0.1, "standard": 0.2, "thick": 0.3},
}

DOOR_STANDARDS = {
    "single":  {"w": 0.9,  "h": 2.1},
    "double":  {"w": 1.8,  "h": 2.1},
    "garage":  {"w": 2.4,  "h": 2.4},
}

WINDOW_STANDARDS = {
    "small":   {"w": 0.6,  "h": 0.6,  "sill": 1.2},
    "standard":{"w": 1.2,  "h": 1.4,  "sill": 0.9},
    "large":   {"w": 1.8,  "h": 1.6,  "sill": 0.8},
    "panoramic":{"w": 2.4, "h": 1.8,  "sill": 0.6},
}
```

### 3. Duvar Segment Sistemi
Duvar artık tek mesh değil, segment listesi:
```
Duvar = [SEG][SEG][SEG][   ][   ][SEG][SEG][SEG]
                         ↑kapı/pencere bölgesi
```

Her segment:
- 0.25m grid'e snap edilmiş
- `blocked` flag'i (opening için boşluk)
- `type` (wall/door/window)

### 4. Kapı Anatomisi (4 Zorunlu Part + 1 Opsiyonel)
```
frame_jamb_left   → sol kasa profili
frame_jamb_right  → sağ kasa profili
frame_head        → üst kasa (lento)
door_leaf         → kapı kanadı (değiştirilebilir)
[threshold]       → eşik (opsiyonel)
```

Slot'lar:
- `wall_interface` → duvarın opening_slot'una takılır
- `doorknob` → kol/kolp
- `hinge_top`, `hinge_bot` → menteşeler

### 5. Pencere Anatomisi (3 Zorunlu Part + 2 Cam Tipi)
```
frame_outer   → dış çerçeve
frame_inner   → iç çerçeve
glass_pane    → cam (inner/outer material farklı olabilir)
[sill_ext]    → dış denizlik (opsiyonel)
[sill_int]    → iç denizlik (opsiyonel)
```

Cam material seçenekleri:
- `transparent` → şeffaf cam (alpha: 0.05)
- `mirror` → ayna cam (metallic: 1.0)
- `frosted` → buzlu cam (roughness: 0.6)
- `tinted` → renkli cam

---

## Geliştirme Fazları

### FAZ 1: Temel Altyapı
**Hedef:** Config ve standartları ekle, mevcut kodu analiz et

**Dosyalar:**
- `src/blenpc/config.py` → WALL/DOOR/WINDOW_STANDARDS ekle
- `src/blenpc/mf_v5/config.py` → SNAP_MODES ekle

**Çıktı:** Güncellenmiş config dosyaları

---

### FAZ 2: Modüler Duvar Sistemi
**Hedef:** Segment-based pre-cut duvar üretimi

**Dosyalar:**
- `src/blenpc/atoms/wall.py` → Tamamen yeniden yaz
  - `build_wall(length, height, thickness, openings)`
  - Segment listesi üretimi
  - Opening slot hesaplama
  - Manifold-safe mesh üretimi

**Fonksiyonlar:**
```python
def build_wall(length, height, thickness=0.2, openings=None):
    """
    openings = [
      {"type": "door",   "center_x": 1.5, "width": 0.9, "height": 2.1, "sill": 0.0},
      {"type": "window", "center_x": 3.0, "width": 1.2, "height": 1.4, "sill": 0.9},
    ]
    
    Döner: {
      "segments": [...],
      "slots": [...],
      "meta": {...}
    }
    """
```

**Test:** `tests/test_wall_precut.py`

---

### FAZ 3: Modüler Kapı Sistemi
**Hedef:** 4-part kapı anatomisi + slot sistemi

**Dosyalar:**
- `src/blenpc/atoms/door.py` → Yeni dosya
  - `build_door(style, material, swing)`
  - `build_jamb(height, side)`
  - `build_head(width)`
  - `build_leaf(width, height, thickness, material)`

**Slot Tanımları:**
```python
wall_interface_slot = {
    "id":   "wall_interface",
    "type": "door_opening",
    "pos":  [W/2, 0, H/2],
    "size": [W, H]
}

accessory_slots = [
    {"id": "doorknob", "type": "door_hardware", ...},
    {"id": "hinge_top", "type": "door_hinge", ...},
    {"id": "hinge_bot", "type": "door_hinge", ...},
]
```

**Test:** `tests/test_door_modular.py`

---

### FAZ 4: Modüler Pencere Sistemi
**Hedef:** 3-part pencere anatomisi + dual material cam

**Dosyalar:**
- `src/blenpc/atoms/window.py` → Yeni dosya
  - `build_window(style, frame_mat, glass_inner, glass_outer)`
  - `build_window_frame(w, h, material, color)`
  - `build_glass(w, h, inner_mat, outer_mat, materials_dict)`
  - `build_sill(width, ext=True)`

**Cam Material Sistemi:**
```python
glass_materials = {
    "transparent": {"alpha": 0.05, "ior": 1.45, "roughness": 0.0},
    "mirror":      {"alpha": 0.0,  "metallic": 1.0, "roughness": 0.0},
    "frosted":     {"alpha": 0.3,  "roughness": 0.6},
    "tinted":      {"alpha": 0.2,  "color": [0.1, 0.1, 0.15]},
}
```

**Test:** `tests/test_window_modular.py`

---

### FAZ 5: Duvar + Kapı/Pencere Entegrasyonu
**Hedef:** Composed wall sistemi (duvar + opening birlikte üretim)

**Dosyalar:**
- `src/blenpc/atoms/wall.py` → `build_wall_composed()` ekle
- `src/blenpc/run_command.py` → Router'a `asset.wall_composed` ekle

**JSON Input Örneği:**
```json
{
  "command": "asset.wall_composed",
  "version": "1.0",
  "seed": 42,
  "wall": {
    "name": "exterior_wall_w_door",
    "length": 5.0,
    "height": 3.0,
    "thickness": 0.2,
    "material": "brick"
  },
  "openings": [
    {
      "type": "door",
      "position": {"x_ratio": 0.3},
      "style": "single",
      "leaf_material": "wood",
      "swing": "inward_left"
    },
    {
      "type": "window",
      "position": {"x_ratio": 0.8},
      "style": "standard",
      "frame_material": "wood",
      "glass_inner": "transparent",
      "glass_outer": "mirror"
    }
  ]
}
```

**Test:** `tests/test_composed_wall.py`

---

### FAZ 6: Slot Sistemi ve Metadata
**Hedef:** Slot validation, compatibility matrix, tag otomasyonu

**Dosyalar:**
- `_registry/slot_types.json` → Compatibility matrix ekle
- `src/blenpc/engine/slot_engine.py` → Validation güncelle

**Compatibility Matrix:**
```json
{
  "compatibility": {
    "window_opening": ["arch_window"],
    "door_opening":   ["arch_door"],
    "shelf_bay":      ["prop_weapon", "prop_book", "prop_plant"]
  }
}
```

**Otomatik Tag Üretimi:**
```python
def auto_size_tag(w, d, h):
    vol = w * d * h
    if vol < 0.1:   return "size_xs"
    elif vol < 1.0: return "size_s"
    elif vol < 8.0: return "size_m"
    else:           return "size_l"
```

**Test:** `tests/test_slot_validation.py`

---

### FAZ 7: Sims-Tarzı Grid ve Oda Otomasyonu
**Hedef:** 3-mode snap sistemi, otomatik oda algılama

**Dosyalar:**
- `src/blenpc/engine/room_detector.py` → Yeni dosya
  - `detect_enclosed_rooms(walls)`
  - `auto_generate_floor(room_bounds)`
  - `auto_generate_ceiling(room_bounds)`
- `src/blenpc/engine/topology.py` → Yeni dosya
  - `detect_wall_intersections(walls)`
  - `generate_corner_mesh(junction_type)`

**Oda Algılama Algoritması:**
1. Tüm duvarların AABB'lerini topla
2. 4 duvar kapalı alan oluşturuyorsa → room objesi oluştur
3. Zemin ve tavan otomatik ekle
4. Room objesi tek parça, taşınabilir

**Test:** `tests/test_room_automation.py`

---

### FAZ 8: MCP Entegrasyonu
**Hedef:** ahujasid/blender-mcp ile Kiro/Cursor entegrasyonu

**Dosyalar:**
- `mcp/blenpc_tools.py` → Yeni dosya
  - `blenpc_create_asset(command_json)`
  - `blenpc_query_library(tags)`
  - `blenpc_place_on_slot(host, guest, slot_id)`

**MCP Tool Tanımları:**
```python
BLENPC_MCP_TOOLS = [
    {
        "name": "blenpc_create_asset",
        "description": "JSON komut ile BlenPC asset üret",
        "input_schema": {
            "command_json": "string — input JSON içeriği"
        }
    },
    ...
]
```

**Entegrasyon Notu:**
- MCP → interaktif düzenleme
- JSON pipeline → batch/headless üretim
- İkisi birlikte çalışır, çakışmaz

**Test:** `tests/test_mcp_integration.py`

---

### FAZ 9: Godot Export Pipeline
**Hedef:** Scene tree JSON, collision shape, LOD sistemi

**Dosyalar:**
- `src/blenpc/mf_v5/export.py` → Godot scene tree ekle
- `src/blenpc/mf_v5/collider.py` → Collision shape seçimi ekle

**Scene Tree JSON:**
```json
{
  "godot_scene": "Node3D",
  "children": [
    {
      "name": "WallNorth",
      "type": "StaticBody3D",
      "mesh": "brick_wall_2m.glb",
      "pos": [0, 0, 0]
    },
    {
      "name": "DoorSlot_0",
      "type": "Marker3D",
      "pos": [2.5, 0, 0],
      "meta": {"slot_type": "door_opening"}
    }
  ]
}
```

**Collision Shape Kuralları:**
```python
COLLISION_SHAPE_MAP = {
    "arch_wall":     "BoxShape3D",
    "arch_door":     "BoxShape3D",
    "arch_window":   "BoxShape3D",
    "prop_weapon":   "ConvexPolygonShape3D",
    "prop_furniture":"BoxShape3D",
}
```

**Test:** `tests/test_godot_export.py`

---

### FAZ 10: Test, Dokümantasyon ve Final Push
**Hedef:** Regression testler, golden file testler, dokümantasyon

**Dosyalar:**
- `tests/test_geometry_regression.py` → AABB karşılaştırma
- `tests/test_slot_completeness.py` → Slot zorunluluk kontrolü
- `tests/golden/` → Altın dosya klasörü
- `docs/MODULAR_SYSTEM.md` → Kullanıcı dokümantasyonu
- `docs/API_EXAMPLES.md` → JSON komut örnekleri

**Regression Test:**
```python
def test_wall_geometry_regression():
    wall = build_wall(5.0, 3.0, 0.2)
    aabb = wall["meta"]["aabb"]
    
    golden = load_golden("wall_5x3.json")
    assert abs(aabb["max"][0] - golden["aabb"]["max"][0]) < 0.01
```

**Golden File Testi:**
1. İlk kez doğru üretilen asset'in JSON'u `tests/golden/` klasörüne kaydedilir
2. Sonraki üretimlerde bu dosya ile karşılaştırılır
3. Fark varsa → intentional change mi kontrol edilir

**Dokümantasyon:**
- API referansı güncelle
- JSON komut örnekleri ekle
- Sims-tarzı grid kullanımı açıkla
- MCP entegrasyonu dokümante et

---

## Buildify ve SkyscrapX'ten Farkımız

| Özellik | Buildify | SkyscrapX | BlenPC 5.0 |
|---------|----------|-----------|------------|
| **Modülerlik** | Facade level | Tek mesh | Segment-based |
| **Stretching** | Kabul ediyor | Kabul ediyor | GRID_UNIT ile engelliyor |
| **Slot Sistemi** | Yok | Yok | ✅ Var |
| **JSON Pipeline** | Yok | Yok | ✅ Var |
| **Pre-cut Openings** | Boolean ops | Boolean ops | ✅ Segment-based |
| **Oda Otomasyonu** | Yok | Yok | ✅ Sims-tarzı |

---

## 30 Öneri - Öncelik Sırası

### Hemen Yapılacak (Bu Sprint)
1. ✅ **Grid Sistemi** (Öneri #6) - 3 mod snap
2. ✅ **Room-as-Object** (Öneri #1) - Otomatik oda algılama
3. ✅ **Wall Topology** (Öneri #3) - Köşe otomasyonu
4. ✅ **Floor Otomasyonu** (Öneri #4) - Zemin tile'ları
5. ✅ **Ceiling Otomasyonu** (Öneri #5) - Tavan otomasyonu

### Sonraki Sprint
6. **Tag Arama İndeksi** (Öneri #11) - O(1) arama
7. **Compatibility Matrix** (Öneri #15) - Slot uyumluluğu
8. **MCP Entegrasyonu** (Öneri #21) - Kiro/Cursor bağlantısı
9. **Watch Modu** (Öneri #22) - Otomatik üretim

### İleride
10. **Scene Tree JSON** (Öneri #16) - Godot entegrasyonu
11. **Collision Shape Seçimi** (Öneri #17)
12. **LOD Sistemi** (Öneri #18)
13. **Navigation Mesh Marker** (Öneri #19)
14. **Physics Material Metadata** (Öneri #20)

### Test Altyapısı (Her Sprint Sonunda)
15. **Geometry Regression** (Öneri #26)
16. **Slot Uyum Testi** (Öneri #27)
17. **Golden File Testi** (Öneri #28)

---

## Başarı Kriterleri

### Teknik
- ✅ Tüm duvarlar segment-based
- ✅ Manifold geometri korunuyor
- ✅ Slot validation çalışıyor
- ✅ Godot'ta hatasız import
- ✅ MCP entegrasyonu aktif

### Performans
- ✅ 5m duvar + kapı + pencere < 2 saniye
- ✅ RAM kullanımı < 3GB
- ✅ GLB dosya boyutu < 5MB (standart oda için)

### Kullanılabilirlik
- ✅ JSON komut tek satır
- ✅ Hata mesajları açık ve anlaşılır
- ✅ Dokümantasyon eksiksiz
- ✅ Kiro'dan natural language ile tetiklenebilir

---

## Sonraki Adımlar

1. **FAZ 1** başlat → Config dosyalarını güncelle
2. Her faz bitiminde GitHub'a push et
3. Test coverage %80+ tut
4. Dokümantasyonu paralel güncelle
5. MCP entegrasyonu son fazda ekle

---

**Hazırlayan:** Manus AI Agent  
**Tarih:** 2026-02-18  
**Versiyon:** 1.0  
**Durum:** Planlama Tamamlandı - Geliştirme Başlıyor

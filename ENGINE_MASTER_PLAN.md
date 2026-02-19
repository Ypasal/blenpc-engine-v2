# 📘 BLENPC ENGINE MASTER PLAN

**Versiyon:** FAZ 8-10 Entegre Roadmap  
**Tarih:** 2026-02-19  
**Durum:** Mimari Refactor Planı  
**Hedef:** Grid sistemini deterministik, minimal ve engine-level bir yapıya dönüştürmek

---

## 0️⃣ Temel İlke

```
Grid = Truth
Engine = Rule System
Content = Visualization
State = Immutable
```

**Kritik Ayırım:**

- **Engine Core:** "Neye izin var?" sorusunu yanıtlar
- **Content Layer:** "Nasıl görünür?" sorusunu yanıtlar

Collision krizi, bu iki sorunun aynı yerde sorulmasından çıkmıştı.

---

## 1️⃣ ENGINE STATE MACHINE

Engine bir script değil, bir **state machine**'dir.

```
[INIT]
   ↓
[PARSE_JSON]
   ↓
[VALIDATE_COMMAND]
   ↓
[SIMULATE_PLACEMENT]
   ↓
[COLLISION_CHECK]
   ↓
[STRUCTURAL_VALIDATION]
   ↓
[STATE_COMMIT]
   ↓
[CONTENT_BUILD]
   ↓
[READY]
```

**Hata Durumları:**
```
[FAIL_FAST] → Herhangi bir aşamada hata olursa derhal dur
```

**Kurallar:**

1. `STATE_COMMIT` olmadan grid değişmez
2. `CONTENT_BUILD` engine state'i değiştiremez
3. Her aşama **pure function** olmalı (side-effect yok)

---

## 2️⃣ ENGINE CORE KURALLARI

### 2.1 Kural: Grid İçerik Bilmez

Grid şunları **bilmez:**

- Door
- Window
- Decoration
- Boolean cutter
- Frame detail

Grid **sadece** şunları bilir:

- Structural object (Wall, Column, Slab, Roof base)
- Footprint (hangi hücreler dolu?)
- Occupancy (bu hücre boş mu?)

### 2.2 Kural: Floating Point Yasak

Engine seviyesinde:

- `float` yasak
- Sadece `int`
- `MICRO_UNIT` enforced (0.025m = 1 unit)

Tüm koordinatlar:

```python
grid_x = int(real_x / MICRO_UNIT)
```

### 2.3 Kural: Collision = Set Intersection

Collision şu demek:

```
Footprint A ∩ Footprint B ≠ ∅
```

Başka hiçbir şey değil. Mesh, bounding box, SAT, physics engine **kullanılmaz**.

### 2.4 Kural: Engine Immutable Commit

Placement:

```
validate → simulate → commit
```

Grid doğrudan mutate edilmez. Her placement yeni bir `GridState` döner.

### 2.5 Kural: Parent–Child

Child object:

- Grid'e **girmez**
- Parent üzerinden hareket eder
- Engine level **değildir**

**Örnek:**

```
Wall (engine-level, grid'e girer)
 └── Door (content-level, grid'e girmez)
```

---

## 3️⃣ VERİ MODELİ

### 3.1 Cell Model

```python
@dataclass(frozen=True)
class StructuralCell:
    object_id: str
```

### 3.2 Footprint Model

```python
Footprint = frozenset[tuple[int, int, int]]
```

### 3.3 Grid State

```python
@dataclass(frozen=True)
class GridState:
    cells: dict[tuple[int, int, int], StructuralCell]
```

**Immutable.** Her değişiklik yeni bir `GridState` döner.

---

## 4️⃣ PURE COLLISION ENGINE (Final Form)

### Minimal Matematik

```
C(A, G) = ∃ c ∈ A : c ∈ G
```

### Kod

```python
def detect_collision(
    footprint: frozenset[Cell], 
    grid: GridState
) -> bool:
    return not footprint.isdisjoint(grid.cells.keys())
```

### Performans

- **Zaman Karmaşıklığı:** O(n), n = footprint size
- **Hash lookup:** O(1)
- **Deterministik:** Evet
- **Floating point:** Hayır

---

## 5️⃣ IMMUTABLE STATE + DIFF SİSTEMİ

Undo/redo için her commit:

- Eski state
- Yeni state
- Diff

### Diff Modeli

```python
@dataclass(frozen=True)
class GridDiff:
    added: frozenset[Cell]
    removed: frozenset[Cell]
```

### Diff Hesaplama

```python
def compute_diff(old: GridState, new: GridState) -> GridDiff:
    old_cells = set(old.cells.keys())
    new_cells = set(new.cells.keys())
    
    return GridDiff(
        added=frozenset(new_cells - old_cells),
        removed=frozenset(old_cells - new_cells),
    )
```

### Undo/Redo

```python
# Undo
grid = previous_state

# Redo
grid = next_state
```

Mutasyon yok. Sadece state değiştirme.

---

## 6️⃣ GRID 3D MİMARİSİ (FAZ 8.5)

Şu an 2D footprint var. FAZ 9 sonrası **z-level** ekliyoruz.

### Hücre Tanımı

```python
Cell = tuple[int, int, int]  # (x, y, z)
```

**Z-level:**

- `0` → ground
- `1` → upper floor
- `n` → vertical stacking

### Grid State

```python
@dataclass(frozen=True)
class GridState:
    cells: dict[Cell, str]
```

Collision değişmez. Sadece hücre tanımı 3D olur.

---

## 7️⃣ ROOM DETECTION (FAZ 9)

Room detection grid üzerinden yapılır.

### Temel Fikir

1. Structural wall hücreleri **dolu**
2. Boş hücreler **gezilebilir alan**
3. Flood-fill ile **kapalı alan tespit**

### Algoritma

```python
def flood_fill(start: Cell, grid: GridState) -> set[Cell]:
    stack = [start]
    visited = set()
    
    while stack:
        cell = stack.pop()
        if cell in visited:
            continue
        
        visited.add(cell)
        
        for neighbor in get_neighbors(cell):
            if neighbor not in grid.cells:
                stack.append(neighbor)
    
    return visited
```

Oluşan alan dış boundary'ye değmiyorsa → **room**.

---

## 8️⃣ STRUCTURAL GRAPH (FAZ 9.2)

Wall adjacency graph çıkar.

### Node

- `wall_id`

### Edge

- Shared boundary

Bu sayede:

- Oda tespiti
- Navmesh
- Structural consistency
- Constraint solving

mümkün olur.

---

## 9️⃣ ENGINE VALIDATION RULE SET

### 9.1 Structural Rules

- ✔ Footprint boundary içinde olmalı
- ✔ Collision olmamalı
- ✔ Z-level valid olmalı
- ✔ Parent-child uyumlu olmalı
- ✔ Minimum wall length olmalı

### 9.2 Determinism Rules

- ✔ Float yok
- ✔ Random seed sabit
- ✔ Placement order sabit
- ✔ State hash kontrolü

---

## 🔟 CONTENT LAYER KURALLARI

Content layer:

- Grid **okur**
- Mesh **üretir**
- Boolean **uygular**
- Visual detail **üretir**

Ama:

- Grid **değiştiremez**
- Collision kararı **veremez**
- Validation **yapamaz**

---

## 1️⃣1️⃣ TAG / METADATA SİSTEMİ (FAZ 8'te Zorunlu)

Her obje şu metadata'yı taşır:

```python
@dataclass
class EngineMeta:
    engine_level: bool
    grid_aware: bool
    grid_type: str  # "structural" | "none" | "derived"
    parent_required: bool
```

### Örnek

**Wall:**

```python
engine_level = True
grid_aware = True
grid_type = "structural"
parent_required = False
```

**Door:**

```python
engine_level = False
grid_aware = False
grid_type = "none"
parent_required = True
```

### Grid Kontrolü

```python
if obj.meta.engine_level is False:
    reject
```

---

## 1️⃣2️⃣ SIK YAPILAN HATALAR

❌ **Door'u IGridObject yapmak**  
❌ **Grid içinde float kullanmak**  
❌ **Mesh üzerinden collision yapmak**  
❌ **Boolean modifier'a güvenmek**  
❌ **Grid mutation yapmak**  
❌ **Content layer'dan grid'e yazmak**  
❌ **Mesh bounding box üzerinden collision**  
❌ **Placement sırasını rastgele bırakmak**

---

## 1️⃣3️⃣ PERFORMANS OPTİMİZASYONLARI

1. **Footprint minimal tut**
2. **Sparse grid kullan** (dict, array değil)
3. **State diff ile incremental build**
4. **Room detection commit sonrası çalıştır**
5. **Grid boyutunu sabit array yapma**

---

## 1️⃣4️⃣ TEST SİSTEMİ

### 14.1 Engine Testleri

Testler:

- Collision deterministik mi?
- Aynı input → aynı state hash?
- Boundary validation doğru mu?
- Parent-child doğru mu?

### 14.2 Property-Based Testing

Rastgele footprint üret:

```python
if A ∩ B = ∅ → collision false
if A ∩ B ≠ ∅ → collision true
```

### 14.3 Determinism Testi

```python
grid1 = place(objA, empty)
grid2 = place(objA, empty)

assert hash(grid1) == hash(grid2)
```

### 14.4 Test Ayrımı

**Engine Testleri:**

- Overlap detection
- Slot validation
- Boundary rules
- Parent-child validity

**Content Testleri:**

- Mesh oluşturuluyor mu?
- Parametre scaling doğru mu?
- Boolean düzgün mü?

**Karışmayacaklar.**

---

## 1️⃣5️⃣ FAZ 8 ADIMLARI

### FAZ 8.1 – Collision Pure Hale Getirme

**Hedef:** Collision motorunu tamamen fonksiyonel (pure) hale getirmek.

**Adımlar:**

1. `detect_collision()` fonksiyonunu pure yap
2. Global state kullanımını kaldır
3. Sadece `frozenset` intersection kullan
4. Test yaz (property-based)

**Süre:** 1 gün

---

### FAZ 8.2 – Grid Immutable Yapma

**Hedef:** `GridState`'i immutable yapmak.

**Adımlar:**

1. `@dataclass(frozen=True)` ekle
2. `place()` fonksiyonu yeni state dönsün
3. Mutation yapan tüm kodu refactor et
4. State hash fonksiyonu ekle

**Süre:** 1 gün

---

### FAZ 8.3 – Validation Ayrıştırma

**Hedef:** Validation'ı engine core'a taşımak.

**Adımlar:**

1. `ValidationEngine` modülü oluştur
2. Boundary check
3. Parent-child check
4. Slot validation

**Süre:** 1 gün

---

### FAZ 8.4 – State Hashing

**Hedef:** Deterministik state hash sistemi.

**Adımlar:**

1. `compute_state_hash()` fonksiyonu
2. Placement sırası sabit
3. Determinism testi

**Süre:** 0.5 gün

---

### FAZ 8.5 – Engine Test Suite

**Hedef:** Engine core için kapsamlı test suite.

**Adımlar:**

1. Collision testleri
2. Validation testleri
3. Determinism testleri
4. Property-based testler

**Süre:** 1 gün

---

### FAZ 8.6 – Grid Sadeleştirme

**Hedef:** Grid'e sadece structural objeler girsin.

**Adımlar:**

1. Grid'e print/log koy, hangi objeler giriyor gör
2. Structural olmayanları çıkar
3. Tag zorunluluğu ekle (`assert obj.grid_aware is True`)
4. Collision sadece `grid_type == "structural"` için çalışsın

**Süre:** 1 gün

---

### FAZ 8.7 – Dosya Yapısı Refactor

**Hedef:** Engine/content ayrımını dosya yapısına yansıtmak.

**Mevcut Yapı:**

```
/engine
    scene_grid.py
    collision.py
    placement.py
/atoms
    wall.py
    door.py
```

**Yeni Yapı:**

```
/engine
    /core
        structural_grid.py
        cell.py
        igrid_object.py
        collision_engine.py
        validation_engine.py
        placement_engine.py
        state_commit.py
        unit_system.py
        json_parser.py

/content
    /atoms
        wall.py
        column.py
        slab.py
        roof.py
        door.py
        window.py
    
    /builders
        mesh_builder.py
```

**Kritik Kural:**

- `/content` klasörü `/engine` import **edemez**
- Engine content **bilmez**
- Content engine'i **okur**

**Süre:** 1 gün

---

## 1️⃣6️⃣ FAZ 9 ADIMLARI

### FAZ 9.1 – Room Detection

Grid üzerinden flood-fill.

**Süre:** 2 gün

---

### FAZ 9.2 – Structural Graph

Duvar adjacency graph çıkar.

**Süre:** 2 gün

---

### FAZ 9.3 – Navmesh Extraction

Empty cell extraction.

**Süre:** 1 gün

---

### FAZ 9.4 – Constraint Solver

- Duvarlar 90° mi?
- Overlap var mı?
- Yük taşıma zinciri?

**Süre:** 3 gün

---

## 1️⃣7️⃣ FAZ 10 – İleri Seviye

1. **Constraint solver**
2. **Structural load simulation**
3. **Network sync**
4. **Multiplayer deterministik replay**
5. **IFC export**
6. **Procedural AI planning**

---

## 1️⃣8️⃣ ENGINE OPTİMİZE HALİ – Nihai Form

```
JSON
  ↓
Parser (pure)
  ↓
Command Object
  ↓
Simulate (pure)
  ↓
Collision (pure)
  ↓
Validation (pure)
  ↓
New Immutable GridState
  ↓
Diff
  ↓
Content Builder
```

**Hiçbir yerde side-effect yok.**

---

## 1️⃣9️⃣ EXTRA ÖNEMLİ NOTLAR (Tecrübe Konuşuyor)

### 19.1 Grid'i büyütme

Grid sade kalmalı. Zekayı grid'in üstüne yaz.

### 19.2 Engine'i Blender'dan bağımsız tut

Engine modülü:

- Blender import **etmemeli**

### 19.3 Engine testleri Blender olmadan çalışmalı

Bu seni addon seviyesinden engine seviyesine taşır.

### 19.4 Collision'ı asla büyütme

Ne mesh, ne bounding box, ne SAT, ne physics engine.

**Sadece set intersection.**

---

## 2️⃣0️⃣ PLACEMENT PIPELINE

```
JSON
 ↓
CommandParser
 ↓
PlacementEngine
 ↓
CollisionEngine
 ↓
ValidationEngine
 ↓
New GridState (immutable)
```

---

## 2️⃣1️⃣ GRID TÜRLER (Çok Grid Mimarisi)

### Tek Grid mi? Çok Grid mi?

Asıl hata şuydu:

```
SceneGrid = her şeyi bilen tek grid
```

FAZ 8 sonrası doğru model şu:

```
StructuralGrid  (engine-level, truth)
DetailGrid      (content-level, bounded)
DecorationGrid  (optional)
```

Ama dikkat:

- Sadece `StructuralGrid` "otorite"dir
- Diğer grid'ler subordinate'dır

### Grid Türlerini Net Tanımlayalım

#### 🧱 1. StructuralGrid (Engine Core)

Bu grid:

- Duvar
- Kolon
- Slab
- Roof base

şeyleri tutar.

Bu grid:

- Collision yapar
- Validasyon yapar
- Fail-fast yapar
- JSON karar verir

Bu grid **"gerçek dünya"**.

#### 🚪 2. ApertureGrid (Duvar İçi Grid)

Door ve Window için ayrı bir grid olabilir.

Ama bu grid:

- **SADECE** parent wall içinde yaşar
- Global **değildir**
- StructuralGrid'e **yazmaz**
- Footprint **üretmez**

Yani:

```
Wall
 └── ApertureGrid
         ├── Door
         └── Window
```

Bu bir **local grid**'dir.

#### 🎨 3. DecorationGrid

Trim, handle, frame detail, boolean cutter gibi şeyler:

- Ya hiç grid'e girmez
- Ya parent-local mikro grid kullanır

Ama:

- Global grid'e **ASLA yazmaz**

### Doğru Mimari Model (FAZ 8 İçin)

```
World
 ├── StructuralGrid   (authoritative)
 │
 ├── Wall
 │     └── ApertureGrid (local)
 │
 └── DecorationLayer (gridless veya local)
```

**Ana prensip:**

Grid hiyerarşik olur, ama authority tek olur.

### Kategori Gridleri Olmalı mı?

| Tür | Global Grid | Local Grid |
|-----|-------------|------------|
| Wall | ✅ | ❌ |
| Column | ✅ | ❌ |
| Door | ❌ | ✅ (Wall içinde) |
| Window | ❌ | ✅ (Wall içinde) |
| Trim | ❌ | Opsiyonel |
| Handle | ❌ | ❌ |
| Boolean cutter | ❌ | ❌ |

### Kritik Kural

Bir obje şunu sor:

```
Bu obje başka yapısal objeleri etkiliyor mu?
```

- Eğer evet → StructuralGrid
- Eğer hayır → Local grid ya da gridless

Door duvarı etkiler ama:

- Dünya topolojisini **etkilemez**

Bu yüzden global grid'e girmez.

---

## 2️⃣2️⃣ MİMARİ DİKKAT EDİLMESİ GEREKENLER

🚨 **Engine hiçbir zaman mesh üretmez**  
🚨 **Content hiçbir zaman collision karar vermez**  
🚨 **Grid her zaman authoritative**  
🚨 **Placement sırası deterministik**  
🚨 **Floating point yasak**  
🚨 **Grid mutation yasak**

---

## 2️⃣3️⃣ SONUÇ

Bu plan sonrası BlenPC:

- ✅ **Deterministik**
- ✅ **Test edilebilir**
- ✅ **Headless stabil**
- ✅ **Genişletilebilir**
- ✅ **Engine seviyesinde**

bir sistem olur.

---

## 2️⃣4️⃣ ELEKTRİK DEVRESİ BENZETMESİ

```
Grid = güç kaynağı
Collision = sigorta
Validation = devre kontrol
State commit = kilit anahtar
Content = LED ışık
```

LED yanabilir. Ama sigorta patlarsa sistem durur.

Bu ayrımı netleştiriyoruz.

---

## 2️⃣5️⃣ EN SERT GERÇEK

Şu an sen addon yazmıyorsun.

Sen:

**Deterministik procedural architecture engine** yazıyorsun.

Bunun kalbi **grid**.

- Grid karmaşıksa her şey karmaşık olur
- Grid sade ise sistem sonsuza kadar genişler

---

**Hazırlayan:** Manus AI Agent  
**Son Güncelleme:** 2026-02-19  
**Durum:** Master Plan Hazır  
**Sonraki Adım:** Kullanıcı onayı ve FAZ 8 implementasyonu

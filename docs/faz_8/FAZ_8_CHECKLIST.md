# ✅ FAZ 8 CHECKLIST – Grid Core Stabilization

**Başlangıç Tarihi:** 2026-02-19  
**Hedef:** Grid sistemini engine-level stabilize etmek  
**Toplam Süre:** ~6.5 gün

---

## 📋 Ön Koşullar

- [ ] `ENGINE_MASTER_PLAN.md` okundu ve anlaşıldı
- [ ] Mevcut grid sistemi analiz edildi
- [ ] Collision problemi anlaşıldı (hierarchical placement çözümü)
- [ ] Tüm testler çalıştırıldı ve mevcut durum kaydedildi

---

## 🎯 FAZ 8.1 – Collision Pure Hale Getirme (1 gün)

### Hedef
Collision motorunu tamamen fonksiyonel (pure) hale getirmek.

### Adımlar

- [ ] **1.1** `collision_engine.py` modülü oluştur
- [ ] **1.2** Pure `detect_collision()` fonksiyonu yaz
  ```python
  def detect_collision(
      footprint: frozenset[Cell], 
      grid: GridState
  ) -> bool:
      return not footprint.isdisjoint(grid.cells.keys())
  ```
- [ ] **1.3** Global state kullanımını kaldır
- [ ] **1.4** Sadece `frozenset` intersection kullan
- [ ] **1.5** Property-based test yaz
  ```python
  def test_collision_property():
      # A ∩ B = ∅ → collision false
      # A ∩ B ≠ ∅ → collision true
  ```
- [ ] **1.6** Mevcut `grid_manager.py` collision kodunu refactor et
- [ ] **1.7** Tüm collision testlerini çalıştır

### Başarı Kriterleri
- ✅ Collision fonksiyonu pure (side-effect yok)
- ✅ Deterministik (aynı input → aynı output)
- ✅ Floating point yok
- ✅ Testler geçiyor

---

## 🎯 FAZ 8.2 – Grid Immutable Yapma (1 gün)

### Hedef
`GridState`'i immutable yapmak.

### Adımlar

- [ ] **2.1** `cell.py` modülü oluştur
  ```python
  @dataclass(frozen=True)
  class StructuralCell:
      object_id: str
  ```
- [ ] **2.2** `GridState` class'ını immutable yap
  ```python
  @dataclass(frozen=True)
  class GridState:
      cells: dict[tuple[int, int, int], StructuralCell]
  ```
- [ ] **2.3** `place()` fonksiyonu yeni state dönsün
  ```python
  def place(obj: IGridObject, grid: GridState) -> GridState:
      # validate
      # yeni state oluştur
      return new_grid_state
  ```
- [ ] **2.4** Mutation yapan tüm kodu refactor et
- [ ] **2.5** State hash fonksiyonu ekle
  ```python
  def compute_state_hash(grid: GridState) -> str:
      return hash(tuple(sorted(grid.cells.items())))
  ```
- [ ] **2.6** Immutability testleri yaz
- [ ] **2.7** Tüm grid testlerini çalıştır

### Başarı Kriterleri
- ✅ `GridState` frozen dataclass
- ✅ Hiçbir mutation yok
- ✅ State hash deterministik
- ✅ Testler geçiyor

---

## 🎯 FAZ 8.3 – Validation Ayrıştırma (1 gün)

### Hedef
Validation'ı engine core'a taşımak.

### Adımlar

- [ ] **3.1** `validation_engine.py` modülü oluştur
- [ ] **3.2** Boundary check fonksiyonu
  ```python
  def validate_boundary(
      footprint: Footprint, 
      bounds: Bounds
  ) -> bool:
      return all(is_within_bounds(cell, bounds) for cell in footprint)
  ```
- [ ] **3.3** Parent-child check fonksiyonu
  ```python
  def validate_parent_child(
      child: IGridObject, 
      parent: IGridObject
  ) -> bool:
      return child.footprint.issubset(parent.footprint)
  ```
- [ ] **3.4** Slot validation fonksiyonu
- [ ] **3.5** Validation testleri yaz
- [ ] **3.6** Mevcut validation kodunu refactor et
- [ ] **3.7** Tüm validation testlerini çalıştır

### Başarı Kriterleri
- ✅ Validation engine ayrı modül
- ✅ Pure fonksiyonlar
- ✅ Mesh/content bilgisi yok
- ✅ Testler geçiyor

---

## 🎯 FAZ 8.4 – State Hashing (0.5 gün)

### Hedef
Deterministik state hash sistemi.

### Adımlar

- [ ] **4.1** `state_commit.py` modülü oluştur
- [ ] **4.2** `compute_state_hash()` fonksiyonu
  ```python
  def compute_state_hash(grid: GridState) -> str:
      sorted_cells = tuple(sorted(grid.cells.items()))
      return hashlib.sha256(str(sorted_cells).encode()).hexdigest()
  ```
- [ ] **4.3** Placement sırası sabit yap
- [ ] **4.4** Determinism testi yaz
  ```python
  def test_determinism():
      grid1 = place_all(objects, empty_grid)
      grid2 = place_all(objects, empty_grid)
      assert compute_state_hash(grid1) == compute_state_hash(grid2)
  ```
- [ ] **4.5** Tüm determinism testlerini çalıştır

### Başarı Kriterleri
- ✅ State hash deterministik
- ✅ Aynı input → aynı hash
- ✅ Testler geçiyor

---

## 🎯 FAZ 8.5 – Engine Test Suite (1 gün)

### Hedef
Engine core için kapsamlı test suite.

### Adımlar

- [ ] **5.1** `tests/test_collision_engine.py` oluştur
  - [ ] Basic collision testleri
  - [ ] Property-based testler
  - [ ] Edge case testleri
- [ ] **5.2** `tests/test_validation_engine.py` oluştur
  - [ ] Boundary testleri
  - [ ] Parent-child testleri
  - [ ] Slot testleri
- [ ] **5.3** `tests/test_determinism.py` oluştur
  - [ ] State hash testleri
  - [ ] Placement order testleri
- [ ] **5.4** `tests/test_grid_state.py` oluştur
  - [ ] Immutability testleri
  - [ ] State transition testleri
- [ ] **5.5** Tüm testleri çalıştır
- [ ] **5.6** Test coverage raporu oluştur (hedef: %90+)

### Başarı Kriterleri
- ✅ Tüm engine testleri geçiyor
- ✅ Coverage %90+
- ✅ Blender olmadan çalışıyor

---

## 🎯 FAZ 8.6 – Grid Sadeleştirme (1 gün)

### Hedef
Grid'e sadece structural objeler girsin.

### Adımlar

- [ ] **6.1** Grid'e print/log koy, hangi objeler giriyor gör
  ```python
  def place(obj: IGridObject, grid: GridState) -> GridState:
      print(f"Placing: {obj.name}, type: {obj.meta.grid_type}")
      # ...
  ```
- [ ] **6.2** Structural olmayanları tespit et
- [ ] **6.3** Tag zorunluluğu ekle
  ```python
  if not obj.meta.grid_aware:
      raise ValueError(f"Object {obj.name} is not grid-aware")
  ```
- [ ] **6.4** Collision sadece `grid_type == "structural"` için çalışsın
  ```python
  def detect_collision(obj: IGridObject, grid: GridState) -> bool:
      if obj.meta.grid_type != "structural":
          return False  # Skip collision for non-structural
      # ...
  ```
- [ ] **6.5** Door/Window'u grid'den çıkar (hierarchical placement)
- [ ] **6.6** Metadata sistemi ekle
  ```python
  @dataclass
  class EngineMeta:
      engine_level: bool
      grid_aware: bool
      grid_type: str  # "structural" | "none" | "derived"
      parent_required: bool
  ```
- [ ] **6.7** Tüm objelere metadata ekle
- [ ] **6.8** Grid sadeleştirme testleri çalıştır

### Başarı Kriterleri
- ✅ Grid'de sadece structural objeler
- ✅ Door/Window grid'e girmiyor
- ✅ Metadata sistemi çalışıyor
- ✅ Testler geçiyor

---

## 🎯 FAZ 8.7 – Dosya Yapısı Refactor (1 gün)

### Hedef
Engine/content ayrımını dosya yapısına yansıtmak.

### Adımlar

- [ ] **7.1** Yeni klasör yapısı oluştur
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
- [ ] **7.2** Mevcut kodu yeni yapıya taşı
- [ ] **7.3** Import path'leri güncelle
- [ ] **7.4** `/content` klasörü `/engine` import etmediğinden emin ol
- [ ] **7.5** Circular dependency kontrolü
- [ ] **7.6** Tüm testleri çalıştır
- [ ] **7.7** Dokümantasyon güncelle

### Başarı Kriterleri
- ✅ Dosya yapısı engine/content ayrımını yansıtıyor
- ✅ Circular dependency yok
- ✅ Tüm testler geçiyor
- ✅ Import path'ler temiz

---

## 🎯 FAZ 8.8 – Entegrasyon ve Dokümantasyon (1 gün)

### Hedef
Tüm değişiklikleri entegre etmek ve dokümante etmek.

### Adımlar

- [ ] **8.1** Tüm FAZ 8 değişikliklerini birleştir
- [ ] **8.2** Regression test suite çalıştır
- [ ] **8.3** `ARCHITECTURE.md` güncelle
- [ ] **8.4** `API_REFERENCE.md` güncelle
- [ ] **8.5** `CHANGELOG.md` güncelle
- [ ] **8.6** Code review yap
- [ ] **8.7** Git commit ve push
- [ ] **8.8** GitHub release oluştur (v5.2.0 → v5.3.0)

### Başarı Kriterleri
- ✅ Tüm testler geçiyor
- ✅ Dokümantasyon güncel
- ✅ Git history temiz
- ✅ Release notları hazır

---

## 📊 FAZ 8 Başarı Metrikleri

### Teknik Metrikler

- [ ] **Collision:** Pure fonksiyon, O(n) karmaşıklık
- [ ] **Grid State:** Immutable, hash deterministik
- [ ] **Validation:** Engine core'da, content bilgisi yok
- [ ] **Test Coverage:** %90+
- [ ] **Determinism:** Aynı input → aynı hash

### Mimari Metrikler

- [ ] **Engine/Content Ayrımı:** Net, circular dependency yok
- [ ] **Grid Sadeleştirme:** Sadece structural objeler
- [ ] **Metadata Sistemi:** Tüm objelerde mevcut
- [ ] **Dosya Yapısı:** Temiz, mantıklı

### Performans Metrikleri

- [ ] **Collision Check:** O(1) per cell
- [ ] **State Hash:** O(n log n)
- [ ] **Memory:** Sparse grid, sadece dolu hücreler

---

## 🚨 Dikkat Edilmesi Gerekenler

1. **Floating point kullanma** – Sadece int
2. **Grid'i mutate etme** – Her zaman yeni state döndür
3. **Content'ten engine'e import etme** – Tek yönlü bağımlılık
4. **Mesh üzerinden collision yapma** – Sadece footprint
5. **Door/Window'u grid'e koyma** – Hierarchical placement

---

## 📝 Notlar

- Her adımda testleri çalıştır
- Commit sık yap, küçük adımlarla ilerle
- Dokümantasyonu güncellemeyi unutma
- Şüphe duyarsan `ENGINE_MASTER_PLAN.md`'ye bak

---

**Hazırlayan:** Manus AI Agent  
**Son Güncelleme:** 2026-02-19  
**Durum:** Checklist Hazır  
**Sonraki Adım:** Kullanıcı onayı ve implementasyon başlangıcı

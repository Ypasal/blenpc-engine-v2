# 📜 BlenPC Sürüm Günlüğü (Changelog)

BlenPC projesindeki tüm önemli değişiklikler bu dosyada takip edilir.

---

## [5.1.1] - 2026-02-18 (Expert Edition)

### 🏗️ Mimari Değişiklikler
- **`src/` Layout**: Proje, standart Python paket yapısına (`src/blenpc`) taşındı.
- **Expert Panel**: 10 uzman disiplinden gelen geri bildirimler doğrultusunda sistem modernize edildi.
- **Blender Bridge**: `run_command.py` ve `blenpc.py` arasındaki köprü, mutlak paket yolları kullanacak şekilde optimize edildi.

### ✨ Yeni Özellikler
- **Advanced CLI**: `Click` kütüphanesi ile modern, renkli ve yardım menüsü destekli komut satırı arayüzü.
- **Batch Production**: YAML dosyaları üzerinden çoklu bina üretim desteği eklendi.
- **Inspect & Validate**: Üretilen GLB/Blend dosyalarını ve registry yapısını doğrulayan yeni komutlar eklendi.
- **Auto-Backup**: Registry kayıtlarında zaman damgalı otomatik yedekleme sistemi.

### 🔧 Düzeltmeler ve İyileştirmeler
- **Windows 11 Uyumluluğu**: Blender yolu otomatik keşfi ve `%APPDATA%` yolları için tam destek.
- **Path Management**: `os.path.join` ve `Pathlib` kullanımıyla cross-platform (Windows/Linux) uyumu sağlandı.
- **Precision Control**: `EXPORT_PRECISION` ayarı ile geometri verilerindeki float kirliliği temizlendi.
- **Safe Imports**: Paket içi dairesel bağımlılıklar ve hatalı import yolları temizlendi.
- **Locking System**: Dosya kilit mekanizması (file locking) daha güvenli ve hata toleranslı hale getirildi.

---

## [5.1.0] - 2026-02-18

### ✨ Yeni Özellikler
- **Initial CLI Framework**: `Click` entegrasyonu başlatıldı.
- **YAML Spec Support**: Bina üretiminde YAML dosyası kullanma desteği eklendi.
- **Progress Bars**: Uzun süren üretim işlemleri için CLI ilerleme çubukları.

---

## [5.0.1] - 2026-02-18

### 🔧 Düzeltmeler
- `atoms/wall.py` içindeki eksik JSON ve OS importları eklendi.
- Blender dışı testlerin çalışmasını engelleyen `bpy` import hataları try-except blokları ile giderildi.
- `inventory_manager.py` içindeki dosya kilit sistemi stabilize edildi.
- **Windows Desteği:** `config.py` dosyasında Blender yolu Windows platformuna uyumlu hale getirildi.
- **Numpy Bağımlılığı:** `engine/slot_engine.py` içindeki `numpy` kullanımı standart Python listeleriyle değiştirilerek bağımlılık azaltıldı.

---

## [5.0.0] - Başlangıç Sürümü

- İlk sürüm; temel bina üretim motoru, duvar atomları ve GLB export desteği.

## v5.2.0 - 2026-02-18

### ✨ Yeni Özellikler

- **Tamsayı Grid Sistemi:**
  - `GridPos` sınıfı ile tamsayı koordinat tabanlı konumlandırma.
  - `SceneGrid` ile sparse hashmap tabanlı O(1) zaman karmaşıklığında obje yönetimi ve çakışma tespiti.
  - `IGridObject` arayüzü ile tip güvenli grid entegrasyonu.
  - `config.py` içinde `MICRO_UNIT`, `SNAP_MODES` ve mimari standartlar tanımlandı.

- **Modüler Duvar Sistemi:**
  - Segment tabanlı (0.25m) pre-cut mimari ile duvar üretimi (`wall_modular.py`).
  - Kapı ve pencere açıklıkları için boolean operasyonlar yerine segment bloklama yöntemi.
  - Duvar segmentleri ve slotları için detaylı metadata.

- **Modüler Kapı Sistemi:**
  - 4 parçalı anatomiye sahip kapı modelleri (`door.py`): `frame_jamb_left`, `frame_jamb_right`, `frame_head`, `door_leaf`.
  - `single`, `double`, `garage` gibi farklı kapı stilleri desteği.
  - `wood`, `glass`, `metal`, `composite` gibi çeşitli malzeme seçenekleri.
  - `inward_left`, `inward_right`, `outward_left`, `outward_right`, `sliding` gibi farklı açılma yönleri.
  - `wall_interface`, `doorknob`, `hinge_top`, `hinge_bot` gibi slot sistemleri.

- **Modüler Pencere Sistemi:**
  - 3 parçalı anatomiye sahip pencere modelleri (`window.py`): `frame_outer`, `frame_inner`, `glass_pane`.
  - `small`, `standard`, `large`, `panoramic` gibi farklı pencere stilleri desteği.
  - `wood`, `aluminum`, `pvc` gibi çeşitli çerçeve malzemeleri.
  - `transparent`, `mirror`, `frosted`, `tinted` gibi çift katmanlı cam (inner/outer) malzeme seçenekleri.
  - İsteğe bağlı iç ve dış denizlik (sill) desteği.
  - `wall_interface`, `blind_slot`, `latch_slot` gibi slot sistemleri.

- **Duvar + Kapı/Pencere Entegrasyonu (Composed Wall):**
  - `build_wall_composed` fonksiyonu ile tek bir komutla duvar, kapı ve pencerelerin entegre bir şekilde oluşturulması.
  - **Hierarchical Placement:** Kapı ve pencereler, duvarın child objeleri olarak yönetilerek grid çakışma sorunları giderildi.

- **Sims-tarzı Oda Otomasyonu:**
  - `RoomDetector` ve `auto_complete_room` fonksiyonları ile duvarlardan otomatik oda tespiti.
  - Tespit edilen odalar için otomatik zemin ve tavan metadata üretimi.

### 🐛 Hata Düzeltmeleri

- `wall_modular.py` içindeki `wall_to_json` fonksiyonunda `GridPos` objelerinin JSON serileştirme hatası giderildi.
- `door.py` içindeki kapı kolu konumlandırma mantığı düzeltildi (`inward_left` ve `inward_right` swing yönleri için).
- `test_room_automation.py` içindeki oda alanı hesaplama testi beklentisi, duvar kalınlığı dikkate alınarak güncellendi.

### 🧪 Testler ve Güvenilirlik

- Kapsamlı bir regresyon test paketi (`test_regression_suite.py`) oluşturuldu.
- Toplam **116 adet** birim ve entegrasyon testi başarıyla geçildi.
- Geliştirilen tüm modüller için %100 test başarı oranı sağlandı.

### 📝 Dokümantasyon

- `COLLISION_PROBLEM_ANALYSIS.md` dosyası ile Composed Wall entegrasyonundaki collision probleminin detaylı analizi ve çözümü belgelendi.
- `PROGRESS_SUMMARY.md` dosyası ile projenin genel ilerlemesi ve tamamlanan fazlar özetlendi.

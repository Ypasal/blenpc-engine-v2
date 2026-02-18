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

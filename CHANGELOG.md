# Değişiklik Günlüğü

Tüm önemli değişiklikler bu dosyada belgelenecektir.

## [5.0.1] - 2026-02-18

### Düzeltildi
- **Windows Desteği:** `config.py` dosyasında Blender yolu Windows platformuna uyumlu hale getirildi.
- **JSON Import:** `atoms/wall.py` dosyasına eksik `json` ve `os` importları eklendi.
- **Global Kontrolü:** `atoms/wall.py` içindeki hatalı `json in globals()` kontrolü kaldırıldı.
- **Import Yolları:** Modüller arası bağımlılıklar için göreceli (relative) importlar düzeltildi.
- **Numpy Bağımlılığı:** `engine/slot_engine.py` içindeki `numpy` kullanımı standart Python listeleriyle değiştirilerek bağımlılık azaltıldı.

### Eklendi
- **Paket Yapısı:** `__init__.py` dosyaları eklenerek proje tam bir Python paketi haline getirildi.
- **Doğrulama Mekanizması:** `run_command.py` ve `mf_v5/engine.py` dosyalarına girdi verisi doğrulamaları eklendi.
- **Slot Doğrulama:** `atoms/wall.py` içine slot verilerini kontrol eden `validate_slot` fonksiyonu eklendi.
- **Envanter Kilidi İyileştirmesi:** `engine/inventory_manager.py` içine zaman aşımına uğramış (stale) kilitleri temizleme özelliği eklendi.
- **Logging:** `config.py` üzerinden yönetilen merkezi logging yapılandırması eklendi.
- **Sabitler:** Sihirli sayılar `config.py` içindeki isimlendirilmiş sabitlere taşındı.

### Güncellendi
- **Dokümantasyon:** `README.md` CLI örnekleriyle güncellendi, `API_REFERENCE.md` yenilendi.
- **Hata Yakalama:** `run_command.py` içindeki exception handling daha detaylı hale getirildi.

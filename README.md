# 🏗️ BlenPC v5.1.1 (Optimized)

BlenPC, **Blender 5.0.1+** ve **Godot Engine** için tasarlanmış, mühendislik standartlarında bir prosedürel bina ve varlık üretim motorudur. Bu sürüm, **Engine V2** ile tamamen modernize edilmiş, immutable ve deterministik bir çekirdek yapıya kavuşmuştur.

---

## 🚀 Engine V2 (Yeni Nesil Çekirdek)

Engine V2, projenin kalbidir ve aşağıdaki prensiplerle geliştirilmiştir:
- **Immutability:** Tüm state yapısı değişmezdir.
- **Purity:** Tüm fonksiyonlar yan etkisizdir (pure).
- **Determinism:** Aynı girdi her zaman aynı çıktıyı üretir.
- **Blender Independence:** Blender olmadan çalışabilir, test edilebilir.

---

## 🏛️ Mimari Yapı

Proje, katmanlı ve modüler bir yapıda organize edilmiştir:

### 📂 Klasör Organizasyonu
| Dizin / Dosya | Sorumluluk Alanı |
| :--- | :--- |
| `src/blenpc/engine_v2/` | **Yeni Nesil Engine (Tavsiye Edilen)** |
| `├── core/` | Çekirdek modüller (Grid, Collision, Room Detection vb.) |
| `└── tests/` | Engine V2 test suite (165+ test) |
| `src/blenpc/engine/` | Eski nesil engine (Legacy) |
| `src/blenpc/atoms/` | Temel Yapı Taşları (Wall, Window, Door) |
| `src/blenpc/mf_v5/` | Prosedürel Bina Üretim Mantığı |
| `docs/` | Proje dokümantasyonu ve FAZ raporları |
| `_library/` | Üretilen `.blend` Varlık Kütüphanesi |
| `_registry/` | JSON Tabanlı Varlık Envanteri (Inventory) |
| `output/` | Final Çıktılar (GLB, Manifest) |

---

## 💻 Kullanım

### Testleri Çalıştırma
Engine V2'nin stabilitesini doğrulamak için:
```bash
pytest src/blenpc/engine_v2/tests/ -v
```

### Hızlı Başlangıç (Engine V2)
```python
from blenpc.engine_v2.core import Engine

engine = Engine()
engine.place("wall_01", frozenset({(0, 0, 0), (1, 0, 0)}))
print(engine.state.is_occupied((0, 0, 0))) # True
```

---

## 📚 Dokümantasyon
Detaylı API ve mimari bilgileri için aşağıdaki dosyalara göz atabilirsiniz:
- [Engine V2 Detaylı README](src/blenpc/engine_v2/README.md)
- [FAZ 8 Tamamlama Raporu](docs/faz_8/FAZ_8_COMPLETION_REPORT.md)
- [Final Teslimat Özeti](docs/faz_8/FINAL_DELIVERY_SUMMARY.md)

---

## 📄 Lisans
MIT License.

---
**Durum:** FAZ 8 Tamamlandı. Engine V2 Production-Ready. ✅

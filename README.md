# 🏗️ BlenPC v5.1.1 (Expert Edition)

BlenPC, **Blender 5.0.1+** ve modern oyun motorları (Godot, Unity, Unreal) için tasarlanmış, **uzman kadro disiplinleri** ile modernize edilmiş profesyonel bir prosedürel bina ve varlık üretim motorudur. 

Proje, geleneksel mesh üretiminin ötesine geçerek; deterministik matematiksel kurallar, akıllı slot yerleştirme sistemleri ve tam otomatize edilmiş bir komut satırı arayüzü (CLI) sunar.

---

## 🏛️ Uzman Mimari (Expert Architecture)

Bu sürüm, 10 farklı uzman disiplinin (Software Architect, DevOps, QA, UX vb.) ortak kararlarıyla **`src/` tabanlı modern bir paket yapısına** kavuşturulmuştur.

### 📂 Proje Yapısı ve Organizasyonu
| Dizin / Dosya | Sorumluluk Alanı | Uzman Disiplin |
| :--- | :--- | :--- |
| `src/blenpc/` | Ana Kaynak Kod (Package Root) | Software Architect |
| `├── atoms/` | Temel Yapı Taşları (Wall, Window, Door) | Geometry Specialist |
| `├── engine/` | Envanter ve Slot Yerleştirme Motoru | Data Scientist |
| `├── mf_v5/` | Prosedürel Bina Üretim Mantığı | Pipeline Specialist |
| `├── config.py` | Merkezi Ayarlar ve Path Yönetimi | DevOps Engineer |
| `└── run_command.py` | Blender Bridge ve Komut Köprüsü | Systems Engineer |
| `blenpc.py` | Modern Click Tabanlı CLI Giriş Noktası | UX Designer |
| `_library/` | Üretilen `.blend` Varlık Kütüphanesi | Asset Manager |
| `_registry/` | JSON Tabanlı Varlık Veritabanı (Inventory) | Database Specialist |
| `output/` | Final Çıktılar (GLB, FBX, Manifest) | Export Specialist |

---

## 🚀 Temel Özellikler ve Yenilikler

### 1. Deterministik Üretim (Seed-Based)
Aynı `seed` değeri, farklı zamanlarda veya makinelerde çalıştırılsa bile **birebir aynı** kat planını ve geometriyi üretir. Bu, takım çalışmalarında ve versiyon kontrolünde tam tutarlılık sağlar.

### 2. Akıllı Slot ve Envanter Sistemi
Her üretilen varlık (örneğin bir duvar), üzerinde matematiksel olarak hesaplanmış **bağlantı noktaları (slots)** barındırır. Bu slotlar, kapı ve pencerelerin otomatik ve hatasız yerleştirilmesini sağlar.

### 3. Windows 11 & Blender 5.0.1 Optimizasyonu
- **Otomatik Keşif:** Blender yolu, Windows Registry ve standart kurulum dizinlerinde otomatik olarak bulunur.
- **Path Uyumluluğu:** Tüm dosya yolları `%APPDATA%` ve Windows dosya sistemi standartlarına tam uyumludur.

### 4. Manifold Geometri Garantisi
Euler formülü (**V - E + F = 2**) kullanılarak her üretilen mesh'in manifold (kapalı ve hatasız) olduğu matematiksel olarak doğrulanır.

---

## 💻 CLI Kullanım Rehberi

BlenPC, `blenpc.py` üzerinden modern ve güçlü bir komut satırı arayüzü sunar.

### 🏢 Bina Üretimi (Generate)
```bash
# Doğrudan parametrelerle üretim
python blenpc.py generate --width 25 --depth 18 --floors 3 --seed 2026 --roof hip

# YAML Spec dosyasından üretim (Önerilen)
python blenpc.py generate --spec mansion.yaml
```

### 📦 Toplu Üretim (Batch)
Yüzlerce binayı tek bir komutla ve paralel işleme desteğiyle üretebilirsiniz:
```bash
python blenpc.py batch --spec city_block.yaml
```

### 🔍 Denetleme ve Doğrulama (Inspect & Validate)
```bash
# GLB dosyasını analiz et
python blenpc.py inspect output/MyBuilding.glb

# Spec dosyasını veya Registry'yi doğrula
python blenpc.py validate --spec mansion.yaml
python blenpc.py validate --registry
```

---

## 🔧 Uzman Ayarları (`config.py`)

Proje, `src/blenpc/config.py` üzerinden 10+ kritik ayar ile özelleştirilebilir:
- **`I18N_LANGUAGE`:** Çoklu dil desteği (Varsayılan: `tr`).
- **`EXPORT_PRECISION`:** Koordinat hassasiyeti (Hafif ve tutarlı GLB'ler için).
- **`AUTO_BACKUP_REGISTRY`:** Her asset kaydında otomatik yedekleme.
- **`STRICT_VALIDATION`:** Üretim öncesi sıkı geometri kontrolü.

---

## 🛠️ Kurulum ve Gereksinimler

1. **Blender 5.0.1+** yüklü olduğundan emin olun.
2. Repoyu klonlayın:
   ```bash
   git clone https://github.com/ozyorionlast-cloud/blenpc-5.0-optimized
   ```
3. Bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

---

## 📄 Lisans ve Katkıda Bulunma
Bu proje **MIT Lisansı** ile korunmaktadır. Uzman kadro tarafından geliştirilen bu sistem, topluluk katkılarına açıktır.

---
*BlenPC v5.1.1 - Geleceğin Prosedürel Mimarisi için Bugünün Mühendisliği.*

# BlenPC v5.1 - Uzman Kadro Analiz ve Karar Raporu

BlenPC projesini endüstriyel standartlara taşımak için kurulan uzman kadro, aşağıdaki kararları almıştır:

## 1. Uzman Kadro (10 Disiplin)
1.  **Yazılım Mimarı (Software Architect):** `src/` tabanlı standart paket yapısına geçiş kararı.
2.  **Blender Pipeline Uzmanı:** `bpy` bağımlılığının `headless` ve `UI` modları arasında net ayrımı.
3.  **DevOps Mühendisi:** Windows 11 ortamı için platform bağımsız yol (path) yönetimi.
4.  **QA Otomasyon Uzmanı:** Testlerin modüler hale getirilmesi ve `conftest.py` iyileştirmesi.
5.  **Veri Bilimci (Data Scientist):** JSON registry yapısının ilişkisel ve sorgulanabilir hale getirilmesi.
6.  **UX Tasarımcısı:** CLI çıktılarını daha okunabilir ve renkli hale getirme (Rich/Click).
7.  **Siber Güvenlik Uzmanı:** Dosya kilitleme ve registry yazma süreçlerinde yetki kontrolü.
8.  **Teknik Yazar:** API referanslarının otomatik üretimi ve i18n (çoklu dil) desteği.
9.  **Sistem Mühendisi:** Bellek (RAM) kullanımı için Blender process izolasyonu.
10. **Proje Yöneticisi:** Versiyonlama (v5.1.1) ve sürüm günlüğü (Changelog) standartları.

## 2. Mimari Kararlar (Klasör Yapısı)
Eski düzensiz yapı yerine `src/blenpc/` altında toplanan, testlerin ve dokümanların kök dizinde olduğu modern yapıya geçilecektir.

## 3. 10 Kritik Düzeltme (Özet)
-   Dinamik `PROJECT_ROOT` tespiti.
-   `config.py`'nin `Settings` sınıfına dönüştürülmesi.
-   Hatalı `sys.path` eklemelerinin temizlenmesi.
-   Blender yolunun otomatik keşfi (Windows Registry/PATH).
-   `__init__.py` hiyerarşisinin tamiri.
-   Gereksiz `numpy` kalıntılarının temizliği.
-   Hata mesajlarının standardize edilmesi.
-   Log dosyalarının Windows `%APPDATA%` uyumlu olması.
-   Registry dosya kilidinin (lock) daha güvenli hale getirilmesi.
-   Asset export formatlarının parametrik yapılması.

## 4. 10 Yeni Ayar (Özet)
-   `I18N_LANGUAGE` (tr/en).
-   `EXPORT_PRECISION` (float hassasiyeti).
-   `WINDOWS_BLENDER_REG_PATH` (Otomatik Blender bulma).
-   `CACHE_ENABLED` (Hızlı üretim).
-   `CLI_COLOR_THEME` (Terminals).
-   `MAX_WORKER_PROCESSES` (Paralel işlem).
-   `LOG_FORMAT_EXTENDED`.
-   `DEFAULT_UNIT_SYSTEM` (Metric/Imperial).
-   `AUTO_BACKUP_REGISTRY`.
-   `STRICT_VALIDATION` (Üretim öncesi sıkı kontrol).

# ⚡ Günlük Enerji Depolama & Yatırım Raporu

Her gün otomatik olarak güncellenen global enerji depolama istihbarat platformu.

**[→ Raporu Gör](https://KULLANICI_ADI.github.io/REPO_ADI/)**

---

## 📊 İçerik

- **179+ kaynak** — Energy Storage News, PV Magazine, Clean Energy Wire, Google News (TR/EN/CN)
- **7 bölge** — Türkiye, AB, ABD, Çin, APAC, İngiltere, Global
- **NLP sınıflandırma** — Yatırım (Equity/Hibe), Startup, Regülasyon, Enerji
- **Şirket profil kartları** — Skor (0-100), trend (↑↓→), yatırım tutarları
- **Otomatik Türkçe çeviri** — İngilizce başlıklar Türkçe'ye çevriliyor

## 🔄 Güncelleme

Her gün saat **10:00 Türkiye saati** (07:00 UTC) otomatik çalışır.

Manuel tetiklemek için: **Actions → Günlük Enerji Raporu → Run workflow**

## 🛠️ Kurulum

### 1. Repo'yu fork et veya klonla

```bash
git clone https://github.com/KULLANICI_ADI/REPO_ADI.git
cd REPO_ADI
```

### 2. GitHub Pages'i aktive et

`Settings → Pages → Source: Deploy from branch → Branch: main → Folder: /docs`

### 3. İlk raporu üret

`Actions → Günlük Enerji Raporu → Run workflow`

### Yerel çalıştırma (Colab veya terminal)

```bash
pip install -r requirements.txt
python run.py
```

## 📁 Dosya Yapısı

```
├── energy_monitor_v6.py   # Ana platform
├── run.py                 # GitHub Actions wrapper
├── requirements.txt       # Bağımlılıklar
├── docs/
│   └── index.html         # 🌐 GitHub Pages — günlük rapor
└── .github/workflows/
    └── daily.yml          # Günlük otomasyon
```

## ⚙️ Özelleştirme

`energy_monitor_v6.py` içinde:

```python
# Pencere: kaç günlük haber alınsın
hours=168  # 7 gün

# Güncelleme sıklığı
EnergyMonitor(interval_min=1440)  # 1440 = günde 1
```

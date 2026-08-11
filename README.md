# 🐰 Berry Coffee Photo Booth

Self-servis fotoğraf kabini uygulaması. Android tablet + foto yazıcı ile çalışır.

## Özellikler
- 📸 3 saniyelik geri sayımlı fotoğraf çekimi
- 🖼️ Otomatik Berry Coffee çerçevesi + logo
- 🎨 8 farklı sticker seçeneği
- 🖨️ Tek tıkla yazdırma (10×15 cm)
- 🔄 Baskı sonrası otomatik başa dönüş

## Dosyalar

| Dosya | Açıklama |
|-------|----------|
| `index.html` | Ana uygulama (kamera, önizleme, baskı) |
| `server.py` | HTTP sunucusu |
| `make_frame.py` | Çerçeve PNG üreteci (300 DPI) |
| `frame_overlay.png` | Şeffaf çerçeve katmanı |
| `frame_preview.png` | Önizleme görseli |
| `logo.png` | Berry Coffee logosu |
| `manifest.json` | PWA manifest (tam ekran) |

## Kurulum

### 1. Gereksinimler
```bash
pip install Pillow
```

### 2. Çerçeveyi üret
```bash
python make_frame.py
```

### 3. Sunucuyu başlat
```bash
python server.py
# veya:
python -m http.server 8080
```

### 4. Uygulamayı aç
- **PC:** `http://localhost:8080`
- **Android tablet:** `http://[PC_IP]:8080`

## Yazıcı Ayarı

`server.py` içinde 17. satırı düzenle:
```python
PRINTER_NAME = None              # Windows varsayılan yazıcı
# PRINTER_NAME = "Canon SELPHY CP1300"  # Belirli yazıcı
```

## Kiosk Kurulumu (Android)

**Fully Kiosk Browser** (Play Store) → Start URL: `http://[PC_IP]:8080` → Kiosk Mode: ON

---
Berry Coffee Company © 2026

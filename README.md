# 🐱 Kicau Mania Detector

# Project ini merupakan sistem interaktif berbasis computer vision yang mampu mendeteksi gesture real-time melalui kamera, lalu meresponsnya dengan membuka video MP4 di tab baru. Trigger dibuat dari kombinasi gesture 2 tangan: menutup mulut dan mengibas kiri-kanan. Konsep ini menciptakan pengalaman interaksi tanpa sentuhan yang intuitif dan visual.

> 2 tangan + tutup mulut + kibas → Video kucing terbuka di tab baru!

---

## 📋 Yang Dibutuhkan

- Laptop/PC dengan kamera (webcam)
- Python 3.9 – 3.11 (direkomendasikan 3.10)
- Koneksi internet (untuk install library)

---

## 🚀 Cara Setup (Langkah demi Langkah)

### Langkah 1 — Install Python
Kalau belum punya Python, download di: https://www.python.org/downloads/

> ⚠️ Saat install, centang **"Add Python to PATH"**

---

### Langkah 2 — Buka Terminal / Command Prompt

- **Windows**: Tekan `Win + R`, ketik `cmd`, Enter
- **Mac**: Tekan `Cmd + Space`, ketik `Terminal`, Enter

---

### Langkah 3 — Masuk ke Folder Project

```bash
cd path/ke/folder/kicau_mania
```

Contoh di Windows:
```
cd C:\Users\NamaKamu\Downloads\kicau_mania
```

---

### Langkah 4 — Install Library yang Dibutuhkan

```bash
pip install -r requirements.txt
```

Tunggu sampai selesai (bisa 2–5 menit tergantung koneksi).

---

### Langkah 5 — Siapkan Video MP4 Kucing Joget 🐱

1. Pakai video MP4 dengan nama **`kicau-mania.mp4`**
2. Simpan file video di folder yang sama dengan `main.py`
3. Jika nama berbeda, tetap bisa selama formatnya `.mp4`

Struktur folder harus seperti ini:
```
kicau_mania/
├── main.py          ← kode utama
├── requirements.txt
├── README.md
└── kicau-mania.mp4  ← video trigger
```

---

### Langkah 6 — Jalankan!

```bash
python main.py
```

---

## 🎮 Cara Main

| Aksi | Hasil |
|------|-------|
| 2 tangan terdeteksi + tutup mulut + kibas | MP4 terbuka di tab baru |
| Syarat belum lengkap | Status deteksi ditampilkan di layar kamera |
| Tekan **Q** | Keluar dari aplikasi |

---

## ⚙️ Pengaturan (Opsional)

Buka `main.py`, di bagian atas ada **KONFIGURASI** yang bisa kamu ubah:

```python
CAT_SIZE       = (220, 220)  # Ukuran kucing (lebih besar = angka lebih besar)
WAVE_THRESHOLD = 2           # Jumlah perubahan arah untuk dianggap kibas
MOVE_MINIMUM   = 0.018       # Sensitivitas gerakan (lebih kecil = lebih sensitif)
MOUTH_COVER_DISTANCE = 0.16  # Jarak tangan ke mulut agar dianggap menutup mulut
TRIGGER_COOLDOWN = 4.0       # Jeda antar trigger (detik)
```

---

## 🛠️ Troubleshooting

| Masalah | Solusi |
|---------|--------|
| `ModuleNotFoundError` | Jalankan `pip install -r requirements.txt` lagi |
| Kamera tidak terbuka | Coba ganti `cv2.VideoCapture(0)` menjadi `cv2.VideoCapture(1)` |
| Video tidak terbuka di tab baru | Pastikan browser default aktif & file MP4 ada di folder project |
| Gesture sulit terdeteksi | Coba turunkan `MOVE_MINIMUM` ke `0.015` |
| Trigger terlalu sering | Naikkan `WAVE_THRESHOLD` atau `TRIGGER_COOLDOWN` |

---

## 🧠 Cara Kerja (Singkat)

```
Kamera → MediaPipe Hands (2 tangan) + Face Mesh (mulut)
→ Cek tangan menutup mulut + deteksi kibas
→ Jika valid, buka MP4 di tab baru
```

---

## 📦 Library yang Digunakan

- **OpenCV** → Akses kamera & tampilkan video
- **MediaPipe** → Deteksi dan tracking tangan (dari Google)
- **MediaPipe Face Mesh** → Landmark wajah untuk area mulut
- **Pillow** → Utilitas pembacaan GIF (opsional)
- **NumPy** → Olah data gambar

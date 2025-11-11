# 🤖 FelixBaseUserBot

<div align="center">
  <img src="https://raw.githubusercontent.com/sandyparadox59-alt/fel/refs/heads/main/assets/felix-banner.png" alt="FelixBaseUserBot Banner" width="80%">
  <br><br>
  <b>💬 Telegram Userbot sederhana berbasis Python & Telethon</b><br>
  🔹 Dibuat sebagai base untuk pengembangan userbot modular
  <br><br>
  <a href="https://github.com/sandyparadox59-alt/fel"><img src="https://img.shields.io/github/stars/sandyparadox59-alt/fel?color=yellow&style=for-the-badge"></a>
  <a href="https://t.me/GlobalBotzXD"><img src="https://img.shields.io/badge/Telegram-Join%20Chat-blue?style=for-the-badge&logo=telegram"></a>
</div>

---

## ⚙️ Fitur Dasar

✅ **plugin** – Ringan dan langsung jalan  
✅ **Command otomatis** – Ketik di Telegram dengan awalan titik (.)  
✅ **Logging chat** – Semua pesan masuk dan keluar tercatat di terminal  
✅ **Khusus owner/reseller** – Fitur forward ke seluruh grup hanya untuk user tertentu  
✅ **Mudah dikembangkan** – Bisa kamu ubah jadi sistem Market dan ubot panel kapan saja  

---

## 🧠 Command Tersedia

| Command | Fungsi |
|----------|--------|
| `.help` | Menampilkan menu bantuan |
| `.ping` | Cek kecepatan respon bot |
| `$` | $ ls Menampilkan Data (hanya untuk owner) |
| `.id` `.idgc` | Menampilkan ID pengguna atau chat |
| `.bc` `.bcgc` `.all` | Forward pesan ke semua grup (hanya untuk owner/reseller) |
| `.tourl` `.hd` `.removebg ` | Upload gambar to url Hd foto hapus background foto (ai) |

---

## 🚀 Cara Install

### 1️⃣ Update sistem
```bash
apt update && apt upgrade -y
```

### 2️⃣ Install Python, pip, dan Git
```bash
apt install python3 python3-pip git -y
```

### 3️⃣ Install dependensi Python
```bash
pip install -r requirements.txt
```
⚠️ Jika muncul error `externally-managed-environment`, gunakan:
```bash
pip install -r requirements.txt --break-system-packages
```

---

### 4️⃣ Download source code
```bash
git clone https://github.com/sandyparadox59-alt/fel.git
cd fel
```

---

### 5️⃣ Jalankan Userbot
```bash
python3 Felix.py
```

Lalu isi data berikut saat diminta:
```
Please enter your phone (or bot token): 62xxxxxxxxxx
Please enter the code you received: [OTP]
Please enter your password: [jika ada 2FA]
```

Jika login berhasil ✅, maka bot akan langsung aktif dan menampilkan:
```
🚀 Menjalankan Userbot Telegram tanpa plugin...
✅ Userbot aktif! Ketik `.help` di Telegram.
```

---

## 📁 Struktur Folder
```
fel/
├── Felix.py         # File utama userbot
|  ├── plugins       # plugins
├── config.py        # Konfigurasi API dan Owner
├── requirements.txt # Dependensi Python (opsional)
└── README.md        # Dokumentasi
```

---

## 🧩 Konfigurasi `config.py`
Buat file `config.py` di folder yang sama, lalu isi:
```python
API_ID = 123456
API_HASH = "abcdef1234567890abcdef1234567890"
SESSION = "FelixSession"
OWNER_ID = 123456789
RESELLERS = [987654321, 1122334455]
```

---

## 🧩𝘊𝘳𝘦𝘢𝘵𝘦 𝘈𝘱𝘪 𝘐𝘥 𝘈𝘱𝘪 𝘏𝘢𝘴𝘩

https://my.telegram.org

```bash
𝘔𝘢𝘴𝘶𝘬𝘢𝘯 𝘯𝘢𝘮𝘢 𝘵𝘪𝘵𝘭𝘦 , shorts name 𝘣𝘦𝘣𝘢𝘴
𝘜𝘯𝘵𝘶𝘬 𝘭𝘢𝘪𝘯𝘺𝘢 𝘵𝘪𝘥𝘢𝘬 𝘶𝘴𝘢𝘩 𝘥𝘪 𝘪𝘴𝘪 
𝘋𝘢𝘯 𝘬𝘭𝘪𝘬 𝘤𝘳𝘦𝘢𝘵𝘦 𝘭𝘢𝘭𝘶 𝘥𝘰𝘯𝘦 🗿😹 
```

---

## 🧰 Tips Tambahan
💡 Jalankan bot di background (VPS):
```bash
nohup python3 Felix.py &
```
💡 Untuk menghentikan bot:
```bash
ps aux | grep Felix.py
kill -9 [PID]
```

---

## 📸 Preview
<div align="center">
  <img src="https://raw.githubusercontent.com/sandyparadox59-alt/fel/refs/heads/main/assets/felix-preview.png" alt="FelixBaseUserBot Preview" width="70%">
</div>

---

## 🧑‍💻 Author
**Created by [@sandyparadox59-alt](https://github.com/sandyparadox59-alt)**  
> “Aku hanya membuat base — kembangkan sesukamu 😎”

---

## ⭐ Support
Jika kamu suka proyek ini, bantu dengan menekan ⭐ **Star** di repositori ini 🙏  
Kamu juga bisa fork dan ubah jadi sistem plugin penuh sesuai kebutuhanmu!

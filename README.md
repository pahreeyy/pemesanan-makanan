# README.md — Sistem Informasi POS & Manajemen Pemesanan Restoran

# 🍽️ Sistem Informasi POS — Restoran

Aplikasi desktop Point of Sales (POS) dan Manajemen Pemesanan Restoran berbasis **Python 3** dengan antarmuka grafis modern menggunakan **CustomTkinter** dan penyimpanan data lokal melalui **JSON**.

---

## 📁 Struktur Proyek

```
pemesanan-makanan/
│
├── main.py                         # Entry point — inisialisasi app & router navigasi
├── requirements.txt                # Dependensi Python
│
├── data/                           # Penyimpanan data JSON
│   ├── menu.json                   # Katalog menu (CRUD)
│   ├── paket.json                  # Paket bundling menu
│   └── transaksi.json              # Riwayat transaksi
│
├── models/                         # Domain model (OOP Classes)
│   ├── menu.py                     # Class Menu
│   ├── paket.py                    # Class Paket
│   ├── item_pesanan.py             # Class ItemPesanan
│   ├── keranjang.py                # Class Keranjang (shopping cart)
│   ├── pelanggan.py                # Class Pelanggan
│   ├── pesanan.py                  # Class Pesanan (kitchen order lifecycle)
│   ├── transaksi.py                # Class Transaksi (payment record)
│   ├── nota_pesanan.py             # Class NotaPesanan (receipt formatter)
│   └── laporan_penjualan.py        # Class LaporanPenjualan (sales analytics)
│
├── data_handlers/                  # JSON CRUD layer
│   ├── base_handler.py             # Abstract BaseHandler (interface contract)
│   ├── menu_handler.py             # MenuHandler — CRUD untuk menu.json
│   ├── paket_handler.py            # PaketHandler — CRUD untuk paket.json
│   └── transaksi_handler.py        # TransaksiHandler — CRUD untuk transaksi.json
│
├── controllers/                    # Business logic / service layer
│   ├── admin_restoran.py           # AdminRestoran — manajemen menu & laporan
│   └── kasir.py                    # Kasir — session, cart, payment, receipt
│
└── views/                          # UI layer (CustomTkinter)
    ├── theme.py                    # Design tokens (colors, fonts, spacing)
    ├── components.py               # Reusable widget components
    ├── login_view.py               # Login / role selection screen
    ├── dashboard_kasir_view.py     # Kasir POS dashboard
    └── dashboard_admin_view.py     # Admin CRUD + Laporan dashboard
```

---

## 🚀 Cara Menjalankan

### 1. Install dependensi

```bash
pip install -r requirements.txt
```

### 2. Jalankan aplikasi

```bash
python main.py
```

---

## ✨ Fitur Utama

| Fitur | Keterangan |
|---|---|
| **Role Selection** | Login sebagai Kasir atau Admin/Manajer |
| **Katalog Menu CRUD** | Tambah, edit, hapus, dan toggle ketersediaan menu |
| **POS Order Entry** | Grid menu dengan filter kategori & pencarian |
| **Keranjang Belanja** | Tambah/ubah jumlah/hapus item secara real-time |
| **Kalkulasi Otomatis** | Total, kembalian dihitung otomatis |
| **Metode Pembayaran** | Tunai & Non-Tunai |
| **Nota Pesanan** | Struk format termal printer ditampilkan setelah bayar |
| **Laporan Penjualan** | Total pendapatan, jumlah transaksi, menu terlaris |
| **Filter Laporan** | Filter berdasarkan rentang tanggal |
| **Riwayat Transaksi** | Tabel lengkap semua transaksi selesai |

---

## 🏗️ Arsitektur

Proyek mengikuti pola **MVC (Model-View-Controller)**:

- **Models** (`/models`): Representasi domain bisnis murni. Tidak tahu UI maupun file storage.
- **Data Handlers** (`/data_handlers`): Lapisan abstraksi CRUD ke file JSON. Semua `json.load()` / `json.dump()` ada di sini.
- **Controllers** (`/controllers`): Service layer — logika bisnis yang mengorkestrasi model dan handler.
- **Views** (`/views`): Lapisan UI dengan CustomTkinter. Memanggil handlers langsung atau via controllers.

---

## 📦 Teknologi

- **Python 3.10+**
- **CustomTkinter 5.2+** — Modern dark-mode GUI framework
- **Pillow** — Image support (dibutuhkan CustomTkinter)
- **json** (built-in) — Data storage

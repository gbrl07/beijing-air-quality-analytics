# 📊 Proyek Akhir: Fundamental Analisis Data - Beijing Air Quality Analytics

Dokumen ini berisi informasi proyek, kriteria penilaian, dan panduan lengkap untuk menjalankan **Dashboard Interaktif Streamlit** serta dokumen analisis data.

- **Nama Pengembang:** Gabriel Alfareslanda Riyadi
- **Email:** gabrielriyadi715@gmail.com
- **ID Dicoding:** `gbrlalfrs`
- **Dataset:** *Beijing Multi-Site Air-Quality Data* (2013–2017)

---

## 🚀 Panduan Menjalankan Dashboard di Local Environment

Ikuti langkah-langkah berikut untuk menjalankan antarmuka dashboard interaktif Streamlit di komputer lokal Anda:

### 1. Prasyarat (*Prerequisites*)
Pastikan Python versi 3.9 atau yang lebih baru sudah terpasang di komputer Anda.

### 2. Buka Terminal / Command Prompt
Arahkan direktori terminal ke folder proyek:
```bash
cd "folder path"
```

### 3. (Opsional) Buat dan Aktifkan Virtual Environment
```bash
# Membuat virtual environment
python -m venv .venv

# Mengaktifkan virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Atau (Windows Command Prompt)
.\.venv\Scripts\activate.bat
```

### 4. Instalasi Dependensi / Pustaka
Instal seluruh pustaka yang tercantum pada berkas `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 5. Jalankan Dashboard Streamlit
Jalankan aplikasi Streamlit dengan perintah berikut:
```bash
streamlit run dashboard/dashboard.py
```
*Atau jika Anda sedang berada di dalam folder `dashboard/`:*
```bash
cd dashboard
streamlit run dashboard.py
```
Aplikasi dashboard akan otomatis terbuka di peramban web (*browser*) Anda pada alamat `http://localhost:8501`.

---

## 🎛️ Fitur Dashboard Interaktif

Dashboard dirancang secara modular dan responsif dengan fitur-fitur unggulan:
1. **Interactive Sidebar Filters:**
   - **Filter Rentang Tanggal (`date_input`):** Memungkinkan pemilihan periode spesifik dari 1 Maret 2013 hingga 28 Februari 2017.
   - **Filter Stasiun Pemantau (`multiselect` & Checkbox):** Memilih satu, beberapa, atau seluruh 12 stasiun pemantau di Beijing.
   - **Filter Parameter Polutan (`selectbox`):** Fleksibilitas analisis polutan utama ($PM_{2.5}, PM_{10}, SO_2, NO_2, CO, O_3$).
2. **Dynamic KPI Metrics Cards:**
   - Menampilkan total jam pengamatan, rata-rata konsentrasi $PM_{2.5}$ beserta status baku mutu, rata-rata $PM_{10}$, stasiun terbersih (*cleanest station*), dan stasiun terpolusi (*worst station*).
3. **Tab 1: Tren Temporal & Siklus Musiman (Pertanyaan 1):**
   - Grafik garis runtun waktu bulanan dengan anotasi titik puncak polusi tertinggi dan garis ambang batas baku mutu nasional.
   - Grafik batang siklus musiman bulanan (Januari–Desember) dengan pewarnaan musim dingin/gugur vs musim semi/panas.
   - Analisis diurnal harian (rata-rata per jam 00:00–23:00) untuk mendeteksi dampak inversi termal malam hari.
4. **Tab 2: Perbandingan Spasial 12 Stasiun (Pertanyaan 2):**
   - Grafik horizontal bar chart ganda membandingkan tingkat $PM_{2.5}$ dan $PM_{10}$ di seluruh 12 stasiun.
   - Tabel peringkat stasiun dengan status indikator kualitas udara.
   - Analisis disparitas geografis (kawasan urban pusat vs suburban/pegunungan utara).
5. **Tab 3: Analisis Lanjutan (Clustering/Binning AQI):**
   - Pengelompokan kualitas udara ke dalam 6 kategori standar baku mutu kesehatan (Baik, Sedang, Tidak Sehat Sensitif, Tidak Sehat, Sangat Tidak Sehat, Berbahaya).
   - Donut chart distribusi jam kualitas udara dan horizontal stacked bar proporsi per stasiun.
6. **Tab 4: Analisis Faktor Meteorologi:**
   - Heatmap korelasi parameter cuaca (Suhu, Tekanan, Hujan, Kecepatan Angin) terhadap konsentrasi polutan.
   - Analisis efek dispersi kecepatan angin (*WSPM*) dan pencucian oleh air hujan (*wet scavenging*).
7. **Tab 5: Kesimpulan & Rekomendasi Aksi:**
   - Jawaban tuntas untuk Pertanyaan Bisnis 1 & 2.
   - 3 Rekomendasi *Action Items* nyata bagi pemangku kebijakan tata kota dan lingkungan hidup.
   - **Tombol Unduh Data Terfilter:** Mengunduh data hasil filter pengguna langsung dalam format `.csv`.

---

## 📁 Struktur Berkas Proyek

```text
Fundamental Analisis Data/
├── dashboard/
│   ├── main_data.csv               # Dataset bersih yang dikonsumsi oleh dashboard (420.768 baris)
│   └── dashboard.py                # Skrip aplikasi interaktif Streamlit
├── data/                           # Direktori berkas dataset mentah asli (12 file stasiun PRSA)
│   ├── PRSA_Data_Aotizhongxin_20130301-20170228.csv
│   ├── PRSA_Data_Changping_20130301-20170228.csv
│   └── ... (stasiun lainnya)
├── Fundamental_Analisis_Data.ipynb # Jupyter Notebook analisis data end-to-end (lengkap dengan output)
├── README.md                       # Panduan lengkap proyek & cara menjalankan dashboard
├── requirements.txt                # Daftar pustaka Python yang dibutuhkan
└── url.txt                         # Tautan live deployment Streamlit Cloud (jika di-deploy)
```

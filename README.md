# Gold Price Analytics Dashboard 📈✨

Proyek ini merupakan analisis data harga emas Indonesia yang bertujuan untuk memahami tren harga emas, volatilitas pasar, distribusi harga, serta hubungan antara harga emas global dan nilai tukar USD/IDR. Dashboard dibangun menggunakan Streamlit dan Plotly untuk menyajikan insight bisnis secara interaktif dan mudah dipahami.

## Project Structure

```text
gold-price-analysis
│
├── dashboard
│   ├── app.py
│   └── gold_data_cache.csv
│
├── tambah_eda.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

## Business Questions

1. Bagaimana tren harga emas Indonesia selama 10 tahun terakhir?
2. Bagaimana distribusi harga emas dalam periode observasi?
3. Bagaimana pola perubahan harga emas harian (daily return)?
4. Bagaimana tren jangka pendek dan jangka panjang berdasarkan Moving Average?
5. Seberapa besar volatilitas harga emas dari waktu ke waktu?
6. Apakah terdapat outlier yang menunjukkan perubahan harga yang signifikan?
7. Bagaimana hubungan antara harga emas global, kurs USD/IDR, dan harga emas Indonesia?

## Setup Environment

### Menggunakan Anaconda

```bash
conda create --name gold-price-analysis python=3.10
conda activate gold-price-analysis
pip install -r requirements.txt
```

### Menggunakan Terminal / Shell

```bash
mkdir gold-price-analysis
cd gold-price-analysis
pip install -r requirements.txt
```

## Run Streamlit Dashboard

Masuk ke folder dashboard kemudian jalankan aplikasi Streamlit.

```bash
cd dashboard
streamlit run app.py
```

Setelah dijalankan, dashboard akan terbuka secara otomatis pada alamat:

```text
http://localhost:8501
```

## Dashboard Features

Dashboard ini menampilkan beberapa analisis utama:

### Executive Summary

Ringkasan performa harga emas Indonesia dalam bentuk KPI Cards yang menampilkan harga terbaru, harga tertinggi, harga terendah, dan jumlah observasi data.

### Gold Price Trend Analysis

Visualisasi tren harga emas Indonesia selama 10 tahun terakhir untuk mengidentifikasi pola pertumbuhan dan perubahan harga.

### Price Distribution Analysis

Analisis distribusi harga emas menggunakan histogram untuk memahami persebaran data dan rentang harga dominan.

### Daily Return Analysis

Analisis perubahan harga harian untuk mengukur fluktuasi dan kestabilan harga emas.

### Moving Average Analysis

Visualisasi Moving Average 7 hari dan 30 hari untuk mengidentifikasi tren jangka pendek dan jangka panjang.

### Volatility Analysis

Pengukuran volatilitas harga emas menggunakan rolling standard deviation untuk melihat tingkat risiko pergerakan harga.

### Outlier Detection

Analisis outlier menggunakan boxplot untuk mengidentifikasi anomali dan lonjakan harga yang signifikan.

### Correlation Analysis

Heatmap korelasi untuk memahami hubungan antara harga emas global, kurs USD/IDR, dan harga emas Indonesia.

### Feature Engineering

Menampilkan fitur-fitur hasil transformasi data yang digunakan untuk kebutuhan forecasting dan machine learning, seperti:

* Return_1D
* MA7
* MA30
* Volatility30

### Dataset Download

Fitur untuk mengunduh dataset hasil feature engineering dalam format CSV.

## Key Insights

* Harga emas Indonesia menunjukkan tren meningkat secara konsisten selama periode observasi.
* Kenaikan harga emas dipengaruhi oleh kombinasi harga emas global dan pergerakan nilai tukar USD/IDR.
* Periode volatilitas tertinggi terjadi ketika kondisi ekonomi global mengalami ketidakpastian.
* Outlier yang ditemukan merepresentasikan perubahan harga riil dan bukan kesalahan pencatatan data.
* Moving Average membantu mengidentifikasi perubahan tren harga secara lebih jelas.

## Dataset

Data diperoleh dari Yahoo Finance dengan sumber utama:

* Gold Futures (GC=F)
* USD/IDR Exchange Rate (IDR=X)

Harga emas Indonesia dihitung menggunakan konversi:

Harga Emas (IDR/gram) = Harga Emas Global (USD/OZ) × Kurs USD/IDR ÷ 31.1035

## Technologies Used

* Python
* Streamlit
* Plotly
* Pandas
* NumPy
* Yahoo Finance (yfinance)

## Author Data Scientist

**Nama:** Fairuz

**Email:** [fairuz@gmail.com](mailto:sifamutiasya@gmail.com)

**ID Dicoding:** CDCC222D6X0835

**Nama:** Sifa Mutiasya Hendayana Puteri

**Email:** [sifamutiasya@gmail.com](mailto:sifamutiasya@gmail.com)

**ID Dicoding:** CDCC222D6X0835

**Dashboard Streamlit:** https://goldenticsds.streamlit.app/

## Dashboard Preview

Gold Price Analytics Dashboard menyediakan visualisasi interaktif yang membantu pengguna memahami kondisi pasar emas Indonesia melalui pendekatan Business Intelligence dan Exploratory Data Analysis (EDA).

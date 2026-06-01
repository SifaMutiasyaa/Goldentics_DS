import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os

# Konfigurasi halaman
st.set_page_config(
    page_title="Gold Price Analytics Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main { background-color: #f8f9fc; }
    .css-1r6slb0, .css-1y4p8pa, [data-testid="stMetric"] {
        background-color: white;
        border-radius: 20px;
        padding: 1rem;
        border: 1px solid #e6d5a8;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        border-color: #d4af37;
        box-shadow: 0 8px 20px rgba(212,175,55,0.15);
    }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e6d5a8; }
    h1, h2, h3 { color: #b8860b; font-weight: 600; }
    body, .stMarkdown, .stText, .stSelectbox label { color: #1e2a3e; }
    .stButton button {
        background: linear-gradient(90deg, #d4af37, #b8860b);
        color: white;
        font-weight: bold;
        border-radius: 30px;
        border: none;
        padding: 0.5rem 1rem;
    }
    .stButton button:hover {
        background: linear-gradient(90deg, #e6c85c, #d4af37);
        color: #1e2a3e;
        transform: scale(1.02);
    }
    .streamlit-expanderHeader {
        background-color: #fef9e6;
        border-radius: 15px;
        font-weight: bold;
        color: #b8860b;
        border: 1px solid #f0e2b6;
    }
    .stSelectbox div[data-baseweb="select"] {
        background-color: white;
        border-radius: 12px;
        border: 1px solid #d4af37;
    }
    .info-box {
        background: #fef9e6;
        padding: 1rem;
        border-radius: 20px;
        border-left: 5px solid #d4af37;
        margin-bottom: 1rem;
        color: #1e2a3e;
    }
    .dataframe { font-size: 12px; border-radius: 12px; background: white; }
    [data-testid="stMetricLabel"] { color: #5a6e7c; }
    [data-testid="stMetricValue"] { color: #b8860b; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ======================= LOAD DATA DENGAN FALLBACK CACHE =======================
DATA_CACHE_FILE = "gold_data_cache.csv"

@st.cache_data(ttl=86400)
def load_data():
    # Coba download dari Yahoo Finance
    try:
        with st.spinner("Mengunduh data dari Yahoo Finance..."):
            gold = yf.download("GC=F", period="10y", interval="1d", auto_adjust=True, progress=False)
            usd = yf.download("IDR=X", period="10y", interval="1d", auto_adjust=True, progress=False)
            if gold.empty or usd.empty:
                raise ValueError("Data kosong dari Yahoo Finance")
            df = pd.DataFrame()
            df["Gold_USD_OZ"] = gold["Close"]
            df["USDIDR"] = usd["Close"]
            df = df.dropna()
            df["Close"] = (df["Gold_USD_OZ"] * df["USDIDR"]) / 31.1035
            df.reset_index(inplace=True)
            df.rename(columns={"index": "Date"}, inplace=True)
            df["Return_1D"] = df["Close"].pct_change()
            df["MA7"] = df["Close"].rolling(7).mean()
            df["MA30"] = df["Close"].rolling(30).mean()
            df["Volatility30"] = df["Return_1D"].rolling(30).std()
            df["Upper_BB"] = df["MA30"] + 2 * df["Close"].rolling(30).std()
            df["Lower_BB"] = df["MA30"] - 2 * df["Close"].rolling(30).std()
            df["Year"] = df["Date"].dt.year
            df["Month"] = df["Date"].dt.month
            # Simpan cache
            df.to_csv(DATA_CACHE_FILE, index=False)
            return df
    except Exception as e:
        st.warning(f"Gagal mengunduh data dari Yahoo Finance: {e}")
        # Coba baca dari file cache
        if os.path.exists(DATA_CACHE_FILE):
            try:
                df = pd.read_csv(DATA_CACHE_FILE)
                df["Date"] = pd.to_datetime(df["Date"])
                st.info("✅ Menggunakan data cache terakhir.")
                return df
            except Exception as ex:
                st.error(f"Gagal membaca cache: {ex}")
        else:
            st.error("❌ Tidak ada data cache. Silakan coba lagi nanti atau upload file CSV.")
        return pd.DataFrame()

df_raw = load_data()

# ======================= VALIDASI DATA =======================
if df_raw.empty:
    st.stop()

# ======================= SIDEBAR FILTER =======================
st.sidebar.title("🔍 Filter Data")
min_date_ts = df_raw["Date"].min()
max_date_ts = df_raw["Date"].max()
if pd.notna(min_date_ts) and pd.notna(max_date_ts):
    min_date = min_date_ts.date()
    max_date = max_date_ts.date()
else:
    min_date = datetime.today().date() - timedelta(days=365)
    max_date = datetime.today().date()
date_range = st.sidebar.date_input("📅 Rentang Waktu", value=(min_date, max_date), min_value=min_date, max_value=max_date)
if len(date_range) == 2:
    start_date, end_date = date_range
    df = df_raw[(df_raw["Date"].dt.date >= start_date) & (df_raw["Date"].dt.date <= end_date)]
else:
    df = df_raw
if df.empty:
    st.warning("⚠️ Tidak ada data untuk rentang tanggal yang dipilih. Silakan pilih rentang lain.")
    st.stop()

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Parameter")
show_ma = st.sidebar.checkbox("Tampilkan Moving Average", value=True)
show_bb = st.sidebar.checkbox("Tampilkan Bollinger Bands", value=False)
volatility_window = st.sidebar.slider("Window Volatilitas (hari)", 5, 60, 30)
df["Volatility30"] = df["Return_1D"].rolling(volatility_window).std()
df["Upper_BB"] = df["MA30"] + 2 * df["Close"].rolling(volatility_window).std()
df["Lower_BB"] = df["MA30"] - 2 * df["Close"].rolling(volatility_window).std()

menu = st.sidebar.selectbox(
    "📊 Navigasi Dashboard",
    [
        "🏠 Executive Summary",
        "📈 Tren Harga Emas",
        "📊 Distribusi Harga",
        "📉 Daily Return & Volatilitas",
        "📐 Moving Average & Bollinger Bands",
        "🔍 Outlier Analysis",
        "🔗 Correlation Analysis",
        "🧠 Feature Engineering"
    ]
)

# ======================= HELPER FUNCTIONS =======================
def make_light_fig(fig, title=""):
    fig.update_layout(
        template="plotly_white",
        title=dict(text=title, font=dict(size=20, color="#b8860b"), x=0.5),
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(showgrid=True, gridcolor="#e6e6e6", title_font=dict(color="#1e2a3e")),
        yaxis=dict(showgrid=True, gridcolor="#e6e6e6", title_font=dict(color="#1e2a3e")),
        legend=dict(bgcolor="rgba(255,255,255,0.8)", bordercolor="#d4af37", borderwidth=1),
        hovermode="x unified"
    )
    return fig

# ======================= PAGE CONTENT =======================
if menu == "🏠 Executive Summary":
    st.title("✨ Gold Price Analytics Dashboard")
    st.markdown("""
    <div class="info-box">
    Dashboard interaktif untuk menganalisis pergerakan harga emas di Indonesia selama 10 tahun terakhir.
    Dilengkapi filter tanggal, moving average, Bollinger Bands, dan metrik risiko.
    </div>
    """, unsafe_allow_html=True)
    
    last_price = df["Close"].iloc[-1]
    max_price = df["Close"].max()
    min_price = df["Close"].min()
    avg_vol = df["Volatility30"].mean()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🏅 Harga Emas / gram", f"Rp {last_price:,.0f}", delta=f"{((last_price/df['Close'].iloc[-2])-1)*100:.2f}%")
    col2.metric("🔺 Tertinggi", f"Rp {max_price:,.0f}")
    col3.metric("🔻 Terendah", f"Rp {min_price:,.0f}")
    col4.metric("🌊 Volatilitas Rata-rata", f"{avg_vol*100:.2f}%")
    
    fig = px.line(df, x="Date", y="Close", template="plotly_white",
                  title="<b>Perkembangan Harga Emas Indonesia (Rp/gram)</b>",
                  color_discrete_sequence=["#d4af37"])
    fig.update_traces(line=dict(width=2.5))
    fig = make_light_fig(fig, "")
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("📋 Statistik Deskriptif Harga Emas (Rp/gram)"):
        st.dataframe(df["Close"].describe().to_frame().T.style.format("{:,.0f}"), use_container_width=True)

elif menu == "📈 Tren Harga Emas":
    st.header("Tren Harga Emas : Perubahan 5x Lipat dalam 10 Tahun")
    with st.expander("💡 Insight Bisnis"):
        st.markdown("""
        - Harga emas dalam Rupiah mengalami **kenaikan hampir 5 kali lipat** dalam satu dekade.
        - Terjadi **percepatan kenaikan** yang signifikan pada periode 2024–2026.
        - Tren menunjukkan kecenderungan bullish jangka panjang.
        """)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Date"], y=df["Close"], mode="lines", name="Harga Emas", line=dict(color="#d4af37", width=2.5)))
    fig.add_vrect(x0=pd.Timestamp("2024-01-01"), x1=df["Date"].max(), fillcolor="rgba(212,175,55,0.1)", line_width=0, annotation_text="Percepatan Kenaikan")
    fig = make_light_fig(fig, "")
    fig.update_xaxes(title_text="Tanggal")
    fig.update_yaxes(title_text="Harga (Rp/gram)")
    st.plotly_chart(fig, use_container_width=True)
    
    df["Growth"] = (df["Close"] / df["Close"].iloc[0]) * 100
    fig2 = px.area(df, x="Date", y="Growth", template="plotly_white",
                   title="<b>Indeks Pertumbuhan Harga Emas (basis = awal data)</b>",
                   color_discrete_sequence=["#d4af37"])
    fig2.update_traces(fill="tozeroy", opacity=0.3, line=dict(color="#d4af37"))
    fig2 = make_light_fig(fig2, "")
    st.plotly_chart(fig2, use_container_width=True)

elif menu == "📊 Distribusi Harga":
    st.header("Distribusi Frekuensi Harga Emas")
    with st.expander("💡 Insight Bisnis"):
        st.markdown("""
        - Sebagian besar harga emas terkonsentrasi pada rentang **Rp 500.000 – Rp 900.000 per gram**.
        - Distribusi condong ke kanan (right-skewed) karena tren kenaikan jangka panjang.
        """)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        fig = px.histogram(df, x="Close", nbins=40, template="plotly_white",
                           marginal="box", color_discrete_sequence=["#d4af37"],
                           title="Histogram Harga Emas per Gram")
        fig.update_layout(bargap=0.05)
        fig = make_light_fig(fig, "")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.metric("Median Harga", f"Rp {df['Close'].median():,.0f}")
        st.metric("Std Dev", f"Rp {df['Close'].std():,.0f}")
        st.metric("Kemiringan (Skewness)", f"{df['Close'].skew():.2f}")

elif menu == "📉 Daily Return & Volatilitas":
    st.header("Return Harian dan Volatilitas Bergulir")
    with st.expander("💡 Insight Risiko"):
        st.markdown("""
        - Return harian umumnya stabil dengan lonjakan ekstrem saat gejolak ekonomi.
        - Volatilitas bergulir menunjukkan periode ketidakpastian tinggi (misalnya 2020, 2024).
        """)
    
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                        subplot_titles=("Daily Return (%)", "Rolling Volatility (30 hari)"))
    fig.add_trace(go.Scatter(x=df["Date"], y=df["Return_1D"]*100, mode="lines", name="Return", line=dict(color="#2c7fb8")), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["Date"], y=df["Volatility30"]*100, mode="lines", name="Volatilitas", line=dict(color="#d4af37", width=2)), row=2, col=1)
    fig.update_yaxes(title_text="%", row=1, col=1)
    fig.update_yaxes(title_text="%", row=2, col=1)
    fig.update_layout(template="plotly_white", hovermode="x unified", height=600)
    fig = make_light_fig(fig, "")
    st.plotly_chart(fig, use_container_width=True)

elif menu == "📐 Moving Average & Bollinger Bands":
    st.header("Indikator Teknikal : MA & Bollinger Bands")
    with st.expander("💡 Insight Trading"):
        st.markdown("""
        - **MA7 (hijau)** : tren jangka pendek. **MA30 (merah)** : tren menengah.
        - **Bollinger Bands** : harga menyentuh band atas → overbought; band bawah → oversold.
        """)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Date"], y=df["Close"], name="Harga Aktual", line=dict(color="black", width=1.5)))
    if show_ma:
        fig.add_trace(go.Scatter(x=df["Date"], y=df["MA7"], name="MA7", line=dict(color="#2ecc71", width=2)))
        fig.add_trace(go.Scatter(x=df["Date"], y=df["MA30"], name="MA30", line=dict(color="#e74c3c", width=2)))
    if show_bb:
        fig.add_trace(go.Scatter(x=df["Date"], y=df["Upper_BB"], name="Upper Band", line=dict(color="gray", dash="dash")))
        fig.add_trace(go.Scatter(x=df["Date"], y=df["Lower_BB"], name="Lower Band", line=dict(color="gray", dash="dash")))
        fig.add_trace(go.Scatter(x=df["Date"], y=df["MA30"], name="Middle Band", line=dict(color="purple", width=1)))
    fig = make_light_fig(fig, "")
    st.plotly_chart(fig, use_container_width=True)

elif menu == "🔍 Outlier Analysis":
    st.header("Identifikasi Outlier pada Harga Emas")
    with st.expander("💡 Insight Outlier"):
        st.markdown("""
        - Outlier adalah **lonjakan harga riil** akibat krisis atau kebijakan moneter.
        - Metode IQR menunjukkan titik di luar 1.5×IQR.
        """)
    
    fig = px.box(df, y="Close", points="all", template="plotly_white",
                 title="Boxplot Harga Emas dengan Outlier", color_discrete_sequence=["#d4af37"])
    fig.update_traces(boxmean="sd")
    fig = make_light_fig(fig, "")
    st.plotly_chart(fig, use_container_width=True)
    
    Q1 = df["Close"].quantile(0.25)
    Q3 = df["Close"].quantile(0.75)
    IQR = Q3 - Q1
    outliers = df[(df["Close"] < Q1 - 1.5*IQR) | (df["Close"] > Q3 + 1.5*IQR)]
    st.info(f"📌 Terdapat **{len(outliers)}** outlier berdasarkan metode IQR.")
    if len(outliers) > 0:
        st.dataframe(outliers[["Date", "Close"]].sort_values("Close", ascending=False).style.format({"Close": "Rp {:,.0f}"}), use_container_width=True)

elif menu == "🔗 Correlation Analysis":
    st.header("Korelasi : Emas Dunia, Kurs, dan Harga Lokal")
    with st.expander("💡 Insight Korelasi"):
        st.markdown("""
        - Harga emas lokal (Rp/gram) memiliki korelasi **sangat tinggi (0.99)** dengan harga emas global.
        - Kurs USD/IDR juga berkontribusi positif (~0.79).
        """)
    
    corr = df[["Gold_USD_OZ", "USDIDR", "Close"]].corr()
    fig = px.imshow(corr, text_auto=True, color_continuous_scale="Bluered_r",
                    title="Heatmap Korelasi", zmin=-1, zmax=1)
    fig.update_layout(template="plotly_white")
    fig = make_light_fig(fig, "")
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Scatter Plot Matrix")
    fig2 = px.scatter_matrix(df[["Gold_USD_OZ", "USDIDR", "Close"]], dimensions=["Gold_USD_OZ", "USDIDR", "Close"],
                             color_discrete_sequence=["#d4af37"], template="plotly_white")
    fig2.update_traces(diagonal_visible=False)
    st.plotly_chart(fig2, use_container_width=True)

elif menu == "🧠 Feature Engineering":
    st.header("⚙️ Dataset Siap Forecasting")
    with st.expander("📝 Keterangan Fitur"):
        st.markdown("""
        - **Return_1D** : perubahan persen harga harian.
        - **MA7 / MA30** : moving average 7 & 30 hari.
        - **Volatility30** : standar deviasi return 30 hari.
        - **Upper_BB / Lower_BB** : Bollinger Bands.
        - **Year, Month** : fitur temporal.
        """)
    
    st.dataframe(df.tail(100).style.format({
        "Close": "Rp {:,.0f}",
        "Gold_USD_OZ": "{:.2f}",
        "USDIDR": "{:.0f}",
        "Return_1D": "{:.4%}",
        "Volatility30": "{:.4%}"
    }), use_container_width=True)
    
    csv = df.to_csv(index=False)
    st.download_button("📥 Download Dataset (CSV)", csv, "gold_feature_engineering.csv", "text/csv")
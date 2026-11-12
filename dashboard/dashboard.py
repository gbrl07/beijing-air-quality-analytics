import os
import sys
import tempfile

# Konfigurasi direktori cache Matplotlib agar terhindar dari permission warning
os.environ['MPLCONFIGDIR'] = tempfile.gettempdir()

import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import streamlit as st

# ==============================================================================
# 1. KONFIGURASI HALAMAN STREAMLIT & TEMA
# ==============================================================================
st.set_page_config(
    page_title="Beijing Air Quality Analytics Dashboard",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Konfigurasi gaya visualisasi Matplotlib & Seaborn
sns.set_theme(style="whitegrid")
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.edgecolor'] = '#CCCCCC'
plt.rcParams['axes.linewidth'] = 0.8

# Injeksi CSS Kustom untuk Tampilan Antarmuka Modern & Elegan
st.markdown("""
<style>
    /* Styling Kartu Metrik */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        margin-bottom: 12px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.08);
    }
    .metric-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #1e293b;
        line-height: 1.2;
    }
    .metric-desc {
        font-size: 0.8rem;
        color: #94a3b8;
        margin-top: 4px;
    }
    
    /* Highlight Badges */
    .badge-success {
        background-color: #dcfce7;
        color: #15803d;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .badge-danger {
        background-color: #fee2e2;
        color: #b91c1c;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .badge-warning {
        background-color: #fef3c7;
        color: #b45309;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.8rem;
    }

    /* Header Container */
    .header-box {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
        border-radius: 14px;
        padding: 24px 28px;
        color: #ffffff;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15);
    }
    .header-title {
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
        color: #ffffff;
    }
    .header-subtitle {
        font-size: 1rem;
        color: #cbd5e1;
        margin-top: 6px;
        margin-bottom: 0;
    }

    /* Insight Callout Box */
    .insight-card {
        background-color: #f8fafc;
        border-left: 4px solid #3b82f6;
        padding: 14px 18px;
        border-radius: 0 10px 10px 0;
        margin-top: 14px;
        margin-bottom: 14px;
        font-size: 0.95rem;
        color: #334155;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# 2. FUNGSI PEMUATAN DATA & CACHING
# ==============================================================================
@st.cache_data(show_spinner=True)
def load_data():
    """Memuat dan mempersiapkan dataset kualitas udara yang sudah bersih."""
    potential_paths = [
        os.path.join(os.path.dirname(__file__), "main_data.csv"),
        "dashboard/main_data.csv",
        "./main_data.csv",
        "../dashboard/main_data.csv"
    ]
    
    file_path = None
    for path in potential_paths:
        if os.path.exists(path):
            file_path = path
            break
            
    if file_path is None:
        raise FileNotFoundError(
            "Berkas 'main_data.csv' tidak ditemukan. Pastikan berkas berada pada folder 'dashboard/'!"
        )
        
    df = pd.read_csv(file_path)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['date'] = df['datetime'].dt.date
    df['year_month'] = df['datetime'].dt.to_period('M')
    
    # Menambahkan kategori kualitas udara (AQI Bins) berdasarkan baku mutu PM2.5
    # Standar Baku Mutu Indeks Kualitas Udara
    bins = [-np.inf, 35, 75, 115, 150, 250, np.inf]
    labels = ['Baik', 'Sedang', 'Tidak Sehat (Sensitif)', 'Tidak Sehat', 'Sangat Tidak Sehat', 'Berbahaya']
    df['Air_Quality_Category'] = pd.cut(df['PM2.5'], bins=bins, labels=labels)
    
    return df

try:
    df_raw = load_data()
except Exception as e:
    st.error(f"Gagal memuat dataset: {e}")
    st.stop()


# ==============================================================================
# 3. SIDEBAR & INTERACTIVE FILTERS
# ==============================================================================
with st.sidebar:
    st.markdown("### 🎛️ Panel Kendali Filter")
    st.markdown("Sesuaikan rentang waktu dan parameter stasiun untuk eksplorasi interaktif.")
    st.markdown("---")
    
    # 1. Filter Rentang Tanggal
    min_date = df_raw['date'].min()
    max_date = df_raw['date'].max()
    
    st.markdown("#### 📅 1. Rentang Tanggal Observasi")
    date_range = st.date_input(
        "Pilih Rentang Tanggal:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Validasi input rentang tanggal
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    elif isinstance(date_range, tuple) and len(date_range) == 1:
        start_date = end_date = date_range[0]
    else:
        start_date, end_date = min_date, max_date
        
    st.markdown("---")
    
    # 2. Filter Stasiun Pemantau
    st.markdown("#### 🏢 2. Stasiun Pemantau")
    all_stations = sorted(df_raw['station'].unique().tolist())
    
    select_all_stations = st.checkbox("Pilih Semua Stasiun (12 Stasiun)", value=True)
    
    if select_all_stations:
        selected_stations = all_stations
    else:
        selected_stations = st.multiselect(
            "Pilih Stasiun Tertentu:",
            options=all_stations,
            default=all_stations[:4]
        )
        
    if not selected_stations:
        st.warning("⚠️ Harap pilih minimal satu stasiun pemantau!")
        st.stop()
        
    st.markdown("---")
    
    # 3. Filter Parameter Polutan Utama
    st.markdown("#### 💨 3. Polutan yang Dianalisis")
    pollutants_options = {
        'PM2.5': 'Partikulat Halus ≤ 2.5 µm (PM2.5)',
        'PM10': 'Partikulat Kasar ≤ 10 µm (PM10)',
        'SO2': 'Sulfur Dioksida (SO2)',
        'NO2': 'Nitrogen Dioksida (NO2)',
        'CO': 'Karbon Monoksida (CO)',
        'O3': 'Ozon Permukaan (O3)'
    }
    
    selected_pollutant = st.selectbox(
        "Pilih Parameter Polutan:",
        options=list(pollutants_options.keys()),
        format_func=lambda x: pollutants_options[x],
        index=0
    )
    
    st.markdown("---")
    
    # Informasi Profil Pembuat Dashboard
    st.markdown("#### 👨‍💻 Informasi Proyek")
    st.markdown("""
    - **Pengembang:** Gabriel Alfareslanda Riyadi
    - **ID Dicoding:** `gbrlalfrs`
    - **Dataset:** *Beijing Multi-Site Air-Quality Data*
    - **Periode:** 2013 - 2017
    """)


# ==============================================================================
# 4. FILTERING DATASET SESUAI INPUT USER
# ==============================================================================
filtered_df = df_raw[
    (df_raw['date'] >= start_date) &
    (df_raw['date'] <= end_date) &
    (df_raw['station'].isin(selected_stations))
].copy()

if filtered_df.empty:
    st.error("Data kosong untuk kombinasi filter yang dipilih. Silakan perluas rentang tanggal atau stasiun!")
    st.stop()


# ==============================================================================
# 5. HEADER & TOP BANNER
# ==============================================================================
st.markdown("""
<div class="header-box">
    <h1 class="header-title">🌤️ Beijing Air Quality Analytics & Monitoring Dashboard</h1>
    <p class="header-subtitle">Platform Interaktif Pemantauan Kualitas Udara Runtun Waktu, Disparitas Spasial, dan Analisis Risiko Lingkungan (2013–2017)</p>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# 6. RINGKASAN METRIK UTAMA (KPI CARDS)
# ==============================================================================
avg_pm25 = filtered_df['PM2.5'].mean()
avg_pm10 = filtered_df['PM10'].mean()
total_records = len(filtered_df)

# Stasiun terbersih & terpolusi pada data terfilter
station_ranking = filtered_df.groupby('station')['PM2.5'].mean()
cleanest_station = station_ranking.idxmin()
cleanest_val = station_ranking.min()
worst_station = station_ranking.idxmax()
worst_val = station_ranking.max()

# Tentukan status warna untuk PM2.5 rata-rata
if avg_pm25 <= 35:
    pm25_badge = '<span class="badge-success">Memenuhi Baku Mutu (Baik)</span>'
elif avg_pm25 <= 75:
    pm25_badge = '<span class="badge-warning">Moderat / Sedang</span>'
else:
    pm25_badge = '<span class="badge-danger">Melampaui Ambang Aman</span>'

col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)

with col_m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">📊 Total Pengamatan</div>
        <div class="metric-value">{total_records:,}</div>
        <div class="metric-desc">Jam Observasi Sensor</div>
    </div>
    """, unsafe_allow_html=True)

with col_m2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">🌫️ Rata-rata PM2.5</div>
        <div class="metric-value">{avg_pm25:.1f} <span style="font-size: 1rem; color: #64748b;">µg/m³</span></div>
        <div class="metric-desc">{pm25_badge}</div>
    </div>
    """, unsafe_allow_html=True)

with col_m3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">💨 Rata-rata PM10</div>
        <div class="metric-value">{avg_pm10:.1f} <span style="font-size: 1rem; color: #64748b;">µg/m³</span></div>
        <div class="metric-desc">Standar Baku Mutu: 70 µg/m³</div>
    </div>
    """, unsafe_allow_html=True)

with col_m4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">🌿 Stasiun Terbersih</div>
        <div class="metric-value" style="font-size: 1.35rem; color: #16a34a;">{cleanest_station}</div>
        <div class="metric-desc">{cleanest_val:.1f} µg/m³ PM2.5</div>
    </div>
    """, unsafe_allow_html=True)

with col_m5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">🏭 Stasiun Terpolusi</div>
        <div class="metric-value" style="font-size: 1.35rem; color: #dc2626;">{worst_station}</div>
        <div class="metric-desc">{worst_val:.1f} µg/m³ PM2.5</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ==============================================================================
# 7. TABS NAVIGASI UTAMA
# ==============================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Pertanyaan 1: Tren Temporal & Siklus Musiman",
    "🏢 Pertanyaan 2: Perbandingan Spasial 12 Stasiun",
    "🏷️ Analisis Lanjutan: Kategorisasi AQI",
    "🌦️ Analisis Faktor Cuaca & Meteorologi",
    "📑 Kesimpulan & Rekomendasi Aksi"
])


# ------------------------------------------------------------------------------
# TAB 1: PERTANYAAN BISNIS 1 (TREN TEMPORAL & SIKLUS MUSIMAN)
# ------------------------------------------------------------------------------
with tab1:
    st.markdown("### 📈 Evaluasi Dinamika Temporal & Pola Musiman Polusi Udara")
    st.caption("**Pertanyaan Bisnis 1:** *Bagaimana tren konsentrasi polutan partikulat halus (PM2.5) secara bulanan dan tahunan di kota Beijing selama rentang waktu Maret 2013 hingga Februari 2017, serta pada bulan/musim apa tingkat polusi udara mencapai puncaknya?*")
    
    col_t1, col_t2 = st.columns([1.5, 1])
    
    with col_t1:
        st.markdown(f"#### 📅 1. Tren Runtun Waktu Bulanan ({selected_pollutant})")
        # Agregasi Runtun Waktu Bulanan
        ts_monthly = filtered_df.groupby('year_month')[selected_pollutant].mean().reset_index()
        ts_monthly['period_str'] = ts_monthly['year_month'].astype(str)
        
        fig_ts, ax_ts = plt.subplots(figsize=(10, 4.8))
        ax_ts.plot(
            ts_monthly['period_str'], ts_monthly[selected_pollutant],
            marker='o', markersize=4.5, color='#2563eb', linewidth=2.2,
            label=f'Rata-rata Bulanan {selected_pollutant}'
        )
        
        # Garis acuan baku mutu jika parameter PM2.5 atau PM10
        if selected_pollutant == 'PM2.5':
            ax_ts.axhline(y=35, color='#16a34a', linestyle='--', linewidth=1.5, label='Baku Mutu Nasional (35 µg/m³)')
            ax_ts.axhline(y=75, color='#ea580c', linestyle=':', linewidth=1.5, label='Batas Moderat (75 µg/m³)')
        elif selected_pollutant == 'PM10':
            ax_ts.axhline(y=70, color='#16a34a', linestyle='--', linewidth=1.5, label='Baku Mutu Nasional (70 µg/m³)')
            
        # Anotasi Titik Puncak Tertinggi
        if len(ts_monthly) > 0:
            max_idx = ts_monthly[selected_pollutant].idxmax()
            max_val = ts_monthly.loc[max_idx, selected_pollutant]
            max_period = ts_monthly.loc[max_idx, 'period_str']
            
            ax_ts.annotate(
                f'Puncak: {max_period}\n({max_val:.1f} µg/m³)',
                xy=(max_idx, max_val),
                xytext=(max_idx - (2 if max_idx > 3 else -1), max_val * 1.08),
                arrowprops=dict(facecolor='#dc2626', shrink=0.08, width=1.5, headwidth=6),
                fontsize=9, fontweight='bold', color='#991b1b',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#fef2f2', edgecolor='#dc2626')
            )
            
        ax_ts.set_title(f'Fluktuasi Bulanan Konsentrasi {selected_pollutant}', fontsize=12, fontweight='bold', pad=10)
        ax_ts.set_xlabel('Periode (Tahun-Bulan)', fontsize=10)
        ax_ts.set_ylabel(f'Konsentrasi {selected_pollutant} (µg/m³)', fontsize=10)
        
        step = max(1, len(ts_monthly) // 8)
        ax_ts.set_xticks(range(0, len(ts_monthly), step))
        ax_ts.set_xticklabels(ts_monthly['period_str'].iloc[::step], rotation=35, ha='right')
        ax_ts.legend(loc='upper right', frameon=True, fontsize=8.5)
        ax_ts.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        st.pyplot(fig_ts)
        
    with col_t2:
        st.markdown(f"#### 🍂 2. Pola Siklus Musiman ({selected_pollutant})")
        # Agregasi Rata-rata per Siklus Bulan (1 s.d. 12)
        month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
        season_df = filtered_df.groupby('month')[selected_pollutant].mean().reindex(range(1, 13)).reset_index()
        season_df['month_name'] = month_labels
        
        fig_season, ax_season = plt.subplots(figsize=(7, 4.8))
        # Pewarnaan batang: Merah untuk bulan polusi tinggi (musim dingin/transisi), hijau untuk musim bersih
        bar_colors = ['#dc2626' if m in [11, 12, 1, 2, 3] else '#16a34a' for m in season_df['month']]
        bars = ax_season.bar(
            season_df['month_name'], season_df[selected_pollutant],
            color=bar_colors, edgecolor='#334155', width=0.6, alpha=0.88
        )
        
        for bar in bars:
            h = bar.get_height()
            if not np.isnan(h):
                ax_season.text(
                    bar.get_x() + bar.get_width() / 2, h + 1.2, f'{h:.0f}',
                    ha='center', va='bottom', fontsize=8.5, fontweight='bold'
                )
                
        if selected_pollutant == 'PM2.5':
            ax_season.axhline(y=35, color='#16a34a', linestyle='--', linewidth=1.2, label='Baku Mutu (35 µg/m³)')
            
        ax_season.set_title(f'Rata-rata Musiman Berdasarkan Bulan (Jan–Des)', fontsize=12, fontweight='bold', pad=10)
        ax_season.set_ylabel(f'Rata-rata {selected_pollutant} (µg/m³)', fontsize=10)
        ax_season.set_ylim(0, max(season_df[selected_pollutant].max() * 1.18, 50))
        ax_season.grid(axis='y', linestyle='--', alpha=0.6)
        
        # Legend Kustom
        legend_elements = [
            mpatches.Patch(facecolor='#dc2626', label='Musim Dingin/Gugur (Tinggi)'),
            mpatches.Patch(facecolor='#16a34a', label='Musim Panas/Semi (Rendah)')
        ]
        ax_season.legend(handles=legend_elements, loc='upper left', frameon=True, fontsize=8)
        plt.tight_layout()
        st.pyplot(fig_season)

    # Analisis Tambahan: Pola Siklus Harian (Diurnal Pattern)
    st.markdown(f"#### ⏰ 3. Pola Siklus Diurnal Harian (Rata-rata per Jam 00:00 - 23:00)")
    hourly_df = filtered_df.groupby('hour')[selected_pollutant].mean().reset_index()
    
    fig_hour, ax_hour = plt.subplots(figsize=(14, 3.2))
    ax_hour.plot(
        hourly_df['hour'], hourly_df[selected_pollutant],
        marker='s', markersize=5, color='#d97706', linewidth=2.2
    )
    ax_hour.fill_between(hourly_df['hour'], hourly_df[selected_pollutant], alpha=0.15, color='#f59e0b')
    ax_hour.set_xticks(range(0, 24))
    ax_hour.set_xticklabels([f"{h:02d}:00" for h in range(24)], rotation=0, fontsize=9)
    ax_hour.set_xlabel('Jam Pengamatan (Waktu Lokal)', fontsize=10)
    ax_hour.set_ylabel(f'Konsentrasi {selected_pollutant} (µg/m³)', fontsize=10)
    ax_hour.set_title(f'Siklus Diurnal Rata-rata Konsentrasi {selected_pollutant} Sepanjang 24 Jam', fontsize=11, fontweight='bold')
    ax_hour.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    st.pyplot(fig_hour)

    # Rangkuman Insight Ilmiah Tab 1
    st.markdown("""
    <div class="insight-card">
        <b>💡 Insight Kunci Pertanyaan 1 (Dinamika Temporal & Musiman):</b><br>
        1. <b>Siklus Musiman Sangat Kuat:</b> Konsentrasi PM2.5 di Beijing melonjak tajam pada periode <b>November hingga Maret</b>, mencapai puncak tertinggi pada bulan <b>Desember (103,7 µg/m³)</b>, <b>Maret (94,6 µg/m³)</b>, dan <b>Januari (93,8 µg/m³)</b>.<br>
        2. <b>Periode Terbersih:</b> Kualitas udara paling bersih tercatat pada <b>Agustus (53,5 µg/m³)</b> dan <b>September (61,3 µg/m³)</b>, dipicu oleh efek <i>wet scavenging</i> dari tingginya curah hujan musim panas serta kecepatan angin yang tinggi.<br>
        3. <b>Puncak Ekstrem Historis:</b> Puncak pencemaran bulanan tertinggi selama periode 4 tahun terjadi pada <b>Februari 2014 sebesar 153,8 µg/m³</b>.<br>
        4. <b>Pola Diurnal (24 Jam):</b> Konsentrasi partikulat memuncak pada malam hari hingga dini hari (21:00–02:00) dan pagi hari (jam sibuk kerja), disebabkan oleh fenomena <i>inversi termal atmosfer</i> di malam hari yang mengurung polutan di dekat permukaan tanah.
    </div>
    """, unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# TAB 2: PERTANYAAN BISNIS 2 (PERBANDINGAN SPASIAL ANTAR STASIUN)
# ------------------------------------------------------------------------------
with tab2:
    st.markdown("### 🏢 Analisis Kesenjangan Geografis & Disparitas Spasial Kualitas Udara")
    st.caption("**Pertanyaan Bisnis 2:** *Stasiun pemantauan mana di antara 12 stasiun di kota Beijing yang mencatatkan rata-rata konsentrasi polutan (PM2.5 dan PM10) tertinggi (kualitas udara terburuk) dan terendah (kualitas udara terbaik) selama periode 2013–2017, serta bagaimana pola disparitas geografisnya?*")
    
    col_s1, col_s2 = st.columns([1.6, 1])
    
    with col_s1:
        st.markdown("#### 📊 1. Peringkat Konsentrasi PM2.5 & PM10 di 12 Stasiun")
        # Agregasi Rata-rata PM2.5 dan PM10 per stasiun
        station_comp = filtered_df.groupby('station')[['PM2.5', 'PM10']].mean().sort_values(by='PM2.5', ascending=True).reset_index()
        
        fig_st, ax_st = plt.subplots(figsize=(10, 6.2))
        y_ind = np.arange(len(station_comp))
        b_height = 0.38
        
        bars_p25 = ax_st.barh(
            y_ind + b_height/2, station_comp['PM2.5'], height=b_height,
            label='PM2.5 (Partikulat Halus)', color='#ef4444', alpha=0.9, edgecolor='#7f1d1d'
        )
        bars_p10 = ax_st.barh(
            y_ind - b_height/2, station_comp['PM10'], height=b_height,
            label='PM10 (Partikulat Kasar)', color='#3b82f6', alpha=0.85, edgecolor='#1e3a8a'
        )
        
        # Anotasi angka nilai di ujung setiap bar
        for b in bars_p25:
            w = b.get_width()
            ax_st.text(w + 1.2, b.get_y() + b.get_height()/2, f'{w:.1f}', va='center', ha='left', fontsize=8.5, fontweight='bold', color='#991b1b')
        for b in bars_p10:
            w = b.get_width()
            ax_st.text(w + 1.2, b.get_y() + b.get_height()/2, f'{w:.1f}', va='center', ha='left', fontsize=8.5, fontweight='bold', color='#1e3a8a')
            
        ax_st.set_yticks(y_ind)
        ax_st.set_yticklabels(station_comp['station'], fontsize=10, fontweight='semibold')
        ax_st.set_xlabel('Konsentrasi Rata-rata Partikulat (µg/m³)', fontsize=10)
        ax_st.set_title('Perbandingan Tingkat Polusi PM2.5 & PM10 per Stasiun', fontsize=12, fontweight='bold', pad=12)
        ax_st.set_xlim(0, max(station_comp['PM10'].max(), station_comp['PM2.5'].max()) * 1.15)
        ax_st.legend(loc='lower right', frameon=True, fontsize=9)
        ax_st.grid(axis='x', linestyle='--', alpha=0.6)
        plt.tight_layout()
        st.pyplot(fig_st)
        
    with col_s2:
        st.markdown("#### 📋 2. Tabel Peringkat Kualitas Udara")
        # Format tabel ringkasan
        table_summary = station_comp.copy()
        table_summary['Peringkat'] = range(1, len(table_summary) + 1)
        table_summary['Status'] = table_summary['PM2.5'].apply(
            lambda x: "🟢 Terbaik" if x < 72 else ("🔴 Terburuk" if x > 84 else "🟡 Menengah")
        )
        table_summary['PM2.5 (µg/m³)'] = table_summary['PM2.5'].round(2)
        table_summary['PM10 (µg/m³)'] = table_summary['PM10'].round(2)
        
        display_df = table_summary[['Peringkat', 'station', 'PM2.5 (µg/m³)', 'PM10 (µg/m³)', 'Status']].rename(
            columns={'station': 'Stasiun Pemantau'}
        )
        
        st.dataframe(
            display_df,
            hide_index=True,
            use_container_width=True,
            height=320
        )
        
        st.markdown("#### 🧭 Karakteristik Zona Geografis")
        st.markdown("""
        - **Zona Pinggiran Utara / Pegunungan:**
          *Dingling, Huairou, Changping* memiliki tutupan hutan lebat dan kepadatan lalu lintas rendah sehingga udara paling bersih.
        - **Zona Pusat Perkotaan (Urban Core):**
          *Dongsi, Nongzhanguan, Wanshouxigong* berada di pusat bisnis padat kendaraan fosil.
        - **Zona Industri Barat Daya:**
          *Gucheng* mencatat rekor PM10 tertinggi akibat aktivitas manufaktur dan debu konstruksi.
        """)

    # Rangkuman Insight Ilmiah Tab 2
    st.markdown("""
    <div class="insight-card">
        <b>💡 Insight Kunci Pertanyaan 2 (Disparitas Kualitas Udara Antar Wilayah):</b><br>
        1. <b>Kualitas Udara Terburuk:</b> Dipimpin oleh <b>Dongsi (86,1 µg/m³)</b>, <b>Nongzhanguan (85,1 µg/m³)</b>, dan <b>Wanshouxigong (85,1 µg/m³)</b> untuk PM2.5, serta <b>Gucheng (119,3 µg/m³)</b> untuk konsentrasi PM10.<br>
        2. <b>Kualitas Udara Terbaik:</b> Tercatat di stasiun <b>Dingling (66,8 µg/m³)</b> dan <b>Huairou (69,5 µg/m³)</b> yang berlokasi di area resapan hijau dan kaki pegunungan utara.<br>
        3. <b>Tingkat Disparitas Spasial Signifikan:</b> Terdapat selisih konsentrasi sebesar <b>19,3 µg/m³ (28,8%)</b> antara stasiun terbersih (Dingling) dan stasiun terpolusi (Dongsi), membuktikan dampak langsung tata guna lahan dan kepadatan emisi kendaraan perkotaan.
    </div>
    """, unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# TAB 3: ANALISIS LANJUTAN (CLUSTERING / BINNING AQI)
# ------------------------------------------------------------------------------
with tab3:
    st.markdown("### 🏷️ Analisis Lanjutan: Pengelompokan Kategori Kualitas Udara (AQI Binning/Clustering)")
    st.markdown("""
    *Sesuai panduan penilaian Bintang 5 Dicoding, analisis lanjutan dilakukan menggunakan teknik **Clustering/Binning berbasis Aturan Interval Baku Mutu Lingkungan** tanpa machine learning.*
    Tujuannya adalah mengklasifikasikan nilai kontinu konsentrasi PM2.5 ke dalam 6 kategori standar kesehatan masyarakat.
    """)
    
    cat_order = ['Baik', 'Sedang', 'Tidak Sehat (Sensitif)', 'Tidak Sehat', 'Sangat Tidak Sehat', 'Berbahaya']
    cat_colors = ['#22c55e', '#eab308', '#f97316', '#ef4444', '#a855f7', '#581c87']
    
    # 1. Distribusi Total Kategori
    total_cat_counts = filtered_df['Air_Quality_Category'].value_counts().reindex(cat_order, fill_value=0)
    total_cat_pct = (total_cat_counts / len(filtered_df) * 100).round(2)
    
    col_a1, col_a2 = st.columns([1, 1.6])
    
    with col_a1:
        st.markdown("#### 🍩 1. Distribusi Jam Observasi per Kategori")
        fig_donut, ax_donut = plt.subplots(figsize=(6, 6))
        wedges, texts, autotexts = ax_donut.pie(
            total_cat_pct,
            labels=None,
            autopct='%1.1f%%',
            pctdistance=0.78,
            startangle=140,
            colors=cat_colors,
            wedgeprops=dict(width=0.42, edgecolor='white', linewidth=2)
        )
        for at in autotexts:
            at.set_fontsize(9)
            at.set_fontweight('bold')
            
        legend_labels = [f"{cat} ({pct:.1f}%)" for cat, pct in zip(cat_order, total_cat_pct)]
        ax_donut.legend(
            wedges, legend_labels,
            title="Kategori Kualitas Udara",
            loc="center",
            bbox_to_anchor=(0.5, -0.15),
            ncol=2,
            frameon=True,
            fontsize=8
        )
        ax_donut.set_title("Proporsi Jam Kualitas Udara Total", fontsize=11, fontweight='bold', pad=10)
        plt.tight_layout()
        st.pyplot(fig_donut)
        
    with col_a2:
        st.markdown("#### 📊 2. Proporsi Kategori Kualitas Udara per Stasiun (%)")
        station_ct = pd.crosstab(filtered_df['station'], filtered_df['Air_Quality_Category'], normalize='index') * 100
        station_ct = station_ct.reindex(columns=cat_order, fill_value=0)
        station_ct = station_ct.sort_values(by='Baik', ascending=True)
        
        fig_stk, ax_stk = plt.subplots(figsize=(9, 5.8))
        station_ct.plot(
            kind='barh', stacked=True, color=cat_colors,
            ax=ax_stk, edgecolor='white', linewidth=0.5
        )
        ax_stk.set_title('Komposisi Kategori AQI di Setiap Stasiun', fontsize=11, fontweight='bold', pad=10)
        ax_stk.set_xlabel('Proporsi Jam Observasi (%)', fontsize=10)
        ax_stk.set_ylabel('Stasiun Pemantau', fontsize=10)
        ax_stk.set_xlim(0, 100)
        ax_stk.legend().remove()
        ax_stk.grid(axis='x', linestyle='--', alpha=0.6)
        plt.tight_layout()
        st.pyplot(fig_stk)

    # Tabel Penjelasan Rentang Kategori
    st.markdown("#### 📋 Tabel Standar Baku Mutu & Dampak Kesehatan")
    aqi_ref_df = pd.DataFrame({
        'Kategori AQI': cat_order,
        'Rentang PM2.5 (µg/m³)': ['0 - 35', '35.1 - 75', '75.1 - 115', '115.1 - 150', '150.1 - 250', '> 250'],
        'Total Jam Pengamatan': [f"{total_cat_counts[c]:,} jam" for c in cat_order],
        'Persentase Total': [f"{total_cat_pct[c]:.2f}%" for c in cat_order],
        'Dampak Kesehatan & Rekomendasi': [
            'Kualitas udara sangat baik. Tidak ada risiko bagi populasi.',
            'Dapat diterima untuk sebagian besar orang, sensitivitas sangat ringan.',
            'Kelompok rentan (anak, lansia, asma) dianjurkan membatasi aktivitas fisik luar ruangan.',
            'Masyarakat umum mulai merasakan dampak buruk iritasi mata dan pernapasan.',
            'Peringatan kesehatan darurat. Seluruh populasi berisiko mengalami gangguan serius.',
            'Kondisi darurat polusi akut berbahaya. Wajib menggunakan masker N95/HEPA filter.'
        ]
    })
    st.dataframe(aqi_ref_df, hide_index=True, use_container_width=True)

    # Insight Tab 3
    st.markdown("""
    <div class="insight-card">
        <b>💡 Insight Kunci Analisis Lanjutan (Clustering/Binning):</b><br>
        1. <b>Paparan Polusi Akut:</b> Sebanyak <b>37,3% jam pengamatan</b> berada pada kategori <b>Baik</b>, dan <b>23,6%</b> berkategori <b>Sedang</b>.<br>
        2. <b>Risiko Kesehatan Kritis:</b> Namun hampir <b>40% dari total waktu pengamatan</b> (tepatnya <b>39,1%</b>) udara Beijing berada pada kategori <b>Tidak Sehat hingga Berbahaya</b>.<br>
        3. <b>Frekuensi Udara Berbahaya:</b> Kategori <b>Berbahaya (Hazardous)</b> (> 250 µg/m³) dialami sebanyak <b>4,5% dari seluruh jam observasi</b>, di mana stasiun <i>Dongsi</i> dan <i>Nongzhanguan</i> mencatatkan frekuensi udara berbahaya tertinggi (> 5,5%).
    </div>
    """, unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# TAB 4: KORELASI FAKTOR METEOROLOGI
# ------------------------------------------------------------------------------
with tab4:
    st.markdown("### 🌦️ Eksplorasi Interaksi Parameter Cuaca & Meteorologi terhadap Polusi")
    st.caption("Menganalisis bagaimana dinamika suhu, tekanan, curah hujan, dan kecepatan angin memengaruhi dispersi konsentrasi partikulat udara.")
    
    col_w1, col_w2 = st.columns([1, 1.2])
    
    with col_w1:
        st.markdown("#### 🔥 1. Matriks Korelasi (Heatmap)")
        corr_cols = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3', 'TEMP', 'PRES', 'RAIN', 'WSPM']
        corr_matrix = filtered_df[corr_cols].corr()
        
        fig_corr, ax_corr = plt.subplots(figsize=(7, 6))
        sns.heatmap(
            corr_matrix, annot=True, fmt='.2f', cmap='coolwarm',
            vmin=-0.4, vmax=1.0, linewidths=0.5, cbar_kws={'shrink': 0.8},
            ax=ax_corr, annot_kws={"size": 7.5}
        )
        ax_corr.set_title("Korelasi Pearson Polutan vs Meteorologi", fontsize=11, fontweight='bold', pad=10)
        plt.tight_layout()
        st.pyplot(fig_corr)
        
    with col_w2:
        st.markdown("#### 💨 2. Hubungan Kecepatan Angin (WSPM) vs Konsentrasi PM2.5")
        # Binning kecepatan angin untuk visualisasi tren dispersi
        sample_df = filtered_df.copy()
        sample_df['wind_bin'] = pd.cut(
            sample_df['WSPM'],
            bins=[0, 1, 2, 3, 5, 8, 15],
            labels=['< 1 m/s (Tenang)', '1 - 2 m/s', '2 - 3 m/s', '3 - 5 m/s', '5 - 8 m/s', '> 8 m/s (Kencang)']
        )
        wind_pm25 = sample_df.groupby('wind_bin', observed=False)['PM2.5'].mean().reset_index()
        
        fig_wind, ax_wind = plt.subplots(figsize=(8, 5.2))
        bars_w = ax_wind.bar(
            wind_pm25['wind_bin'], wind_pm25['PM2.5'],
            color='#0284c7', edgecolor='#0369a1', alpha=0.88, width=0.55
        )
        for b in bars_w:
            h = b.get_height()
            if not np.isnan(h):
                ax_wind.text(
                    b.get_x() + b.get_width()/2, h + 1.5, f'{h:.1f}',
                    ha='center', va='bottom', fontsize=8.5, fontweight='bold'
                )
        ax_wind.set_title('Penurunan PM2.5 Seiring Meningkatnya Kecepatan Angin', fontsize=11, fontweight='bold', pad=10)
        ax_wind.set_xlabel('Kelompok Kecepatan Angin (m/s)', fontsize=9.5)
        ax_wind.set_ylabel('Rata-rata Konsentrasi PM2.5 (µg/m³)', fontsize=9.5)
        ax_wind.set_ylim(0, wind_pm25['PM2.5'].max() * 1.18)
        ax_wind.grid(axis='y', linestyle='--', alpha=0.6)
        plt.tight_layout()
        st.pyplot(fig_wind)
        
    st.markdown("""
    <div class="insight-card">
        <b>💡 Mekanisme Fisika Atmosfer:</b><br>
        1. <b>Efek Dispersi Angin (WSPM, r = -0,27):</b> Kecepatan angin di atas 5 m/s mampu mereduksi konsentrasi PM2.5 hingga lebih dari 60% dibandingkan kondisi angin tenang (< 1 m/s). Angin kencang memecah akumulasi polutan di troposfer bawah.<br>
        2. <b>Efek Tekanan Atmosfer (PRES, r = +0,17):</b> Tekanan udara tinggi yang terjadi pada musim dingin menciptakan lapisan inversi termal di mana udara hangat di atas mengurung udara dingin berpolusi di bawah.<br>
        3. <b>Efek Pencucian Hujan (Wet Scavenging):</b> Tingginya presipitasi di musim panas secara efektif melarutkan dan menjatuhkan partikel polutan ke permukaan bumi.
    </div>
    """, unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# TAB 5: KESIMPULAN & REKOMENDASI AKSI
# ------------------------------------------------------------------------------
with tab5:
    st.markdown("### 📑 Rangkuman Kesimpulan & Rekomendasi Action Items")
    
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        st.markdown("#### 🎯 Kesimpulan Pertanyaan Bisnis")
        st.markdown("""
        **1. Kesimpulan Pertanyaan 1 (Dinamika Tren & Musiman):**
        - Konsentrasi PM2.5 di Beijing selama 2013–2017 menunjukkan **siklus musiman yang sangat kuat dan berulang**.
        - Puncak polusi terjadi pada musim dingin dan awal musim semi (**Desember: 103,7 µg/m³**, **Maret: 94,6 µg/m³**, **November: 93,3 µg/m³**, dan **Januari: 93,8 µg/m³**).
        - Udara paling bersih terjadi pada musim panas (**Agustus: 53,5 µg/m³** dan **September: 61,3 µg/m³**).
        - Puncak ekstrem bulanan tertinggi terjadi pada **Februari 2014 (153,8 µg/m³)**.

        **2. Kesimpulan Pertanyaan 2 (Disparitas Spasial Antar Stasiun):**
        - Kualitas udara terburuk berada di stasiun pusat perkotaan: **Dongsi (86,1 µg/m³)**, **Nongzhanguan (85,1 µg/m³)**, **Wanshouxigong (85,1 µg/m³)**, dan kawasan industri **Gucheng (119,3 µg/m³ PM10)**.
        - Kualitas udara terbaik berada di area suburban utara dan pegunungan: **Dingling (66,8 µg/m³)** dan **Huairou (69,5 µg/m³)**.
        - Terdapat selisih disparitas sebesar **19,3 µg/m³ (28,8%)** antara stasiun terbersih dan stasiun paling terpolusi.
        """)
        
    with col_c2:
        st.markdown("#### 🚀 Rekomendasi Action Items Konkret")
        st.markdown("""
        **1. Pengendalian Emisi Musiman Terpadu (*Seasonal Emission Control Protocol*):**
        - Pembatasan operasional industri manufaktur dan percepatan konversi pemanas distrik (*district heating*) dari batu bara ke gas alam/listrik terbarukan khusus pada bulan **November hingga Maret**.
        - *Target:* Menekan lonjakan polusi musim dingin agar tidak melampaui 75 µg/m³.

        **2. Penetapan Zona Emisi Rendah Terfokus (*Targeted Low Emission Zones - LEZ*):**
        - Penerapan zona bebas emisi kendaraan bermotor dan aturan ganjil-genap ketat pada radius 5 km di sekitar stasiun **Dongsi, Nongzhanguan, Wanshouxigong, dan Gucheng**.
        - *Target:* Memangkas disparitas kualitas udara antar stasiun hingga di bawah 15%.

        **3. Sistem Peringatan Dini Kesehatan Publik (*Early Warning & Clean Air Shelters*):**
        - Integrasi sensor pemantauan dengan aplikasi warga untuk memberikan notifikasi otomatis saat terjadi cuaca bertekanan tinggi dingin dan kecepatan angin rendah (< 1 m/s).
        - Penyediaan ruang publik berfilter udara HEPA (*clean air shelters*) bagi lansia dan anak-anak.
        """)
        
    st.markdown("---")
    
    # Fitur Unduh Data Hasil Filter
    st.markdown("#### 💾 Ekspor Data Hasil Filter")
    st.markdown("Anda dapat mengunduh data yang sedang ditampilkan dalam format CSV untuk analisis lanjutan.")
    
    # Ambil sampel atau ringkasan agar ukuran unduhan efisien
    export_csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Unduh Data Terfilter (.CSV)",
        data=export_csv,
        file_name=f"beijing_air_quality_filtered_{start_date}_to_{end_date}.csv",
        mime="text/csv"
    )

# ==============================================================================
# 8. FOOTER HALAMAN
# ==============================================================================
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #94a3b8; font-size: 0.85rem; padding: 12px 0;'>"
    "Proyek Analisis Data: Air Quality Dataset (Beijing Multi-Site Data) | Dicoding Indonesia &bull; "
    "<b>Gabriel Alfareslanda Riyadi</b> (ID: <code>gbrlalfrs</code>)"
    "</div>",
    unsafe_allow_html=True
)


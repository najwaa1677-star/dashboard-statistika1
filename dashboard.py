import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman Dashboard
st.set_page_config(
    page_title="Dashboard Analisis Media Sosial & Belajar",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Judul Dashboard
st.title("📊 Dashboard Dampak Media Sosial Terhadap Fokus Belajar Mahasiswa")
st.markdown("Dashboard interaktif ini menyajikan visualisasi data dari hasil kuesioner responden.")

# 3. Fungsi untuk Memuat Data
@st.cache_data
def load_data():
    df = pd.read_excel("Data responden.xlsx")
    # Bersihkan spasi di nama kolom
    df.columns = df.columns.str.strip()
    if "Program Studi" in df.columns:
        df["Program Studi"] = df["Program Studi"].str.strip().str.title()
    return df

try:
    df = load_data()
    
    # 4. Membuat Sidebar Filter Kontrol Interaktif
    st.sidebar.header("🎛️ Filter Data")
    
    # Filter Berdasarkan Jenis Kelamin
    list_jk = ["Semua"] + list(df["Jenis Kelamin"].unique())
    selected_jk = st.sidebar.selectbox("Pilih Jenis Kelamin:", list_jk)
    
    # Filter Berdasarkan Program Studi
    list_prodi = ["Semua"] + list(df["Program Studi"].unique())
    selected_prodi = st.sidebar.selectbox("Pilih Program Studi:", list_prodi)
    
    # Menerapkan Filter ke Dataframe
    df_filtered = df.copy()
    if selected_jk != "Semua":
        df_filtered = df_filtered[df_filtered["Jenis Kelamin"] == selected_jk]
    if selected_prodi != "Semua":
        df_filtered = df_filtered[df_filtered["Program Studi"] == selected_prodi]
        
    # 5. Menampilkan Metrik Utama (KPI) di Bagian Atas
    col1, col2, col3 = st.columns(3)
    total = df_filtered.shape[0]
    with col1:
        st.metric("Total Responden (Terfilter)", f"{total} orang")
    with col2:
        if total > 0 and "Jenis Kelamin" in df_filtered.columns:
            p_count = df_filtered[df_filtered["Jenis Kelamin"] == "Perempuan"].shape[0]
            st.metric("Responden Perempuan", f"{(p_count/total)*100:.1f}%")
        else:
            st.metric("Responden Perempuan", "0%")
    with col3:
        # Otomatis cari kolom notifikasi berdasarkan kata kunci 'notifikasi'
        col_notif = [c for c in df_filtered.columns if 'notifikasi' in c.lower()]
        if total > 0 and col_notif:
            notif_ya = df_filtered[df_filtered[col_notif[0]] == "Ya"].shape[0]
            st.metric("Notifikasi Hack", f"{(notif_ya/total)*100:.1f}%")
        else:
            st.metric("Notifikasi Aktif", "0%")

    st.markdown("---")

    # JIKA DATA KOSONG KARENA FILTER
    if df_filtered.empty:
        st.warning("Data tidak tersedia untuk kombinasi filter ini. Silakan ubah filter Anda.")
    else:
        # OTOMATIS MENCARI KOLOM BERDASARKAN KATA KUNCI (Mencegah salah nama kolom)
        col_durasi = [c for c in df_filtered.columns if 'lama rata-rata' in c.lower() or 'durasi' in c.lower() or 'berapa lama' in c.lower()][0]
        col_fokus = [c for c in df_filtered.columns if 'fokus anda saat belajar' in c.lower() or 'seberapa fokus' in c.lower()][0]
        col_buka = [c for c in df_filtered.columns if 'membuka media sosial' in c.lower() or 'sering anda membuka' in c.lower()][0]
        col_pengaruh = [c for c in df_filtered.columns if 'pengaruh penggunaan' in c.lower() or 'dampak' in c.lower() or 'kebiasaan belajar' in c.lower() or 'pengaruh media' in c.lower()][0]

        # 6. Baris Grafik Bagian Pertama (Visualisasi Durasi & Fokus)
        st.subheader("📈 Analisis Durasi & Tingkat Fokus")
        left_chart, right_chart = st.columns(2)
        
        with left_chart:
            df_durasi = df_filtered[col_durasi].value_counts().reset_index()
            df_durasi.columns = ['Durasi', 'Jumlah']
            
            fig_durasi = px.bar(
                df_durasi, x='Durasi', y='Jumlah',
                title="Durasi Penggunaan Media Sosial Harian",
                labels={'Durasi': 'Kategori Waktu', 'Jumlah': 'Jumlah Mahasiswa'},
                color='Durasi', color_discrete_sequence=px.colors.qualitative.Set2
            )
            st.plotly_chart(fig_durasi, use_container_width=True)
            
        with right_chart:
            df_fokus = df_filtered[col_fokus].value_counts().reset_index()
            df_fokus.columns = ['Tingkat Fokus', 'Jumlah']
            
            # Mengurutkan kategori agar lebih rapi secara visual
            fokus_order = ["Tidak fokus", "Cukup fokus", "Fokus", "Sangat fokus"]
            df_fokus['Tingkat Fokus'] = pd.Categorical(df_fokus['Tingkat Fokus'], categories=fokus_order, ordered=True)
            df_fokus = df_fokus.sort_values('Tingkat Fokus')
            
            fig_fokus = px.bar(
                df_fokus, x='Tingkat Fokus', y='Jumlah',
                title="Tingkat Fokus Mahasiswa Saat Belajar",
                labels={'Tingkat Fokus': 'Kategori Fokus', 'Jumlah': 'Jumlah Mahasiswa'},
                color='Tingkat Fokus', 
                color_discrete_sequence=px.colors.sequential.Viridis
            )
            st.plotly_chart(fig_fokus, use_container_width=True)

        # 7. Baris Grafik Bagian Kedua (Distribusi Frekuensi & Pengaruh)
        st.subheader("🔍 Korelasi Perilaku Belajar & Media Sosial")
        bottom_left, bottom_right = st.columns(2)
        
        with bottom_left:
            df_buka = df_filtered[col_buka].value_counts().reset_index()
            df_buka.columns = ['Frekuensi', 'Jumlah']
            
            fig_buka = px.pie(
                df_buka, names='Frekuensi', values='Jumlah',
                title="Frekuensi Membuka Media Sosial Saat Belajar",
                hole=0.4
            )
            st.plotly_chart(fig_buka, use_container_width=True)
            
        with bottom_right:
            df_pengaruh = df_filtered[col_pengaruh].value_counts().reset_index()
            df_pengaruh.columns = ['Dampak', 'Jumlah']
            
            fig_pengaruh = px.bar(
                df_pengaruh, x='Jumlah', y='Dampak', orientation='h',
                title="Pengaruh Media Sosial pada Kebiasaan Belajar",
                labels={'Jumlah': 'Jumlah Responden', 'Dampak': 'Kategori Pengaruh'},
                color='Dampak', color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig_pengaruh, use_container_width=True)

except FileNotFoundError:
    st.error("❌ File 'Data responden.xlsx' tidak ditemukan! Pastikan file excel berada di dalam satu direktori repository GitHub Anda.")
except IndexError:
    st.error("❌ Gagal mendeteksi kolom kuesioner! Periksa apakah pertanyaan di file Excel Anda sudah benar atau sedikit berbeda kata-katanya.")

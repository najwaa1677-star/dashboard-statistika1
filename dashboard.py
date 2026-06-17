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
    # Membaca data (Pastikan file 'Data responden.xlsx' berada di folder yang sama di GitHub nanti)
    df = pd.read_excel("Data responden.xlsx")
    # Pembersihan data ringan seperti di notebook Anda
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
    with col1:
        st.metric("Total Responden (Terfilter)", f"{df_filtered.shape[0]} orang")
    with col2:
        # Menghitung persentase perempuan
        total = df_filtered.shape[0]
        if total > 0 and "Jenis Kelamin" in df_filtered.columns:
            p_count = df_filtered[df_filtered["Jenis Kelamin"] == "Perempuan"].shape[0]
            st.metric("Responden Perempuan", f"{(p_count/total)*100:.1f}%")
        else:
            st.metric("Responden Perempuan", "0%")
    with col3:
        if total > 0 and "Apakah Anda mengaktifkan notifikasi media sosial di ponsel?" in df_filtered.columns:
            notif_ya = df_filtered[df_filtered["Apakah Anda mengaktifkan notifikasi media sosial di ponsel?"] == "Ya"].shape[0]
            st.metric("Notifikasi Aktif", f"{(notif_ya/total)*100:.1f}%")
        else:
            st.metric("Notifikasi Aktif", "0%")

    st.markdown("---")

    # JIKA DATA KOSONG KARENA FILTER
    if df_filtered.empty:
        st.warning("Data tidak tersedia untuk kombinasi filter ini. Silakan ubah filter Anda.")
    else:
        # 6. Baris Grafik Bagian Pertama (Visualisasi Durasi & Fokus)
        st.subheader("📈 Analisis Durasi & Tingkat Fokus")
        left_chart, right_chart = st.columns(2)
        
        with left_chart:
            # Grafik 1: Durasi Penggunaan Media Sosial Harian
            col_durasi = "Berapa lama rata-rata Anda menggunakan media sosial setiap hari?"
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
            # Grafik 2: Tingkat Fokus Mahasiswa Saat Belajar
            col_fokus = df_filtered.columns[5] # Memastikan pakai indeks kolom agar aman
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
                color_discrete_sequence=px.colors.sequential.Viridis # DIUBAH: Menggunakan 'Viridis' atau 'Blues' yang pasti ada
            )
            st.plotly_chart(fig_fokus, width='stretch') # DIUBAH: use_container_width=True diganti width='stretch'

        # 7. Baris Grafik Bagian Kedua (Distribusi Frekuensi & Pengaruh)
        st.subheader("🔍 Korelasi Perilaku Belajar & Media Sosial")
        bottom_left, bottom_right = st.columns(2)
        
        with bottom_left:
            # Grafik 3: Seberapa sering membuka medsos saat belajar
            col_buka = "Seberapa sering Anda membuka media sosial saat sedang belajar?"
            df_buka = df_filtered[col_buka].value_counts().reset_index()
            df_buka.columns = ['Frekuensi', 'Jumlah']
            
            fig_buka = px.pie(
                df_buka, names='Frekuensi', values='Jumlah',
                title="Frekuensi Membuka Media Sosial Saat Belajar",
                hole=0.4
            )
            st.plotly_chart(fig_buka, use_container_width=True)
            
        with bottom_right:
            # Grafik 4: Pengaruh penggunaan media sosial harian terhadap kebiasaan belajar
            col_pengaruh = "Bagaimana pengaruh media sosial pengaruh penggunaan media sosial terhadap kebiasaan belajar Anda sehari-hari?"
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

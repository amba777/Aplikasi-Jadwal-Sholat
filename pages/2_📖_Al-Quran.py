import streamlit as st
import json
import os
import time

st.set_page_config(page_title="Al-Quran Digital", layout="wide")

# --- FUNGSI LOADING DATA ---

@st.cache_data
def load_surah_list():
    """Memuat daftar surah"""
    path_file = 'data/list_surah.json'
    try:
        with open(path_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f'File "{path_file}" tidak ditemukan.')
        return None

@st.cache_data
def load_surah_data(surah_number):
    """Memuat data surah spesifik"""
    path_file = f'surah/{surah_number}.json'
    try:
        with open(path_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f'File "{path_file}" tidak ditemukan.')
        return None

@st.cache_data
def load_surah_locations():
    """Memuat data lokasi turunnya surah"""
    path_file = 'data/surah_locations.json'
    try:
        with open(path_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f'File "{path_file}" tidak ditemukan.')
        return None

# --- LOGIKA UTAMA APLIKASI ---

# Load semua data
surah_list = load_surah_list()
surah_locations = load_surah_locations()

if not surah_list or not surah_locations:
    st.stop()

# Sidebar untuk navigasi
st.sidebar.header("🕌 Navigasi")

# Buat daftar opsi surah
surah_options = [f"{surah['number']}. {surah['name_latin']}" for surah in surah_list]

# --- PERBAIKAN: GUNAKAN SESSION STATE UNTUK MENGINGAT PILIHAN TERAKHIR ---
if 'last_selected_surah' not in st.session_state:
    st.session_state.last_selected_surah = surah_options[0]  # Default ke surah pertama

# Tampilkan selectbox dengan index yang sesuai dengan pilihan terakhir
selected_index = surah_options.index(st.session_state.last_selected_surah)
selected_surah_str = st.sidebar.selectbox(
    "Pilih Surah:", 
    surah_options,
    index=selected_index,  # Set index ke pilihan terakhir
    key="surah_selector"
)

# Update session state dengan pilihan terbaru
st.session_state.last_selected_surah = selected_surah_str

# Dapatkan nomor surah dari pilihan
selected_number = int(selected_surah_str.split('.')[0])

# Tampilkan informasi surah yang dipilih di sidebar
st.sidebar.markdown("---")
st.sidebar.info(f"**Surah Terpilih:**\n{selected_surah_str}")

# Mengambil data ringkasan dari list surah
surah_summary = surah_list[selected_number - 1]

# Muat data detail ayat
surah_data = load_surah_data(selected_number)

# Ambil lokasi dari file surah_locations.json
revelation_place = surah_locations.get(str(selected_number), "-")

# Ambil data lainnya dari file surah.json
arabic_name = ""
translation_id = ""
number_of_verses = ""

if surah_data:
    surah_info = surah_data.get(str(selected_number))
    if surah_info:
        arabic_name = surah_info.get('name', '')
        translation_id = surah_info.get('translations', {}).get('id', {}).get('name', '')
        number_of_verses = surah_info.get('number_of_ayah', '')

# Fallback ke data dari list_surah.json jika masih kosong
if not arabic_name:
    arabic_name = surah_summary.get('name', '')
if not translation_id:
    translation_id = surah_summary.get('translation_id', '')
if not number_of_verses:
    number_of_verses = surah_summary.get('number_of_verses', '')

# Tampilkan Judul Utama
st.markdown(f"## 📖 {surah_summary.get('name_latin', '')} - {arabic_name}")
st.markdown("---")

# Tampilkan informasi surah
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">Artinya</div>
        <div class="metric-value">{translation_id if translation_id else '-'}</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">Jumlah Ayat</div>
        <div class="metric-value">{number_of_verses if number_of_verses else '-'}</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">Diturunkan di</div>
        <div class="metric-value">{revelation_place if revelation_place else '-'}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

if surah_data:
    surah_info = surah_data.get(str(selected_number))

    if not surah_info:
        st.error(f"Struktur data tidak valid dalam file surah/{selected_number}.json.")
        st.stop()
    
    text_data = surah_info.get('text')
    translation_data = surah_info.get('translations', {}).get('id', {}).get('text')
    
    if text_data and translation_data:
        # Notifikasi 3 detik
        success_placeholder = st.empty()
        success_placeholder.success(f"Berhasil memuat {len(text_data)} ayat.")
        time.sleep(3)
        success_placeholder.empty()
        
        # Tampilkan ayat-ayat
        for ayat_number in sorted(text_data.keys(), key=int):
            arabic_text = text_data.get(str(ayat_number))
            translation_text = translation_data.get(str(ayat_number), "Terjemahan tidak tersedia.")

            st.markdown(f"""
            <div class="verse-container">
                <p class="verse-number"> Ayat {ayat_number} </p>
                <p class="arabic-text">{arabic_text}</p>
                <div class="translation-box">
                    <p class="translation-text"><b>Terjemahan:</b> <i>{translation_text}</i></p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.error("Data teks Arab atau terjemahan tidak ditemukan dalam file JSON ini.")
else:
    st.error(f"Gagal memuat data untuk Surah {selected_number}")

# --- CSS UNTUK TAMPILAN MODERN ---
st.markdown("""
<style>
    .metric-box {
        padding: 1rem;
        border-radius: 10px;
        background-color: #262730;
        text-align: center;
        border: 1px solid #444;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #aaa;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #fafafa;
    }
    .verse-container {
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-radius: 10px;
        background-color: #262730;
        border-left: 5px solid #00aaff;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .verse-number {
        font-weight: bold;
        color: #00aaff;
        margin-bottom: 1rem;
    }
    .arabic-text {
        font-family: 'Amiri', serif;
        direction: rtl;
        text-align: right;
        font-size: 28px;
        line-height: 2.2;
        color: #fafafa;
    }
    .translation-box {
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid #444;
    }
    .translation-text {
        font-size: 16px;
        line-height: 1.8;
        color: #ccc;
    }
</style>
""", unsafe_allow_html=True)
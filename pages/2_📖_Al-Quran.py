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
    except json.JSONDecodeError as e:
        st.error(f'Error parsing JSON di "{path_file}": {e}')
        return None

@st.cache_data
def load_surah_data(surah_number):
    """Memuat data surah spesifik dengan berbagai fallback"""
    # Coba berbagai format path
    possible_paths = [
        f'surah/{surah_number}.json',
        f'data/surah/{surah_number}.json',
        f'surah/surah_{surah_number}.json',
        f'data/surah/surah_{surah_number}.json'
    ]
    
    for path_file in possible_paths:
        try:
            if os.path.exists(path_file):
                with open(path_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Debug: tampilkan struktur data
                    st.sidebar.info(f"✅ Loaded from: {path_file}")
                    return data
        except FileNotFoundError:
            continue
        except json.JSONDecodeError as e:
            st.error(f'Error parsing JSON di "{path_file}": {e}')
            continue
    
    st.error(f'File surah {surah_number} tidak ditemukan di semua path yang dicoba.')
    return None

@st.cache_data
def load_surah_locations():
    """Memuat data lokasi turunnya surah"""
    path_file = 'data/surah_locations.json'
    try:
        with open(path_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback jika file tidak ada
        return {}
    except json.JSONDecodeError as e:
        st.error(f'Error parsing JSON di "{path_file}": {e}')
        return {}

# --- FUNGSI HELPER UNTUK EXTRACT DATA ---

def extract_surah_info(surah_data, surah_number):
    """Extract informasi surah dari berbagai struktur JSON yang mungkin"""
    
    # Cek apakah data dalam bentuk dict dengan key nomor surah
    if isinstance(surah_data, dict):
        # Coba dengan key string
        if str(surah_number) in surah_data:
            return surah_data[str(surah_number)]
        # Coba dengan key integer
        elif surah_number in surah_data:
            return surah_data[surah_number]
        # Jika data langsung adalah info surah
        elif 'text' in surah_data or 'name' in surah_data:
            return surah_data
    
    return None

# --- LOGIKA UTAMA APLIKASI ---

# Load semua data
surah_list = load_surah_list()
surah_locations = load_surah_locations()

if not surah_list:
    st.stop()

# Sidebar untuk navigasi
st.sidebar.header("🕌 Navigasi")

# Buat daftar opsi surah
surah_options = [f"{surah['number']}. {surah['name_latin']}" for surah in surah_list]

# --- GUNAKAN SESSION STATE UNTUK MENGINGAT PILIHAN TERAKHIR ---
if 'last_selected_surah' not in st.session_state:
    st.session_state.last_selected_surah = surah_options[0]

# Tampilkan selectbox dengan index yang sesuai dengan pilihan terakhir
try:
    selected_index = surah_options.index(st.session_state.last_selected_surah)
except ValueError:
    selected_index = 0

selected_surah_str = st.sidebar.selectbox(
    "Pilih Surah:", 
    surah_options,
    index=selected_index,
    key="surah_selector"
)

# Update session state dengan pilihan terbaru
st.session_state.last_selected_surah = selected_surah_str

# Dapatkan nomor surah dari pilihan
selected_number = int(selected_surah_str.split('.')[0])

# Tampilkan informasi surah yang dipilih di sidebar
st.sidebar.markdown("---")
st.sidebar.info(f"**Surah Terpilih:**\n{selected_surah_str}")

# Debug info
with st.sidebar.expander("🔍 Debug Info"):
    st.write(f"Nomor Surah: {selected_number}")
    st.write(f"Path dicoba: surah/{selected_number}.json")

# Mengambil data ringkasan dari list surah
surah_summary = surah_list[selected_number - 1]

# Muat data detail ayat
surah_data = load_surah_data(selected_number)

# Ambil lokasi dari file surah_locations.json
revelation_place = surah_locations.get(str(selected_number), "Mekah" if selected_number <= 86 else "Madinah")

# Inisialisasi variabel
arabic_name = surah_summary.get('name', '')
translation_id = surah_summary.get('translation_id', '')
number_of_verses = surah_summary.get('number_of_verses', 0)
text_data = None
translation_data = None

# Extract data dari surah_data jika ada
if surah_data:
    surah_info = extract_surah_info(surah_data, selected_number)
    
    if surah_info:
        # Update informasi jika ada di data detail
        if 'name' in surah_info:
            arabic_name = surah_info['name']
        
        if 'translations' in surah_info:
            trans = surah_info['translations']
            if isinstance(trans, dict) and 'id' in trans:
                if 'name' in trans['id']:
                    translation_id = trans['id']['name']
                if 'text' in trans['id']:
                    translation_data = trans['id']['text']
        
        if 'number_of_ayah' in surah_info:
            number_of_verses = surah_info['number_of_ayah']
        
        if 'text' in surah_info:
            text_data = surah_info['text']

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

# Tampilkan ayat-ayat
if text_data and translation_data:
    # Notifikasi 3 detik
    success_placeholder = st.empty()
    success_placeholder.success(f"✅ Berhasil memuat {len(text_data)} ayat dari Surah {surah_summary.get('name_latin', '')}.")
    time.sleep(3)
    success_placeholder.empty()
    
    # Tampilkan ayat-ayat
    for ayat_number in sorted(text_data.keys(), key=int):
        arabic_text = text_data.get(str(ayat_number), "")
        translation_text = translation_data.get(str(ayat_number), "Terjemahan tidak tersedia.")

        st.markdown(f"""
        <div class="verse-container">
            <p class="verse-number">🔖 Ayat {ayat_number}</p>
            <p class="arabic-text">{arabic_text}</p>
            <div class="translation-box">
                <p class="translation-text"><b>Terjemahan:</b> <i>{translation_text}</i></p>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    # Tampilkan pesan error yang lebih informatif
    st.warning(f"⚠️ Data ayat untuk Surah {selected_number} ({surah_summary.get('name_latin', '')}) tidak dapat dimuat.")
    
    with st.expander("🔧 Informasi Troubleshooting"):
        st.write("**Kemungkinan penyebab:**")
        st.write("1. File `surah/{selected_number}.json` tidak ada atau corrupt")
        st.write("2. Struktur JSON tidak sesuai format yang diharapkan")
        st.write("3. Path file salah")
        st.write(f"\n**Expected path:** `surah/{selected_number}.json`")
        
        if surah_data:
            st.write("\n**Data yang terload:**")
            st.json(surah_data)
        else:
            st.write("\n❌ Tidak ada data yang terload sama sekali")
    
    st.info("💡 **Saran:** Pastikan file JSON ada dan strukturnya benar. Surah lain bisa muncul karena strukturnya berbeda atau filenya ada.")

# --- CSS UNTUK TAMPILAN MODERN ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap');
    
    .stApp {
        background-color: #0f1419;
    }
    
    .metric-box {
        padding: 1.5rem;
        border-radius: 12px;
        background: linear-gradient(135deg, #1e2128 0%, #2d3139 100%);
        text-align: center;
        border: 1px solid #3d4450;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-box:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 12px rgba(0, 170, 255, 0.2);
        border-color: #00aaff;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #8b92a5;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .metric-value {
        font-size: 1.6rem;
        font-weight: bold;
        color: #ffffff;
    }
    
    .verse-container {
        padding: 2rem;
        margin-bottom: 1.5rem;
        border-radius: 15px;
        background: linear-gradient(135deg, #1a1d24 0%, #252930 100%);
        border-left: 5px solid #00aaff;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .verse-container:hover {
        transform: translateX(5px);
        box-shadow: 0 12px 24px rgba(0, 170, 255, 0.15);
        border-left-color: #00d4ff;
    }
    
    .verse-number {
        font-weight: 600;
        color: #00aaff;
        margin-bottom: 1.2rem;
        font-size: 1.1rem;
        display: inline-block;
        padding: 0.3rem 1rem;
        background: rgba(0, 170, 255, 0.1);
        border-radius: 20px;
    }
    
    .arabic-text {
        font-family: 'Amiri', 'Traditional Arabic', 'Al Qalam', serif;
        direction: rtl;
        text-align: right;
        font-size: 32px;
        line-height: 2.5;
        color: #ffffff;
        margin: 1.5rem 0;
        padding: 1rem;
        background: rgba(0, 170, 255, 0.03);
        border-radius: 10px;
    }
    
    .translation-box {
        margin-top: 1.5rem;
        padding-top: 1.5rem;
        border-top: 2px solid #3d4450;
    }
    
    .translation-text {
        font-size: 17px;
        line-height: 2;
        color: #c5cad6;
        font-weight: 400;
    }
    
    .translation-text b {
        color: #00aaff;
        font-weight: 600;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1a1d24;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #3d4450;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #00aaff;
    }
</style>
""", unsafe_allow_html=True)

import streamlit as st
import json
import os
import time

st.set_page_config(page_title="Al-Quran Digital", layout="wide", page_icon="📖")

# --- CUSTOM CSS MODERN & RESPONSIF ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Poppins:wght@300;400;500;600;700&display=swap');
    
    /* Background dan Theme */
    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #1a1f35 100%);
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1419 0%, #1a1f2e 100%);
        border-right: 1px solid #2d3748;
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #00d4ff !important;
        font-family: 'Poppins', sans-serif;
    }
    
    /* Header dengan Gradient */
    .main-header {
        text-align: center;
        padding: 2rem 1rem;
        background: linear-gradient(135deg, rgba(0, 170, 255, 0.1) 0%, rgba(0, 212, 255, 0.05) 100%);
        border-radius: 20px;
        margin-bottom: 2rem;
        border: 1px solid rgba(0, 170, 255, 0.2);
    }
    
    .main-title {
        font-family: 'Poppins', sans-serif;
        font-size: clamp(1.8rem, 5vw, 3rem);
        font-weight: 700;
        color: #ffffff;
        margin: 0;
        text-shadow: 0 0 20px rgba(0, 170, 255, 0.5);
    }
    
    .main-subtitle {
        font-family: 'Amiri', serif;
        font-size: clamp(1.5rem, 4vw, 2.5rem);
        color: #00d4ff;
        margin: 0.5rem 0 0 0;
    }
    
    /* Info Cards - Grid Responsif */
    .info-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .metric-box {
        padding: 1.8rem 1.5rem;
        border-radius: 16px;
        background: linear-gradient(135deg, rgba(30, 33, 40, 0.9) 0%, rgba(45, 49, 57, 0.9) 100%);
        backdrop-filter: blur(10px);
        text-align: center;
        border: 1px solid rgba(0, 170, 255, 0.2);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, #00aaff, #00d4ff, #00aaff);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .metric-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 32px rgba(0, 170, 255, 0.3);
        border-color: #00aaff;
    }
    
    .metric-box:hover::before {
        transform: scaleX(1);
    }
    
    .metric-label {
        font-size: clamp(0.75rem, 2vw, 0.9rem);
        color: #8b92a5;
        margin-bottom: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 500;
        font-family: 'Poppins', sans-serif;
    }
    
    .metric-value {
        font-size: clamp(1.3rem, 4vw, 1.8rem);
        font-weight: 700;
        color: #ffffff;
        font-family: 'Poppins', sans-serif;
    }
    
    .metric-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
        opacity: 0.8;
    }
    
    /* Verse Container - Responsif */
    .verse-container {
        padding: clamp(1.5rem, 3vw, 2.5rem);
        margin-bottom: 2rem;
        border-radius: 20px;
        background: linear-gradient(135deg, rgba(26, 29, 36, 0.95) 0%, rgba(37, 41, 48, 0.95) 100%);
        backdrop-filter: blur(15px);
        border-left: 5px solid #00aaff;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
    }
    
    .verse-container::after {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 100px;
        height: 100px;
        background: radial-gradient(circle, rgba(0, 170, 255, 0.1) 0%, transparent 70%);
        border-radius: 50%;
    }
    
    .verse-container:hover {
        transform: translateX(8px);
        box-shadow: 0 15px 40px rgba(0, 170, 255, 0.2);
        border-left-color: #00d4ff;
    }
    
    .verse-number {
        font-weight: 600;
        color: #00aaff;
        margin-bottom: 1.5rem;
        font-size: clamp(0.95rem, 2.5vw, 1.1rem);
        display: inline-block;
        padding: 0.5rem 1.2rem;
        background: linear-gradient(135deg, rgba(0, 170, 255, 0.15), rgba(0, 212, 255, 0.1));
        border-radius: 25px;
        border: 1px solid rgba(0, 170, 255, 0.3);
        font-family: 'Poppins', sans-serif;
        backdrop-filter: blur(10px);
    }
    
    .arabic-text {
        font-family: 'Amiri', 'Traditional Arabic', 'Al Qalam', serif;
        direction: rtl;
        text-align: right;
        font-size: clamp(1.5rem, 5vw, 2.2rem);
        line-height: 2.5;
        color: #ffffff;
        margin: 1.8rem 0;
        padding: clamp(1rem, 2vw, 1.5rem);
        background: rgba(0, 170, 255, 0.04);
        border-radius: 15px;
        border: 1px solid rgba(0, 170, 255, 0.1);
        font-weight: 400;
    }
    
    .translation-box {
        margin-top: 1.8rem;
        padding-top: 1.8rem;
        border-top: 2px solid rgba(0, 170, 255, 0.2);
    }
    
    .translation-text {
        font-size: clamp(0.95rem, 2.5vw, 1.1rem);
        line-height: 2;
        color: #c5cad6;
        font-weight: 400;
        font-family: 'Poppins', sans-serif;
    }
    
    .translation-text b {
        color: #00d4ff;
        font-weight: 600;
    }
    
    /* Loading Animation */
    .loading-container {
        text-align: center;
        padding: 3rem;
    }
    
    .loading-text {
        font-size: 1.2rem;
        color: #00aaff;
        font-family: 'Poppins', sans-serif;
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Success Message */
    .success-message {
        background: linear-gradient(135deg, rgba(0, 170, 255, 0.2), rgba(0, 212, 255, 0.1));
        border: 1px solid rgba(0, 170, 255, 0.4);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        color: #00d4ff;
        font-family: 'Poppins', sans-serif;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Scrollbar Custom */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0f1419;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #00aaff, #00d4ff);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #00d4ff, #00aaff);
    }
    
    /* Mobile Responsiveness */
    @media (max-width: 768px) {
        .verse-container {
            border-left-width: 3px;
        }
        
        .arabic-text {
            line-height: 2.2;
        }
        
        .info-grid {
            grid-template-columns: 1fr;
            gap: 1rem;
        }
        
        .main-header {
            padding: 1.5rem 1rem;
            margin-bottom: 1.5rem;
        }
    }
    
    @media (max-width: 480px) {
        .verse-container {
            padding: 1.2rem;
            margin-bottom: 1.5rem;
        }
        
        .translation-text {
            line-height: 1.8;
        }
    }
    
    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- FUNGSI LOADING DATA ---

@st.cache_data
def load_surah_list():
    """Memuat daftar surah"""
    path_file = 'data/list_surah.json'
    try:
        with open(path_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f'❌ File "{path_file}" tidak ditemukan.')
        return None
    except json.JSONDecodeError as e:
        st.error(f'❌ Error parsing JSON: {e}')
        return None

@st.cache_data
def load_surah_data(surah_number):
    """Memuat data surah spesifik dengan berbagai fallback"""
    possible_paths = [
        f'surah/{surah_number}.json',
        f'data/surah/{surah_number}.json',
        f'surah/surah_{surah_number}.json',
    ]
    
    for path_file in possible_paths:
        try:
            if os.path.exists(path_file):
                with open(path_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            continue
    
    return None

@st.cache_data
def load_surah_locations():
    """Memuat data lokasi turunnya surah"""
    path_file = 'data/surah_locations.json'
    try:
        with open(path_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

# --- FUNGSI HELPER ---

def extract_surah_info(surah_data, surah_number):
    """Extract informasi surah dari berbagai struktur JSON"""
    if isinstance(surah_data, dict):
        if str(surah_number) in surah_data:
            return surah_data[str(surah_number)]
        elif surah_number in surah_data:
            return surah_data[surah_number]
        elif 'text' in surah_data or 'name' in surah_data:
            return surah_data
    return None

# --- LOGIKA UTAMA ---

surah_list = load_surah_list()
surah_locations = load_surah_locations()

if not surah_list:
    st.stop()

# Sidebar
with st.sidebar:
    st.markdown("### 🕌 Navigasi Al-Quran")
    st.markdown("---")
    
    # Buat daftar opsi surah
    surah_options = [f"{surah['number']}. {surah['name_latin']}" for surah in surah_list]
    
    if 'last_selected_surah' not in st.session_state:
        st.session_state.last_selected_surah = surah_options[0]
    
    try:
        selected_index = surah_options.index(st.session_state.last_selected_surah)
    except ValueError:
        selected_index = 0
    
    selected_surah_str = st.selectbox(
        "Pilih Surah:", 
        surah_options,
        index=selected_index,
        key="surah_selector",
        label_visibility="collapsed"
    )
    
    st.session_state.last_selected_surah = selected_surah_str
    
    # Info surah di sidebar
    st.markdown("---")
    selected_number = int(selected_surah_str.split('.')[0])
    surah_summary = surah_list[selected_number - 1]
    
    st.markdown(f"""
    <div style='background: rgba(0, 170, 255, 0.1); padding: 1rem; border-radius: 10px; border: 1px solid rgba(0, 170, 255, 0.3);'>
        <p style='margin: 0; color: #00d4ff; font-weight: 600; font-size: 0.9rem;'>📖 Surah Terpilih</p>
        <p style='margin: 0.5rem 0 0 0; color: #fff; font-size: 1rem;'>{surah_summary.get('name_latin', '')}</p>
        <p style='margin: 0.3rem 0 0 0; color: #8b92a5; font-size: 0.85rem;'>Surah ke-{selected_number}</p>
    </div>
    """, unsafe_allow_html=True)

# Load data surah
surah_data = load_surah_data(selected_number)
revelation_place = surah_locations.get(str(selected_number), "Mekah" if selected_number <= 86 else "Madinah")

# Inisialisasi variabel
arabic_name = surah_summary.get('name', '')
translation_id = surah_summary.get('translation_id', '')
number_of_verses = surah_summary.get('number_of_verses', 0)
text_data = None
translation_data = None

# Extract data
if surah_data:
    surah_info = extract_surah_info(surah_data, selected_number)
    if surah_info:
        arabic_name = surah_info.get('name', arabic_name)
        number_of_verses = surah_info.get('number_of_ayah', number_of_verses)
        text_data = surah_info.get('text')
        
        if 'translations' in surah_info:
            trans = surah_info['translations']
            if isinstance(trans, dict) and 'id' in trans:
                translation_id = trans['id'].get('name', translation_id)
                translation_data = trans['id'].get('text')

# Header
st.markdown(f"""
<div class="main-header">
    <h1 class="main-title">📖 {surah_summary.get('name_latin', '')}</h1>
    <p class="main-subtitle">{arabic_name}</p>
</div>
""", unsafe_allow_html=True)

# Info Cards
st.markdown(f"""
<div class="info-grid">
    <div class="metric-box">
        <div class="metric-icon">📝</div>
        <div class="metric-label">Artinya</div>
        <div class="metric-value">{translation_id if translation_id else '-'}</div>
    </div>
    <div class="metric-box">
        <div class="metric-icon">🔢</div>
        <div class="metric-label">Jumlah Ayat</div>
        <div class="metric-value">{number_of_verses if number_of_verses else '-'}</div>
    </div>
    <div class="metric-box">
        <div class="metric-icon">📍</div>
        <div class="metric-label">Diturunkan di</div>
        <div class="metric-value">{revelation_place}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Tampilkan ayat-ayat
if text_data and translation_data:
    st.markdown(f"""
    <div class="success-message">
        ✅ Berhasil memuat {len(text_data)} ayat dari Surah {surah_summary.get('name_latin', '')}
    </div>
    """, unsafe_allow_html=True)
    
    for ayat_number in sorted(text_data.keys(), key=int):
        arabic_text = text_data.get(str(ayat_number), "")
        translation_text = translation_data.get(str(ayat_number), "Terjemahan tidak tersedia.")
        
        st.markdown(f"""
        <div class="verse-container">
            <div class="verse-number">🔖 Ayat {ayat_number}</div>
            <div class="arabic-text">{arabic_text}</div>
            <div class="translation-box">
                <p class="translation-text"><b>Terjemahan:</b> {translation_text}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.warning(f"⚠️ Data ayat untuk Surah {surah_summary.get('name_latin', '')} tidak dapat dimuat.")
    st.info("💡 Pastikan file JSON ada dan strukturnya sesuai format.")

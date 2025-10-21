import streamlit as st
import json
import time

# Konfigurasi halaman
st.set_page_config(
    page_title="Asmaul Husna - 99 Nama Allah",
    page_icon="✨",
    layout="wide"
)

# --- CSS BARU (disesuaikan dengan tema Al-Quran) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap');

.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #1a1f35 100%);
    color: #c9d1d9;
    font-family: 'Poppins', sans-serif;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1419 0%, #1a1f2e 100%);
    border-right: 1px solid #2d3748;
}

/* KONSISTENSI FONT SIDEBAR */
[data-testid="stSidebarNav"] li > a {
    font-size: 1rem;
    font-weight: 500;
    color: #c9d1d9;
    transition: color 0.2s ease, background-color 0.2s ease;
}
[data-testid="stSidebarNav"] li > a:hover {
    color: #00d4ff;
    background-color: rgba(0, 212, 255, 0.1);
}
[data-testid="stSidebarNav"] li > a.current-selection {
    background-color: #00aaff;
    color: white;
    border-radius: 8px;
    font-weight: 600;
}
[data-testid="stSidebarNav"] li > a.current-selection:hover {
    background-color: #00d4ff;
    color: white;
}

.main-header {
    text-align: center;
    padding: 2rem 1rem;
    background: linear-gradient(135deg, rgba(0, 170, 255, 0.1) 0%, rgba(0, 212, 255, 0.05) 100%);
    border-radius: 20px;
    margin-bottom: 2rem;
    border: 1px solid rgba(0, 170, 255, 0.2);
}
.main-header h1 {
    font-family: 'Poppins', sans-serif;
    font-size: 2.8rem;
    font-weight: 700;
    color: #ffffff;
    text-shadow: 0 0 15px rgba(0, 212, 255, 0.5);
    margin: 0;
}
.main-header p {
    color: #8b949e;
    font-size: 1.1rem;
    margin-top: 10px;
}

/* Styling kartu Asmaul Husna */
.asma-card {
    background: rgba(22, 27, 34, 0.8);
    backdrop-filter: blur(10px);
    padding: 1.5rem;
    border-radius: 15px;
    border: 1px solid #30363d;
    margin-bottom: 1rem;
    transition: transform 0.3s ease, border-color 0.3s ease;
    height: 100%;
    color: #fafafa;
}
.asma-card:hover {
    transform: translateY(-5px);
    border-color: #00aaff;
}
.arabic-text {
    font-size: 2.2rem;
    text-align: right;
    font-family: 'Amiri', 'Traditional Arabic', serif;
    margin-bottom: 0.5rem;
    direction: rtl;
    line-height: 1.5;
    color: #fafafa;
}
.latin-text {
    font-size: 1.3rem;
    font-weight: bold;
    color: #00d4ff; /* Warna aksen baru */
    margin-bottom: 0.5rem;
}
.meaning-text {
    color: #c9d1d9;
    font-size: 1rem;
    line-height: 1.5;
}
.number-badge {
    background: #00aaff; /* Warna aksen baru */
    color: white;
    width: 35px;
    height: 35px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    margin-bottom: 1rem;
}
.search-info {
    background: rgba(22, 27, 34, 0.8);
    border: 1px solid #30363d;
    padding: 10px 15px;
    border-radius: 8px;
    margin-bottom: 1rem;
}

/* Styling Search Box dan Tombol */
div[data-testid="stTextInput"] input {
    background-color: #21262d;
    border: 1px solid #30363d;
    border-radius: 8px;
    color: #c9d1d9;
}
.stButton button {
    border: 1px solid #4c566a;
    background-color: #3b4252;
    color: #eceff4;
    border-radius: 8px;
    transition: all 0.2s ease;
}
.stButton button:hover {
    border-color: #d8dee9;
    color: white;
}
</style>
""", unsafe_allow_html=True)


def clear_search():
    st.session_state.search_input = ""

@st.cache_data
def load_data():
    try:
        with open('data/asmaul_husna.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        st.error("❌ File 'data/asmaul_husna.json' tidak ditemukan.")
        st.info("Pastikan file berada di folder 'data/asmaul_husna.json'")
        return []
    except Exception as e:
        st.error(f"❌ Terjadi error saat memuat data: {e}")
        return []

def filter_data(data, query):
    if not query:
        return data
    query = query.lower()
    return [
        item for item in data 
        if query in item.get('latin', '').lower() or 
           query in item.get('meaning', '').lower()
    ]

def display_asma_card(item):
    number = item.get('no', '')
    arabic = item.get('name', '')
    latin = item.get('latin', '')
    meaning = item.get('meaning', '')
    
    card_html = f"""
    <div class="asma-card">
        <div class="number-badge">{number}</div>
        <div class="arabic-text">{arabic}</div>
        <div class="latin-text">{latin}</div>
        <div class="meaning-text">{meaning}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def display_asmaul_husna_grid(data):
    if not data:
        st.warning("⚠️ Tidak ada hasil yang ditemukan.")
        return
    
    cols_per_row = 3
    for i in range(0, len(data), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            if i + j < len(data):
                with cols[j]:
                    display_asma_card(data[i + j])

def display_footer():
    st.markdown("---")
    st.markdown("""
    <div style='margin-top: 1.5rem; padding: 1rem; background: rgba(0, 0, 0, 0.3); border-radius: 8px;'>
        <p style='color: #888; font-size: 0.85rem; margin: 0; font-style: italic;'>
            "Dan Allah memiliki Asma'ul-husna (nama-nama yang terbaik), maka bermohonlah kepada-Nya dengan menyebutnya Asma'ul-husna itu..."<br>
            <span style='color: #00aaff;'>(QS. Al-A'raf: 180)</span>
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style='margin-top: 1.5rem; text-align: center;'>
        <p style='color: #666; font-size: 0.8rem; margin: 0.3rem 0;'>© 2025 Aplikasi Asmaul Husna</p>
        <p style='color: #666; font-size: 0.8rem; margin: 0.3rem 0;'>Developed with ❤️ for Hamba Allah</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    # Header baru yang sudah di-styling
    st.markdown("""
    <div class="main-header">
        <h1>✨ Asmaul Husna - 99 Nama Allah</h1>
        <p>Mengenal Nama-Nama Indah Allah SWT</p>
    </div>
    """, unsafe_allow_html=True)
    
    asmaul_husna_data = load_data()
    if not asmaul_husna_data:
        return
    
    # Tampilkan search box dan tombol reset
    st.markdown("### 🔍 Cari nama Allah")
    col_search, col_button = st.columns([4, 1])
    with col_search:
        search_query = st.text_input(
            "Cari", 
            placeholder="Ketik nama latin atau arti...",
            key="search_input",
            label_visibility="collapsed"
        )
    with col_button:
        st.button("❌ Hapus Pencarian", on_click=clear_search, use_container_width=True)
            
    st.markdown("---")
    
    filtered_data = filter_data(asmaul_husna_data, search_query)
    
    if search_query:
        st.markdown(f"""
        <div class="search-info">
            <strong>🔍 Hasil Pencarian:</strong> '{search_query}'<br>
            <strong>📊 Menampilkan:</strong> {len(filtered_data)} dari {len(asmaul_husna_data)} nama
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"**📊 Total: {len(asmaul_husna_data)} nama Allah**")
    
    display_asmaul_husna_grid(filtered_data)
    display_footer()

if __name__ == "__main__":
    main()

import streamlit as st

st.set_page_config(page_title="Tasbih Digital", layout="wide")

# Inisialisasi state jika belum ada
if 'count' not in st.session_state:
    st.session_state.count = 0

# --- CSS BARU (disesuaikan dengan tema Al-Quran) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@700&display=swap');
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

/* KONSISTENSI FONT SIDEBAR - BARU */
[data-testid="stSidebarNav"] li > a {
    font-size: 1rem; /* Ukuran font item menu sidebar */
    font-weight: 500;
    color: #c9d1d9; /* Warna teks normal */
    transition: color 0.2s ease, background-color 0.2s ease;
}

[data-testid="stSidebarNav"] li > a:hover {
    color: #00d4ff; /* Warna teks saat hover */
    background-color: rgba(0, 212, 255, 0.1);
}

[data-testid="stSidebarNav"] li > a.current-selection {
    background-color: #00aaff; /* Warna background untuk item aktif */
    color: white; /* Warna teks untuk item aktif */
    border-radius: 8px;
    font-weight: 600;
}
[data-testid="stSidebarNav"] li > a.current-selection:hover {
    background-color: #00d4ff;
    color: white;
}
/* Akhir KONSISTENSI FONT SIDEBAR */

.main-header {
    text-align: center;
    margin-bottom: 2rem;
    padding: 2rem 1rem;
    background: linear-gradient(135deg, rgba(0, 170, 255, 0.1) 0%, rgba(0, 212, 255, 0.05) 100%); /* Latar belakang gradasi baru */
    border-radius: 20px;
    border: 1px solid rgba(0, 170, 255, 0.2);
}

.main-header h1 {
    font-family: 'Poppins', sans-serif;
    font-size: 2.8rem;
    font-weight: 700;
    color: #ffffff;
    text-shadow: 0 0 15px rgba(0, 212, 255, 0.5);
    margin: 0; /* Pastikan tidak ada margin default */
}

.count-display {
    text-align: center;
    font-size: clamp(5rem, 15vw, 9rem);
    font-weight: 700;
    color: #00d4ff;
    margin: 2rem 0;
    text-shadow: 0 0 25px rgba(0, 212, 255, 0.6);
    font-family: 'JetBrains Mono', monospace;
}

.styled-container {
    background: rgba(22, 27, 34, 0.8);
    backdrop-filter: blur(10px);
    border: 1px solid #30363d;
    border-radius: 20px;
    padding: 1.5rem 2rem;
    margin-bottom: 2rem;
    transition: all 0.3s ease;
}

.styled-container:hover {
    border-color: #00aaff;
}

.styled-container h3 {
    color: #00aaff; /* Warna aksen yang konsisten */
    font-family: 'Poppins', sans-serif;
    margin-top: 0;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.7rem;
}

.stButton button {
    width: 100%;
    height: 70px;
    font-size: 1.2rem;
    font-weight: 600;
    border-radius: 15px;
    border: none;
    transition: all 0.3s ease;
}

.stButton button:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 12px rgba(0,0,0,0.3);
}

.add-button-wrapper .stButton button {
    background: linear-gradient(135deg, #00aaff, #00d4ff);
    color: white;
}

.reset-button-wrapper .stButton button {
    background: linear-gradient(135deg, #434c5e, #3b4252);
    color: #eceff4;
    border: 1px solid #4c566a;
}
.reset-button-wrapper .stButton button:hover {
    border-color: #d8dee9;
}

.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #00aaff, #00d4ff);
}

/* Styling untuk st.number_input */
.stNumberInput div[data-baseweb="input"] {
    background-color: #21262d;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 5px 10px;
}
.stNumberInput div[data-baseweb="input"] input {
    color: #c9d1d9;
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.1rem;
}
.stNumberInput div[data-baseweb="input"] button {
    color: #00aaff !important;
    background-color: transparent !important;
    border: none !important;
}
.stNumberInput div[data-baseweb="input"] button:hover {
    background-color: rgba(0, 170, 255, 0.1) !important;
}


@media (max-width: 992px) {
    .main-grid { grid-template-columns: 1fr; }
}
@media (max-width: 768px) {
    .schedule-grid { grid-template-columns: repeat(3, 1fr); }
    .digital-clock { font-size: 4rem; }
}
@media (max-width: 576px) {
    .schedule-grid { grid-template-columns: repeat(2, 1fr); }
    .main-header h1 { font-size: 2.2rem; }
    .count-display { font-size: 3rem; }
    .stButton button { height: 60px; font-size: 1rem; }
}
</style>
""", unsafe_allow_html=True)

# SECTION 0: Header Utama
st.markdown('<div class="main-header"><h1>📿 Tasbih Digital</h1></div>', unsafe_allow_html=True)


# SECTION 1: Target Dzikir
st.markdown('<div class="styled-container">', unsafe_allow_html=True)
st.markdown("<h3>🎯 Target Dzikir</h3>", unsafe_allow_html=True)

target_col1, target_col2 = st.columns([2, 1])
with target_col1:
    target = st.number_input(
        "Set target dzikir Anda:",
        min_value=0, value=33, step=33,
        help="Biasanya dzikir dilakukan 33x, 99x, atau sesuai kebutuhan",
        label_visibility="collapsed"
    )
with target_col2:
    progress = min(st.session_state.count / target * 100, 100) if target > 0 else 0
    st.metric("Progress", f"{progress:.1f}%")

st.progress(progress / 100)
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.count >= target > 0:
    st.success(f"🎉 Selamat! Anda telah mencapai target {target} dzikir!")

# SECTION 2: Tampilan hitungan utama
st.markdown(f"<div class='count-display'>{st.session_state.count}</div>", unsafe_allow_html=True)

# SECTION 3: Tombol-tombol
col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="add-button-wrapper">', unsafe_allow_html=True)
    if st.button("➕ Tambah (+1)", use_container_width=True):
        st.session_state.count += 1
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="reset-button-wrapper">', unsafe_allow_html=True)
    if st.button("🔄 Reset (0)", use_container_width=True):
        st.session_state.count = 0
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# SECTION 4: Petunjuk Penggunaan
st.markdown("""
<div class="styled-container" style="margin-top: 2rem;">
    <h4 style='margin:0; color: #00aaff;'>💡 Petunjuk Penggunaan</h4>
    <p style='margin:0.5rem 0 0 0; color: #ccc;'>
        Klik tombol <strong>'Tambah'</strong> untuk menghitung dzikir Anda.<br>
        Gunakan tombol <strong>'Reset'</strong> untuk mengulang dari 0.
    </p>
</div>
""", unsafe_allow_html=True)

# === BAGIAN FOOTER ===
def display_footer():
    st.markdown("---")
    st.markdown("""
    <div style='margin-top: 1.5rem; 
                padding: 1rem; 
                background: rgba(0, 0, 0, 0.3); 
                border-radius: 8px;'>
        <p style='color: #888; font-size: 0.85rem; margin: 0; font-style: italic;'>
            "Wahai orang-orang yang beriman! Ingatlah kepada Allah dengan zikir yang sebanyak-banyaknya."<br>
            <span style='color: #00aaff;'>(QS. Al-Ahzab: 41)</span>
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style='margin-top: 1.5rem; text-align: center;'>
        <p style='color: #666; font-size: 0.8rem; margin: 0.3rem 0;'>© 2025 Tasbih Digital</p>
        <p style='color: #666; font-size: 0.8rem; margin: 0.3rem 0;'>Developed with ❤️ for Hamba Allah</p>
    </div>
    """, unsafe_allow_html=True)

display_footer()

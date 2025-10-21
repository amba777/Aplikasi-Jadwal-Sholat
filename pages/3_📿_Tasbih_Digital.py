import streamlit as st

st.set_page_config(page_title="Tasbih Digital", layout="wide")

st.title("📿 Tasbih Digital")

# Inisialisasi state jika belum ada
if 'count' not in st.session_state:
    st.session_state.count = 0

# CSS untuk styling modern
st.markdown("""
<style>
    .count-display {
        text-align: center;
        font-size: 120px;
        font-weight: bold;
        color: #00aaff;
        margin: 2rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        font-family: 'Arial', sans-serif;
    }
    .button-container {
        display: flex;
        gap: 1rem;
        margin: 2rem 0;
    }
    .stButton button {
        width: 100%;
        height: 80px;
        font-size: 20px;
        font-weight: bold;
        border-radius: 15px;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .add-button {
        background: linear-gradient(135deg, #00aaff, #0088cc);
        color: white;
    }
    .reset-button {
        background: linear-gradient(135deg, #ff6b6b, #ee5a52);
        color: white;
    }
    .info-box {
        background-color: #262730;
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #00aaff;
        margin-top: 2rem;
    }
    .target-section {
        background-color: #262730;
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #ffa500;
        margin-bottom: 2rem;
    }
    @media (max-width: 768px) {
        .count-display {
            font-size: 80px;
            margin: 1rem 0;
        }
        .stButton button {
            height: 60px;
            font-size: 18px;
        }
    }
</style>
""", unsafe_allow_html=True)

# SECTION 1: Target Dzikir (DI ATAS)
st.markdown("---")
st.markdown("""
<div class="target-section">
    <h3 style='margin:0; color: #ffa500;'>🎯 Target Dzikir</h3>
</div>
""", unsafe_allow_html=True)

target_col1, target_col2 = st.columns([2, 1])

with target_col1:
    target = st.number_input(
        "Set target dzikir Anda:",
        min_value=0,
        value=33,
        step=33,
        help="Biasanya dzikir dilakukan 33x, 99x, atau sesuai kebutuhan"
    )

with target_col2:
    st.markdown("<br>", unsafe_allow_html=True)
    progress = min(st.session_state.count / target * 100, 100) if target > 0 else 0
    st.metric("Progress", f"{progress:.1f}%")

# Progress bar
st.progress(progress / 100)

if st.session_state.count >= target > 0:
    st.success(f"🎉 Selamat! Anda telah mencapai target {target} dzikir!")

# SECTION 2: Tampilan hitungan utama
st.markdown(f"<div class='count-display'>{st.session_state.count}</div>", unsafe_allow_html=True)

# SECTION 3: Tombol-tombol
# Custom class untuk tombol tidak bisa langsung diterapkan di st.button,
# jadi kita gunakan styling umum .stButton button dari CSS di atas.
col1, col2 = st.columns(2)

with col1:
    if st.button(
        "➕ Tambah (+1)", 
        use_container_width=True
    ):
        st.session_state.count += 1
        st.rerun()

with col2:
    if st.button(
        "🔄 Reset (0)", 
        use_container_width=True
    ):
        st.session_state.count = 0
        st.rerun()

# SECTION 4: Petunjuk Penggunaan (DI BAWAH)
st.markdown("""
<div class="info-box">
    <h4 style='margin:0; color: #00aaff;'>💡 Petunjuk Penggunaan</h4>
    <p style='margin:0.5rem 0 0 0; color: #ccc;'>
        Klik tombol <strong>'Tambah'</strong> untuk menghitung dzikir Anda.<br>
        Gunakan tombol <strong>'Reset'</strong> untuk mengulang dari 0.
    </p>
</div>
""", unsafe_allow_html=True)

# === BAGIAN FOOTER BARU ===
def display_footer():
    """Menampilkan footer aplikasi dengan ayat Quran dan copyright."""
    st.markdown("---")
    
    # Ayat Al-Quran
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

    # Copyright
    st.markdown("""
    <div style='margin-top: 1.5rem; text-align: center;'>
        <p style='color: #666; font-size: 0.8rem; margin: 0.3rem 0;'>© 2025 Tasbih Digital</p>
        <p style='color: #666; font-size: 0.8rem; margin: 0.3rem 0;'>Developed with ❤️ for Hamba Allah</p>
    </div>
    """, unsafe_allow_html=True)

# Panggil fungsi footer di akhir aplikasi
display_footer()

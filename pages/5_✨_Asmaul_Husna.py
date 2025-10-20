import streamlit as st
import json
import time

# Konfigurasi halaman
st.set_page_config(
    page_title="Asmaul Husna - 99 Nama Allah",
    page_icon="🕌",
    layout="wide"
)

# CSS styling untuk tampilan modern dan responsif
st.markdown("""
<style>
    /* Card untuk setiap nama */
    .asma-card {
        background-color: #262730; 
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #444; 
        margin-bottom: 1rem;
        border-left: 5px solid #00aaff;
        transition: transform 0.2s, border-color 0.2s;
        height: 100%;
        color: #fafafa;
    }
    .asma-card:hover {
        transform: translateY(-3px);
        border-left-color: #1890ff;
    }
    /* Teks Arab */
    .arabic-text {
        font-size: 2.2rem;
        text-align: right;
        font-family: 'Amiri', 'Traditional Arabic', serif;
        margin-bottom: 0.5rem;
        direction: rtl;
        line-height: 1.5;
        color: #fafafa;
    }
    /* Teks Latin */
    .latin-text {
        font-size: 1.3rem;
        font-weight: bold;
        color: #00aaff;
        margin-bottom: 0.5rem;
    }
    /* Teks Arti */
    .meaning-text {
        color: #ccc;
        font-size: 1rem;
        line-height: 1.5;
    }
    /* Badge Nomor */
    .number-badge {
        background-color: #00aaff;
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
    /* Info box untuk hasil pencarian */
    .search-info {
        background-color: #1e1e1e;
        padding: 10px 15px;
        border-radius: 8px;
        border-left: 4px solid #00aaff;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def clear_search():
    """Fungsi callback untuk mengosongkan input pencarian."""
    st.session_state.search_input = ""


def load_data():
    """Memuat data dari file JSON dengan notifikasi sementara."""
    try:
        # Placeholder untuk notifikasi
        placeholder = st.empty()
        placeholder.info("🔄 Memuat data Asmaul Husna...")
        
        # Buka file JSON
        with open('data/asmaul_husna.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Tampilkan pesan sukses dan hapus setelah 3 detik
        placeholder.success(f"✅ Berhasil memuat {len(data)} data Asmaul Husna")
        time.sleep(3)
        placeholder.empty()
        
        return data
    except FileNotFoundError:
        st.error("❌ File 'data/asmaul_husna.json' tidak ditemukan.")
        st.info("Pastikan file berada di folder 'data/asmaul_husna.json'")
        return []
    except Exception as e:
        st.error(f"❌ Terjadi error saat memuat data: {e}")
        return []


def filter_data(data, query):
    """Filter data berdasarkan query pencarian."""
    if not query:
        return data
    
    query = query.lower()
    return [
        item for item in data 
        if query in item.get('latin', '').lower() or 
           query in item.get('meaning', '').lower()
    ]


def display_asma_card(item):
    """Tampilkan satu kartu untuk setiap nama Asmaul Husna."""
    number = item.get('no', '')
    arabic = item.get('name', '')
    latin = item.get('latin', '')
    meaning = item.get('meaning', '')
    
    # HTML untuk kartu, menggunakan class dari CSS di atas
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
    """Tampilkan semua data Asmaul Husna dalam grid yang responsif."""
    if not data:
        st.warning("⚠️ Tidak ada hasil yang ditemukan.")
        return
    
    # Atur grid 3 kolom untuk desktop
    cols_per_row = 3
    for i in range(0, len(data), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            if i + j < len(data):
                with cols[j]:
                    display_asma_card(data[i + j])


def main():
    """Fungsi utama untuk menjalankan aplikasi."""
    st.title("🕌 Asmaul Husna - 99 Nama Allah")
    st.caption("Mengenal Nama-Nama Indah Allah SWT")
    st.markdown("---")
    
    # Memuat data
    asmaul_husna_data = load_data()
    if not asmaul_husna_data:
        return
    
    # Tampilkan search box dan tombol reset
    st.markdown("### 🔍 Cari nama Allah")
    col_search, col_button = st.columns([4, 1], vertical_alignment="center")
    
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
    
    # Filter data berdasarkan pencarian
    filtered_data = filter_data(asmaul_husna_data, search_query)
    
    # Tampilkan info hasil pencarian
    if search_query:
        st.markdown(f"""
        <div class="search-info">
            <strong>🔍 Hasil Pencarian:</strong> '{search_query}'<br>
            <strong>📊 Menampilkan:</strong> {len(filtered_data)} dari {len(asmaul_husna_data)} nama
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"**📊 Total: {len(asmaul_husna_data)} nama Allah**")
    
    # Tampilkan grid kartu
    display_asmaul_husna_grid(filtered_data)


# Jalankan aplikasi
if __name__ == "__main__":
    main()
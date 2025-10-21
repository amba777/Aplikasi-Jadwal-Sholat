import streamlit as st
import math
import requests

try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("⚠️ Plotly tidak terinstall. Kompas visual tidak tersedia.")

st.set_page_config(page_title="Arah Kiblat", layout="wide")

st.title("🕋 Arah Kiblat")

# CSS untuk styling modern
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1e3a8a;
        margin-bottom: 2rem;
    }
    .input-section {
        background-color: #262730;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border-left: 5px solid #00aaff;
    }
    .result-section {
        background-color: #262730;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border-left: 5px solid #ffa500;
    }
    .compass-section {
        background-color: #262730;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .qibla-direction {
        font-size: 4rem;
        font-weight: bold;
        color: #00aaff;
        text-align: center;
        margin: 1rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .degree-display {
        font-size: 3rem;
        font-weight: bold;
        color: #ffa500;
        text-align: center;
        margin: 1rem 0;
    }
    .instruction-box {
        background-color: #1e3a8a;
        padding: 1.5rem;
        border-radius: 10px;
        margin-top: 1rem;
    }
    .stButton button {
        width: 100%;
        height: 60px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 10px;
        border: none;
        background: linear-gradient(135deg, #00aaff, #0088cc);
        color: white;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    @media (max-width: 768px) {
        .qibla-direction {
            font-size: 2.5rem;
        }
        .degree-display {
            font-size: 2rem;
        }
        .input-section, .result-section, .compass-section {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Koordinat Ka'bah di Mekah
KAABA_LAT = 21.4225
KAABA_LON = 39.8262

def get_coordinates(city, country):
    """Mendapatkan koordinat dari nama kota dan negara dengan validasi ketat"""
    try:
        # Cari dengan query yang lebih spesifik
        query = f'{city},{country}'
        url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&addressdetails=1&limit=5"
        headers = {'User-Agent': 'AplikasiArahKiblat/1.0'}
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if not data or len(data) == 0:
            return None, None, f"Kota '{city}' tidak ditemukan di negara '{country}'"
        
        # Cari hasil yang benar-benar sesuai dengan negara yang diminta
        matched_result = None
        for result in data:
            address = result.get('address', {})
            result_country = address.get('country', '').lower()
            location_type = result.get('type', '')
            
            # Skip jika tipe lokasi adalah negara
            if location_type == 'country':
                continue
            
            # Cek apakah negara benar-benar cocok
            if result_country == country.lower() or country.lower() in result_country:
                matched_result = result
                break
        
        if not matched_result:
            return None, None, f"Kota '{city}' tidak ditemukan di negara '{country}'. Pastikan kota dan negara sesuai!"
        
        # Validasi tambahan: pastikan bukan negara
        if matched_result.get('type', '') == 'country':
            return None, None, f"'{city}' adalah nama negara, bukan kota. Harap masukkan nama kota yang valid"
        
        # Ambil koordinat
        lat = float(matched_result['lat'])
        lon = float(matched_result['lon'])
        
        # Validasi final: cek apakah alamat lengkap mengandung negara yang benar
        display_name = matched_result.get('display_name', '').lower()
        address = matched_result.get('address', {})
        result_country = address.get('country', '').lower()
        
        # Daftar negara yang umum dan variasinya
        country_variations = {
            'indonesia': ['indonesia'],
            'malaysia': ['malaysia'],
            'singapore': ['singapore', 'singapura'],
            'thailand': ['thailand'],
            'spain': ['spain', 'españa', 'spanyol'],
            'france': ['france', 'perancis'],
            'germany': ['germany', 'jerman', 'deutschland'],
            'italy': ['italy', 'italia'],
            'united kingdom': ['united kingdom', 'uk', 'inggris'],
            'united states': ['united states', 'usa', 'amerika'],
            'japan': ['japan', 'jepang', 'nihon'],
            'china': ['china', 'cina', 'tiongkok'],
            'india': ['india'],
            'australia': ['australia'],
            'saudi arabia': ['saudi arabia', 'arab saudi'],
            'egypt': ['egypt', 'mesir'],
            'turkey': ['turkey', 'turki', 'türkiye'],
        }
        
        # Normalisasi input negara
        country_lower = country.lower().strip()
        country_found = False
        
        # Cek apakah negara input cocok dengan hasil
        for key, variations in country_variations.items():
            if country_lower in variations or key == country_lower:
                if any(var in result_country or var in display_name for var in variations):
                    country_found = True
                    break
        
        # Fallback: cek langsung
        if not country_found:
            if country_lower in result_country or country_lower in display_name:
                country_found = True
        
        if not country_found:
            actual_country = address.get('country', 'Unknown')
            return None, None, f"Kota '{city}' ditemukan di negara '{actual_country}', bukan '{country}'. Harap periksa kembali!"
        
        return lat, lon, None
        
    except requests.exceptions.Timeout:
        return None, None, "Timeout - Koneksi terlalu lama. Silakan coba lagi"
    except requests.exceptions.RequestException as e:
        return None, None, f"Error koneksi: Tidak dapat terhubung ke server"
    except Exception as e:
        return None, None, f"Terjadi kesalahan: {str(e)}"

def calculate_qibla_direction(lat, lon):
    """Menghitung arah kiblat dari koordinat yang diberikan"""
    lat_k = math.radians(KAABA_LAT)
    lon_k = math.radians(KAABA_LON)
    lat_u = math.radians(lat)
    lon_u = math.radians(lon)
    
    delta_lon = lon_k - lon_u
    
    y = math.sin(delta_lon)
    x = math.cos(lat_u) * math.tan(lat_k) - math.sin(lat_u) * math.cos(delta_lon)
    
    bearing_rad = math.atan2(y, x)
    bearing_deg = math.degrees(bearing_rad)
    
    qibla_direction = (bearing_deg + 360) % 360
    return qibla_direction

def create_compass_figure(qibla_angle):
    """Membuat visualisasi kompas dengan Plotly"""
    if not PLOTLY_AVAILABLE:
        return None
    
    fig = go.Figure()
    
    # Background lingkaran kompas dengan gradient
    fig.add_trace(go.Scatterpolar(
        r=[1] * 360,
        theta=list(range(360)),
        mode='none',
        fill='toself',
        fillcolor='rgba(30, 58, 138, 0.8)',
        line=dict(color='rgba(255,255,255,0.3)', width=2),
        showlegend=False
    ))
    
    # Garis arah utama (Utara, Timur, Selatan, Barat)
    for angle, color in [(0, '#ff6b6b'), (90, '#4ecdc4'), (180, '#ffa500'), (270, '#cc65fe')]:
        fig.add_trace(go.Scatterpolar(
            r=[0, 0.9],
            theta=[angle, angle],
            mode='lines',
            line=dict(color=color, width=3, dash='dash'),
            showlegend=False
        ))
    
    # Label arah utama
    directions = ['UTARA', 'TIMUR', 'SELATAN', 'BARAT']
    for i, (angle, direction) in enumerate(zip([0, 90, 180, 270], directions)):
        fig.add_trace(go.Scatterpolar(
            r=[1.1],
            theta=[angle],
            mode='text',
            text=[direction],
            textfont=dict(size=16, color='white', family='Arial Black'),
            showlegend=False
        ))
    
    # Label arah sekunder
    secondary_directions = ['TL', 'TG', 'BD', 'BL']
    secondary_angles = [45, 135, 225, 315]
    for angle, direction in zip(secondary_angles, secondary_directions):
        fig.add_trace(go.Scatterpolar(
            r=[1.05],
            theta=[angle],
            mode='text',
            text=[direction],
            textfont=dict(size=12, color='#ccc'),
            showlegend=False
        ))
    
    # Jarum arah kiblat (panah besar)
    fig.add_trace(go.Scatterpolar(
        r=[0, 0.85, 0.85, 0],
        theta=[qibla_angle, qibla_angle-10, qibla_angle+10, qibla_angle],
        mode='lines+markers',
        fill='toself',
        fillcolor='rgba(0, 170, 255, 0.8)',
        line=dict(color='#00aaff', width=3),
        marker=dict(size=0),
        name='Arah Kiblat'
    ))
    
    # Lingkaran tengah
    fig.add_trace(go.Scatterpolar(
        r=[0.1],
        theta=[0],
        mode='markers',
        marker=dict(size=20, color='white', line=dict(color='#00aaff', width=3)),
        showlegend=False
    ))
    
    # Label KIBLAT di ujung jarum
    fig.add_trace(go.Scatterpolar(
        r=[0.95],
        theta=[qibla_angle],
        mode='text',
        text=['🕋'],
        textfont=dict(size=20),
        showlegend=False
    ))
    
    # Garis derajat
    for angle in range(0, 360, 30):
        fig.add_trace(go.Scatterpolar(
            r=[0.92, 1.0],
            theta=[angle, angle],
            mode='lines',
            line=dict(color='rgba(255,255,255,0.3)', width=1),
            showlegend=False
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=False, range=[0, 1.2]),
            angularaxis=dict(
                direction="clockwise",
                rotation=90,
                tickvals=list(range(0, 360, 30)),
                ticktext=[''] * 12,
                tickfont=dict(size=10, color='#ccc')
            ),
            bgcolor='rgba(0,0,0,0)',
            gridshape='circular',
        ),
        showlegend=False,
        height=500,
        width=500,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def get_direction_name(degrees):
    """Mengubah derajat menjadi nama arah mata angin lengkap"""
    directions = [
        (0, 22.5, "Utara"), 
        (22.5, 67.5, "Timur Laut"), 
        (67.5, 112.5, "Timur"),
        (112.5, 157.5, "Tenggara"), 
        (157.5, 202.5, "Selatan"), 
        (202.5, 247.5, "Barat Daya"),
        (247.5, 292.5, "Barat"), 
        (292.5, 337.5, "Barat Laut"), 
        (337.5, 360, "Utara")
    ]
    
    for start, end, name in directions:
        if start <= degrees < end:
            return name
    return "Utara"

# --- Input Section ---
st.markdown("""
<div class="input-section">
    <h3 style='color: #00aaff; margin-bottom: 1rem;'>📍 Masukkan Lokasi Anda</h3>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    city_input = st.text_input("**Kota**", "", placeholder="Contoh: Medan, Jakarta, Surabaya")
    st.caption("⚠️ Masukkan nama KOTA, bukan negara")
with col2:
    country_input = st.text_input("**Negara**", "", placeholder="Contoh: Indonesia, Malaysia")
    st.caption("⚠️ Masukkan nama NEGARA")

calculate_button = st.button("🧭 Hitung Arah Kiblat", use_container_width=True)

if calculate_button:
    if not city_input or not country_input:
        st.warning("⚠️ Harap masukkan nama Kota dan Negara.")
    else:
        with st.spinner("🔄 Mencari koordinat lokasi..."):
            user_lat, user_lon, error_msg = get_coordinates(city_input, country_input)
        
        if error_msg:
            st.error(f"❌ {error_msg}")
            st.info("""
            **💡 Panduan Pengisian:**
            
            ✅ **Contoh yang BENAR:**
            - Kota: `Jakarta` → Negara: `Indonesia`
            - Kota: `Medan` → Negara: `Indonesia`
            - Kota: `Kuala Lumpur` → Negara: `Malaysia`
            - Kota: `Madrid` → Negara: `Spain`
            - Kota: `Cairo` → Negara: `Egypt`
            
            ❌ **Contoh yang SALAH:**
            - Kota: `Madrid` → Negara: `Indonesia` ❌ (Madrid ada di Spain)
            - Kota: `Indonesia` → Negara: `Jakarta` ❌ (Terbalik)
            - Kota: `Spanyol` → Negara: `Indonesia` ❌ (Spanyol adalah negara)
            
            **Tips:**
            - Pastikan kota yang Anda masukkan **benar-benar ada** di negara tersebut
            - Gunakan ejaan bahasa Inggris untuk hasil terbaik
            - Jangan menukar posisi kota dan negara
            """)
        elif user_lat is not None and user_lon is not None:
            # --- Result Section ---
            st.markdown("""
            <div class="result-section">
                <h3 style='color: #ffa500; margin-bottom: 1rem;'>📊 Informasi Lokasi</h3>
            </div>
            """, unsafe_allow_html=True)
            
            col_info1, col_info2, col_info3 = st.columns(3)
            with col_info1:
                st.metric("📍 Kota", f"{city_input}")
                st.metric("🌍 Negara", f"{country_input}")
            with col_info2:
                st.metric("🌐 Lintang", f"{user_lat:.4f}°")
                st.metric("🌐 Bujur", f"{user_lon:.4f}°")
            with col_info3:
                st.metric("🕋 Ka'bah", "Mekah")
                st.metric("🇸🇦 Negara", "Arab Saudi")
            
            # Hitung arah kiblat
            qibla = calculate_qibla_direction(user_lat, user_lon)
            direction_name = get_direction_name(qibla)
            
            # --- Compass Section ---
            st.markdown("""
            <div class="compass-section">
                <h3 style='color: #00aaff; margin-bottom: 1rem;'>🧭 Arah Kiblat</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Tampilkan kompas yang dipercantik
            if PLOTLY_AVAILABLE:
                compass_fig = create_compass_figure(qibla)
                if compass_fig:
                    st.plotly_chart(compass_fig, use_container_width=True)
            else:
                st.info("📊 Install Plotly untuk menampilkan kompas visual: `pip install plotly`")
            
            # Tampilkan informasi arah
            col_deg, col_dir = st.columns(2)
            with col_deg:
                st.markdown(f'<div class="degree-display">{qibla:.2f}°</div>', unsafe_allow_html=True)
                st.caption("Dari Arah Utara Sejati")
            with col_dir:
                st.markdown(f'<div class="qibla-direction">🕋 {direction_name}</div>', unsafe_allow_html=True)
                st.caption("Arah Mata Angin")
            
            # --- Instruction Section ---
            st.markdown(f"""
            <div class="instruction-box">
                <h4 style='color: white; margin-bottom: 1rem;'>📝 Cara Menentukan Arah Kiblat:</h4>
                <ol style='color: #ccc; margin: 0; padding-left: 1.5rem;'>
                    <li>Berdiri menghadap <strong>Utara</strong> menggunakan kompas</li>
                    <li>Putar tubuh Anda sebesar <strong>{qibla:.2f}°</strong> searah jarum jam</li>
                    <li>Anda sekarang menghadap ke arah <strong>{direction_name}</strong> menuju Ka'bah</li>
                    <li>Gunakan patokan tetap untuk mempermudah penentuan arah</li>
                </ol>
                <p style='color: #ffa500; margin: 1rem 0 0 0; font-weight: bold;'>
                    🎯 Arah Kiblat Anda: <strong>{qibla:.2f}° dari Utara</strong> menuju <strong>{direction_name}</strong>
                </p>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            st.error(f"❌ Tidak dapat menemukan lokasi untuk '{city_input}, {country_input}'. Periksa kembali ejaan.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 14px;'>"
    "🕋 Arah Kiblat - Membantu Anda menemukan arah sholat yang tepat • "
    "Koordinat Ka'bah: 21.4225°N, 39.8262°E"
    "</div>",
    unsafe_allow_html=True
)

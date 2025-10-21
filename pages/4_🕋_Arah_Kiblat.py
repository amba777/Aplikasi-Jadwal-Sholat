import streamlit as st
import math
import requests

try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

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

# Database koordinat kota-kota populer (fallback jika API tidak bekerja)
CITY_COORDINATES = {
    # Indonesia
    'jakarta': (-6.2088, 106.8456),
    'surabaya': (-7.2575, 112.7521),
    'bandung': (-6.9175, 107.6191),
    'medan': (3.5952, 98.6722),
    'makassar': (-5.1477, 119.4327),
    'semarang': (-6.9667, 110.4167),
    'yogyakarta': (-7.7956, 110.3695),
    'denpasar': (-8.6705, 115.2126),
    'palembang': (-2.9910, 104.7574),
    'batam': (1.0456, 104.0305),
    
    # Internasional
    'tokyo': (35.6762, 139.6503),
    'osaka': (34.6937, 135.5023),
    'kyoto': (35.0116, 135.7681),
    'moscow': (55.7558, 37.6173),
    'moskow': (55.7558, 37.6173),
    'london': (51.5074, -0.1278),
    'paris': (48.8566, 2.3522),
    'berlin': (52.5200, 13.4050),
    'rome': (41.9028, 12.4964),
    'madrid': (40.4168, -3.7038),
    'new york': (40.7128, -74.0060),
    'los angeles': (34.0522, -118.2437),
    'chicago': (41.8781, -87.6298),
    'toronto': (43.6532, -79.3832),
    'sydney': (-33.8688, 151.2093),
    'melbourne': (-37.8136, 144.9631),
    'dubai': (25.2048, 55.2708),
    'riyadh': (24.7136, 46.6753),
    'cairo': (30.0444, 31.2357),
    'istanbul': (41.0082, 28.9784),
    'seoul': (37.5665, 126.9780),
    'beijing': (39.9042, 116.4074),
    'shanghai': (31.2304, 121.4737),
    'bangkok': (13.7563, 100.5018),
    'kuala lumpur': (3.1390, 101.6869),
    'singapore': (1.3521, 103.8198),
    'manila': (14.5995, 120.9842),
    'hanoi': (21.0278, 105.8342),
    'ho chi minh': (10.8231, 106.6297),
    'mumbai': (19.0760, 72.8777),
    'delhi': (28.7041, 77.1025),
    'dhaka': (23.8103, 90.4125),
    'karachi': (24.8607, 67.0011),
    'tehran': (35.6892, 51.3890),
    'baghdad': (33.3152, 44.3661),
    'jeddah': (21.4858, 39.1925),
    'mecca': (21.4225, 39.8262),
    'medina': (24.5247, 39.5692),
}

def normalize_input(text):
    """Normalisasi input menjadi lowercase dan hapus spasi berlebih"""
    return ' '.join(text.lower().strip().split())

def get_coordinates_fallback(city, country):
    """Mendapatkan koordinat dengan fallback ke database lokal"""
    try:
        city_normalized = normalize_input(city)
        country_normalized = normalize_input(country)
        
        # Coba dulu dari database lokal
        if city_normalized in CITY_COORDINATES:
            lat, lon = CITY_COORDINATES[city_normalized]
            return lat, lon, None
        
        # Jika tidak ada di database, coba API dengan approach yang lebih sederhana
        query = f"{city_normalized}, {country_normalized}"
        url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=1"
        
        headers = {
            'User-Agent': 'AplikasiArahKiblat/1.0 (https://example.com)'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                result = data[0]
                lat = float(result['lat'])
                lon = float(result['lon'])
                return lat, lon, None
            else:
                return None, None, f"Kota '{city}' tidak ditemukan. Coba gunakan nama kota yang lebih umum."
        else:
            return None, None, "Server sibuk. Silakan coba lagi nanti."
            
    except requests.exceptions.Timeout:
        return None, None, "Timeout - Koneksi terlalu lama"
    except requests.exceptions.RequestException:
        # Fallback ke kota utama jika API error
        major_cities = ['jakarta', 'surabaya', 'bandung', 'tokyo', 'london', 'singapore']
        for major_city in major_cities:
            if major_city in city_normalized:
                lat, lon = CITY_COORDINATES[major_city]
                return lat, lon, f"Menggunakan koordinat {major_city.title()} (fallback)"
        
        return None, None, "Tidak dapat terhubung ke server. Coba gunakan kota utama seperti Jakarta, Tokyo, London, dll."
    except Exception as e:
        return None, None, f"Error: {str(e)}"

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
    
    # Background lingkaran kompas
    fig.add_trace(go.Scatterpolar(
        r=[1] * 360,
        theta=list(range(360)),
        mode='none',
        fill='toself',
        fillcolor='rgba(30, 58, 138, 0.8)',
        line=dict(color='rgba(255,255,255,0.3)', width=2),
        showlegend=False
    ))
    
    # Garis arah utama
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
    
    # Jarum arah kiblat
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
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=False, range=[0, 1.2]),
            angularaxis=dict(
                direction="clockwise",
                rotation=90,
                tickvals=[],
                ticktext=[],
            ),
            bgcolor='rgba(0,0,0,0)',
        ),
        showlegend=False,
        height=500,
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
    city_input = st.text_input("**Kota**", "Jakarta", placeholder="Contoh: Jakarta, Tokyo, London")
    st.caption("⚠️ Masukkan nama KOTA (bisa huruf besar/kecil)")
    
    # Tampilkan contoh kota populer
    with st.expander("📋 Contoh Kota yang Didukung"):
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.write("**Indonesia:**")
            st.write("- Jakarta")
            st.write("- Surabaya")
            st.write("- Bandung")
            st.write("- Medan")
            st.write("- Makassar")
        with col_b:
            st.write("**Asia:**")
            st.write("- Tokyo")
            st.write("- Seoul")
            st.write("- Bangkok")
            st.write("- Singapore")
            st.write("- Kuala Lumpur")
        with col_c:
            st.write("**Internasional:**")
            st.write("- London")
            st.write("- Paris")
            st.write("- New York")
            st.write("- Sydney")
            st.write("- Dubai")
        
with col2:
    country_input = st.text_input("**Negara**", "Indonesia", placeholder="Contoh: Indonesia, Jepang, Amerika Serikat")
    st.caption("⚠️ Masukkan nama NEGARA (bisa huruf besar/kecil)")

calculate_button = st.button("🧭 Hitung Arah Kiblat", use_container_width=True)

if calculate_button:
    if not city_input or not country_input:
        st.warning("⚠️ Harap masukkan nama Kota dan Negara.")
    else:
        with st.spinner("🔄 Mencari koordinat lokasi..."):
            user_lat, user_lon, error_msg = get_coordinates_fallback(city_input, country_input)
        
        if error_msg and user_lat is None:
            st.error(f"❌ {error_msg}")
            
            # Berikan daftar kota yang didukung
            st.info("""
            **🏙️ Kota-kota yang didukung:**
            - **Indonesia**: Jakarta, Surabaya, Bandung, Medan, Makassar, Semarang, Yogyakarta, Denpasar, Palembang, Batam
            - **Asia**: Tokyo, Osaka, Kyoto, Seoul, Beijing, Shanghai, Bangkok, Kuala Lumpur, Singapore, Manila
            - **Timur Tengah**: Dubai, Riyadh, Cairo, Istanbul, Jeddah
            - **Eropa**: London, Paris, Berlin, Rome, Madrid, Moscow
            - **Amerika**: New York, Los Angeles, Chicago, Toronto
            - **Oseania**: Sydney, Melbourne
            
            **💡 Tips:** Gunakan nama kota dari daftar di atas untuk hasil terbaik.
            """)
        else:
            if error_msg and user_lat is not None:
                st.warning(f"⚠️ {error_msg}")
            
            # --- Result Section ---
            st.markdown("""
            <div class="result-section">
                <h3 style='color: #ffa500; margin-bottom: 1rem;'>📊 Informasi Lokasi</h3>
            </div>
            """, unsafe_allow_html=True)
            
            col_info1, col_info2, col_info3 = st.columns(3)
            with col_info1:
                st.metric("📍 Kota", f"{city_input.title()}")
                st.metric("🌍 Negara", f"{country_input.title()}")
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

# Informasi default
else:
    st.markdown("""
    <div style='background: rgba(0, 170, 255, 0.1); padding: 1.5rem; border-radius: 10px; margin: 2rem 0;'>
        <h4 style='color: #00aaff; margin-bottom: 1rem;'>💡 Cara Menggunakan:</h4>
        <ul style='color: #ccc; margin: 0;'>
            <li>Masukkan <strong>nama kota</strong> dan <strong>nama negara</strong> tempat Anda berada</li>
            <li>Gunakan kota-kota utama untuk hasil terbaik</li>
            <li>Bisa menggunakan <strong>huruf besar</strong> atau <strong>huruf kecil</strong></li>
            <li>Klik tombol <strong>"Hitung Arah Kiblat"</strong> untuk melihat hasil</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 14px;'>"
    "🕋 Arah Kiblat - Membantu Anda menemukan arah sholat yang tepat • "
    "Koordinat Ka'bah: 21.4225°N, 39.8262°E"
    "</div>",
    unsafe_allow_html=True
)

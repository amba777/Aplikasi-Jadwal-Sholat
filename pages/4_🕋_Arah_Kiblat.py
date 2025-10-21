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

# Daftar negara dan variasi ejaan dalam bahasa Indonesia
COUNTRY_VARIATIONS = {
    'indonesia': ['indonesia', 'indonesian', 'republik indonesia', 'ri'],
    'malaysia': ['malaysia', 'malaysian', 'malaysia'],
    'singapore': ['singapore', 'singapura', 'singapura', 'republik singapura'],
    'thailand': ['thailand', 'thai', 'muang thai', 'kerajaan thailand'],
    'brunei': ['brunei', 'brunei darussalam', 'negara brunei darussalam'],
    'filipina': ['filipina', 'philippines', 'pilipinas', 'republik filipina'],
    'vietnam': ['vietnam', 'viet nam', 'republik sosialis vietnam'],
    'kamboja': ['kamboja', 'cambodia', 'kampuchea', 'kerajaan kamboja'],
    'laos': ['laos', 'lao', 'republik demokratik rakyat laos'],
    'myanmar': ['myanmar', 'burma', 'republik myanmar'],
    
    # Timur Tengah
    'saudi arabia': ['saudi arabia', 'arab saudi', 'kerajaan arab saudi', 'saudi'],
    'united arab emirates': ['united arab emirates', 'uae', 'uni emirat arab', 'emirat arab'],
    'qatar': ['qatar', 'qatar', 'negara qatar'],
    'kuwait': ['kuwait', 'kuwait', 'negara kuwait'],
    'oman': ['oman', 'oman', 'kesultanan oman'],
    'yaman': ['yaman', 'yemen', 'republik yaman'],
    'mesir': ['mesir', 'egypt', 'misr', 'republik arab mesir'],
    'turki': ['turki', 'turkey', 'türkiye', 'republik turki'],
    'iran': ['iran', 'iran', 'republik islam iran'],
    'irak': ['irak', 'iraq', 'republik irak'],
    
    # Asia Timur
    'jepang': ['jepang', 'japan', 'nippon', 'nihon'],
    'korea selatan': ['korea selatan', 'south korea', 'republik korea'],
    'korea utara': ['korea utara', 'north korea', 'republik rakyat demokratik korea'],
    'china': ['china', 'cina', 'tiongkok', 'republik rakyat china'],
    'taiwan': ['taiwan', 'taiwan', 'republik china'],
    'hong kong': ['hong kong', 'hongkong', 'xianggang'],
    'macau': ['macau', 'macao', 'aomen'],
    
    # Asia Selatan
    'india': ['india', 'india', 'bharat', 'republik india'],
    'pakistan': ['pakistan', 'pakistan', 'republik islam pakistan'],
    'bangladesh': ['bangladesh', 'bangladesh', 'republik rakyat bangladesh'],
    'sri lanka': ['sri lanka', 'sri lanka', 'republik sosialis demokratik sri lanka'],
    'nepal': ['nepal', 'nepal', 'republik federal demokratik nepal'],
    'bhutan': ['bhutan', 'bhutan', 'kerajaan bhutan'],
    'maladewa': ['maladewa', 'maldives', 'republik maladewa'],
    
    # Eropa
    'inggris': ['inggris', 'united kingdom', 'uk', 'britania raya', 'british'],
    'jerman': ['jerman', 'germany', 'deutschland', 'republik federal jerman'],
    'perancis': ['perancis', 'france', 'republik perancis'],
    'italia': ['italia', 'italy', 'italia', 'republik italia'],
    'spanyol': ['spanyol', 'spain', 'españa', 'kerajaan spanyol'],
    'belanda': ['belanda', 'netherlands', 'nederland', 'kerajaan belanda'],
    'belgia': ['belgia', 'belgium', 'belgique', 'kerajaan belgia'],
    'swiss': ['swiss', 'switzerland', 'schweiz', 'konfederasi swiss'],
    'swedia': ['swedia', 'sweden', 'sverige', 'kerajaan swedia'],
    'norwegia': ['norwegia', 'norway', 'norge', 'kerajaan norwegia'],
    'denmark': ['denmark', 'denmark', 'danmark', 'kerajaan denmark'],
    'finlandia': ['finlandia', 'finland', 'suomi', 'republik finlandia'],
    'rusia': ['rusia', 'russia', 'russian federation', 'federasi rusia'],
    
    # Amerika
    'amerika serikat': ['amerika serikat', 'united states', 'usa', 'us', 'amerika'],
    'kanada': ['kanada', 'canada', 'kanada'],
    'mexico': ['mexico', 'mexico', 'meksiko', 'estados unidos mexicanos'],
    'brazil': ['brazil', 'brasil', 'republik federal brasil'],
    'argentina': ['argentina', 'argentina', 'republik argentina'],
    'chile': ['chile', 'chile', 'republik chile'],
    
    # Afrika
    'afrika selatan': ['afrika selatan', 'south africa', 'republik afrika selatan'],
    'nigeria': ['nigeria', 'nigeria', 'republik federal nigeria'],
    'kenya': ['kenya', 'kenya', 'republik kenya'],
    'ethiopia': ['ethiopia', 'ethiopia', 'republik federal demokratik ethiopia'],
    'maroko': ['maroko', 'morocco', 'kerajaan maroko'],
    'aljazair': ['aljazair', 'algeria', 'republik demokratik rakyat aljazair'],
    
    # Oseania
    'australia': ['australia', 'australia', 'commonwealth of australia'],
    'selandia baru': ['selandia baru', 'new zealand', 'aotearoa'],
}

# Daftar kota utama di Indonesia
MAJOR_CITIES = {
    'indonesia': [
        'jakarta', 'surabaya', 'bandung', 'medan', 'semarang', 'makassar', 'palembang',
        'depok', 'tangerang', 'bekasi', 'bogor', 'malang', 'yogyakarta', 'surakarta',
        'denpasar', 'batam', 'pekanbaru', 'bandar lampung', 'padang', 'banjarmasin',
        'samarinda', 'manado', 'balikpapan', 'jambi', 'pontianak', 'mataram', 'kupang',
        'bengkulu', 'palu', 'ambon', 'ternate', 'gorontalo', 'mamuju', 'kendari',
        'jayapura', 'manokwari', 'sorong', 'merauke', 'biak', 'nabire'
    ]
}

def normalize_country_name(country_input):
    """Normalisasi nama negara ke bentuk standar"""
    country_lower = country_input.lower().strip()
    
    for standard_name, variations in COUNTRY_VARIATIONS.items():
        if country_lower in variations:
            return standard_name
    
    # Jika tidak ditemukan, kembalikan input asli
    return country_input.lower()

def get_coordinates(city, country):
    """Mendapatkan koordinat dari nama kota dan negara dengan validasi yang lebih baik"""
    try:
        # Normalisasi nama negara
        normalized_country = normalize_country_name(country)
        
        # Cari dengan query yang lebih spesifik
        query = f'{city}, {normalized_country}'
        url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&addressdetails=1&limit=5"
        headers = {'User-Agent': 'AplikasiArahKiblat/1.0 (contact: admin@example.com)'}
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if not data or len(data) == 0:
            # Coba lagi dengan query yang lebih umum
            query_fallback = f'{city}'
            url_fallback = f"https://nominatim.openstreetmap.org/search?q={query_fallback}&format=json&addressdetails=1&limit=10"
            response_fallback = requests.get(url_fallback, headers=headers, timeout=10)
            data_fallback = response_fallback.json()
            
            if not data_fallback:
                return None, None, f"Lokasi '{city}' tidak ditemukan"
            
            # Cari di hasil fallback yang sesuai dengan negara
            for result in data_fallback:
                address = result.get('address', {})
                result_country = address.get('country', '').lower()
                
                # Cek apakah negara cocok
                country_found = False
                for standard_name, variations in COUNTRY_VARIATIONS.items():
                    if normalized_country == standard_name:
                        if any(var in result_country for var in variations):
                            country_found = True
                            break
                
                if country_found:
                    lat = float(result['lat'])
                    lon = float(result['lon'])
                    return lat, lon, None
            
            return None, None, f"Kota '{city}' tidak ditemukan di negara '{country}'"
        
        # Ambil hasil pertama yang paling relevan
        first_result = data[0]
        lat = float(first_result['lat'])
        lon = float(first_result['lon'])
        
        # Validasi negara dari hasil
        address = first_result.get('address', {})
        result_country = address.get('country', '').lower()
        
        # Cek apakah negara hasil cocok dengan input
        country_match = False
        for standard_name, variations in COUNTRY_VARIATIONS.items():
            if normalized_country == standard_name:
                if any(var in result_country for var in variations):
                    country_match = True
                    break
        
        if not country_match:
            actual_country = address.get('country', 'Tidak Diketahui')
            return None, None, f"Kota '{city}' ditemukan di '{actual_country}', bukan '{country}'"
        
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
    city_input = st.text_input("**Kota**", "", placeholder="Contoh: Jakarta, Medan, Surabaya")
    st.caption("⚠️ Masukkan nama KOTA (bisa huruf besar/kecil)")
    
    # Tampilkan contoh kota populer
    with st.expander("📋 Contoh Kota Populer"):
        st.write("**Indonesia:** Jakarta, Surabaya, Bandung, Medan, Makassar")
        st.write("**Malaysia:** Kuala Lumpur, Penang, Johor Bahru")
        st.write("**Singapore:** Singapore")
        st.write("**Timur Tengah:** Dubai, Riyadh, Istanbul, Cairo")
        
with col2:
    country_input = st.text_input("**Negara**", "", placeholder="Contoh: Indonesia, Malaysia, Singapore")
    st.caption("⚠️ Masukkan nama NEGARA (bisa huruf besar/kecil)")
    
    # Tampilkan contoh negara
    with st.expander("🌍 Contoh Negara"):
        col_a, col_b = st.columns(2)
        with col_a:
            st.write("**Asia:**")
            st.write("- Indonesia")
            st.write("- Malaysia") 
            st.write("- Singapore")
            st.write("- Thailand")
            st.write("- Jepang")
        with col_b:
            st.write("**Lainnya:**")
            st.write("- Arab Saudi")
            st.write("- Amerika Serikat")
            st.write("- Inggris")
            st.write("- Australia")

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
            **💡 Tips Pencarian:**
            - **Kota**: Jakarta, Medan, Surabaya, Bandung, Makassar, dll.
            - **Negara**: Indonesia, Malaysia, Singapore, Thailand, Jepang, Arab Saudi, dll.
            - Bisa menggunakan huruf **BESAR** atau **kecil**
            - Untuk negara bisa menggunakan ejaan Indonesia atau Inggris
            - Contoh: 
              - Kota: `jakarta`, Negara: `indonesia` 
              - Kota: `dubai`, Negara: `united arab emirates`
              - Kota: `tokyo`, Negara: `jepang`
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
            
        else:
            st.error(f"❌ Tidak dapat menemukan lokasi untuk '{city_input}, {country_input}'. Periksa kembali ejaan.")

# Informasi default
else:
    st.markdown("""
    <div style='background: rgba(0, 170, 255, 0.1); padding: 1.5rem; border-radius: 10px; margin: 2rem 0;'>
        <h4 style='color: #00aaff; margin-bottom: 1rem;'>💡 Cara Menggunakan:</h4>
        <ul style='color: #ccc; margin: 0;'>
            <li>Masukkan <strong>nama kota</strong> dan <strong>nama negara</strong> tempat Anda berada</li>
            <li>Bisa menggunakan <strong>huruf besar</strong> atau <strong>huruf kecil</strong></li>
            <li>Untuk negara bisa menggunakan ejaan <strong>Indonesia</strong> atau <strong>Inggris</strong></li>
            <li>Contoh: Kota: <code>jakarta</code>, Negara: <code>indonesia</code></li>
            <li>Klik tombol <strong>"Hitung Arah Kiblat"</strong> untuk melihat hasil</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 14px;'>"
    "🕋 Arah Kiblat - Membantu Anda menemukan arah sholat yang tepat • "
    "Koordinat Ka'bah: 21.4225°N, 39.8262°E • "
    "Mendukung 60+ negara di seluruh dunia"
    "</div>",
    unsafe_allow_html=True
)

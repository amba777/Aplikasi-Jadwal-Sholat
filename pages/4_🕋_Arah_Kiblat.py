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

# Daftar 100 negara terkenal dari berbagai benua dengan variasi ejaan
COUNTRY_MAPPING = {
    # Asia (30 negara)
    'indonesia': ['indonesia', 'indonesian', 'republik indonesia', 'ri'],
    'malaysia': ['malaysia', 'malaysian', 'malaysia'],
    'singapore': ['singapore', 'singapura', 'singapura', 'republik singapura'],
    'thailand': ['thailand', 'thai', 'muang thai', 'kerajaan thailand'],
    'vietnam': ['vietnam', 'viet nam', 'republik sosialis vietnam'],
    'filipina': ['filipina', 'philippines', 'pilipinas', 'republik filipina'],
    'myanmar': ['myanmar', 'burma', 'republik myanmar'],
    'kamboja': ['kamboja', 'cambodia', 'kampuchea', 'kerajaan kamboja'],
    'laos': ['laos', 'lao', 'republik demokratik rakyat laos'],
    'brunei': ['brunei', 'brunei darussalam', 'negara brunei darussalam'],
    'timor leste': ['timor leste', 'east timor', 'timor timur'],
    'jepang': ['jepang', 'japan', 'nippon', 'nihon', 'jepun', 'japang'],
    'korea selatan': ['korea selatan', 'south korea', 'republik korea', 'korea'],
    'korea utara': ['korea utara', 'north korea', 'republik rakyat demokratik korea'],
    'china': ['china', 'cina', 'tiongkok', 'republik rakyat china', 'tiongkok'],
    'taiwan': ['taiwan', 'taiwan', 'republik china'],
    'hong kong': ['hong kong', 'hongkong', 'xianggang'],
    'macau': ['macau', 'macao', 'aomen'],
    'mongolia': ['mongolia', 'mongolia', 'mongol uls'],
    'india': ['india', 'india', 'bharat', 'republik india'],
    'pakistan': ['pakistan', 'pakistan', 'republik islam pakistan'],
    'bangladesh': ['bangladesh', 'bangladesh', 'republik rakyat bangladesh'],
    'sri lanka': ['sri lanka', 'sri lanka', 'republik sosialis demokratik sri lanka'],
    'nepal': ['nepal', 'nepal', 'republik federal demokratik nepal'],
    'bhutan': ['bhutan', 'bhutan', 'kerajaan bhutan'],
    'maladewa': ['maladewa', 'maldives', 'republik maladewa'],
    'afghanistan': ['afghanistan', 'afghanistan', 'republik islam afghanistan'],
    'bangladesh': ['bangladesh', 'bangladesh', 'republik rakyat bangladesh'],
    'iran': ['iran', 'iran', 'republik islam iran'],
    'irak': ['irak', 'iraq', 'republik irak'],
    
    # Timur Tengah (20 negara)
    'saudi arabia': ['saudi arabia', 'arab saudi', 'kerajaan arab saudi', 'saudi'],
    'united arab emirates': ['united arab emirates', 'uae', 'uni emirat arab', 'emirat arab'],
    'qatar': ['qatar', 'qatar', 'negara qatar'],
    'kuwait': ['kuwait', 'kuwait', 'negara kuwait'],
    'oman': ['oman', 'oman', 'kesultanan oman'],
    'yaman': ['yaman', 'yemen', 'republik yaman'],
    'bahrain': ['bahrain', 'bahrain', 'kerajaan bahrain'],
    'yordania': ['yordania', 'jordan', 'kerajaan yordania'],
    'lebanon': ['lebanon', 'lebanon', 'republik lebanon'],
    'suriah': ['suriah', 'syria', 'republik arab suriah'],
    'palestina': ['palestina', 'palestine', 'negara palestina'],
    'israel': ['israel', 'israel', 'negara israel'],
    'turki': ['turki', 'turkey', 'türkiye', 'republik turki'],
    'mesir': ['mesir', 'egypt', 'misr', 'republik arab mesir'],
    'libya': ['libya', 'libya', 'negara libya'],
    'tunisia': ['tunisia', 'tunisia', 'republik tunisia'],
    'aljazair': ['aljazair', 'algeria', 'republik demokratik rakyat aljazair'],
    'maroko': ['maroko', 'morocco', 'kerajaan maroko'],
    'sudan': ['sudan', 'sudan', 'republik sudan'],
    'sudan selatan': ['sudan selatan', 'south sudan', 'republik sudan selatan'],
    
    # Eropa (25 negara)
    'rusia': ['rusia', 'russia', 'russian federation', 'federasi rusia', 'rusi'],
    'ukraina': ['ukraina', 'ukraine', 'ukraina'],
    'belarus': ['belarus', 'belarus', 'republik belarus'],
    'polandia': ['polandia', 'poland', 'republik polandia'],
    'jerman': ['jerman', 'germany', 'deutschland', 'republik federal jerman'],
    'perancis': ['perancis', 'france', 'republik perancis', 'prancis'],
    'italia': ['italia', 'italy', 'italia', 'republik italia'],
    'spanyol': ['spanyol', 'spain', 'españa', 'kerajaan spanyol'],
    'portugal': ['portugal', 'portugal', 'republik portugal'],
    'inggris': ['inggris', 'united kingdom', 'uk', 'britania raya', 'british', 'england'],
    'irlandia': ['irlandia', 'ireland', 'republik irlandia'],
    'belanda': ['belanda', 'netherlands', 'nederland', 'kerajaan belanda'],
    'belgia': ['belgia', 'belgium', 'belgique', 'kerajaan belgia'],
    'swiss': ['swiss', 'switzerland', 'schweiz', 'konfederasi swiss'],
    'austria': ['austria', 'austria', 'republik austria'],
    'swedia': ['swedia', 'sweden', 'sverige', 'kerajaan swedia'],
    'norwegia': ['norwegia', 'norway', 'norge', 'kerajaan norwegia'],
    'denmark': ['denmark', 'denmark', 'danmark', 'kerajaan denmark'],
    'finlandia': ['finlandia', 'finland', 'suomi', 'republik finlandia'],
    'islandia': ['islandia', 'iceland', 'island', 'republik islandia'],
    'yunani': ['yunani', 'greece', 'hellas', 'republik helenik'],
    'turki': ['turki', 'turkey', 'türkiye', 'republik turki'],
    'bulgaria': ['bulgaria', 'bulgaria', 'republik bulgaria'],
    'romania': ['romania', 'romania', 'rumania'],
    'hungaria': ['hungaria', 'hungary', 'magyarország', 'republik hungaria'],
    
    # Amerika (15 negara)
    'amerika serikat': ['amerika serikat', 'united states', 'usa', 'us', 'amerika'],
    'kanada': ['kanada', 'canada', 'kanada'],
    'mexico': ['mexico', 'mexico', 'meksiko', 'estados unidos mexicanos'],
    'brazil': ['brazil', 'brasil', 'republik federal brasil'],
    'argentina': ['argentina', 'argentina', 'republik argentina'],
    'chile': ['chile', 'chile', 'republik chile'],
    'kolombia': ['kolombia', 'colombia', 'republik kolombia'],
    'peru': ['peru', 'peru', 'republik peru'],
    'venezuela': ['venezuela', 'venezuela', 'republik bolivar venezuela'],
    'ecuador': ['ecuador', 'ecuador', 'republik ecuador'],
    'bolivia': ['bolivia', 'bolivia', 'negara plurinasional bolivia'],
    'paraguay': ['paraguay', 'paraguay', 'republik paraguay'],
    'uruguay': ['uruguay', 'uruguay', 'republik timur uruguay'],
    'kosta rika': ['kosta rika', 'costa rica', 'republik kosta rika'],
    'panama': ['panama', 'panama', 'republik panama'],
    
    # Afrika (20 negara)
    'afrika selatan': ['afrika selatan', 'south africa', 'republik afrika selatan'],
    'nigeria': ['nigeria', 'nigeria', 'republik federal nigeria'],
    'kenya': ['kenya', 'kenya', 'republik kenya'],
    'ethiopia': ['ethiopia', 'ethiopia', 'republik federal demokratik ethiopia'],
    'mesir': ['mesir', 'egypt', 'misr', 'republik arab mesir'],
    'maroko': ['maroko', 'morocco', 'kerajaan maroko'],
    'aljazair': ['aljazair', 'algeria', 'republik demokratik rakyat aljazair'],
    'tunisia': ['tunisia', 'tunisia', 'republik tunisia'],
    'ghana': ['ghana', 'ghana', 'republik ghana'],
    'tanzania': ['tanzania', 'tanzania', 'republik bersatu tanzania'],
    'uganda': ['uganda', 'uganda', 'republik uganda'],
    'zimbabwe': ['zimbabwe', 'zimbabwe', 'republik zimbabwe'],
    'zambia': ['zambia', 'zambia', 'republik zambia'],
    'senegal': ['senegal', 'senegal', 'republik senegal'],
    'kamerun': ['kamerun', 'cameroon', 'republik kamerun'],
    'pantai gading': ['pantai gading', 'ivory coast', "côte d'ivoire", 'republik pantai gading'],
    'mali': ['mali', 'mali', 'republik mali'],
    'sudan': ['sudan', 'sudan', 'republik sudan'],
    'angola': ['angola', 'angola', 'republik angola'],
    'mozambik': ['mozambik', 'mozambique', 'republik mozambik'],
    
    # Oseania (10 negara)
    'australia': ['australia', 'australia', 'commonwealth of australia'],
    'selandia baru': ['selandia baru', 'new zealand', 'aotearoa'],
    'papua nugini': ['papua nugini', 'papua new guinea', 'papua niugini'],
    'fiji': ['fiji', 'fiji', 'republik fiji'],
    'samoa': ['samoa', 'samoa', 'negara merdeka samoa'],
    'tonga': ['tonga', 'tonga', 'kerajaan tonga'],
    'kepulauan solomon': ['kepulauan solomon', 'solomon islands', 'kepulauan solomon'],
    'vanuatu': ['vanuatu', 'vanuatu', 'republik vanuatu'],
    'kiribati': ['kiribati', 'kiribati', 'republik kiribati'],
    'mikronesia': ['mikronesia', 'micronesia', 'negara federasi mikronesia'],
}

# Mapping kota-kota internasional utama
CITY_COUNTRY_MAPPING = {
    'tokyo': 'jepang',
    'osaka': 'jepang', 
    'kyoto': 'jepang',
    'yokohama': 'jepang',
    'nagoya': 'jepang',
    'sapporo': 'jepang',
    'moscow': 'rusia',
    'moskwa': 'rusia',
    'moskow': 'rusia',
    'saint petersburg': 'rusia',
    'novosibirsk': 'rusia',
    'kyiv': 'ukraina',
    'kiev': 'ukraina',
    'kharkiv': 'ukraina',
    'odessa': 'ukraina',
    'jakarta': 'indonesia',
    'surabaya': 'indonesia',
    'bandung': 'indonesia',
    'medan': 'indonesia',
    'makassar': 'indonesia',
    'semarang': 'indonesia',
    'london': 'inggris',
    'manchester': 'inggris',
    'birmingham': 'inggris',
    'paris': 'perancis',
    'marseille': 'perancis',
    'lyon': 'perancis',
    'berlin': 'jerman',
    'hamburg': 'jerman',
    'munich': 'jerman',
    'rome': 'italia',
    'milan': 'italia',
    'naples': 'italia',
    'madrid': 'spanyol',
    'barcelona': 'spanyol',
    'valencia': 'spanyol',
    'new york': 'amerika serikat',
    'los angeles': 'amerika serikat',
    'chicago': 'amerika serikat',
    'houston': 'amerika serikat',
    'phoenix': 'amerika serikat',
    'toronto': 'kanada',
    'vancouver': 'kanada',
    'montreal': 'kanada',
    'sydney': 'australia',
    'melbourne': 'australia',
    'brisbane': 'australia',
    'dubai': 'united arab emirates',
    'abu dhabi': 'united arab emirates',
    'riyadh': 'saudi arabia',
    'jeddah': 'saudi arabia',
    'cairo': 'mesir',
    'alexandria': 'mesir',
    'istanbul': 'turki',
    'ankara': 'turki',
    'izmir': 'turki',
    'seoul': 'korea selatan',
    'busan': 'korea selatan',
    'incheon': 'korea selatan',
    'beijing': 'china',
    'shanghai': 'china',
    'guangzhou': 'china',
    'mumbai': 'india',
    'delhi': 'india',
    'bangalore': 'india',
    'bangkok': 'thailand',
    'phuket': 'thailand',
    'chiang mai': 'thailand',
    'kuala lumpur': 'malaysia',
    'penang': 'malaysia',
    'johor bahru': 'malaysia',
}

def normalize_input(text):
    """Normalisasi input menjadi lowercase dan hapus spasi berlebih"""
    return ' '.join(text.lower().strip().split())

def correct_country_name(country_input):
    """Koreksi otomatis nama negara berdasarkan mapping"""
    normalized = normalize_input(country_input)
    
    # Cari exact match terlebih dahulu
    for correct_name, variations in COUNTRY_MAPPING.items():
        if normalized in variations:
            return correct_name
    
    # Cari partial match
    for correct_name, variations in COUNTRY_MAPPING.items():
        for variation in variations:
            if normalized in variation or variation in normalized:
                return correct_name
    
    return normalized  # Kembalikan input asli jika tidak dikenali

def get_coordinates_simple(city, country):
    """Mendapatkan koordinat dengan pendekatan yang lebih sederhana dan robust"""
    try:
        # Normalisasi input
        city_clean = normalize_input(city)
        country_clean = correct_country_name(country)
        
        # Coba beberapa variasi query
        queries = [
            f"{city_clean}, {country_clean}",
            f"{city_clean}",
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        for query in queries:
            url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=1"
            
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        result = data[0]
                        lat = float(result['lat'])
                        lon = float(result['lon'])
                        return lat, lon, None
            except:
                continue
        
        return None, None, f"Tidak dapat menemukan koordinat untuk '{city}'. Coba gunakan nama kota yang lebih spesifik."
        
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
    city_input = st.text_input("**Kota**", "", placeholder="Contoh: Tokyo, Jakarta, London")
    st.caption("⚠️ Masukkan nama KOTA (bisa huruf besar/kecil)")
    
    # Tampilkan contoh kota populer
    with st.expander("📋 Contoh Kota Populer di Seluruh Dunia"):
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.write("**Asia:**")
            st.write("- Tokyo (Jepang)")
            st.write("- Jakarta (Indonesia)")
            st.write("- Seoul (Korea)")
            st.write("- Bangkok (Thailand)")
        with col_b:
            st.write("**Eropa:**")
            st.write("- London (Inggris)")
            st.write("- Paris (Perancis)")
            st.write("- Berlin (Jerman)")
            st.write("- Moscow (Rusia)")
        with col_c:
            st.write("**Lainnya:**")
            st.write("- New York (USA)")
            st.write("- Sydney (Australia)")
            st.write("- Dubai (UAE)")
            st.write("- Cairo (Mesir)")
        
with col2:
    country_input = st.text_input("**Negara**", "", placeholder="Contoh: Jepang, Indonesia, Amerika Serikat")
    st.caption("⚠️ Masukkan nama NEGARA (bisa huruf besar/kecil)")
    
    # Tampilkan contoh negara
    with st.expander("🌍 100+ Negara yang Didukung"):
        tab1, tab2, tab3, tab4 = st.tabs(["Asia", "Eropa", "Amerika", "Afrika & Oseania"])
        
        with tab1:
            st.write("**Asia (30 negara):**")
            col1, col2 = st.columns(2)
            with col1:
                st.write("- Indonesia")
                st.write("- Malaysia")
                st.write("- Singapore")
                st.write("- Thailand")
                st.write("- Vietnam")
                st.write("- Filipina")
                st.write("- Jepang")
                st.write("- Korea Selatan")
                st.write("- China")
                st.write("- India")
            with col2:
                st.write("- Pakistan")
                st.write("- Bangladesh")
                st.write("- Sri Lanka")
                st.write("- Nepal")
                st.write("- Iran")
                st.write("- Irak")
                st.write("- Arab Saudi")
                st.write("- Turki")
                st.write("- Uni Emirat Arab")
                st.write("- Qatar")
                
        with tab2:
            st.write("**Eropa (25 negara):**")
            col1, col2 = st.columns(2)
            with col1:
                st.write("- Inggris")
                st.write("- Perancis")
                st.write("- Jerman")
                st.write("- Italia")
                st.write("- Spanyol")
                st.write("- Rusia")
                st.write("- Ukraina")
                st.write("- Belanda")
                st.write("- Belgia")
                st.write("- Swiss")
            with col2:
                st.write("- Swedia")
                st.write("- Norwegia")
                st.write("- Denmark")
                st.write("- Finlandia")
                st.write("- Polandia")
                st.write("- Austria")
                st.write("- Yunani")
                st.write("- Portugal")
                st.write("- Irlandia")
                st.write("- Hungaria")
                
        with tab3:
            st.write("**Amerika (15 negara):**")
            col1, col2 = st.columns(2)
            with col1:
                st.write("- Amerika Serikat")
                st.write("- Kanada")
                st.write("- Mexico")
                st.write("- Brazil")
                st.write("- Argentina")
                st.write("- Chile")
                st.write("- Kolombia")
            with col2:
                st.write("- Peru")
                st.write("- Venezuela")
                st.write("- Ecuador")
                st.write("- Bolivia")
                st.write("- Paraguay")
                st.write("- Uruguay")
                st.write("- Kosta Rika")
                
        with tab4:
            st.write("**Afrika & Oseania (30 negara):**")
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Afrika:**")
                st.write("- Afrika Selatan")
                st.write("- Nigeria")
                st.write("- Kenya")
                st.write("- Ethiopia")
                st.write("- Mesir")
                st.write("- Maroko")
                st.write("- Tunisia")
                st.write("- Ghana")
                st.write("- Tanzania")
                st.write("- Senegal")
            with col2:
                st.write("**Oseania:**")
                st.write("- Australia")
                st.write("- Selandia Baru")
                st.write("- Papua Nugini")
                st.write("- Fiji")
                st.write("- Samoa")
                st.write("- Tonga")
                st.write("- Kep. Solomon")
                st.write("- Vanuatu")
                st.write("- Kiribati")
                st.write("- Mikronesia")

calculate_button = st.button("🧭 Hitung Arah Kiblat", use_container_width=True)

if calculate_button:
    if not city_input or not country_input:
        st.warning("⚠️ Harap masukkan nama Kota dan Negara.")
    else:
        with st.spinner("🔄 Mencari koordinat lokasi..."):
            user_lat, user_lon, error_msg = get_coordinates_simple(city_input, country_input)
        
        if error_msg:
            st.error(f"❌ {error_msg}")
            
            # Berikan saran berdasarkan kota
            normalized_city = normalize_input(city_input)
            if normalized_city in CITY_COUNTRY_MAPPING:
                suggested_country = CITY_COUNTRY_MAPPING[normalized_city]
                st.info(f"💡 **Saran:** Kota '{city_input}' biasanya berada di **{suggested_country.title()}**. Coba gunakan negara tersebut.")
            
            st.info("""
            **💡 Tips Pencarian:**
            - Gunakan **nama kota yang benar** dan **spesifik**
            - Gunakan **nama negara dalam bahasa Indonesia** atau **Inggris**
            - Contoh kombinasi yang bekerja:
              - `Tokyo, Jepang` atau `Tokyo, Japan`
              - `Moscow, Rusia` atau `Moscow, Russia`  
              - `Kyiv, Ukraina` atau `Kyiv, Ukraine`
              - `Jakarta, Indonesia`
              - `London, Inggris` atau `London, United Kingdom`
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
            <li>Mendukung <strong>100+ negara</strong> dari seluruh dunia</li>
            <li>Bisa menggunakan <strong>huruf besar</strong> atau <strong>huruf kecil</strong></li>
            <li>Untuk negara bisa menggunakan ejaan <strong>Indonesia</strong> atau <strong>Inggris</strong></li>
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
    "Mendukung 100+ negara di seluruh dunia"
    "</div>",
    unsafe_allow_html=True
)

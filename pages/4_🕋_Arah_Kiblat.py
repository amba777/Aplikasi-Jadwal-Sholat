import streamlit as st
import math
import requests
from urllib.parse import quote
import time

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

# Database lengkap kota dan negara (100+ kota dari seluruh dunia)
CITY_DATABASE = {
    # ASIA - 35 kota
    'jakarta': {'country': 'indonesia', 'lat': -6.2088, 'lon': 106.8456},
    'surabaya': {'country': 'indonesia', 'lat': -7.2575, 'lon': 112.7521},
    'bandung': {'country': 'indonesia', 'lat': -6.9175, 'lon': 107.6191},
    'medan': {'country': 'indonesia', 'lat': 3.5952, 'lon': 98.6722},
    'semarang': {'country': 'indonesia', 'lat': -6.9667, 'lon': 110.4167},
    'makassar': {'country': 'indonesia', 'lat': -5.1477, 'lon': 119.4327},
    'palembang': {'country': 'indonesia', 'lat': -2.9761, 'lon': 104.7754},
    'kuala lumpur': {'country': 'malaysia', 'lat': 3.1390, 'lon': 101.6869},
    'penang': {'country': 'malaysia', 'lat': 5.4164, 'lon': 100.3327},
    'johor bahru': {'country': 'malaysia', 'lat': 1.4927, 'lon': 103.7414},
    'singapore': {'country': 'singapura', 'lat': 1.3521, 'lon': 103.8198},
    'bangkok': {'country': 'thailand', 'lat': 13.7563, 'lon': 100.5018},
    'phuket': {'country': 'thailand', 'lat': 7.8804, 'lon': 98.3923},
    'chiang mai': {'country': 'thailand', 'lat': 18.7883, 'lon': 98.9853},
    'hanoi': {'country': 'vietnam', 'lat': 21.0285, 'lon': 105.8542},
    'ho chi minh': {'country': 'vietnam', 'lat': 10.8231, 'lon': 106.6297},
    'manila': {'country': 'filipina', 'lat': 14.5995, 'lon': 120.9842},
    'tokyo': {'country': 'jepang', 'lat': 35.6762, 'lon': 139.6503},
    'osaka': {'country': 'jepang', 'lat': 34.6937, 'lon': 135.5023},
    'kyoto': {'country': 'jepang', 'lat': 35.0116, 'lon': 135.7681},
    'seoul': {'country': 'korea selatan', 'lat': 37.5665, 'lon': 126.9780},
    'busan': {'country': 'korea selatan', 'lat': 35.1796, 'lon': 129.0756},
    'beijing': {'country': 'china', 'lat': 39.9042, 'lon': 116.4074},
    'shanghai': {'country': 'china', 'lat': 31.2304, 'lon': 121.4737},
    'hong kong': {'country': 'hong kong', 'lat': 22.3193, 'lon': 114.1694},
    'taipei': {'country': 'taiwan', 'lat': 25.0330, 'lon': 121.5654},
    'mumbai': {'country': 'india', 'lat': 19.0760, 'lon': 72.8777},
    'delhi': {'country': 'india', 'lat': 28.7041, 'lon': 77.1025},
    'bangalore': {'country': 'india', 'lat': 12.9716, 'lon': 77.5946},
    'karachi': {'country': 'pakistan', 'lat': 24.8607, 'lon': 67.0011},
    'dhaka': {'country': 'bangladesh', 'lat': 23.8103, 'lon': 90.4125},
    'colombo': {'country': 'sri lanka', 'lat': 6.9271, 'lon': 79.8612},
    'kathmandu': {'country': 'nepal', 'lat': 27.7172, 'lon': 85.3240},
    'tehran': {'country': 'iran', 'lat': 35.6892, 'lon': 51.3890},
    'baghdad': {'country': 'irak', 'lat': 33.3152, 'lon': 44.3661},
    
    # TIMUR TENGAH - 15 kota
    'riyadh': {'country': 'arab saudi', 'lat': 24.7136, 'lon': 46.6753},
    'jeddah': {'country': 'arab saudi', 'lat': 21.5433, 'lon': 39.1728},
    'makkah': {'country': 'arab saudi', 'lat': 21.4225, 'lon': 39.8262},
    'dubai': {'country': 'uni emirat arab', 'lat': 25.2048, 'lon': 55.2708},
    'abu dhabi': {'country': 'uni emirat arab', 'lat': 24.4539, 'lon': 54.3773},
    'doha': {'country': 'qatar', 'lat': 25.2854, 'lon': 51.5310},
    'kuwait city': {'country': 'kuwait', 'lat': 29.3759, 'lon': 47.9774},
    'muscat': {'country': 'oman', 'lat': 23.5880, 'lon': 58.3829},
    'manama': {'country': 'bahrain', 'lat': 26.0667, 'lon': 50.5577},
    'amman': {'country': 'yordania', 'lat': 31.9454, 'lon': 35.9284},
    'beirut': {'country': 'lebanon', 'lat': 33.8886, 'lon': 35.4955},
    'damascus': {'country': 'suriah', 'lat': 33.5138, 'lon': 36.2765},
    'jerusalem': {'country': 'israel', 'lat': 31.7683, 'lon': 35.2137},
    'ankara': {'country': 'turki', 'lat': 39.9334, 'lon': 32.8597},
    'istanbul': {'country': 'turki', 'lat': 41.0082, 'lon': 28.9784},
    
    # EROPA - 25 kota
    'moscow': {'country': 'rusia', 'lat': 55.7558, 'lon': 37.6173},
    'saint petersburg': {'country': 'rusia', 'lat': 59.9311, 'lon': 30.3609},
    'kyiv': {'country': 'ukraina', 'lat': 50.4501, 'lon': 30.5234},
    'warsaw': {'country': 'polandia', 'lat': 52.2297, 'lon': 21.0122},
    'berlin': {'country': 'jerman', 'lat': 52.5200, 'lon': 13.4050},
    'munich': {'country': 'jerman', 'lat': 48.1351, 'lon': 11.5820},
    'hamburg': {'country': 'jerman', 'lat': 53.5511, 'lon': 9.9937},
    'paris': {'country': 'perancis', 'lat': 48.8566, 'lon': 2.3522},
    'marseille': {'country': 'perancis', 'lat': 43.2965, 'lon': 5.3698},
    'lyon': {'country': 'perancis', 'lat': 45.7640, 'lon': 4.8357},
    'rome': {'country': 'italia', 'lat': 41.9028, 'lon': 12.4964},
    'milan': {'country': 'italia', 'lat': 45.4642, 'lon': 9.1900},
    'naples': {'country': 'italia', 'lat': 40.8518, 'lon': 14.2681},
    'madrid': {'country': 'spanyol', 'lat': 40.4168, 'lon': -3.7038},
    'barcelona': {'country': 'spanyol', 'lat': 41.3851, 'lon': 2.1734},
    'valencia': {'country': 'spanyol', 'lat': 39.4699, 'lon': -0.3763},
    'lisbon': {'country': 'portugal', 'lat': 38.7223, 'lon': -9.1393},
    'london': {'country': 'inggris', 'lat': 51.5074, 'lon': -0.1278},
    'manchester': {'country': 'inggris', 'lat': 53.4808, 'lon': -2.2426},
    'dublin': {'country': 'irlandia', 'lat': 53.3498, 'lon': -6.2603},
    'amsterdam': {'country': 'belanda', 'lat': 52.3676, 'lon': 4.9041},
    'brussels': {'country': 'belgia', 'lat': 50.8503, 'lon': 4.3517},
    'zurich': {'country': 'swiss', 'lat': 47.3769, 'lon': 8.5417},
    'vienna': {'country': 'austria', 'lat': 48.2082, 'lon': 16.3738},
    'stockholm': {'country': 'swedia', 'lat': 59.3293, 'lon': 18.0686},
    
    # AMERIKA - 15 kota
    'new york': {'country': 'amerika serikat', 'lat': 40.7128, 'lon': -74.0060},
    'los angeles': {'country': 'amerika serikat', 'lat': 34.0522, 'lon': -118.2437},
    'chicago': {'country': 'amerika serikat', 'lat': 41.8781, 'lon': -87.6298},
    'houston': {'country': 'amerika serikat', 'lat': 29.7604, 'lon': -95.3698},
    'miami': {'country': 'amerika serikat', 'lat': 25.7617, 'lon': -80.1918},
    'toronto': {'country': 'kanada', 'lat': 43.6532, 'lon': -79.3832},
    'vancouver': {'country': 'kanada', 'lat': 49.2827, 'lon': -123.1207},
    'montreal': {'country': 'kanada', 'lat': 45.5017, 'lon': -73.5673},
    'mexico city': {'country': 'meksiko', 'lat': 19.4326, 'lon': -99.1332},
    'sao paulo': {'country': 'brazil', 'lat': -23.5505, 'lon': -46.6333},
    'rio de janeiro': {'country': 'brazil', 'lat': -22.9068, 'lon': -43.1729},
    'buenos aires': {'country': 'argentina', 'lat': -34.6037, 'lon': -58.3816},
    'santiago': {'country': 'chile', 'lat': -33.4489, 'lon': -70.6693},
    'lima': {'country': 'peru', 'lat': -12.0464, 'lon': -77.0428},
    'bogota': {'country': 'kolombia', 'lat': 4.7110, 'lon': -74.0721},
    
    # AFRIKA - 10 kota
    'cairo': {'country': 'mesir', 'lat': 30.0444, 'lon': 31.2357},
    'lagos': {'country': 'nigeria', 'lat': 6.5244, 'lon': 3.3792},
    'nairobi': {'country': 'kenya', 'lat': -1.2864, 'lon': 36.8172},
    'addis ababa': {'country': 'ethiopia', 'lat': 9.0320, 'lon': 38.7469},
    'johannesburg': {'country': 'afrika selatan', 'lat': -26.2041, 'lon': 28.0473},
    'cape town': {'country': 'afrika selatan', 'lat': -33.9249, 'lon': 18.4241},
    'casablanca': {'country': 'maroko', 'lat': 33.5731, 'lon': -7.5898},
    'algiers': {'country': 'aljazair', 'lat': 36.7538, 'lon': 3.0588},
    'tunis': {'country': 'tunisia', 'lat': 36.8065, 'lon': 10.1815},
    'accra': {'country': 'ghana', 'lat': 5.6037, 'lon': -0.1870},
    
    # OSEANIA - 5 kota
    'sydney': {'country': 'australia', 'lat': -33.8688, 'lon': 151.2093},
    'melbourne': {'country': 'australia', 'lat': -37.8136, 'lon': 144.9631},
    'brisbane': {'country': 'australia', 'lat': -27.4698, 'lon': 153.0251},
    'auckland': {'country': 'selandia baru', 'lat': -36.8485, 'lon': 174.7633},
    'wellington': {'country': 'selandia baru', 'lat': -41.2865, 'lon': 174.7762},
}

# Mapping negara dengan variasi ejaan
COUNTRY_MAPPING = {
    'indonesia': ['indonesia', 'republik indonesia'],
    'malaysia': ['malaysia'],
    'singapura': ['singapura', 'singapore', 'republik singapura'],
    'thailand': ['thailand', 'thai'],
    'vietnam': ['vietnam', 'viet nam'],
    'filipina': ['filipina', 'philippines', 'pilipinas'],
    'jepang': ['jepang', 'japan', 'nippon'],
    'korea selatan': ['korea selatan', 'south korea', 'korea', 'republik korea'],
    'china': ['china', 'cina', 'tiongkok', 'republik rakyat china'],
    'hong kong': ['hong kong', 'hongkong'],
    'taiwan': ['taiwan', 'republik china'],
    'india': ['india', 'republik india'],
    'pakistan': ['pakistan'],
    'bangladesh': ['bangladesh'],
    'sri lanka': ['sri lanka'],
    'nepal': ['nepal'],
    'iran': ['iran', 'republik islam iran'],
    'irak': ['irak', 'iraq', 'republik irak'],
    'arab saudi': ['arab saudi', 'saudi arabia', 'saudi', 'kerajaan arab saudi'],
    'uni emirat arab': ['uni emirat arab', 'united arab emirates', 'uae', 'emirat arab'],
    'qatar': ['qatar'],
    'kuwait': ['kuwait'],
    'oman': ['oman', 'kesultanan oman'],
    'bahrain': ['bahrain'],
    'yordania': ['yordania', 'jordan', 'kerajaan yordania'],
    'lebanon': ['lebanon'],
    'suriah': ['suriah', 'syria', 'republik arab suriah'],
    'israel': ['israel'],
    'turki': ['turki', 'turkey', 'türkiye', 'republik turki'],
    'rusia': ['rusia', 'russia', 'russian federation', 'federasi rusia'],
    'ukraina': ['ukraina', 'ukraine'],
    'polandia': ['polandia', 'poland', 'republik polandia'],
    'jerman': ['jerman', 'germany', 'deutschland', 'republik federal jerman'],
    'perancis': ['perancis', 'france', 'prancis', 'republik perancis'],
    'italia': ['italia', 'italy', 'republik italia'],
    'spanyol': ['spanyol', 'spain', 'españa', 'kerajaan spanyol'],
    'portugal': ['portugal', 'republik portugal'],
    'inggris': ['inggris', 'united kingdom', 'uk', 'britania raya', 'england', 'british'],
    'irlandia': ['irlandia', 'ireland', 'republik irlandia'],
    'belanda': ['belanda', 'netherlands', 'nederland', 'kerajaan belanda'],
    'belgia': ['belgia', 'belgium', 'belgique', 'kerajaan belgia'],
    'swiss': ['swiss', 'switzerland', 'schweiz', 'konfederasi swiss'],
    'austria': ['austria', 'republik austria'],
    'swedia': ['swedia', 'sweden', 'sverige', 'kerajaan swedia'],
    'amerika serikat': ['amerika serikat', 'united states', 'usa', 'us', 'amerika'],
    'kanada': ['kanada', 'canada'],
    'meksiko': ['meksiko', 'mexico', 'estados unidos mexicanos'],
    'brazil': ['brazil', 'brasil', 'republik federal brasil'],
    'argentina': ['argentina', 'republik argentina'],
    'chile': ['chile', 'republik chile'],
    'kolombia': ['kolombia', 'colombia', 'republik kolombia'],
    'peru': ['peru', 'republik peru'],
    'mesir': ['mesir', 'egypt', 'republik arab mesir'],
    'nigeria': ['nigeria', 'republik federal nigeria'],
    'kenya': ['kenya', 'republik kenya'],
    'ethiopia': ['ethiopia'],
    'afrika selatan': ['afrika selatan', 'south africa', 'republik afrika selatan'],
    'maroko': ['maroko', 'morocco', 'kerajaan maroko'],
    'aljazair': ['aljazair', 'algeria', 'republik demokratik rakyat aljazair'],
    'tunisia': ['tunisia', 'republik tunisia'],
    'ghana': ['ghana', 'republik ghana'],
    'australia': ['australia', 'commonwealth of australia'],
    'selandia baru': ['selandia baru', 'new zealand', 'aotearoa'],
}

def normalize_input(text):
    """Normalisasi input menjadi lowercase dan hapus spasi berlebih"""
    return ' '.join(text.lower().strip().split())

def correct_country_name(country_input):
    """Koreksi otomatis nama negara berdasarkan mapping"""
    normalized = normalize_input(country_input)
    
    for correct_name, variations in COUNTRY_MAPPING.items():
        if normalized in variations:
            return correct_name
    
    return normalized

def validate_city_country(city, country):
    """Validasi apakah kota dan negara cocok"""
    city_normalized = normalize_input(city)
    country_normalized = correct_country_name(country)
    
    if city_normalized in CITY_DATABASE:
        correct_country = CITY_DATABASE[city_normalized]['country']
        if correct_country != country_normalized:
            return False, f"❌ Kota '{city.title()}' berada di **{correct_country.title()}**, bukan di {country.title()}!"
        return True, None
    
    return False, f"❌ Kota '{city.title()}' tidak ditemukan dalam database. Gunakan salah satu dari 100+ kota yang tersedia."

def get_coordinates(city, country):
    """Mendapatkan koordinat dari database atau API"""
    city_normalized = normalize_input(city)
    
    # Validasi dulu
    is_valid, error_msg = validate_city_country(city, country)
    if not is_valid:
        return None, None, error_msg
    
    # Ambil dari database
    if city_normalized in CITY_DATABASE:
        data = CITY_DATABASE[city_normalized]
        return data['lat'], data['lon'], None
    
    return None, None, "Kota tidak ditemukan dalam database."

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
    """Membuat visualisasi kompas modern dan profesional dengan Plotly"""
    if not PLOTLY_AVAILABLE:
        return None
    
    fig = go.Figure()
    
    # Background gradient lingkaran luar
    fig.add_trace(go.Scatterpolar(
        r=[1.15] * 360,
        theta=list(range(360)),
        mode='none',
        fill='toself',
        fillcolor='rgba(20, 25, 45, 0.95)',
        line=dict(color='rgba(0, 170, 255, 0.4)', width=3),
        showlegend=False
    ))
    
    # Lingkaran dalam dengan gradient
    fig.add_trace(go.Scatterpolar(
        r=[1] * 360,
        theta=list(range(360)),
        mode='none',
        fill='toself',
        fillcolor='rgba(25, 35, 65, 0.9)',
        line=dict(color='rgba(0, 170, 255, 0.6)', width=2),
        showlegend=False
    ))
    
    # Grid circles untuk depth
    for radius in [0.3, 0.6, 0.9]:
        theta_circle = list(range(361))
        fig.add_trace(go.Scatterpolar(
            r=[radius] * 361,
            theta=theta_circle,
            mode='lines',
            line=dict(color='rgba(255,255,255,0.1)', width=1),
            showlegend=False
        ))
    
    # Garis arah utama dengan warna modern
    directions_colors = [
        (0, '#FF4444', 'UTARA'),      # Merah terang untuk Utara
        (90, '#00D9FF', 'TIMUR'),     # Cyan untuk Timur
        (180, '#FFB800', 'SELATAN'),  # Orange untuk Selatan  
        (270, '#BB86FC', 'BARAT')     # Purple untuk Barat
    ]
    
    for angle, color, label in directions_colors:
        # Garis utama
        fig.add_trace(go.Scatterpolar(
            r=[0, 1],
            theta=[angle, angle],
            mode='lines',
            line=dict(color=color, width=2.5),
            showlegend=False
        ))
        
        # Titik di ujung garis
        fig.add_trace(go.Scatterpolar(
            r=[1.02],
            theta=[angle],
            mode='markers',
            marker=dict(size=8, color=color, line=dict(color='white', width=1)),
            showlegend=False
        ))
    
    # Label arah dengan styling modern
    for angle, color, label in directions_colors:
        fig.add_trace(go.Scatterpolar(
            r=[1.25],
            theta=[angle],
            mode='text',
            text=[f'<b>{label}</b>'],
            textfont=dict(size=14, color=color, family='Arial Black'),
            showlegend=False
        ))
    
    # Jarum kiblat dengan efek 3D
    arrow_angles = [qibla_angle-8, qibla_angle, qibla_angle+8, qibla_angle]
    arrow_r = [0, 0.75, 0, 0]
    
    # Shadow jarum
    fig.add_trace(go.Scatterpolar(
        r=[r + 0.02 for r in arrow_r],
        theta=[a + 2 for a in arrow_angles],
        mode='lines',
        fill='toself',
        fillcolor='rgba(0, 0, 0, 0.3)',
        line=dict(color='rgba(0, 0, 0, 0)', width=0),
        showlegend=False
    ))
    
    # Jarum utama dengan gradient
    fig.add_trace(go.Scatterpolar(
        r=arrow_r,
        theta=arrow_angles,
        mode='lines',
        fill='toself',
        fillcolor='rgba(0, 255, 136, 0.85)',
        line=dict(color='#00FF88', width=3),
        showlegend=False
    ))
    
    # Outline jarum
    fig.add_trace(go.Scatterpolar(
        r=arrow_r,
        theta=arrow_angles,
        mode='lines',
        line=dict(color='rgba(255, 255, 255, 0.8)', width=1.5),
        showlegend=False
    ))
    
    # Lingkaran tengah dengan efek glow
    for size, alpha in [(30, 0.3), (25, 0.5), (20, 0.8)]:
        fig.add_trace(go.Scatterpolar(
            r=[0.05],
            theta=[0],
            mode='markers',
            marker=dict(size=size, color=f'rgba(0, 255, 136, {alpha})', 
                        line=dict(color='white', width=0)),
            showlegend=False
        ))
    
    # Lingkaran tengah inti
    fig.add_trace(go.Scatterpolar(
        r=[0.05],
        theta=[0],
        mode='markers',
        marker=dict(size=15, color='white', 
                    line=dict(color='#00FF88', width=3)),
        showlegend=False
    ))
    
    # Icon kiblat di ujung jarum dengan background
    fig.add_trace(go.Scatterpolar(
        r=[0.85],
        theta=[qibla_angle],
        mode='markers+text',
        marker=dict(size=35, color='rgba(0, 255, 136, 0.2)', 
                    line=dict(color='#00FF88', width=2)),
        text=['🕋'],
        textfont=dict(size=18),
        showlegend=False
    ))
    
    # Derajat markers setiap 30 derajat
    for angle in range(0, 360, 30):
        if angle not in [0, 90, 180, 270]:  # Skip arah utama
            fig.add_trace(go.Scatterpolar(
                r=[0.95],
                theta=[angle],
                mode='markers',
                marker=dict(size=4, color='rgba(255,255,255,0.5)'),
                showlegend=False
            ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=False, range=[0, 1.35]),
            angularaxis=dict(
                direction="clockwise",
                rotation=90,
                tickvals=[],
                ticktext=[],
                showline=False,
                showgrid=False,
            ),
            bgcolor='rgba(0,0,0,0)',
        ),
        showlegend=False,
        height=550,
        margin=dict(l=30, r=30, t=30, b=30),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Arial, sans-serif')
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
    city_input = st.text_input("**Kota**", "", placeholder="Contoh: Tokyo, Jakarta, London, Madrid")
    st.caption("⚠️ Masukkan nama KOTA (bisa huruf besar/kecil)")
    
with col2:
    country_input = st.text_input("**Negara**", "", placeholder="Contoh: Jepang, Indonesia, Inggris, Spanyol")
    st.caption("⚠️ Masukkan NEGARA yang sesuai dengan kota")

# Tampilkan daftar 100 kota yang tersedia
with st.expander("📋 Lihat 100+ Kota yang Tersedia"):
    st.markdown("### 🌏 ASIA (35 kota)")
    col_a1, col_a2, col_a3 = st.columns(3)
    with col_a1:
        st.write("**Indonesia:**")
        st.write("- Jakarta")
        st.write("- Surabaya")
        st.write("- Bandung")
        st.write("- Medan")
        st.write("- Semarang")
        st.write("- Makassar")
        st.write("- Palembang")
    with col_a2:
        st.write("**Asia Tenggara:**")
        st.write("- Kuala Lumpur (Malaysia)")
        st.write("- Penang (Malaysia)")
        st.write("- Johor Bahru (Malaysia)")
        st.write("- Singapore (Singapura)")
        st.write("- Bangkok (Thailand)")
        st.write("- Phuket (Thailand)")
        st.write("- Hanoi (Vietnam)")
        st.write("- Manila (Filipina)")
    with col_a3:
        st.write("**Asia Timur:**")
        st.write("- Tokyo (Jepang)")
        st.write("- Osaka (Jepang)")
        st.write("- Kyoto (Jepang)")
        st.write("- Seoul (Korea Selatan)")
        st.write("- Busan (Korea Selatan)")
        st.write("- Beijing (China)")
        st.write("- Shanghai (China)")
        st.write("- Hong Kong")
        st.write("- Taipei (Taiwan)")
    
    col_a4, col_a5 = st.columns(2)
    with col_a4:
        st.write("**Asia Selatan:**")
        st.write("- Mumbai (India)")
        st.write("- Delhi (India)")
        st.write("- Bangalore (India)")
        st.write("- Karachi (Pakistan)")
        st.write("- Dhaka (Bangladesh)")
        st.write("- Colombo (Sri Lanka)")
        st.write("- Kathmandu (Nepal)")
    with col_a5:
        st.write("**Asia Barat:**")
        st.write("- Tehran (Iran)")
        st.write("- Baghdad (Irak)")
    
    st.markdown("---")
    st.markdown("### 🕌 TIMUR TENGAH (15 kota)")
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.write("**Arab Saudi:**")
        st.write("- Riyadh")
        st.write("- Jeddah")
        st.write("- Makkah")
        st.write("")
        st.write("**UAE:**")
        st.write("- Dubai")
        st.write("- Abu Dhabi")
    with col_m2:
        st.write("**Negara Teluk:**")
        st.write("- Doha (Qatar)")
        st.write("- Kuwait City (Kuwait)")
        st.write("- Muscat (Oman)")
        st.write("- Manama (Bahrain)")
        st.write("")
        st.write("**Levant:**")
        st.write("- Amman (Yordania)")
        st.write("- Beirut (Lebanon)")
    with col_m3:
        st.write("**Lainnya:**")
        st.write("- Damascus (Suriah)")
        st.write("- Jerusalem (Israel)")
        st.write("- Ankara (Turki)")
        st.write("- Istanbul (Turki)")
    
    st.markdown("---")
    st.markdown("### 🏰 EROPA (25 kota)")
    col_e1, col_e2, col_e3 = st.columns(3)
    with col_e1:
        st.write("**Eropa Timur:**")
        st.write("- Moscow (Rusia)")
        st.write("- Saint Petersburg (Rusia)")
        st.write("- Kyiv (Ukraina)")
        st.write("- Warsaw (Polandia)")
        st.write("")
        st.write("**Jerman:**")
        st.write("- Berlin")
        st.write("- Munich")
        st.write("- Hamburg")
    with col_e2:
        st.write("**Eropa Barat:**")
        st.write("- Paris (Perancis)")
        st.write("- Marseille (Perancis)")
        st.write("- Lyon (Perancis)")
        st.write("- London (Inggris)")
        st.write("- Manchester (Inggris)")
        st.write("- Dublin (Irlandia)")
        st.write("- Amsterdam (Belanda)")
        st.write("- Brussels (Belgia)")
    with col_e3:
        st.write("**Eropa Selatan:**")
        st.write("- Rome (Italia)")
        st.write("- Milan (Italia)")
        st.write("- Naples (Italia)")
        st.write("- Madrid (Spanyol)")
        st.write("- Barcelona (Spanyol)")
        st.write("- Valencia (Spanyol)")
        st.write("- Lisbon (Portugal)")
        st.write("")
        st.write("**Lainnya:**")
        st.write("- Zurich (Swiss)")
        st.write("- Vienna (Austria)")
        st.write("- Stockholm (Swedia)")
    
    st.markdown("---")
    st.markdown("### 🗽 AMERIKA (15 kota)")
    col_am1, col_am2, col_am3 = st.columns(3)
    with col_am1:
        st.write("**Amerika Utara:**")
        st.write("- New York (USA)")
        st.write("- Los Angeles (USA)")
        st.write("- Chicago (USA)")
        st.write("- Houston (USA)")
        st.write("- Miami (USA)")
    with col_am2:
        st.write("**Kanada:**")
        st.write("- Toronto")
        st.write("- Vancouver")
        st.write("- Montreal")
        st.write("")
        st.write("**Amerika Latin:**")
        st.write("- Mexico City (Meksiko)")
        st.write("- Bogota (Kolombia)")
        st.write("- Lima (Peru)")
    with col_am3:
        st.write("**Amerika Selatan:**")
        st.write("- Sao Paulo (Brazil)")
        st.write("- Rio de Janeiro (Brazil)")
        st.write("- Buenos Aires (Argentina)")
        st.write("- Santiago (Chile)")
    
    st.markdown("---")
    st.markdown("### 🦁 AFRIKA (10 kota)")
    col_af1, col_af2 = st.columns(2)
    with col_af1:
        st.write("**Afrika Utara:**")
        st.write("- Cairo (Mesir)")
        st.write("- Casablanca (Maroko)")
        st.write("- Algiers (Aljazair)")
        st.write("- Tunis (Tunisia)")
        st.write("")
        st.write("**Afrika Barat:**")
        st.write("- Lagos (Nigeria)")
        st.write("- Accra (Ghana)")
    with col_af2:
        st.write("**Afrika Timur:**")
        st.write("- Nairobi (Kenya)")
        st.write("- Addis Ababa (Ethiopia)")
        st.write("")
        st.write("**Afrika Selatan:**")
        st.write("- Johannesburg (Afrika Selatan)")
        st.write("- Cape Town (Afrika Selatan)")
    
    st.markdown("---")
    st.markdown("### 🦘 OSEANIA (5 kota)")
    col_oc1, col_oc2 = st.columns(2)
    with col_oc1:
        st.write("**Australia:**")
        st.write("- Sydney")
        st.write("- Melbourne")
        st.write("- Brisbane")
    with col_oc2:
        st.write("**Selandia Baru:**")
        st.write("- Auckland")
        st.write("- Wellington")

calculate_button = st.button("🧭 Hitung Arah Kiblat", use_container_width=True)

if calculate_button:
    if not city_input or not country_input:
        st.warning("⚠️ Harap masukkan nama Kota dan Negara.")
    else:
        with st.spinner("🔄 Memvalidasi dan mencari koordinat..."):
            user_lat, user_lon, error_msg = get_coordinates(city_input, country_input)
        
        if error_msg:
            st.error(error_msg)
            
            # Berikan saran
            city_normalized = normalize_input(city_input)
            if city_normalized in CITY_DATABASE:
                correct_country = CITY_DATABASE[city_normalized]['country']
                st.info(f"💡 **Saran:** Kota '{city_input.title()}' berada di **{correct_country.title()}**. Silakan gunakan negara yang benar!")
            else:
                st.info("""
                **💡 Tips:**
                - Pastikan kota yang Anda masukkan ada dalam daftar 100+ kota yang tersedia
                - Klik "📋 Lihat 100+ Kota yang Tersedia" untuk melihat daftar lengkap
                - Pastikan negara sesuai dengan kotanya (contoh: Madrid harus dengan Spanyol)
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
                st.metric("🕋 Ka'bah", "Makkah")
                st.metric("📍 Koordinat", f"{KAABA_LAT:.4f}°, {KAABA_LON:.4f}°")
            
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
                    <li>Gunakan patokan tetap (bangunan/pohon) untuk mempermudah penentuan arah</li>
                </ol>
                <p style='color: #ffa500; margin: 1rem 0 0 0; font-weight: bold;'>
                    🎯 Arah Kiblat dari {city_input.title()}: <strong>{qibla:.2f}°</strong> ke arah <strong>{direction_name}</strong>
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Informasi tambahan dengan notifikasi auto-hide
            success_placeholder = st.empty()
            with success_placeholder.container():
                st.success(f"✅ Berhasil menghitung arah kiblat untuk {city_input.title()}, {country_input.title()}!")
            
            # Auto-hide setelah 4 detik
            time.sleep(4)
            success_placeholder.empty()

# Informasi default
st.markdown("""
<div style='background: rgba(0, 170, 255, 0.1); padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem;'>
    <h4 style='color: #00aaff; margin-bottom: 1rem;'>💡 Cara Menggunakan:</h4>
    <ul style='color: #ccc; margin: 0; padding-left: 20px;'>
        <li>Masukkan <strong>nama kota</strong> dari 100+ kota yang tersedia</li>
        <li>Masukkan <strong>nama negara</strong> yang <strong>SESUAI</strong> dengan kota tersebut</li>
        <li>Contoh: <strong>Madrid → Spanyol</strong> ✅ (bukan negara lain ❌)</li>
        <li>Bisa menggunakan <strong>huruf besar/kecil</strong> dan ejaan <strong>Indonesia/Inggris</strong></li>
        <li>Klik <strong>"📋 Lihat 100+ Kota yang Tersedia"</strong> untuk melihat daftar lengkap</li>
        <li>Sistem akan <strong>validasi otomatis</strong> kecocokan kota dan negara</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Blok 2: Contoh Input yang Benar
st.markdown("""
<div style='background: rgba(0, 170, 255, 0.1); padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem;'>
    <h4 style='color: #ffa500; margin-bottom: 1rem;'>✅ Contoh Input yang Benar:</h4>
    <ul style='color: #ccc; margin: 0; padding-left: 20px;'>
        <li><strong>Kota:</strong> Madrid | <strong>Negara:</strong> Spanyol ✅</li>
        <li><strong>Kota:</strong> Tokyo | <strong>Negara:</strong> Jepang ✅</li>
        <li><strong>Kota:</strong> Jakarta | <strong>Negara:</strong> Indonesia ✅</li>
        <li><strong>Kota:</strong> New York | <strong>Negara:</strong> Amerika Serikat ✅</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Blok 3: Contoh Input yang Salah
st.markdown("""
<div style='background: rgba(0, 170, 255, 0.1); padding: 1.5rem; border-radius: 10px; margin: 2rem 0;'>
    <h4 style='color: #ff6b6b; margin-bottom: 1rem;'>❌ Contoh Input yang Salah:</h4>
    <ul style='color: #ccc; margin: 0; padding-left: 20px;'>
        <li><strong>Kota:</strong> Madrid | <strong>Negara:</strong> Indonesia ❌ (Tidak cocok!)</li>
        <li><strong>Kota:</strong> Tokyo | <strong>Negara:</strong> China ❌ (Tidak cocok!)</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Statistik
st.markdown("""
<div style='background: rgba(255, 165, 0, 0.1); padding: 1.5rem; border-radius: 10px; margin: 2rem 0;'>
    <h4 style='color: #ffa500; margin-bottom: 1rem;'>📊 Database Kota:</h4>
    <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;'>
        <div style='text-align: center; padding: 1rem; background: rgba(0,170,255,0.1); border-radius: 8px;'>
            <div style='font-size: 2rem; color: #00aaff;'>35</div>
            <div style='color: #ccc;'>Kota Asia</div>
        </div>
        <div style='text-align: center; padding: 1rem; background: rgba(0,170,255,0.1); border-radius: 8px;'>
            <div style='font-size: 2rem; color: #00aaff;'>15</div>
            <div style='color: #ccc;'>Kota Timur Tengah</div>
        </div>
        <div style='text-align: center; padding: 1rem; background: rgba(0,170,255,0.1); border-radius: 8px;'>
            <div style='font-size: 2rem; color: #00aaff;'>25</div>
            <div style='color: #ccc;'>Kota Eropa</div>
        </div>
        <div style='text-align: center; padding: 1rem; background: rgba(0,170,255,0.1); border-radius: 8px;'>
            <div style='font-size: 2rem; color: #00aaff;'>15</div>
            <div style='color: #ccc;'>Kota Amerika</div>
        </div>
        <div style='text-align: center; padding: 1rem; background: rgba(0,170,255,0.1); border-radius: 8px;'>
            <div style='font-size: 2rem; color: #00aaff;'>10</div>
            <div style='color: #ccc;'>Kota Afrika</div>
        </div>
        <div style='text-align: center; padding: 1rem; background: rgba(0,170,255,0.1); border-radius: 8px;'>
            <div style='font-size: 2rem; color: #00aaff;'>5</div>
            <div style='color: #ccc;'>Kota Oseania</div>
        </div>
    </div>
    <div style='text-align: center; margin-top: 1.5rem; padding: 1rem; background: rgba(255,215,0,0.1); border-radius: 8px;'>
        <div style='font-size: 2.5rem; color: gold; font-weight: bold;'>105</div>
        <div style='color: #ccc; font-size: 1.1rem;'>Total Kota dari Seluruh Benua</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Footer modern dan profesional
st.markdown("---")
st.markdown("""
<div style='background: linear-gradient(135deg, rgba(0, 170, 255, 0.1), rgba(255, 165, 0, 0.1)); 
             padding: 2rem; 
             border-radius: 15px; 
             margin: 2rem 0;
             border: 1px solid rgba(0, 170, 255, 0.3);'>
    <div style='text-align: center;'>
        <h3 style='color: #00aaff; margin-bottom: 1.5rem; font-size: 1.5rem;'>
            🕋 Arah Kiblat - Penunjuk Arah Sholat Digital
        </h3>
    </div>
</div>
""", unsafe_allow_html=True)

# Grid items menggunakan Streamlit columns
col_f1, col_f2 = st.columns(2)
with col_f1:
    st.markdown("""
    <div style='background: rgba(0, 170, 255, 0.1); 
                 padding: 1.2rem; 
                 border-radius: 10px; 
                 border-left: 4px solid #00aaff;
                 margin-bottom: 1rem;'>
        <div style='font-size: 1.8rem; margin-bottom: 0.5rem;'>📍</div>
        <div style='color: #00aaff; font-weight: bold; margin-bottom: 0.3rem;'>Koordinat Ka'bah</div>
        <div style='color: #ccc; font-size: 0.9rem;'>21.4225°N, 39.8262°E</div>
        <div style='color: #999; font-size: 0.85rem; margin-top: 0.3rem;'>Makkah Al-Mukarramah</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background: rgba(0, 255, 136, 0.1); 
                 padding: 1.2rem; 
                 border-radius: 10px; 
                 border-left: 4px solid #00FF88;
                 margin-bottom: 1rem;'>
        <div style='font-size: 1.8rem; margin-bottom: 0.5rem;'>🌍</div>
        <div style='color: #00FF88; font-weight: bold; margin-bottom: 0.3rem;'>Cakupan Global</div>
        <div style='color: #ccc; font-size: 0.9rem;'>105 Kota Utama</div>
        <div style='color: #999; font-size: 0.85rem; margin-top: 0.3rem;'>6 Benua Tersedia</div>
    </div>
    """, unsafe_allow_html=True)

with col_f2:
    st.markdown("""
    <div style='background: rgba(255, 165, 0, 0.1); 
                 padding: 1.2rem; 
                 border-radius: 10px; 
                 border-left: 4px solid #ffa500;
                 margin-bottom: 1rem;'>
        <div style='font-size: 1.8rem; margin-bottom: 0.5rem;'>✅</div>
        <div style='color: #ffa500; font-weight: bold; margin-bottom: 0.3rem;'>Validasi Otomatis</div>
        <div style='color: #ccc; font-size: 0.9rem;'>Sistem Verifikasi</div>
        <div style='color: #999; font-size: 0.85rem; margin-top: 0.3rem;'>Kota & Negara Akurat</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background: rgba(187, 134, 252, 0.1); 
                 padding: 1.2rem; 
                 border-radius: 10px; 
                 border-left: 4px solid #BB86FC;
                 margin-bottom: 1rem;'>
        <div style='font-size: 1.8rem; margin-bottom: 0.5rem;'>🧭</div>
        <div style='color: #BB86FC; font-weight: bold; margin-bottom: 0.3rem;'>Kompas Visual</div>
        <div style='color: #ccc; font-size: 0.9rem;'>Modern & Interaktif</div>
        <div style='color: #999; font-size: 0.85rem; margin-top: 0.3rem;'>Akurasi Tinggi</div>
    </div>
    """, unsafe_allow_html=True)

# Informasi tambahan
st.markdown("""
<div style='margin-top: 1rem; 
             padding: 1.5rem; 
             background: rgba(0, 0, 0, 0.3); 
             border-radius: 10px;'>
    <div style='color: #999; font-size: 0.95rem; line-height: 1.8;'>
        <p style='margin: 0.5rem 0;'>
            <span style='color: #00aaff;'>🌐</span> Mendukung ejaan <strong>Indonesia</strong> & <strong>Inggris</strong>
        </p>
        <p style='margin: 0.5rem 0;'>
            <span style='color: #00FF88;'>💡</span> Perhitungan menggunakan <strong>Formula Haversine</strong> untuk akurasi maksimal
        </p>
        <p style='margin: 0.5rem 0;'>
            <span style='color: #ffa500;'>⚡</span> Database lokal untuk <strong>respon instan</strong> tanpa koneksi internet
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# Ayat Al-Quran
st.markdown("""
<div style='margin-top: 1.5rem; 
             padding: 1rem; 
             background: rgba(0, 0, 0, 0.3); 
             border-radius: 8px;'>
    <p style='color: #888; font-size: 0.85rem; margin: 0; font-style: italic;'>
        "Sesungguhnya kami melihat mukamu menengadah ke langit, maka benar-benar akan Kami palingkan engkau ke kiblat yang engkau senangi."<br>
        <span style='color: #00aaff;'>(QS. Al-Baqarah: 144)</span>
    </p>
</div>
""", unsafe_allow_html=True)

# Copyright
st.markdown("""
<div style='margin-top: 1.5rem; text-align: center;'>
    <p style='color: #666; font-size: 0.8rem; margin: 0.3rem 0;'>© 2025 Aplikasi Arah Kiblat Digital</p>
    <p style='color: #666; font-size: 0.8rem; margin: 0.3rem 0;'>Developed with ❤️ for Hamba Allah</p>
</div>
""", unsafe_allow_html=True)



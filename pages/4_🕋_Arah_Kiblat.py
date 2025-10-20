import streamlit as st
import math
import requests
import plotly.graph_objects as go

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
    try:
        query = f'{city},{country}'
        url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json"
        headers = {'User-Agent': 'AplikasiJadwalSholat/1.0'}
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        if data:
            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])
            return lat, lon
        else:
            return None, None
    except Exception as e:
        st.error(f"Gagal mendapatkan koordinat: {e}")
        return None, None

def calculate_qibla_direction(lat, lon):
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
            textfont=dict(size=16, color='white', weight='bold'),
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
                ticktext=[''] * 12,  # Sembunyikan tick default
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
    city_input = st.text_input("**Kota**", "Medan", placeholder="Contoh: Jakarta")
with col2:
    country_input = st.text_input("**Negara**", "Indonesia", placeholder="Contoh: Indonesia")

calculate_button = st.button("🧭 Hitung Arah Kiblat", use_container_width=True)

if calculate_button:
    if not city_input or not country_input:
        st.warning("⚠️ Harap masukkan nama Kota dan Negara.")
    else:
        with st.spinner("🔄 Mencari koordinat lokasi..."):
            user_lat, user_lon = get_coordinates(city_input, country_input)
        
        if user_lat is not None and user_lon is not None:
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
            compass_fig = create_compass_figure(qibla)
            st.plotly_chart(compass_fig, use_container_width=True)
            
            # Tampilkan informasi arah
            col_deg, col_dir = st.columns(2)
            with col_deg:
                st.markdown(f'<div class="degree-display">{qibla:.2f}°</div>', unsafe_allow_html=True)
                st.caption("Dari Arah Utara Sejati")
            with col_dir:
                st.markdown(f'<div class="qibla-direction">🕋 {direction_name}</div>', unsafe_allow_html=True)
                st.caption("Arah Mata Angin")
            
            # --- Instruction Section ---
            st.markdown("""
            <div class="instruction-box">
                <h4 style='color: white; margin-bottom: 1rem;'>📝 Cara Menentukan Arah Kiblat:</h4>
                <ol style='color: #ccc; margin: 0; padding-left: 1.5rem;'>
                    <li>Berdiri menghadap <strong>Utara</strong> menggunakan kompas</li>
                    <li>Putar tubuh Anda sebesar <strong>{}°</strong> searah jarum jam</li>
                    <li>Anda sekarang menghadap ke arah <strong>{}</strong> menuju Ka'bah</li>
                    <li>Gunakan patokan tetap untuk mempermudah penentuan arah</li>
                </ol>
                <p style='color: #ffa500; margin: 1rem 0 0 0; font-weight: bold;'>
                    🎯 Arah Kiblat Anda: <strong>{}° dari Utara</strong> menuju <strong>{}</strong>
                </p>
            </div>
            """.format(f"{qibla:.2f}", direction_name, f"{qibla:.2f}", direction_name), unsafe_allow_html=True)
            
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
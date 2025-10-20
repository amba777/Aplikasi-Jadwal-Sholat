import streamlit as st
from datetime import datetime, timedelta
import requests
import time as time_module
import locale
import base64
import os
from pathlib import Path

# --- LOKALISASI BAHASA INDONESIA ---
try:
    locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')
except locale.Error:
    pass

hijri_months_id = {
    "Muharram": "Muharram", "Safar": "Safar", "Rabi' al-awwal": "Rabiul Awal",
    "Rabi' al-thani": "Rabiul Akhir", "Jumada al-ula": "Jumadil Awal",
    "Jumada al-akhirah": "Jumadil Akhir", "Rajab": "Rajab", "Sha'ban": "Sya'ban",
    "Ramadan": "Ramadhan", "Shawwal": "Syawal", "Dhu al-Qi'dah": "Dzulqa'dah",
    "Dhu al-Hijjah": "Dzulhijjah"
}

# --- Konfigurasi Halaman ---
st.set_page_config(
    page_title="Jadwal Sholat Kota Medan",
    page_icon="🕌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INISIALISASI SESSION STATE ---
if 'azan_played_today' not in st.session_state:
    st.session_state.azan_played_today = {
        "Subuh": False,
        "Dzuhur": False, 
        "Ashar": False,
        "Maghrib": False,
        "Isya": False
    }

if 'current_azan' not in st.session_state:
    st.session_state.current_azan = None

if 'last_date' not in st.session_state:
    st.session_state.last_date = datetime.now().strftime("%Y-%m-%d")

if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()

# --- PATH FIX untuk Streamlit Cloud ---
BASE_DIR = Path(__file__).parent
AUDIO_DIR = BASE_DIR / "assets" / "audio"

# File audio azan berdasarkan jenis sholat
AZAN_FILES = {
    "Subuh": "fajr_128_44.mp3",
    "Dzuhur": "Adzan-Misyari-Rasyid.mp3", 
    "Ashar": "Adzan-Misyari-Rasyid.mp3",
    "Maghrib": "Adzan-Misyari-Rasyid.mp3",
    "Isya": "Adzan-Misyari-Rasyid.mp3"
}

# --- CSS Kustom Modern & Responsif ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@700&display=swap');

.stApp {
    background-color: #0d1117;
    color: #c9d1d9;
}

body::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: radial-gradient(circle at 10% 20%, rgba(102, 126, 234, 0.2) 0%, transparent 40%),
                radial-gradient(circle at 80% 70%, rgba(118, 75, 162, 0.2) 0%, transparent 40%);
    z-index: -1;
    animation: move-gradient 20s linear infinite;
}

@keyframes move-gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.main-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.header-section {
    text-align: center;
    color: #fafafa;
    padding: 20px 0;
    margin-bottom: 30px;
}

.header-title {
    font-family: 'Poppins', sans-serif;
    font-size: 2.8rem;
    font-weight: 700;
    margin: 0 0 10px 0;
    text-shadow: 0 0 15px rgba(102, 126, 234, 0.5);
}

.header-subtitle {
    font-family: 'Poppins', sans-serif;
    font-size: 1.1rem;
    color: #8b949e;
    margin: 0;
    font-weight: 400;
}

.main-grid {
    display: grid;
    grid-template-columns: 1.2fr 1fr;
    gap: 25px;
    margin-bottom: 30px;
}

.card {
    background: rgba(22, 27, 34, 0.7);
    backdrop-filter: blur(15px);
    border-radius: 20px;
    padding: 30px;
    border: 1px solid #30363d;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.5);
    border-color: #58a6ff;
}

.digital-clock {
    font-size: 5rem;
    font-weight: 700;
    color: #fafafa;
    margin-bottom: 15px;
    font-family: 'JetBrains Mono', monospace;
    text-shadow: 0 0 20px rgba(88, 166, 255, 0.6);
}

.clock-separator {
    animation: blink 1s infinite;
}

@keyframes blink {
    50% { opacity: 0.5; }
}

.date-display {
    font-family: 'Poppins', sans-serif;
    font-size: 1.4rem;
    color: #c9d1d9;
    margin-bottom: 10px;
    font-weight: 500;
}

.hijri-date {
    font-family: 'Poppins', sans-serif;
    font-size: 1.1rem;
    color: #8b949e;
    background: #21262d;
    padding: 8px 16px;
    border-radius: 20px;
}

.next-label {
    font-family: 'Poppins', sans-serif;
    font-size: 1.1rem;
    font-weight: 500;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 10px;
}

.next-name {
    font-family: 'Poppins', sans-serif;
    font-size: 2.5rem;
    font-weight: 700;
    color: #58a6ff;
    margin: 10px 0;
}

.next-time {
    font-size: 1.5rem;
    font-weight: 500;
    color: #c9d1d9;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 20px;
}

.countdown {
    font-family: 'Poppins', sans-serif;
    font-size: 1.2rem;
    font-weight: 500;
    color: #c9d1d9;
    background: #21262d;
    padding: 10px 20px;
    border-radius: 20px;
    width: 100%;
}

.schedule-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 20px;
}

.prayer-card {
    background: rgba(22, 27, 34, 0.7);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 25px 20px;
    text-align: center;
    border: 1px solid #30363d;
    transition: all 0.3s ease;
    color: #c9d1d9;
}

.prayer-card:hover {
    transform: translateY(-8px);
    border-color: #58a6ff;
    box-shadow: 0 8px 24px rgba(88, 166, 255, 0.2);
}

.prayer-icon {
    font-size: 2.2rem;
    margin-bottom: 10px;
}

.prayer-name {
    font-family: 'Poppins', sans-serif;
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 8px;
    color: #fafafa;
}

.prayer-time {
    font-size: 1.8rem;
    font-weight: 700;
    color: #58a6ff;
    font-family: 'JetBrains Mono', monospace;
}

.section-title {
    font-family: 'Poppins', sans-serif;
    color: #fafafa;
    font-size: 1.8rem;
    font-weight: 600;
    margin: 40px 0 20px 0;
    text-align: center;
}

.azan-notification {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 15px;
    margin: 20px 0;
    text-align: center;
    font-weight: bold;
    font-size: 1.5rem;
    animation: pulse 2s infinite;
    box-shadow: 0 8px 32px rgba(102, 126, 234, 0.4);
}

@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.02); }
    100% { transform: scale(1); }
}

.file-status {
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
    font-family: 'Poppins', sans-serif;
}

.file-found {
    background: rgba(46, 160, 67, 0.2);
    border: 1px solid #2ea043;
    color: #3fb950;
}

.file-not-found {
    background: rgba(248, 81, 73, 0.2);
    border: 1px solid #f85149;
    color: #ff7b72;
}

@media (max-width: 992px) {
    .main-grid {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 768px) {
    .schedule-grid {
        grid-template-columns: repeat(3, 1fr);
    }
    .digital-clock { font-size: 4rem; }
}

@media (max-width: 576px) {
    .schedule-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    .header-title { font-size: 2.2rem; }
    .digital-clock { font-size: 3rem; }
    .next-name { font-size: 2rem; }
    .prayer-time { font-size: 1.5rem; }
}
</style>
""", unsafe_allow_html=True)

# --- FUNGSI UNTUK MEMUTAR AZAN ---
def get_azan_file(prayer_name):
    """Mendapatkan file azan yang sesuai berdasarkan nama sholat"""
    if prayer_name in AZAN_FILES:
        audio_file = AZAN_FILES[prayer_name]
        audio_path = AUDIO_DIR / audio_file
        if audio_path.exists():
            return audio_path
    return None

def play_azan_audio(prayer_name):
    """Memutar suara azan dari file lokal menggunakan HTML5 Audio dengan base64"""
    
    azan_file = get_azan_file(prayer_name)
    
    if azan_file:
        try:
            # Baca file audio dan konversi ke base64
            with open(azan_file, "rb") as audio_file:
                audio_bytes = audio_file.read()
                audio_base64 = base64.b64encode(audio_bytes).decode()
            
            # Embed audio dengan autoplay
            st.markdown(f"""
                <audio id="azanAudio" autoplay controls style="display: none;">
                    <source src="data:audio/mpeg;base64,{audio_base64}" type="audio/mpeg">
                    Browser Anda tidak mendukung audio HTML5.
                </audio>
                <script>
                    var audio = document.getElementById('azanAudio');
                    audio.volume = 0.8;
                    
                    // Fungsi untuk memutar audio dengan user interaction
                    function playAudio() {{
                        audio.play().then(function() {{
                            console.log("Audio berhasil diputar");
                        }}).catch(function(error) {{
                            console.log("Autoplay prevented:", error);
                            // Tampilkan pesan untuk user
                            alert("Klik OK untuk memutar azan...");
                            audio.play();
                        }});
                    }}
                    
                    // Coba putar audio
                    playAudio();
                </script>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"❌ Error membaca file audio: {e}")
            # Fallback ke URL online jika file lokal error
            play_azan_online()
    else:
        # Fallback ke URL online jika file tidak ada
        play_azan_online()

def play_azan_online():
    """Fallback: Memutar azan dari URL online"""
    azan_url = "https://www.islamcan.com/audio/adhan/azan1.mp3"
    
    st.markdown(f"""
        <audio id="azanAudio" autoplay controls style="display: none;">
            <source src="{azan_url}" type="audio/mpeg">
        </audio>
        <script>
            var audio = document.getElementById('azanAudio');
            audio.volume = 0.8;
            
            function playAudio() {{
                audio.play().then(function() {{
                    console.log("Audio online berhasil diputar");
                }}).catch(function(error) {{
                    console.log("Autoplay prevented:", error);
                    alert("Klik OK untuk memutar azan...");
                    audio.play();
                }});
            }}
            
            playAudio();
        </script>
    """, unsafe_allow_html=True)

def check_audio_files():
    """Memeriksa keberadaan semua file audio azan"""
    status = {}
    for prayer_name, audio_file in AZAN_FILES.items():
        audio_path = AUDIO_DIR / audio_file
        status[prayer_name] = {
            'exists': audio_path.exists(),
            'path': str(audio_path),
            'size': f"{audio_path.stat().st_size / (1024 * 1024):.2f} MB" if audio_path.exists() else 'N/A'
        }
    return status

def check_azan_time(prayer_times_dict):
    """Memeriksa apakah sudah waktunya sholat"""
    sekarang = datetime.now()
    waktu_sekarang_str = sekarang.strftime("%H:%M")
    tanggal_sekarang = sekarang.strftime("%Y-%m-%d")
    
    # Reset azan played jika hari berganti
    if st.session_state.last_date != tanggal_sekarang:
        st.session_state.azan_played_today = {
            "Subuh": False,
            "Dzuhur": False, 
            "Ashar": False,
            "Maghrib": False,
            "Isya": False
        }
        st.session_state.last_date = tanggal_sekarang
        st.session_state.current_azan = None
    
    sholat_mapping = {
        "Subuh": "fajr",
        "Dzuhur": "dhuhr", 
        "Ashar": "asr",
        "Maghrib": "maghrib",
        "Isya": "isha"
    }
    
    for nama_sholat, key in sholat_mapping.items():
        waktu_sholat = prayer_times_dict.get(key, "00:00")
        
        # Cek jika waktu sekarang sama dengan waktu sholat
        if waktu_sholat == waktu_sekarang_str:
            if not st.session_state.azan_played_today[nama_sholat]:
                st.session_state.azan_played_today[nama_sholat] = True
                st.session_state.current_azan = nama_sholat
                return nama_sholat
    
    # Reset notifikasi setelah 1 menit
    if st.session_state.current_azan:
        for nama_sholat, key in sholat_mapping.items():
            waktu_sholat = prayer_times_dict.get(key, "00:00")
            waktu_sholat_dt = datetime.strptime(waktu_sholat, "%H:%M").replace(
                year=sekarang.year, month=sekarang.month, day=sekarang.day
            )
            if (sekarang - waktu_sholat_dt).total_seconds() > 60:
                if st.session_state.current_azan == nama_sholat:
                    st.session_state.current_azan = None
            
    return None

# --- Fungsi Backend ---
@st.cache_data(ttl=3600)
def get_prayer_times(lat, lon, date_str):
    """Mengambil data jadwal sholat dari API."""
    try:
        url = f"http://api.aladhan.com/v1/timings/{date_str}"
        params = {"latitude": lat, "longitude": lon, "method": 2}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get('code') == 200:
            timings = data['data']['timings']
            hijri = data['data']['date']['hijri']
            gregorian = data['data']['date']['gregorian']
            
            english_month = hijri['month']['en']
            indonesian_month = hijri_months_id.get(english_month, english_month)
            
            gregorian_date_obj = datetime.strptime(gregorian['date'], "%d-%m-%Y")
            gregorian_date_id = gregorian_date_obj.strftime("%A, %d %B %Y")

            return {
                'fajr': timings['Fajr'], 'dhuhr': timings['Dhuhr'],
                'asr': timings['Asr'], 'maghrib': timings['Maghrib'],
                'isha': timings['Isha'],
                'hijri_date': f"{hijri['day']} {indonesian_month} {hijri['year']} H",
                'gregorian_date_id': gregorian_date_id
            }
    except Exception as e:
        st.error(f"Error API: {e}")
        return None

def find_next_prayer(prayer_times_dict):
    """Mencari sholat berikutnya dan menghitung mundur."""
    sekarang = datetime.now()
    waktu_sekarang_str = sekarang.strftime("%H:%M")
    urutan_sholat = [("fajr", "Subuh"), ("dhuhr", "Dzuhur"), ("asr", "Ashar"), ("maghrib", "Maghrib"), ("isha", "Isya")]
    
    sholat_berikutnya = "Subuh (Besok)"
    if not prayer_times_dict: 
        return sholat_berikutnya, "00:00", "Memuat..."
    
    waktu_sholat_berikutnya = prayer_times_dict.get("fajr", "00:00")
    
    ditemukan_sholat_hari_ini = False
    for key, nama in urutan_sholat:
        if prayer_times_dict.get(key, "99:99") > waktu_sekarang_str:
            sholat_berikutnya = nama
            waktu_sholat_berikutnya = prayer_times_dict[key]
            ditemukan_sholat_hari_ini = True
            break

    waktu_berikutnya_dt = datetime.strptime(waktu_sholat_berikutnya, "%H:%M").replace(
        year=sekarang.year, month=sekarang.month, day=sekarang.day
    )
    
    if not ditemukan_sholat_hari_ini:
        waktu_berikutnya_dt += timedelta(days=1)
        
    selisih = waktu_berikutnya_dt - sekarang
    detik_selisih = selisih.total_seconds()
    jam = int(detik_selisih // 3600)
    menit = int((detik_selisih % 3600) // 60)
    detik = int(detik_selisih % 60)
    
    return sholat_berikutnya, waktu_sholat_berikutnya, f"{jam:02d}:{menit:02d}:{detik:02d}"

# --- UI Utama ---
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="header-section">
        <h1 class="header-title">🕌 Aplikasi Jadwal Sholat</h1>
        <p class="header-subtitle">Waktu sholat terkini dengan notifikasi azan otomatis</p>
    </div>
""", unsafe_allow_html=True)

# --- SIDEBAR INFORMASI ---
with st.sidebar:
    st.header("📊 Informasi Aplikasi")
    
    # Status File Audio
    st.subheader("🔊 Status Audio Azan")
    audio_status = check_audio_files()
    
    subuh_ready = audio_status["Subuh"]['exists']
    others_ready = all(audio_status[prayer]['exists'] for prayer in ["Dzuhur", "Ashar", "Maghrib", "Isya"])
    
    if subuh_ready and others_ready:
        st.success("✅ Semua file azan tersedia")
        st.info("**Konfigurasi Audio:**\n- Subuh: fajr_128_44.mp3\n- Lainnya: Adzan-Misyari-Rasyid.mp3")
    elif subuh_ready:
        st.warning("⚠️ File azan Subuh tersedia, lainnya menggunakan fallback")
    elif others_ready:
        st.warning("⚠️ File azan Dzuhur-Isya tersedia, Subuh menggunakan fallback")
    else:
        st.error("❌ File azan tidak ditemukan, menggunakan audio online")
    
    st.divider()
    
    # Informasi Lokasi
    st.subheader("📍 Lokasi")
    st.write("**Kota:** Medan")
    st.write("**Koordinat:** 3.5952° N, 98.6722° E")
    
    st.divider()
    
    # Status Azan Hari Ini
    st.subheader("🕒 Status Azan Hari Ini")
    for sholat, status in st.session_state.azan_played_today.items():
        icon = "✅" if status else "⏳"
        st.write(f"{icon} **{sholat}**: {'Sudah' if status else 'Belum'} diputar")

# Data lokasi
lat, lon = 3.5952, 98.6722  # Koordinat Kota Medan
hari_ini = datetime.now()
data_sholat = get_prayer_times(lat, lon, hari_ini.strftime("%d-%m-%Y"))

if data_sholat:
    # Cek waktu azan
    sholat_sekarang = check_azan_time(data_sholat)
    
    # Tampilkan notifikasi dan putar azan jika waktunya
    if st.session_state.current_azan:
        display_name = st.session_state.current_azan.upper()
        st.markdown(
            f'<div class="azan-notification">🕌 WAKTU SHOLAT {display_name} 🕌</div>', 
            unsafe_allow_html=True
        )
        play_azan_audio(st.session_state.current_azan)
    
    # Format waktu dan tanggal
    waktu_sekarang = datetime.now()
    format_waktu = waktu_sekarang.strftime("%H<span class='clock-separator'>:</span>%M<span class='clock-separator'>:</span>%S")
    tanggal_gregorian = data_sholat.get('gregorian_date_id', "Memuat...")
    tanggal_hijriyah = data_sholat.get("hijri_date", "Memuat...")
    
    # Cari sholat berikutnya
    nama_sholat_berikutnya, waktu_sholat_berikutnya, hitung_mundur = find_next_prayer(data_sholat)
    
    # Grid utama (Jam dan Sholat Berikutnya)
    st.markdown(f'''
    <div class="main-grid">
        <div class="card">
            <div class="digital-clock">{format_waktu}</div>
            <div class="date-display">{tanggal_gregorian}</div>
            <div class="hijri-date">{tanggal_hijriyah}</div>
        </div>
        <div class="card">
            <div class="next-label">Sholat Berikutnya</div>
            <div class="next-name">{nama_sholat_berikutnya}</div>
            <div class="next-time">{waktu_sholat_berikutnya}</div>
            <div class="countdown">⏳ {hitung_mundur}</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Jadwal Sholat Hari Ini
    st.markdown('<div class="section-title">📅 Jadwal Sholat Hari Ini</div>', unsafe_allow_html=True)
    
    daftar_sholat = [
        ("Subuh", data_sholat['fajr'], "🌙"), 
        ("Dzuhur", data_sholat['dhuhr'], "☀️"),
        ("Ashar", data_sholat['asr'], "🌤️"), 
        ("Maghrib", data_sholat['maghrib'], "🌆"),
        ("Isya", data_sholat['isha'], "🌃")
    ]
    
    kolom = st.columns(5)
    for i, (nama, waktu, ikon) in enumerate(daftar_sholat):
        with kolom[i]:
            st.markdown(f'''
            <div class="prayer-card">
                <div class="prayer-icon">{ikon}</div>
                <div class="prayer-name">{nama}</div>
                <div class="prayer-time">{waktu}</div>
            </div>
            ''', unsafe_allow_html=True)
    
    # Informasi tambahan
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("""
        **Fitur Aplikasi:**
        - ✅ Jadwal sholat otomatis untuk Kota Medan
        - ✅ Notifikasi azan tepat waktu
        - ✅ Audio azan berbeda untuk Subuh dan sholat lainnya
        - ✅ Tampilan responsif untuk semua device
        - ✅ Kalender Hijriyah dan Masehi
        - ✅ Auto-refresh setiap 10 detik
        """)
    with col2:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
    
else:
    st.error("❌ Gagal mengambil data jadwal sholat. Periksa koneksi internet Anda.")

st.markdown('</div>', unsafe_allow_html=True)

# Auto-refresh dengan logic yang lebih baik
current_time = datetime.now()
if (current_time - st.session_state.last_refresh).total_seconds() > 10:
    st.session_state.last_refresh = current_time
    st.rerun()
import streamlit as st
from datetime import datetime, timedelta
import requests
import time as time_module
import locale
import base64
import os
from pathlib import Path
import pytz

# --- LOKALISASI & KONFIGURASI ZONA WAKTU ---
try:
    locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')
except locale.Error:
    pass

WIB = pytz.timezone('Asia/Jakarta')

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
        "Subuh": False, "Dzuhur": False, "Ashar": False, "Maghrib": False, "Isya": False
    }
if 'current_azan' not in st.session_state:
    st.session_state.current_azan = None
if 'last_date' not in st.session_state:
    st.session_state.last_date = datetime.now(WIB).strftime("%Y-%m-%d")
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now(WIB)

# --- PATH FIX untuk Streamlit Cloud ---
BASE_DIR = Path(__file__).parent
AUDIO_DIR = BASE_DIR / "assets" / "audio"

AZAN_FILES = {
    "Subuh": "fajr_128_44.mp3",
    "Dzuhur": "Adzan-Misyari-Rasyid.mp3",
    "Ashar": "Adzan-Misyari-Rasyid.mp3",
    "Maghrib": "Adzan-Misyari-Rasyid.mp3",
    "Isya": "Adzan-Misyari-Rasyid.mp3"
}

# --- CSS BARU (disesuaikan dengan tema Al-Quran) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap');

.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #1a1f35 100%);
    color: #c9d1d9;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1419 0%, #1a1f2e 100%);
    border-right: 1px solid #2d3748;
}
.main-container { max-width: 1200px; margin: 0 auto; padding: 20px; }
.main-header { text-align: center; color: #fafafa; padding: 2rem 1rem; margin-bottom: 30px; background: linear-gradient(135deg, rgba(0, 170, 255, 0.1) 0%, rgba(0, 212, 255, 0.05) 100%); border-radius: 20px; border: 1px solid rgba(0, 170, 255, 0.2); }
.header-title { font-family: 'Poppins', sans-serif; font-size: 2.8rem; font-weight: 700; margin: 0 0 10px 0; text-shadow: 0 0 15px rgba(0, 212, 255, 0.5); color: #ffffff; }
.header-subtitle { font-family: 'Poppins', sans-serif; font-size: 1.1rem; color: #8b949e; margin: 0; font-weight: 400; }
.main-grid { display: grid; grid-template-columns: 1.2fr 1fr; gap: 25px; margin-bottom: 30px; }
.card { background: rgba(22, 27, 34, 0.8); backdrop-filter: blur(15px); border-radius: 20px; padding: 30px; border: 1px solid #30363d; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37); height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; transition: transform 0.3s ease, box-shadow 0.3s ease; }
.card:hover { transform: translateY(-5px); box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.5); border-color: #00aaff; }
.digital-clock { font-size: 5rem; font-weight: 700; color: #fafafa; margin-bottom: 15px; font-family: 'JetBrains Mono', monospace; text-shadow: 0 0 20px rgba(0, 212, 255, 0.6); }
.clock-separator { animation: blink 1s infinite; }
@keyframes blink { 50% { opacity: 0.5; } }
.date-display { font-family: 'Poppins', sans-serif; font-size: 1.4rem; color: #c9d1d9; margin-bottom: 10px; font-weight: 500; }
.hijri-date { font-family: 'Poppins', sans-serif; font-size: 1.1rem; color: #8b949e; background: #21262d; padding: 8px 16px; border-radius: 20px; }
.next-label { font-family: 'Poppins', sans-serif; font-size: 1.1rem; font-weight: 500; color: #8b949e; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 10px; }
.next-name { font-family: 'Poppins', sans-serif; font-size: 2.5rem; font-weight: 700; color: #00d4ff; margin: 10px 0; }
.next-time { font-size: 1.5rem; font-weight: 500; color: #c9d1d9; font-family: 'JetBrains Mono', monospace; margin-bottom: 20px; }
.countdown { font-family: 'Poppins', sans-serif; font-size: 1.2rem; font-weight: 500; color: #c9d1d9; background: #21262d; padding: 10px 20px; border-radius: 20px; width: 100%; }
.schedule-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 20px; }
.prayer-card { background: rgba(22, 27, 34, 0.8); backdrop-filter: blur(10px); border-radius: 15px; padding: 25px 20px; text-align: center; border: 1px solid #30363d; transition: all 0.3s ease; color: #c9d1d9; }
.prayer-card:hover { transform: translateY(-8px); border-color: #00aaff; box-shadow: 0 8px 24px rgba(0, 170, 255, 0.2); }
.prayer-icon { font-size: 2.2rem; margin-bottom: 10px; }
.prayer-name { font-family: 'Poppins', sans-serif; font-size: 1.1rem; font-weight: 600; margin-bottom: 8px; color: #fafafa; }
.prayer-time { font-size: 1.8rem; font-weight: 700; color: #00d4ff; font-family: 'JetBrains Mono', monospace; }
.section-title { font-family: 'Poppins', sans-serif; color: #fafafa; font-size: 1.8rem; font-weight: 600; margin: 40px 0 20px 0; text-align: center; }
.azan-notification { background: linear-gradient(135deg, #00aaff 0%, #00d4ff 100%); color: white; padding: 20px; border-radius: 15px; margin: 20px 0; text-align: center; font-weight: bold; font-size: 1.5rem; animation: pulse 2s infinite; box-shadow: 0 8px 32px rgba(0, 170, 255, 0.4); }
@keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.02); } 100% { transform: scale(1); } }
.feature-box { background: rgba(22, 27, 34, 0.7); border: 1px solid #30363d; border-radius: 15px; padding: 25px; margin-top: 20px; transition: all 0.3s ease; }
.feature-box:hover { border-color: #00aaff; }
.feature-list { list-style-type: none; padding-left: 0; margin: 0; }
.feature-item { display: flex; align-items: center; margin-bottom: 12px; font-size: 0.95rem; color: #c9d1d9; }
.feature-icon { color: #3fb950; margin-right: 12px; font-size: 1.2rem; font-weight: bold; }
.refresh-button-wrapper .stButton button { border: 1px solid #00aaff; background-color: transparent; color: #00aaff; transition: all 0.3s ease; border-radius: 10px; height: 50px; margin-top: 20px; }
.refresh-button-wrapper .stButton button:hover { background-color: #00aaff; color: white; transform: translateY(-2px); box-shadow: 0 0 15px rgba(0, 170, 255, 0.5); }
.refresh-button-wrapper .stButton button:focus { box-shadow: 0 0 15px rgba(0, 170, 255, 0.5) !important; }
@media (max-width: 992px) { .main-grid { grid-template-columns: 1fr; } }
@media (max-width: 768px) { .schedule-grid { grid-template-columns: repeat(3, 1fr); } .digital-clock { font-size: 4rem; } }
@media (max-width: 576px) { .schedule-grid { grid-template-columns: repeat(2, 1fr); } .header-title { font-size: 2.2rem; } .digital-clock { font-size: 3rem; } .next-name { font-size: 2rem; } .prayer-time { font-size: 1.5rem; } }
</style>
""", unsafe_allow_html=True)

# --- (Sisa fungsi-fungsi Anda tetap sama, tidak perlu diubah) ---
def get_azan_file(prayer_name):
    if prayer_name in AZAN_FILES:
        audio_path = AUDIO_DIR / AZAN_FILES[prayer_name]
        if audio_path.exists():
            return audio_path
    return None
def play_azan_audio(prayer_name):
    azan_file = get_azan_file(prayer_name)
    if azan_file:
        try:
            with open(azan_file, "rb") as f:
                audio_bytes = f.read()
            audio_base64 = base64.b64encode(audio_bytes).decode()
            st.markdown(f'<audio autoplay><source src="data:audio/mpeg;base64,{audio_base64}" type="audio/mpeg"></audio>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"❌ Error membaca file audio: {e}")
            play_azan_online()
    else:
        play_azan_online()
def play_azan_online():
    azan_url = "https://www.islamcan.com/audio/adhan/azan1.mp3"
    st.markdown(f'<audio autoplay><source src="{azan_url}" type="audio/mpeg"></audio>', unsafe_allow_html=True)
def check_audio_files():
    status = {}
    for prayer_name, audio_file in AZAN_FILES.items():
        audio_path = AUDIO_DIR / audio_file
        status[prayer_name] = {'exists': audio_path.exists()}
    return status
def check_azan_time(prayer_times_dict):
    sekarang = datetime.now(WIB)
    waktu_sekarang_str = sekarang.strftime("%H:%M")
    tanggal_sekarang = sekarang.strftime("%Y-%m-%d")
    if st.session_state.last_date != tanggal_sekarang:
        st.session_state.azan_played_today = {k: False for k in st.session_state.azan_played_today}
        st.session_state.last_date = tanggal_sekarang
        st.session_state.current_azan = None
    sholat_mapping = {"Subuh": "fajr", "Dzuhur": "dhuhr", "Ashar": "asr", "Maghrib": "maghrib", "Isya": "isha"}
    for nama_sholat, key in sholat_mapping.items():
        waktu_sholat = prayer_times_dict.get(key, "00:00")
        if waktu_sholat == waktu_sekarang_str and not st.session_state.azan_played_today[nama_sholat]:
            st.session_state.azan_played_today[nama_sholat] = True
            st.session_state.current_azan = nama_sholat
            return nama_sholat
    if st.session_state.current_azan:
        nama_sholat_aktif = st.session_state.current_azan
        key_sholat_aktif = sholat_mapping[nama_sholat_aktif]
        waktu_sholat_aktif_str = prayer_times_dict.get(key_sholat_aktif, "00:00")
        waktu_sholat_dt = WIB.localize(datetime.strptime(waktu_sholat_aktif_str, "%H:%M").replace(year=sekarang.year, month=sekarang.month, day=sekarang.day))
        if (sekarang - waktu_sholat_dt).total_seconds() > 60:
            st.session_state.current_azan = None
    return None
@st.cache_data(ttl=3600)
def get_prayer_times(lat, lon, date_str):
    try:
        url = f"http://api.aladhan.com/v1/timings/{date_str}"
        params = {"latitude": lat, "longitude": lon, "method": 2}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get('code') == 200:
            timings = data['data']['timings']; hijri = data['data']['date']['hijri']; gregorian = data['data']['date']['gregorian']
            english_month = hijri['month']['en']; indonesian_month = hijri_months_id.get(english_month, english_month)
            gregorian_date_obj = datetime.strptime(gregorian['date'], "%d-%m-%Y"); gregorian_date_id = gregorian_date_obj.strftime("%A, %d %B %Y")
            return {'fajr': timings['Fajr'], 'dhuhr': timings['Dhuhr'], 'asr': timings['Asr'], 'maghrib': timings['Maghrib'], 'isha': timings['Isha'], 'hijri_date': f"{hijri['day']} {indonesian_month} {hijri['year']} H", 'gregorian_date_id': gregorian_date_id}
    except Exception as e:
        st.error(f"Error API: {e}"); return None
def find_next_prayer(prayer_times_dict):
    sekarang = datetime.now(WIB); urutan_sholat = [("fajr", "Subuh"), ("dhuhr", "Dzuhur"), ("asr", "Ashar"), ("maghrib", "Maghrib"), ("isha", "Isya")]
    if not prayer_times_dict: return "Subuh (Besok)", "00:00", "Memuat..."
    for key, nama in urutan_sholat:
        waktu_sholat_str = prayer_times_dict.get(key)
        if waktu_sholat_str > sekarang.strftime("%H:%M"):
            sholat_berikutnya = nama; waktu_sholat_berikutnya_str = waktu_sholat_str; break
    else:
        sholat_berikutnya = "Subuh (Besok)"; waktu_sholat_berikutnya_str = prayer_times_dict.get("fajr", "00:00")
    waktu_berikutnya_dt = WIB.localize(datetime.strptime(waktu_sholat_berikutnya_str, "%H:%M").replace(year=sekarang.year, month=sekarang.month, day=sekarang.day))
    if "Besok" in sholat_berikutnya or waktu_berikutnya_dt < sekarang: waktu_berikutnya_dt += timedelta(days=1)
    selisih = waktu_berikutnya_dt - sekarang; jam, sisa = divmod(selisih.total_seconds(), 3600); menit, detik = divmod(sisa, 60)
    return sholat_berikutnya, waktu_sholat_berikutnya_str, f"{int(jam):02d}:{int(menit):02d}:{int(detik):02d}"
def display_footer():
    st.markdown("---")
    st.markdown("""
    <div style='margin-top: 1.5rem; padding: 1rem; background: rgba(0, 0, 0, 0.3); border-radius: 8px;'>
        <p style='color: #888; font-size: 0.85rem; margin: 0; font-style: italic;'>
            "Dirikanlah shalat dari sesudah matahari tergelincir sampai gelap malam dan (dirikanlah pula shalat) subuh. Sesungguhnya shalat subuh itu disaksikan (oleh malaikat)."<br>
            <span style='color: #00aaff;'>(QS. Al-Isra': 78)</span>
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style='margin-top: 1.5rem; text-align: center;'>
        <p style='color: #666; font-size: 0.8rem; margin: 0.3rem 0;'>© 2025 Jadwal Sholat Digital</p>
        <p style='color: #666; font-size: 0.8rem; margin: 0.3rem 0;'>Developed with ❤️ for Hamba Allah</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.markdown('<div class="main-header"><h1 class="header-title">🕌 Aplikasi Jadwal Sholat</h1><p class="header-subtitle">Waktu sholat terkini dengan notifikasi azan otomatis</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("📊 Informasi Aplikasi")
    with st.expander("Tampilkan Detail & Status"):
        st.subheader("🔊 Status Audio Azan")
        audio_status = check_audio_files(); subuh_ready = audio_status["Subuh"]['exists']; others_ready = all(audio_status[p]['exists'] for p in ["Dzuhur", "Ashar", "Maghrib", "Isya"])
        if subuh_ready and others_ready: st.success("✅ Semua file azan tersedia"); st.info("**Konfigurasi Audio:**\n- Subuh: fajr_128_44.mp3\n- Lainnya: Adzan-Misyari-Rasyid.mp3")
        elif subuh_ready: st.warning("⚠️ File azan Subuh tersedia, lainnya menggunakan fallback")
        elif others_ready: st.warning("⚠️ File azan Dzuhur-Isya tersedia, Subuh menggunakan fallback")
        else: st.error("❌ File azan tidak ditemukan, menggunakan audio online")
        st.divider(); st.subheader("📍 Lokasi"); st.write("**Kota:** Medan"); st.write("**Koordinat:** 3.5952° N, 98.6722° E"); st.divider()
        st.subheader("🕒 Status Azan Hari Ini")
        for sholat, status in st.session_state.azan_played_today.items():
            st.write(f"{'✅' if status else '⏳'} **{sholat}**: {'Sudah' if status else 'Belum'}")

lat, lon = 3.5952, 98.6722
hari_ini_str = datetime.now(WIB).strftime("%d-%m-%Y")
data_sholat = get_prayer_times(lat, lon, hari_ini_str)

if data_sholat:
    sholat_sekarang = check_azan_time(data_sholat)
    if st.session_state.current_azan:
        st.markdown(f'<div class="azan-notification">🕌 WAKTU SHOLAT {st.session_state.current_azan.upper()} 🕌</div>', unsafe_allow_html=True)
        play_azan_audio(st.session_state.current_azan)
    waktu_sekarang = datetime.now(WIB); format_waktu = waktu_sekarang.strftime("%H<span class='clock-separator'>:</span>%M<span class='clock-separator'>:</span>%S")
    nama_sholat_berikutnya, waktu_sholat_berikutnya, hitung_mundur = find_next_prayer(data_sholat)
    st.markdown(f'''
    <div class="main-grid">
        <div class="card"><div class="digital-clock">{format_waktu}</div><div class="date-display">{data_sholat.get('gregorian_date_id', "...")}</div><div class="hijri-date">{data_sholat.get("hijri_date", "...")}</div></div>
        <div class="card"><div class="next-label">Sholat Berikutnya</div><div class="next-name">{nama_sholat_berikutnya}</div><div class="next-time">{waktu_sholat_berikutnya}</div><div class="countdown">⏳ {hitung_mundur}</div></div>
    </div>''', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📅 Jadwal Sholat Hari Ini</div>', unsafe_allow_html=True)
    daftar_sholat = [("Subuh", data_sholat['fajr'], "🌙"), ("Dzuhur", data_sholat['dhuhr'], "☀️"), ("Ashar", data_sholat['asr'], "🌤️"), ("Maghrib", data_sholat['maghrib'], "🌆"), ("Isya", data_sholat['isha'], "🌃")]
    kolom = st.columns(5)
    for i, (nama, waktu, ikon) in enumerate(daftar_sholat):
        with kolom[i]:
            st.markdown(f'<div class="prayer-card"><div class="prayer-icon">{ikon}</div><div class="prayer-name">{nama}</div><div class="prayer-time">{waktu}</div></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div class="feature-box">', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""<h4 style="font-family: 'Poppins', sans-serif; color: #fafafa; margin-top: 0; margin-bottom: 15px;">Fitur Aplikasi</h4><ul class="feature-list"><li class="feature-item"><span class="feature-icon">✓</span> Jadwal sholat otomatis untuk Kota Medan</li><li class="feature-item"><span class="feature-icon">✓</span> Notifikasi azan tepat waktu</li><li class="feature-item"><span class="feature-icon">✓</span> Audio azan berbeda untuk Subuh</li><li class="feature-item"><span class="feature-icon">✓</span> Kalender Hijriyah & Masehi</li><li class="feature-item"><span class="feature-icon">✓</span> Auto-refresh</li></ul>""", unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="refresh-button-wrapper">', unsafe_allow_html=True)
        if st.button("🔄 Refresh Data", use_container_width=True): st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.error("❌ Gagal mengambil data jadwal sholat. Periksa koneksi internet Anda.")

display_footer()
st.markdown('</div>', unsafe_allow_html=True)
time_module.sleep(1)
st.rerun()

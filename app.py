import io
import json
import os
import random
import sqlite3
import hashlib
import urllib.request
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google import genai

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
import streamlit as st

# Map rendering libraries
import folium
from streamlit_folium import st_folium

# -------------------------------------------------------------------
# Environment & Configuration
# -------------------------------------------------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

st.set_page_config(
    page_title="RailxAI Express - AI Reservation & Tracking Portal",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------------
# Optimized Glassmorphism CSS
# -------------------------------------------------------------------
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background: radial-gradient(circle at top right, #1e1b4b 0%, #090d16 50%, #030712 100%);
        color: #f1f5f9;
    }
    
    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.9) 0%, rgba(49, 46, 129, 0.9) 50%, rgba(67, 56, 202, 0.8) 100%);
        backdrop-filter: blur(12px);
        padding: 28px;
        border-radius: 20px;
        box-shadow: 0 15px 35px -15px rgba(67, 56, 202, 0.4);
        margin-bottom: 24px;
        border: 1px solid rgba(255, 255, 255, 0.12);
    }
    .hero-title {
        font-size: 32px;
        font-weight: 800;
        color: #ffffff;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        font-size: 14px;
        color: #c7d2fe;
        margin-top: 6px;
        line-height: 1.5;
    }

    /* Auth Page Cards */
    .auth-form-card {
        background: rgba(15, 23, 42, 0.85);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 24px;
        padding: 32px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
    }

    .feature-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(99, 102, 241, 0.25);
        border: 1px solid rgba(165, 180, 252, 0.4);
        color: #e0e7ff;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
    }

    .metric-card {
        background: rgba(15, 23, 42, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 14px 10px;
        text-align: center;
    }

    /* Train & Policy Cards */
    .train-card {
        background: rgba(18, 24, 38, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 18px;
        margin-bottom: 14px;
    }
    .policy-card {
        background: rgba(18, 24, 38, 0.75);
        border-left: 4px solid #6366f1;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 14px;
    }
    
    /* Enhanced Live Tracking Cards */
    .tracking-card {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 18px;
        padding: 22px;
        margin-bottom: 18px;
    }
    .weather-grid-card {
        background: rgba(30, 41, 59, 0.7);
        border-left: 3px solid #38bdf8;
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 12px;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* Badges */
    .badge-tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
    }
    .badge-seats { background: rgba(34, 197, 94, 0.15); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.3); }
    .badge-fare { background: rgba(99, 102, 241, 0.15); color: #a5b4fc; border: 1px solid rgba(99, 102, 241, 0.3); }
    .badge-ontime { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-live { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        width: 100%;
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.4) !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%) !important;
    }

    /* Large Progress Bar */
    .progress-bar-container-lg {
        width: 100%;
        background-color: rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        overflow: hidden;
        height: 14px;
        margin: 14px 0 20px 0;
    }
    .progress-bar-fill-lg {
        height: 100%;
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 50%, #22c55e 100%);
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# Cached Weather Fetcher
# -------------------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def get_station_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        req = urllib.request.Request(url, headers={'User-Agent': 'RailXApp'})
        with urllib.request.urlopen(req, timeout=1.0) as response:
            data = json.loads(response.read().decode())
            current = data.get("current_weather", {})
            temp = current.get("temperature", "28")
            code = current.get("weathercode", 0)
            wind = current.get("windspeed", "12")
            
            weather_codes = {
                0: "☀️ Clear Sky", 1: "🌤️ Fair", 2: "⛅ Partly Cloudy", 3: "☁️ Overcast",
                45: "🌫️ Dense Fog", 51: "🌦️ Light Drizzle", 61: "🌧️ Heavy Rain", 95: "⛈️ Thunderstorm"
            }
            return {
                "temp": f"{temp}°C",
                "condition": weather_codes.get(code, "🌤️ Fair"),
                "wind": f"{wind} km/h"
            }
    except Exception:
        return {"temp": "28°C", "condition": "☀️ Clear Sky", "wind": "10 km/h"}

# -------------------------------------------------------------------
# Database Setup
# -------------------------------------------------------------------
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def get_db_connection():
    conn = sqlite3.connect("railway.db", timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT,
                email TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                pnr TEXT PRIMARY KEY,
                username TEXT,
                passenger_name TEXT,
                passenger_age INTEGER,
                train_no TEXT,
                train_name TEXT,
                from_station TEXT,
                to_station TEXT,
                fare INTEGER,
                status TEXT
            )
        ''')

init_db()

def create_user(username, password, email):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('INSERT INTO users(username, password, email) VALUES (?,?,?)', (username, make_hashes(password), email))

def login_user(username, password):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, make_hashes(password)))
        return c.fetchall()

def pnr_exists(pnr):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT 1 FROM bookings WHERE pnr = ?', (pnr,))
        return c.fetchone() is not None

def generate_unique_pnr():
    while True:
        pnr = str(random.randint(1000000000, 9999999999))
        if not pnr_exists(pnr):
            return pnr

def save_booking_to_db(booking):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO bookings (
                pnr, username, passenger_name, passenger_age, train_no, 
                train_name, from_station, to_station, fare, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            booking['pnr'], booking['username'], booking['passenger_name'],
            booking['passenger_age'], booking['train_no'], booking['train_name'],
            booking['from_station'], booking['to_station'], booking['fare'], booking['status']
        ))

def get_user_bookings(username):
    with get_db_connection() as conn:
        return pd.read_sql_query(
            "SELECT pnr, username, passenger_name, passenger_age, train_no, train_name, from_station, to_station, fare, status FROM bookings WHERE username = ?", 
            conn, params=(username,)
        )

def get_booking_by_pnr(pnr, username):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM bookings WHERE pnr = ? AND username = ?', (pnr, username))
        return c.fetchone()

# -------------------------------------------------------------------
# PDF Generator
# -------------------------------------------------------------------
def generate_pdf_ticket(booking_data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('HeaderStyle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor("#1e1b4b"), alignment=1, spaceAfter=10)
    story.append(Paragraph("<b>RailX Express E-Ticket</b>", title_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#4338ca"), spaceAfter=15))
    
    table_data = [
        ["PNR Number:", booking_data['pnr'], "Status:", booking_data['status']],
        ["Passenger Name:", booking_data['passenger_name'], "Passenger Age:", str(booking_data['passenger_age'])],
        ["Train:", f"{booking_data['train_no']} - {booking_data['train_name']}", "Total Fare:", f"INR {booking_data['fare']}"],
        ["From Station:", booking_data['from_station'], "To Station:", booking_data['to_station']]
    ]
    
    t = Table(table_data, colWidths=[110, 160, 110, 160])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor("#0f172a")),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(t)
    story.append(Spacer(1, 20))
    footer_style = ParagraphStyle('FooterStyle', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor("#64748b"), alignment=1)
    story.append(Paragraph("Wish you a safe journey. Please carry a valid Photo ID.", footer_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# -------------------------------------------------------------------
# Datasets
# -------------------------------------------------------------------
TRAINS = pd.DataFrame([
    {"Train No": "12952", "Name": "Mumbai Rajdhani Express", "From": "New Delhi", "To": "Mumbai", "Departure": "16:55", "Duration": "15h 35m", "Seats Available": 14, "Fare (INR)": 2400},
    {"Train No": "12002", "Name": "Shatabdi Express", "From": "New Delhi", "To": "Bhopal", "Departure": "06:00", "Duration": "8h 30m", "Seats Available": 42, "Fare (INR)": 1150},
    {"Train No": "12626", "Name": "Kerala Express", "From": "New Delhi", "To": "Kochi", "Departure": "20:10", "Duration": "40h 00m", "Seats Available": 6, "Fare (INR)": 3100},
    {"Train No": "22436", "Name": "Vande Bharat Express", "From": "New Delhi", "To": "Varanasi", "Departure": "06:00", "Duration": "8h 00m", "Seats Available": 29, "Fare (INR)": 1750}
])

LIVE_ROUTES = {
    "12952": [
        {"station": "New Delhi (NDLS)", "sch_dep": "16:55", "dist_km": 0, "lat": 28.6424, "lon": 77.2195, "status": "Departed"},
        {"station": "Kota Jn (KOTA)", "sch_dep": "21:05", "dist_km": 465, "lat": 25.2138, "lon": 75.8648, "status": "Current Stop"},
        {"station": "Ratlam Jn (RTM)", "sch_dep": "00:35", "dist_km": 731, "lat": 23.3342, "lon": 75.0376, "status": "Upcoming"},
        {"station": "Vadodara Jn (BRC)", "sch_dep": "04:00", "dist_km": 992, "lat": 22.3106, "lon": 73.1812, "status": "Upcoming"},
        {"station": "Mumbai Central (MMCT)", "sch_dep": "08:30", "dist_km": 1384, "lat": 18.9696, "lon": 72.8193, "status": "Destination"}
    ],
    "12002": [
        {"station": "New Delhi (NDLS)", "sch_dep": "06:00", "dist_km": 0, "lat": 28.6424, "lon": 77.2195, "status": "Departed"},
        {"station": "Agra Cantt (AGC)", "sch_dep": "07:50", "dist_km": 195, "lat": 27.1577, "lon": 78.0081, "status": "Departed"},
        {"station": "Gwalior (GWL)", "sch_dep": "09:23", "dist_km": 313, "lat": 26.2124, "lon": 78.1772, "status": "Current Stop"},
        {"station": "VGL Jhansi (VGLJ)", "sch_dep": "10:45", "dist_km": 411, "lat": 25.4484, "lon": 78.5685, "status": "Upcoming"},
        {"station": "Bhopal (BPL)", "sch_dep": "14:30", "dist_km": 703, "lat": 23.2599, "lon": 77.4126, "status": "Destination"}
    ],
    "12626": [
        {"station": "New Delhi (NDLS)", "sch_dep": "20:10", "dist_km": 0, "lat": 28.6424, "lon": 77.2195, "status": "Departed"},
        {"station": "Nagpur (NGP)", "sch_dep": "10:30", "dist_km": 1090, "lat": 21.1524, "lon": 79.0882, "status": "Current Stop"},
        {"station": "Vijayawada (BZA)", "sch_dep": "20:40", "dist_km": 1755, "lat": 16.5193, "lon": 80.6305, "status": "Upcoming"},
        {"station": "Ernakulam/Kochi (ERS)", "sch_dep": "12:10", "dist_km": 2812, "lat": 9.9708, "lon": 76.2847, "status": "Destination"}
    ],
    "22436": [
        {"station": "New Delhi (NDLS)", "sch_dep": "06:00", "dist_km": 0, "lat": 28.6424, "lon": 77.2195, "status": "Departed"},
        {"station": "Kanpur Central (CNB)", "sch_dep": "10:08", "dist_km": 440, "lat": 26.4537, "lon": 80.3512, "status": "Departed"},
        {"station": "Prayagraj Jn (PRYJ)", "sch_dep": "12:08", "dist_km": 634, "lat": 25.4414, "lon": 81.8258, "status": "Current Stop"},
        {"station": "Varanasi Jn (BSB)", "sch_dep": "14:00", "dist_km": 755, "lat": 25.3176, "lon": 82.9876, "status": "Destination"}
    ]
}

RAILWAY_POLICIES = [
    {
        "category": "🧳 Baggage Allowance & Limits",
        "description": "Maximum free baggage limit varies by travel class. Excess baggage is charged at normal freight rates.",
        "details": [
            "AC First Class: Free limit up to 70 kg",
            "AC 2-Tier / Executive Class: Free limit up to 50 kg",
            "AC 3-Tier / AC Chair Car: Free limit up to 40 kg",
            "Sleeper Class: Free limit up to 40 kg"
        ]
    },
    {
        "category": "💸 Ticket Cancellation & Refunds",
        "description": "Cancellation charges depend on time remaining before scheduled train departure.",
        "details": [
            "> 48 Hours before departure: Flat deduction (AC 1st/Executive: ₹240, AC 2-Tier: ₹200, AC 3-Tier: ₹180, Sleeper: ₹120).",
            "Between 48 Hours & 12 Hours: 25% deduction of total fare.",
            "< 4 Hours / After chart preparation: No refund on confirmed tickets."
        ]
    }
]

# -------------------------------------------------------------------
# Session State
# -------------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "last_booking" not in st.session_state:
    st.session_state.last_booking = None

# -------------------------------------------------------------------
# Sidebar
# -------------------------------------------------------------------
with st.sidebar:
    st.title("RailxAI Dashboard")
    if st.session_state.logged_in:
        st.success(f"👤 **{st.session_state.username}**")
        if st.button("🚪 Log Out"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.last_booking = None
            st.rerun()
            
        st.markdown("---")
        if not GEMINI_API_KEY:
            GEMINI_API_KEY = st.text_input("Gemini API Key", type="password")
            
        st.markdown("---")
        user_df = get_user_bookings(st.session_state.username)
        st.metric("Total Trips", len(user_df))
        st.metric("Total Spent", f"₹ {user_df['fare'].sum() if not user_df.empty else 0}")
    else:
        st.info("🔒 Sign in to access portal.")

# -------------------------------------------------------------------
# Main Application Flow
# -------------------------------------------------------------------
if not st.session_state.logged_in:
    col_left, col_right = st.columns([1.1, 0.9], gap="large")

    with col_left:
        st.markdown("""
            <div style="background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%); border-radius: 20px; padding: 32px; border: 1px solid rgba(255,255,255,0.15);">
                <div class="feature-badge">⚡ RailxAI Express Portal 🚆</div>
                <h1 style="font-size: 38px; font-weight: 800; color: #ffffff; line-height: 1.1; margin-top: 14px;">
                    Next-Gen Transit <br><span style="color: #818cf8;">& Live Radar</span> 🧳
                </h1>
                <p style="color: #cbd5e1; font-size: 14px; margin-top: 12px; line-height: 1.5;">
                    Lightning-fast reservations, live route GPS telemetry, atmospheric weather tracking, and e-tickets.
                </p>
            </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="auth-form-card">', unsafe_allow_html=True)
        auth_mode = st.radio("Mode", ["🔓 Sign In", "🚀 Register"], horizontal=True, label_visibility="collapsed")
        st.markdown("<br>", unsafe_allow_html=True)

        if "Sign In" in auth_mode:
            st.markdown("### Sign In")
            u_in = st.text_input("Username", key="l_u")
            p_in = st.text_input("Password", type="password", key="l_p")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Sign In"):
                res = login_user(u_in, p_in)
                if res:
                    st.session_state.logged_in = True
                    st.session_state.username = u_in
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
        else:
            st.markdown("### Register")
            ru = st.text_input("Username", key="r_u")
            re = st.text_input("Email", key="r_e")
            rp = st.text_input("Password", type="password", key="r_p")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Register"):
                if ru and rp and re:
                    try:
                        create_user(ru, rp, re)
                        st.success("Registered! Switch to Sign In.")
                    except sqlite3.IntegrityError:
                        st.error("Username taken.")
                else:
                    st.warning("Fill all fields.")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown("""
        <div class="hero-banner">
            <h1 class="hero-title">🚆 RailxAI Express Portal</h1>
            <p class="hero-subtitle">Manage bookings, track live GPS coordinates, view station weather, check railway guidelines, and download official PDF tickets.</p>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🔍 Find & Book", 
        "🎫 PNR Tracker", 
        "📡 Live Tracking & Weather Hub", 
        "📜 Policies & Rules",
        "🤖 AI Assistant", 
        "📜 Booking History"
    ])

    with tab1:
        st.markdown("### Search Routes")
        c1, c2 = st.columns(2)
        with c1:
            from_city = st.selectbox("Origin", options=TRAINS["From"].unique())
        with c2:
            to_city = st.selectbox("Destination", options=TRAINS["To"].unique())

        av_trains = TRAINS[(TRAINS["From"] == from_city) & (TRAINS["To"] == to_city)]

        if not av_trains.empty:
            for _, t in av_trains.iterrows():
                st.markdown(f"""
                    <div class="train-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <b>{t['Name']} ({t['Train No']})</b>
                            <div>
                                <span class="badge-tag badge-seats">{t['Seats Available']} Seats</span>
                                <span class="badge-tag badge-fare">₹ {t['Fare (INR)']}</span>
                            </div>
                        </div>
                        <p style="color: #94a3b8; font-size: 13px; margin: 8px 0 0 0;">Dep: {t['Departure']} | Duration: {t['Duration']}</p>
                    </div>
                """, unsafe_allow_html=True)

            with st.form("booking_form"):
                ca, cb = st.columns(2)
                with ca:
                    sel_train = st.selectbox("Train No", options=av_trains["Train No"])
                    p_name = st.text_input("Passenger Name")
                with cb:
                    p_age = st.number_input("Age", 1, 120, 25)
                sub = st.form_submit_button("Reserve & Generate PDF")

            if sub:
                if p_name.strip():
                    t_det = TRAINS[TRAINS["Train No"] == sel_train].iloc[0]
                    pnr = generate_unique_pnr()
                    b_data = {
                        "pnr": pnr, "username": st.session_state.username,
                        "passenger_name": p_name, "passenger_age": p_age,
                        "train_no": str(t_det["Train No"]), "train_name": t_det["Name"],
                        "from_station": t_det["From"], "to_station": t_det["To"],
                        "fare": int(t_det["Fare (INR)"]), "status": "CONFIRMED"
                    }
                    save_booking_to_db(b_data)
                    st.session_state.last_booking = b_data
                    st.balloons()
                else:
                    st.error("Enter passenger name.")

            if st.session_state.last_booking:
                bi = st.session_state.last_booking
                st.success(f"Confirmed! PNR: **{bi['pnr']}**")
                st.download_button("📄 Download E-Ticket (PDF)", data=generate_pdf_ticket(bi), file_name=f"Ticket_{bi['pnr']}.pdf", mime="application/pdf")
        else:
            st.info("No direct trains found.")

    with tab2:
        st.markdown("### PNR Status")
        spnr = st.text_input("Enter 10-Digit PNR")
        if st.button("Check PNR"):
            if spnr.strip():
                rec = get_booking_by_pnr(spnr.strip(), st.session_state.username)
                if rec:
                    st.markdown(f"""
                        <div class="train-card">
                            <h3>PNR: {rec['pnr']} <span class="badge-tag badge-ontime">{rec['status']}</span></h3>
                            <p><b>Passenger:</b> {rec['passenger_name']} ({rec['passenger_age']} yrs)</p>
                            <p><b>Train:</b> {rec['train_no']} - {rec['train_name']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    st.download_button("📄 Download E-Ticket", data=generate_pdf_ticket(dict(rec)), file_name=f"Ticket_{rec['pnr']}.pdf", mime="application/pdf")
                else:
                    st.error("PNR not found.")

    # -------------------------------------------------------------------
    # TAB 3: EXPANDED LIVE TRACKING & WEATHER HUB
    # -------------------------------------------------------------------
    with tab3:
        st.markdown("## 📡 Live Express Radar & Weather Command Center")
        
        # Top Train Selector Bar
        sel_col1, sel_col2 = st.columns([1.5, 1.0])
        with sel_col1:
            track_tr = st.selectbox(
                "Select Train to Track Live", 
                options=list(LIVE_ROUTES.keys()), 
                format_func=lambda x: f"Train {x} - {TRAINS[TRAINS['Train No']==x]['Name'].values[0] if not TRAINS[TRAINS['Train No']==x].empty else ''}"
            )
        
        r_data = LIVE_ROUTES[track_tr]
        train_info = TRAINS[TRAINS["Train No"] == track_tr].iloc[0] if not TRAINS[TRAINS["Train No"] == track_tr].empty else None

        # Telemetry Metrics Grid
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Current Speed", "110 km/h", "+5 km/h")
        with m2:
            st.metric("Schedule Delay", "0 mins", "On Time")
        with m3:
            st.metric("Total Route Distance", f"{r_data[-1]['dist_km']} km")
        with m4:
            st.metric("Next Halt", r_data[2]['station'].split('(')[0] if len(r_data)>2 else "Destination")

        # Visual Route Timeline Bar
        st.markdown(f"""
            <div class="tracking-card">
                <div style="display:flex; justify-content:space-between; font-size:14px; font-weight:700; color:#cbd5e1;">
                    <span>🟢 Origin: {r_data[0]['station']}</span>
                    <span style="color:#38bdf8;">🚆 Active Status: Running On Time</span>
                    <span>🔴 Terminus: {r_data[-1]['station']}</span>
                </div>
                <div class="progress-bar-container-lg">
                    <div class="progress-bar-fill-lg" style="width: 52%;"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Main Map & Weather Layout
        col_map, col_weather_list = st.columns([1.4, 0.9], gap="large")

        with col_map:
            st.markdown("### 🗺️ Live Satellite & Route Map")
            
            # Map Rendering with Custom Coordinates
            avg_lat = sum(s['lat'] for s in r_data) / len(r_data)
            avg_lon = sum(s['lon'] for s in r_data) / len(r_data)
            
            m = folium.Map(location=[avg_lat, avg_lon], zoom_start=6, tiles="CartoDB dark_matter")
            
            # Draw Path Line
            points = [[s['lat'], s['lon']] for s in r_data]
            folium.PolyLine(points, color="#6366f1", weight=4, opacity=0.8).add_to(m)

            # Markers for Each Station
            for idx, s in enumerate(r_data):
                color = "green" if idx == 0 else ("red" if idx == len(r_data)-1 else "blue")
                if s["status"] == "Current Stop":
                    color = "orange"
                    
                folium.Marker(
                    [s['lat'], s['lon']], 
                    popup=f"<b>{s['station']}</b><br>Dep: {s['sch_dep']}<br>Dist: {s['dist_km']}km",
                    tooltip=f"{s['station']} ({s['status']})",
                    icon=folium.Icon(color=color, icon="train", prefix="fa")
                ).add_to(m)
                
            st_folium(m, width="100%", height=500)

        with col_weather_list:
            st.markdown("### 🌤️ Station Weather & Radar")
            st.caption("Real-time weather telemetry at scheduled halts along the route.")

            for s in r_data:
                w = get_station_weather(s['lat'], s['lon'])
                status_color = "#4ade80" if s['status']=="Departed" else ("#f59e0b" if s['status']=="Current Stop" else "#94a3b8")
                
                st.markdown(f"""
                    <div class="weather-grid-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <strong style="font-size:15px; color:#f8fafc;">{s['station']}</strong><br>
                                <span style="font-size:12px; color:#94a3b8;">Sch: {s['sch_dep']} | {s['dist_km']} km</span>
                            </div>
                            <div style="text-align:right;">
                                <span style="font-size:16px; font-weight:800; color:#38bdf8;">{w['temp']}</span><br>
                                <span style="font-size:11px; color:#cbd5e1;">{w['condition']}</span>
                            </div>
                        </div>
                        <div style="margin-top:8px; display:flex; justify-content:space-between; align-items:center; font-size:11px;">
                            <span style="color:{status_color}; font-weight:700;">● {s['status']}</span>
                            <span style="color:#64748b;">💨 Wind: {w['wind']}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    with tab4:
        st.markdown("### 📜 Important Railway Policies & Passenger Guidelines")
        for pol in RAILWAY_POLICIES:
            st.markdown(f"""
                <div class="policy-card">
                    <h4 style="margin: 0 0 6px 0; color: #818cf8; font-size: 16px;">{pol['category']}</h4>
                    <p style="color: #cbd5e1; font-size: 13px; margin-bottom: 10px;">{pol['description']}</p>
                    <ul style="color: #94a3b8; font-size: 12px; margin: 0; padding-left: 18px;">
            """, unsafe_allow_html=True)
            for item in pol['details']:
                st.markdown(f"<li style='margin-bottom: 4px;'>{item}</li>", unsafe_allow_html=True)
            st.markdown("</ul></div>", unsafe_allow_html=True)

    with tab5:
        st.markdown("### AI Travel Assistant")
        u_q = st.text_area("Ask anything about your trip", placeholder="e.g. Refund rules?")
        if st.button("Ask AI"):
            if GEMINI_API_KEY and u_q.strip():
                try:
                    client = genai.Client(api_key=GEMINI_API_KEY)
                    resp = client.models.generate_content(model='gemini-2.5-flash', contents=u_q)
                    st.success(resp.text)
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Provide API key and query.")

    with tab6:
        st.markdown("### Booking History")
        hdf = get_user_bookings(st.session_state.username)
        if not hdf.empty:
            st.dataframe(hdf, use_container_width=True, hide_index=True)
        else:
            st.info("No bookings yet.")
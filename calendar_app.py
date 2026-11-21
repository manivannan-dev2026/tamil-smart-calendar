import streamlit as st
import datetime
import numpy as np
import pandas as pd
import io
import wave
import os

st.set_page_config(page_title="Smart Tamil & English Calendar", page_icon="📅")

# 1. நிரந்தர ஃபைல் சேமிப்பு
TASKS_FILE = "saved_tasks.csv"

def load_tasks():
    if os.path.exists(TASKS_FILE):
        return pd.read_csv(TASKS_FILE)
    return pd.DataFrame(columns=["Date", "Time", "Task"])

tasks_df = load_tasks()

# 2. மொழி மாற்றும் பட்டன்
lang = st.radio("🌐 மொழி / Language:", ["தமிழ்", "English"], horizontal=True)

txt = {
    "தமிழ்": {
        "title": "📅 ஸ்மார்ட் தமிழ் & ஆங்கில நாட்காட்டி",
        "t1": "📆 தேதி & விசேஷ நாட்கள்", "t2": "⏰ எனது வேலைகள் & அலாரம்",
        "pick": "தேதியைத் தேர்ந்தெடுக்கவும்:",
        "eng": "ஆங்கிலத் தேதி", "tam": "தமிழ் தேதி",
        "sun": "🏖️ இன்று ஞாயிற்றுக்கிழமை (வார விடுமுறை)",
        "spl": "✨ இன்றைய சிறப்பு:", "norm": "ℹ️ சாதாரண வேலை நாள்",
        "list_h": "📋 2026 முக்கிய பண்டிகை, விடுமுறை, பௌர்ணமி & அமாவாசை:",
        "add_h": "⏰ புதிய வேலையைப் பதிவு செய்யவும்",
        "t_desc": "செய்ய வேண்டிய வேலை:", "save": "✅ வேலையைச் சேமிக்கவும்",
        "saved_h": "📌 நிரந்தரமாகச் சேமிக்கப்பட்ட வேலைகள்:",
        "alarm": "🔔 அலாரம் ஒலியைச் சோதனை செய்"
    },
    "English": {
        "title": "📅 Smart Tamil & English Calendar",
        "t1": "📆 Date & Special Days", "t2": "⏰ Activity Schedule & Alarm",
        "pick": "Select a Date:",
        "eng": "English Date", "tam": "Tamil Date",
        "sun": "🏖️ Sunday (Weekly Holiday)",
        "spl": "✨ Special Occasion:", "norm": "ℹ️ Regular Working Day",
        "list_h": "📋 2026 Holidays, Festivals, Purnima & Amavasya:",
        "add_h": "⏰ Schedule a New Activity",
        "t_desc": "Activity / Task Description:", "save": "✅ Save Activity Permanently",
        "saved_h": "📌 Permanently Saved Activities:",
        "alarm": "🔔 Test Alarm Sound"
    }
}[lang]

st.title(txt["title"])

tamil_months = [
    ("சித்திரை", "Chithirai"), ("வைகாசி", "Vaikasi"), ("ஆனி", "Aani"),
    ("ஆடி", "Aadi"), ("ஆவணி", "Avani"), ("புரட்டாசி", "Purattasi"),
    ("ஐப்பசி", "Aippasi"), ("கார்த்திகை", "Karthigai"), ("மார்கழி", "Margazhi"),
    ("தை", "Thai"), ("மாசி", "Maasi"), ("பங்குனி", "Panguni")
]

def get_tamil_date(d, is_tamil):
    month_starts = [14, 15, 15, 17, 17, 17, 18, 17, 16, 15, 13, 15]
    m_idx = (d.month - 4) % 12
    start_day = month_starts[m_idx]
    if d.day >= start_day:
        t_m = tamil_months[m_idx][0] if is_tamil else tamil_months[m_idx][1]
        t_d = d.day - start_day + 1
    else:
        prev_idx = (m_idx - 1) % 12
        t_m = tamil_months[prev_idx][0] if is_tamil else tamil_months[prev_idx][1]
        t_d = d.day + (30 - month_starts[prev_idx]) + 1
    return f"{t_m} {t_d}"

special_days = {
    "2026-01-01": ("🎉 ஆங்கிலப் புத்தாண்டு", "New Year's Day (Holiday)"),
    "2026-01-14": ("🌾 பொங்கல் பண்டிகை", "Pongal Festival (Holiday)"),
    "2026-04-14": ("🌸 தமிழ் புத்தாண்டு", "Tamil New Year (Holiday)"),
    "2026-05-01": ("🛠️ உழைப்பாளர் தினம்", "May Day / Labour Day (Holiday)"),
    "2026-08-15": ("🇮🇳 சுதந்திர தினம்", "Independence Day (Holiday)"),
    "2026-10-02": ("🕊️ காந்தி ஜெயந்தி", "Gandhi Jayanti (Holiday)"),
    "2026-11-08": ("🪔 தீபாவளி பண்டிகை", "Diwali Festival (Holiday)"),
    "2026-11-09": ("🌑 அமாவாசை", "Amavasya (New Moon)"),
    "2026-11-24": ("🌕 பௌர்ணமி", "Purnima (Full Moon)"),
    "2026-12-08": ("🌑 அமாவாசை", "Amavasya (New Moon)"),
    "2026-12-23": ("🌕 பௌர்ணமி", "Purnima (Full Moon)"),
    "2026-12-25": ("🎄 கிறிஸ்துமஸ்", "Christmas (Holiday)")
}

def generate_alarm():
    sr = 44100
    t = np.linspace(0, 1.0, sr, False)
    beep = 0.5 * np.sin(2 * np.pi * 880 * t)
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(np.int16(beep * 32767).tobytes())
    buf.seek(0)
    return buf

tab1, tab2 = st.tabs([txt["t1"], txt["t2"]])

with tab1:
    sel_date = st.date_input(txt["pick"], datetime.date.today())
    d_str = sel_date.strftime("%Y-%m-%d")
    t_date = get_tamil_date(sel_date, lang == "தமிழ்")
    
    st.info(f"🗓️ **{txt['eng']}:** {sel_date.strftime('%d-%m-%Y')} ({sel_date.strftime('%A')})\n\n🪷 **{txt['tam']}:** {t_date}")
    
    if sel_date.weekday() == 6:
        st.warning(txt["sun"])
    if d_str in special_days:
        occ = special_days[d_str][0] if lang == "தமிழ்" else special_days[d_str][1]
        st.success(f"{txt['spl']} **{occ}**")
    else:
        st.caption(txt["norm"])
        
    st.subheader(txt["list_h"])
    for dt, desc in sorted(special_days.items()):
        st.write(f"• **{dt}** : {desc[0] if lang == 'தமிழ்' else desc[1]}")

with tab2:
    st.subheader(txt["add_h"])
    with st.form("task_form"):
        t_date_in = st.date_input("Date:", datetime.date.today())
        t_time_in = st.time_input("Time:", datetime.time(9, 0))
        t_desc_in = st.text_input(txt["t_desc"])
        if st.form_submit_button(txt["save"]):
            if t_desc_in:
                new_t = pd.DataFrame([{"Date": str(t_date_in), "Time": t_time_in.strftime("%I:%M %p"), "Task": t_desc_in}])
                updated_t = pd.concat([tasks_df, new_t], ignore_index=True)
                updated_t.to_csv(TASKS_FILE, index=False)
                st.success("✅ Saved Permanently!")
                
    st.divider()
    st.subheader(txt["saved_h"])
    latest_tasks = load_tasks()
    if not latest_tasks.empty:
        st.dataframe(latest_tasks, use_container_width=True)
        
    if st.button(txt["alarm"]):
        st.audio(generate_alarm(), format="audio/wav", autoplay=True)
              

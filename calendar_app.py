import streamlit as st
import datetime
import numpy as np
import io
import wave

st.set_page_config(page_title="ஸ்மார்ட் தமிழ் காலண்டர்", page_icon="📅")

st.title("📅 ஸ்மார்ட் தமிழ் & ஆங்கில நாட்காட்டி")
st.write("தமிழ் தேதி, பௌர்ணமி, அமாவாசை, பண்டிகைகள் மற்றும் உங்கள் தினசரி வேலைத் திட்டம்!")

# 1. பொதுவான ஷெட்யூல் மெமரி
@st.cache_resource
def get_schedule_db():
    return []

schedule_db = get_schedule_db()

# 2. தமிழ் மாதம் மற்றும் தேதி கணக்கிடும் எளிய முறை
tamil_months = [
    "சித்திரை", "வைகாசி", "ஆனி", "ஆடி", "ஆவணி", "புரட்டாசி",
    "ஐப்பசி", "கார்த்திகை", "மார்கழி", "தை", "மாசி", "பங்குனி"
]

def get_approx_tamil_date(d):
    # தோராயமான தமிழ் தேதி கணக்கீடு (ஒவ்வொரு ஆங்கில மாதமும் நடுப்பகுதியில் தமிழ் மாதம் பிறக்கும்)
    month_starts = [14, 14, 15, 15, 15, 15, 17, 17, 17, 16, 15, 14]
    m_idx = (d.month - 4) % 12
    start_day = month_starts[m_idx]
    if d.day >= start_day:
        t_month = tamil_months[m_idx]
        t_day = d.day - start_day + 1
    else:
        prev_idx = (m_idx - 1) % 12
        t_month = tamil_months[prev_idx]
        t_day = d.day + (30 - month_starts[prev_idx]) + 1
    return f"{t_month} {t_day}"

# 3. முக்கிய பண்டிகைகள், விடுமுறை, பௌர்ணமி & அமாவாசை விபரங்கள் (2026)
special_days = {
    "2026-01-01": "🎉 ஆங்கிலப் புத்தாண்டு (விடுமுறை)",
    "2026-01-14": "🌾 பொங்கல் பண்டிகை (அரசு விடுமுறை)",
    "2026-01-15": "🐂 மாட்டுப் பொங்கல் (அரசு விடுமுறை)",
    "2026-01-26": "🇮🇳 குடியரசு தினம் (அரசு விடுமுறை)",
    "2026-04-14": "🌸 தமிழ் புத்தாண்டு (அரசு விடுமுறை)",
    "2026-05-01": "🛠️ உழைப்பாளர் தினம் (அரசு விடுமுறை)",
    "2026-08-15": "🇮🇳 சுதந்திர தினம் (அரசு விடுமுறை)",
    "2026-10-02": "🕊️ காந்தி ஜெயந்தி (அரசு விடுமுறை)",
    "2026-11-08": "🪔 தீபாவளி பண்டிகை (அரசு விடுமுறை)",
    "2026-11-09": "🌑 அமாவாசை (விசேஷ நாள்)",
    "2026-11-24": "🌕 பௌர்ணமி (விசேஷ நாள்)",
    "2026-12-08": "🌑 அமாவாசை (விசேஷ நாள்)",
    "2026-12-23": "🌕 பௌர்ணமி (விசேஷ நாள்)",
    "2026-12-25": "🎄 கிறிஸ்துமஸ் (அரசு விடுமுறை)"
}

# அலாரம் ஒலி உருவாக்கும் கருவி
def generate_alarm_sound():
    sample_rate = 44100
    t = np.linspace(0, 1.0, sample_rate, False)
    beep = 0.5 * np.sin(2 * np.pi * 880 * t)
    audio_int16 = np.int16(beep * 32767)
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_int16.tobytes())
    buf.seek(0)
    return buf

# இரண்டு டேப்கள்
tab1, tab2 = st.tabs(["📆 தேதி & விசேஷ நாட்கள்", "⏰ எனது வேலைகள் & அலாரம்"])

with tab1:
    selected_date = st.date_input("தேதியைத் தேர்ந்தெடுக்கவும்:", datetime.date.today())
    date_str = selected_date.strftime("%Y-%m-%d")
    tamil_date_str = get_approx_tamil_date(selected_date)
    day_name = selected_date.strftime("%A")
    
    st.info(f"🗓️ **ஆங்கிலத் தேதி:** {selected_date.strftime('%d-%m-%Y')} ({day_name})\n\n🪷 **தமிழ் தேதி:** {tamil_date_str}")
    
    if selected_date.weekday() == 6:
        st.warning("🏖️ இன்று ஞாயிற்றுக்கிழமை (வார விடுமுறை)")
        
    if date_str in special_days:
        st.success(f"✨ **இன்றைய சிறப்பு:** {special_days[date_str]}")
    else:
        st.caption("ℹ️ இன்று சாதாரண வேலை நாள். கீழே முக்கியப் பண்டிகை & விசேஷ நாட்கள் பட்டியல் உள்ளது:")
        
    st.subheader("📋 முக்கிய பண்டிகை, விடுமுறை, பௌர்ணமி & அமாவாசை பட்டியல்:")
    for dt, desc in sorted(special_days.items()):
        st.write(f"• **{dt}** : {desc}")

with tab2:
    st.subheader("⏰ இன்றைய வேலைகளைத் திட்டமிடுங்கள் (Activity Schedule)")
    with st.form("task_form"):
        task_date = st.date_input("தேதி:", datetime.date.today())
        task_time = st.time_input("நேரம்:", datetime.time(9, 0))
        task_desc = st.text_input("செய்ய வேண்டிய வேலை (எ.கா: கம்பெனி மீட்டிங், பஸ் பயணம்):")
        if st.form_submit_button("வேலையைச் சேர்க்கவும்"):
            if task_desc:
                schedule_db.append({
                    "date": str(task_date),
                    "time": task_time.strftime("%I:%M %p"),
                    "task": task_desc
                })
                st.success("✅ உங்கள் வேலை வெற்றிகரமாகப் பதிவு செய்யப்பட்டது!")
                
    st.divider()
    st.subheader("📌 பதிவு செய்யப்பட்ட வேலைகள்:")
    if schedule_db:
        for item in schedule_db:
            st.info(f"📅 **{item['date']}** | 🕒 **{item['time']}** ➡️ {item['task']}")
    else:
        st.caption("இன்னும் எந்த வேலையும் பதிவு செய்யப்படவில்லை.")
        
    if st.button("🔔 அலாரம் ஒலியைச் சோதனை செய் (Test Alarm)"):
        st.warning("⏰ அலாரம் அடிக்கிறது! உங்கள் வேலையைக் கவனியுங்கள்!")
        st.audio(generate_alarm_sound(), format="audio/wav", autoplay=True)

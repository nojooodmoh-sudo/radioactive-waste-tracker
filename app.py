import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta, date, time

# ---------------------------------------------------------
# 1. إعدادات الصفحة الأولية
# ---------------------------------------------------------
st.set_page_config(page_title="HISN Smart Tag Dashboard", page_icon="☢️", layout="wide")

st.title("☢️ منصة تتبع حاويات النفايات المشعة الذكية (HISN Smart Tag)")
st.write("نظام متكامل يستقبل القراءات عبر الـ API / Wi-Fi ويحللها بالذكاء الاصطناعي لحظياً.")

# 🔊 دالة التنبيه الصوتي المتوافقة مع متصفحات الجوال
def play_alarm_sound():
    sound_js = """
    <script>
    function playBeep() {
        var context = new (window.AudioContext || window.webkitAudioContext)();
        var osc = context.createOscillator();
        var gain = context.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(880, context.currentTime); // تردد التنبيه
        gain.gain.setValueAtTime(1, context.currentTime);
        osc.connect(gain);
        gain.connect(context.destination);
        osc.start();
        osc.stop(context.currentTime + 0.6); // مدة الصوت 0.6 ثانية
    }
    playBeep();
    </script>
    <button onclick="playBeep()" style="
        background-color: #ff4b4b;
        color: white;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
        border-radius: 8px;
        cursor: pointer;
        width: 100%;
        margin-top: 5px;">
        🔊 اضغطي هنا لسماع / إعادة تشغيل صفارة التنبيه
    </button>
    """
    st.components.v1.html(sound_js, height=60)

# ---------------------------------------------------------
# 2. تهيئة ذاكرة البيانات
# ---------------------------------------------------------
if "containers_data" not in st.session_state:
    st.session_state.containers_data = pd.DataFrame(columns=[
        "معرف الجهاز (Tag ID)",
        "المادة المشعة",
        "النشاط المقاس (MBq)",
        "الحجم المقدر بالـ AI (mL)",
        "تاريخ ووقت القياس",
        "طريقة الاتصال",
        "الموقع الحالي",
        "حالة الحركة",
        "مستوى البطارية (%)",
        "موعد التخلص المتوقع (AI Prediction)",
        "حالة الأمان والـ AI"
    ])

df = st.session_state.containers_data

# ---------------------------------------------------------
# 3. لوحة المؤشرات السريعة (Metrics)
# ---------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("إجمالي الحاويات الذكية", len(df))
with col2:
    high_risk_count = len(df[df["حالة الأمان والـ AI"].str.contains("تحذير", na=False)]) if not df.empty else 0
    st.metric("التنبيهات والشذوذ الإشعاعي", high_risk_count)
with col3:
    moving_count = len(df[df["حالة الحركة"] == "قيد نقل (Moving)"]) if not df.empty else 0
    st.metric("الحاويات المتحركة حالياً", moving_count)
with col4:
    low_battery_count = len(df[df["مستوى البطارية (%)"] <= 20]) if not df.empty else 0
    st.metric("تنبيهات انخفاض البطارية 🔋", low_battery_count)

st.divider()

# ---------------------------------------------------------
# 4. قسم الاتصال البرمجي واستقبال البيانات (Wi-Fi / API)
# ---------------------------------------------------------
st.subheader("📡 استقبال أوتوماتيكي عبر شبكة الـ Wi-Fi / 4G والـ API")

col_api1, col_api2 = st.columns([2, 1])

with col_api1:
    api_url_input = st.text_input("رابط خادم/موقع HISN (API Endpoint)", value="https://api.hisn-smarttag.com/v1/live_data")

with col_api2:
    st.write(" ")
    st.write(" ")
    fetch_real_api = st.button("🌐 جلب البيانات الحقيقية من الموقع عبر API")

if fetch_real_api:
    try:
        response = requests.get(api_url_input, timeout=3)
        if response.status_code == 200:
            st.success("تم جلب البيانات الحية بنجاح من الموقع/الخادم!")
        else:
            st.warning(f"لم يتم العثور على استجابة من السيرفر (رمز الحالة: {response.status_code}). يمكنك استخدام المحاكاة أدناه.")
    except Exception as e:
        st.info("تعذر الاتصال بالخادم المباشر حالياً (الموديل يعمل بنمط المحاكاة المباشرة للعرض).")

c_btn1, c_btn2 = st.columns(2)
with c_btn1:
    if st.button("📲 محاكاة استقبال بيانات حية من جهاز (HISN-001) عبر Wi-Fi"):
        now_str = datetime.now().strftime('%d/%m/%Y %H:%M')
        
        wifi_entry = {
            "معرف الجهاز (Tag ID)": "HISN-001",
            "المادة المشعة": "Tc-99m",
            "النشاط المقاس (MBq)": 500.0,
            "الحجم المقدر بالـ AI (mL)": 8500.0,
            "تاريخ ووقت القياس": now_str,
            "طريقة الاتصال": "Wi-Fi",
            "الموقع الحالي": "Storage Room A",
            "حالة الحركة": "ثابت (Stationary)",
            "مستوى البطارية (%)": 78,
            "موعد التخلص المتوقع (AI Prediction)": (datetime.now() + timedelta(hours=14)).strftime('%d/%m/%Y %H:%M'),
            "حالة الأمان والـ AI": "آمن - مستقر"
        }
        
        st.session_state.containers_data = pd.concat(
            [st.session_state.containers_data, pd.DataFrame([wifi_entry])], 
            ignore_index=True
        )
        st.success("تم استقبال حزمة البيانات الحية من جهاز HISN-001 عبر الـ Wi-Fi بنجاح!")
        st.rerun()

with c_btn2:
    if st.button("⚠️ محاكاة جهاز بطاريته منخفضة جداً (HISN-002)"):
        now_str = datetime.now().strftime('%d/%m/%Y %H:%M')
        
        low_bat_entry = {
            "معرف الجهاز (Tag ID)": "HISN-002",
            "المادة المشعة": "I-131",
            "النشاط المقاس (MBq)": 150.0,
            "الحجم المقدر بالـ AI (mL)": 4200.0,
            "تاريخ ووقت القياس": now_str,
            "طريقة الاتصال": "Wi-Fi",
            "الموقع الحالي": "Storage Room B",
            "حالة الحركة": "ثابت (Stationary)",
            "مستوى البطارية (%)": 10,
            "موعد التخلص المتوقع (AI Prediction)": (datetime.now() + timedelta(hours=48)).strftime('%d/%m/%Y %H:%M'),
            "حالة الأمان والـ AI": "تنبيه - بطارية منخفضة جداً"
        }
        
        st.session_state.containers_data = pd.concat(
            [st.session_state.containers_data, pd.DataFrame([low_bat_entry])], 
            ignore_index=True
        )
        st.warning("تم إدراج جهاز بطاريته منخفضة لاختبار نظام التنبيه الصوتي والحركي!")
        st.rerun()

st.divider()

# ---------------------------------------------------------
# 5. نموذج إدخال / تسجيل جهاز يدوي
# ---------------------------------------------------------
st.subheader("📝 إدخال / تسجيل جهاز يدوي")

HALF_LIVES = {
    "Tc-99m": 6,
    "I-131": 192,
    "F-18": 1.83,
    "Ga-68": 1.13,
    "آخر / غير محدد": 24
}

with st.form("smart_container_form", clear_on_submit=True):
    c1, c2, c3 = st.columns(3)
    
    with c1:
        container_id = st.text_input("معرف الجهاز / الحاوية", placeholder="مثال: HISN-003")
        isotope = st.selectbox("المادة المشعة", list(HALF_LIVES.keys()))
        activity = st.number_input("قراءة حساس الإشعاع (MBq)", min_value=0.0, value=0.0, step=10.0)
        
    with c2:
        meas_date = st.date_input("تاريخ القياس", value=date.today())
        meas_time = st.time_input("وقت القياس", value=time(10, 0))
        estimated_volume = st.number_input("تقدير الحجم بالـ AI (mL)", min_value=0.0, value=0.0, step=100.0)
        
    with c3:
        connection_type = st.selectbox("بروتوكول الاتصال", ["Wi-Fi", "4G", "BLE"])
        location_data = st.text_input("الموقع الجغرافي (GPS/BLE)", placeholder="مثال: Storage Room B")
        motion_status = st.selectbox("مستشعر الحركة", ["ثابت (Stationary)", "قيد نقل (Moving)"])
        battery_lvl = st.slider("مستوى البطارية (%)", 0, 100, 90)

    submit_button = st.form_submit_button("معالجة البيانات بالذكاء الاصطناعي")

if submit_button:
    if not container_id:
        st.warning("يرجى إدخال معرف الجهاز أو رقم الحاوية!")
    else:
        measurement_datetime = datetime.combine(meas_date, meas_time)
        full_datetime_str = measurement_datetime.strftime('%d/%m/%Y %H:%M')
        
        half_life_hours = HALF_LIVES.get(isotope, 24)
        target_safe_activity = 100.0
        
        if activity > target_safe_activity:
            hours_needed = half_life_hours * np.log2(activity / target_safe_activity)
            disposal_datetime = measurement_datetime + timedelta(hours=hours_needed)
            disposal_str = disposal_datetime.strftime('%d/%m/%Y %H:%M')
        else:
            disposal_str = "جاهزة للتخلص الآن"
            
        ai_status = "آمن"
        if activity > 1000:
            ai_status = "تحذير - شذوذ إشعاعي مرتفع (Anomaly Detected)"
        elif activity > 500:
            ai_status = "تنبيه - إشعاع متوسط"
            
        if motion_status == "قيد نقل (Moving)" and activity > 800:
            ai_status += " | خطر نقل مادة عالية الإشعاع"
            
        if battery_lvl <= 15:
            ai_status += " | 🔋 خطر: البطارية على وشك النفاد!"

        new_entry = {
            "معرف الجهاز (Tag ID)": container_id,
            "المادة المشعة": isotope,
            "النشاط المقاس (MBq)": activity,
            "الحجم المقدر بالـ AI (mL)": estimated_volume,
            "تاريخ ووقت القياس": full_datetime_str,
            "طريقة الاتصال": connection_type,
            "الموقع الحالي": location_data,
            "حالة الحركة": motion_status,
            "مستوى البطارية (%)": battery_lvl,
            "موعد التخلص المتوقع (AI Prediction)": disposal_str,
            "حالة الأمان والـ AI": ai_status
        }
        
        st.session_state.containers_data = pd.concat(
            [st.session_state.containers_data, pd.DataFrame([new_entry])], 
            ignore_index=True
        )
        st.success(f"تمت معالجة بيانات الجهاز ({container_id}) بنجاح!")
        st.rerun()

# ---------------------------------------------------------
# 6. عرض جدول البيانات المباشر والتنبيهات الصوتية والبصرية
# ---------------------------------------------------------
st.divider()
st.subheader("📊 لوحة المراقبة والسجلات المسبقة (Live IoT Dashboard)")

if not st.session_state.containers_data.empty:
    
    should_alarm = False

    # 🔴 1. تنبيهات الشذوذ الإشعاعي
    high_risk_df = st.session_state.containers_data[
        st.session_state.containers_data["حالة الأمان والـ AI"].str.contains("تحذير", na=False)
    ]

    if not high_risk_df.empty:
        should_alarm = True
        for _, row in high_risk_df.iterrows():
            st.error(
                f"🚨 **تنبيه إشعاعي!** الجهاز **{row['معرف الجهاز (Tag ID)']}** ({row['المادة المشعة']}) "
                f"سجل قراءة **{row['النشاط المقاس (MBq)']} MBq**. "
                f"الموقع: **{row['الموقع الحالي']}**. التشخيص: {row['حالة الأمان والـ AI']}."
            )

    # 🔋 2. تنبيهات انخفاض/انطفاء البطارية التلقائية
    low_battery_df = st.session_state.containers_data[
        st.session_state.containers_data["مستوى البطارية (%)"] <= 20
    ]

    if not low_battery_df.empty:
        should_alarm = True
        for _, row in low_battery_df.iterrows():
            st.error(
                f"🔊 🔋 **تنبيه طاقة حرِج (Battery Alarm)!** الجهاز **{row['معرف الجهاز (Tag ID)']}** "
                f"وصل مستوى البطارية فيه إلى **{row['مستوى البطارية (%)']}%** فقط! "
                f"يرجى إعادة شحن الجهاز أو استبدال البطارية فوراً لتجنب توقف المراقبة الإشعاعية."
            )

    # تشغيل الصوت وإظهار زر التحكم إذا وجد تنبيه
    if should_alarm:
        play_alarm_sound()

    # 🔍 3. أدوات البحث والتصفية
    s1, s2 = st.columns(2)
    with s1:
        search_query = st.text_input("🔍 البحث عن عنصر أو حاوية مختبرة سابقاً:", placeholder="أدخل رقم الحاوية أو اسم المادة...")
    with s2:
        isotope_filter = st.selectbox("تصفية النتائج حسب المادة المشعة:", ["الكل"] + list(st.session_state.containers_data["المادة المشعة"].unique()))

    filtered_df = st.session_state.containers_data.copy()

    if search_query:
        filtered_df = filtered_df[
            filtered_df["معرف الجهاز (Tag ID)"].astype(str).str.contains(search_query, case=False, na=False) |
            filtered_df["المادة المشعة"].astype(str).str.contains(search_query, case=False, na=False)
        ]

    if isotope_filter != "الكل":
        filtered_df = filtered_df[filtered_df["المادة المشعة"] == isotope_filter]

    st.dataframe(filtered_df, use_container_width=True)
else:
    st.info("في انتظار استقبال بيانات من أجهزة HISN Smart Tag عبر الـ Wi-Fi / API أو إدخال اختبار جديد...")

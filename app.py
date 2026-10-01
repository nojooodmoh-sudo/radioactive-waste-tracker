import streamlit as st
import pandas as pd
from datetime import datetime, date, time


st.set_page_config(page_title="نظام تتبع النفايات المشعة", page_icon="☢️", layout="wide")

st.title("☢️ نظام تتبع وحصر النفايات المشعة")
st.write("تسجيل وتتبع الشحنات الإشعاعية والفحص الآلي لمستويات الخطر.")


if "containers_data" not in st.session_state:

    st.session_state.containers_data = pd.DataFrame([
        {
            "المادة المشعة": "Tc-99m",
            "رقم الحاوية": "RW-001",
            "النشاط المقاس (MBq)": 500.0,
            "تاريخ ووقت القياس": "24/09/2026 10:00",
            "الكمية / الحجم": "100 mL",
            "المغادرة / الموقع الحالي": "Nuclear Medicine - Storage",
            "الجهة المصدرة / القسم": "Nuclear Medicine",
            "حالة الحاوية": "Stored",
            "حالة الأمان": "آمن"
        }
    ])




df = st.session_state.containers_data

col1, col2 = st.columns(2)
with col1:
    st.metric("إجمالي الحاويات المسجلة", len(df))
with col2:
    high_risk_count = len(df[df["حالة الأمان"] == "تحذير - إشعاع مرتفع"])
    st.metric("الحاويات ذات الإشعاع المرتفع (تحذير)", high_risk_count)

st.divider()

st.subheader("📝 إدخال بيانات حاوية جديدة")

with st.form("add_container_form", clear_on_submit=True):
    c1, c2, c3 = st.columns(3)
    
    with c1:
        isotope = st.text_input("المادة المشعة", value="Tc-99m")
        container_id = st.text_input("رقم الحاوية", value="RW-001")
        activity = st.number_input("النشاط المقاس (MBq)", min_value=0.0, value=500.0, step=10.0)
        
    with c2:
        meas_date = st.date_input("تاريخ القياس", value=date(2026, 9, 24))
        meas_time = st.time_input("وقت القياس", value=time(10, 0))
        volume = st.text_input("الكمية / الحجم", value="100 mL")
        
    with c3:
        storage_location = st.text_input("الموقع الحالي / التخزين", value="Nuclear Medicine - Storage")
        department = st.text_input("الجهة / القسم", value="Nuclear Medicine")
        status = st.selectbox("حالة الحاوية", ["Stored", "In Transit", "Disposed", "Under Review"])

    submit_button = st.form_submit_button("إضافة الحاوية للنظام")




if submit_button:

    full_datetime = f"{meas_date.strftime('%d/%m/%Y')} {meas_time.strftime('%H:%M')}"
    
    # شرط الفحص والتنبيه الآلي (تعتبر القراءة مرتفعة إذا تجاوزت 1000 MBq)
    safety_status = "تحذير - إشعاع مرتفع" if activity > 1000 else "آمن"
    

    new_entry = {
        "المادة المشعة": isotope,
        "رقم الحاوية": container_id,
        "النشاط المقاس (MBq)": activity,
        "تاريخ ووقت القياس": full_datetime,
        "الكمية / الحجم": volume,
        "المغادرة / الموقع الحالي": storage_location,
        "الجهة المصدرة / القسم": department,
        "حالة الحاوية": status,
        "حالة الأمان": safety_status
    }
    
    st.session_state.containers_data = pd.concat(
        [st.session_state.containers_data, pd.DataFrame([new_entry])], 
        ignore_index=True
    )
    st.success(f"تمت إضافة الحاوية ({container_id}) بنجاح!")
    st.rerun()

# 

# 
st.divider()
st.subheader("📊 سجل الحاويات والنفايات المشعة")


high_risk_df = st.session_state.containers_data[
    st.session_state.containers_data["حالة الأمان"] == "تحذير - إشعاع مرتفع"
]

if not high_risk_df.empty:
    for _, row in high_risk_df.iterrows():
        st.error(
            f"⚠️️ تنبيه إشعاعي مرتفع! الحاوية **{row['رقم الحاوية']}** "
            f"({row['المادة المشعة']}) في موقع **{row['المغادرة / الموقع الحالي']}** "
            f"سجلت نشاطاً قادره **{row['النشاط المقاس (MBq)']} MBq**. يرجى مراجعة العزل فوراً!"
        )


st.dataframe(st.session_state.containers_data, use_container_width=True)

import pandas as pd
import streamlit as st

# إعدادات الصفحة
st.set_page_config(
    page_title="نظام تتبع المخلفات الإشعاعية",
    page_icon="☢️",
    layout="wide",
)

# 1. الترويسة والترحيب
st.title("☢️ نظام تتبع المخلفات الإشعاعية والنظائر")
st.info(
    "أهلاً بك 👋 في نظام التتبع الذكي! يساعدك هذا التطبيق في متابعة الشحنات وتنبيهك للحالات الشاذة."
)

# 2. البيانات الأولية
if "waste_data" not in st.session_state:
    st.session_state.waste_data = pd.DataFrame(
        [
            {
                "كود الشحنة": "RAD-101",
                "النظير المشع": "Tc-99m",
                "النشاط الإشعاعي (mCi)": 450.0,
                "حالة التخزين": "آمن",
                "الموقع": "مخزن A-1",
                "تحليل النظام": "ضمن الحدود الطبيعية",
            },
            {
                "كود الشحنة": "RAD-102",
                "النظير المشع": "I-131",
                "النشاط الإشعاعي (mCi)": 1200.0,
                "حالة التخزين": "تحذير - إشعاع مرتفع",
                "الموقع": "مخزن B-2",
                "تحليل النظام": "قيمة شاذة - يتطلب مراجعة العزل",
            },
            {
                "كود الشحنة": "RAD-103",
                "النظير المشع": "F-18",
                "النشاط الإشعاعي (mCi)": 300.0,
                "حالة التخزين": "آمن",
                "الموقع": "مخزن C-1",
                "تحليل النظام": "ضمن الحدود الطبيعية",
            },
        ]
    )

# 3. الملخص والإحصائيات
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("إجمالي الشحنات", len(st.session_state.waste_data))
with col2:
    high_rad = len(
        st.session_state.waste_data[
            st.session_state.waste_data["حالة التخزين"].str.contains("تحذير")
        ]
    )
    st.metric("حالات التحذير ⚠️", high_rad)
with col3:
    avg_act = st.session_state.waste_data["النشاط الإشعاعي (mCi)"].mean()
    st.metric("متوسط الإشعاع", f"{avg_act:.1f} mCi")

st.divider()

# 4. إدخال شحنة جديدة بسهولة
with st.expander("➕ اضغط هنا لإضافة شحنة جديدة", expanded=False):
    with st.form("add_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            shipment_code = st.text_input("كود الشحنة", value="RAD-104")
            isotope = st.selectbox(
                "النظير المشع", ["Tc-99m", "I-131", "F-18", "غير ذلك"]
            )
        with c2:
            activity = st.number_input(
                "النشاط الإشعاعي (mCi)", min_value=0.0, value=250.0, step=10.0
            )
            location = st.selectbox(
                "موقع التخزين",
                ["مخزن A-1", "مخزن B-2", "مخزن C-1", "وحدة التفكيك"],
            )

        submit = st.form_submit_button("حفظ وإضافة")

        if submit:
            if activity > 1000.0:
                status = "تحذير - إشعاع مرتفع"
                ai_note = "قيمة شاذة - يتطلب مراجعة العزل"
            else:
                status = "آمن"
                ai_note = "ضمن الحدود الطبيعية"

            new_entry = {
                "كود الشحنة": shipment_code,
                "النظير المشع": isotope,
                "النشاط الإشعاعي (mCi)": activity,
                "حالة التخزين": status,
                "الموقع": location,
                "تحليل النظام": ai_note,
            }
            st.session_state.waste_data = pd.concat(
                [st.session_state.waste_data, pd.DataFrame([new_entry])],
                ignore_index=True,
            )
            st.success("تم الحفظ بنجاح!")

# 5. عرض السجل والتنبيهات
st.subheader("📋 سجل الشحنات المباشر")
st.dataframe(st.session_state.waste_data, use_container_width=True)

st.subheader("🔔 تنبيهات الأمان")
anomalies = st.session_state.waste_data[
    st.session_state.waste_data["حالة التخزين"].str.contains("تحذير")
]

if not anomalies.empty:
    for idx, row in anomalies.iterrows():
        st.error(
            f"⚠️ تنبيه لشحنة [{row['كود الشحنة']}]: النظير ({row['النظير المشع']}) في {row['الموقع']} نشاطه مرتفع ({row['النشاط الإشعاعي (mCi)']} mCi) — {row['تحليل النظام']}"
        )
else:
    st.success("✅ جميع الشحنات المسجلة آمنة.")

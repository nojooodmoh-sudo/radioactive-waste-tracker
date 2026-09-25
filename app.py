import pandas as pd
import streamlit as st

# إعدادات الصفحة
st.set_page_config(
    page_page_title="نظام تتبع المخلفات الإشعاعية والنظائر المشعة",
    page_icon="☢️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# تطبيق التنسيق العربي RTL مع إخفاء الهيدر الافتراضي
st.markdown(
    """
    <style>
    /* تطبيق اتجاه النص والخط العربي */
    html, body, [class*="css"] {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stMarkdown, .stSelectbox, .stTextInput, .stNumberInput, .stButton, .stDataFrame {
        direction: rtl;
        text-align: right;
    }
    /* إخفاء القائمة الافتراضية للخصوصية */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

# عنوان التطبيق الرئيسي
st.title("☢️ نظام تتبع المخلفات الإشعاعية والنظائر المشعة")
st.caption(
    "نظام تشغيلي ذكي لتتبع وإدارة المخلفات الإشعاعية والنظائر المشعة وتحديد الحالات الشاذة."
)
st.divider()

# تهيئة قاعدة البيانات في جلسة المستخدم (In-Memory Database)
if "waste_data" not in st.session_state:
    st.session_state.waste_data = pd.DataFrame(
        [
            {
                "كود الشحنة": "RAD-101",
                "النظير المشع": "Tc-99m",
                "النشاط الإشعاعي (mCi)": 450.0,
                "حالة التخزين": "آمن",
                "الموقع": "مخزن A-1",
                "ملاحظات الذكاء الاصطناعي": "ضمن الحدود الطبيعية",
            },
            {
                "كود الشحنة": "RAD-102",
                "النظير المشع": "I-131",
                "النشاط الإشعاعي (mCi)": 1200.0,
                "حالة التخزين": "تحذير - إشعاع مرتفع",
                "الموقع": "مخزن B-2",
                "ملاحظات الذكاء الاصطناعي": "قيمة شاذة - يتطلب مراجعة العزل",
            },
            {
                "كود الشحنة": "RAD-103",
                "النظير المشع": "F-18",
                "النشاط الإشعاعي (mCi)": 300.0,
                "حالة التخزين": "آمن",
                "الموقع": "مخزن C-1",
                "ملاحظات الذكاء الاصطناعي": "ضمن الحدود الطبيعية",
            },
        ]
    )

# الشريط الجانبي - إدخال شحنة جديدة
st.sidebar.header("📥 تسجيل شحنة إشعاعية جديدة")
with st.sidebar.form("add_shipment_form", clear_on_submit=True):
    shipment_code = st.text_input("كود الشحنة", value="RAD-104")
    isotope = st.selectbox("النظير المشع", ["Tc-99m", "I-131", "F-18", "غير ذلك"])
    activity = st.number_input(
        "النشاط الإشعاعي (mCi)", min_value=0.0, value=250.0, step=10.0
    )
    location = st.selectbox(
        "موقع التخزين", ["مخزن A-1", "مخزن B-2", "مخزن C-1", "وحدة التفكيك"]
    )
    submitted = st.form_submit_button("➕ إضافة السجل")

    if submitted:
        # الكشف التلقائي عن القيم الشاذة بسيط
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
            "ملاحظات الذكاء الاصطناعي": ai_note,
        }
        st.session_state.waste_data = pd.concat(
            [st.session_state.waste_data, pd.DataFrame([new_entry])],
            ignore_index=True,
        )
        st.sidebar.success("تم تسجيل الشحنة بنجاح!")

# ملخص الإحصائيات
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("إجمالي الشحنات المسجلة", len(st.session_state.waste_data))
with col2:
    high_rad = len(
        st.session_state.waste_data[
            st.session_state.waste_data["حالة التخزين"].str.contains("تحذير")
        ]
    )
    st.metric("حالات التحذير / الشذوذ", high_rad, delta_color="inverse")
with col3:
    avg_act = st.session_state.waste_data["النشاط الإشعاعي (mCi)"].mean()
    st.metric("متوسط النشاط الإشعاعي", f"{avg_act:.1f} mCi")

st.divider()

# جدول البيانات المباشر
st.subheader("📋 سجل الشحنات والنظائر المشعة الحالي")
st.dataframe(st.session_state.waste_data, use_container_width=True)

# تنبيه الكشف عن الحالات الشاذة بواسطة AI
st.subheader("🤖 تحليل الذكاء الاصطناعي للحالات الشاذة")
anomalies = st.session_state.waste_data[
    st.session_state.waste_data["حالة التخزين"].str.contains("تحذير")
]

if not anomalies.empty:
    for idx, row in anomalies.iterrows():
        st.error(
            f"⚠️ **تنبيه شحنة [{row['كود الشحنة']}]**: النظير ({row['النظير المشع']}) في {row['الموقع']} يُظهر نشاطاً إشعاعياً مرتفعاً قدره {row['النشاط الإشعاعي (mCi)']} mCi. — *{row['ملاحظات الذكاء الاصطناعي']}*"
        )
else:
    st.success("✅ جميع الشحنات والمخلفات المسجلة مستقرة وضمن معايير الأمان الإشعاعي.")

<div dir="rtl"># .</div>  
  
import streamlit as st  
import pandas as pd  
from datetime import datetime  
  
# ---------------------------------------------------------  
# 1. إعدادات الصفحة والواجهة (Page Configuration)  
# ---------------------------------------------------------  
st.set_page_config(  
    page_title="RadTrack AI - نظام تتبع المخلفات الإشعاعية",  
    page_icon="☢️",  
    layout="wide"  
)  
  
# ---------------------------------------------------------  
# 2. قاعدة بيانات النظائر المرجعية (Isotopes Reference DB)  
# ---------------------------------------------------------  
ISOTOPES_DB = {  
    "Tc-99m": {  
        "name": "Technetium-99m",  
        "half_life": "6.0 ساعات",  
        "medical_use": "التصوير التشخيصي الطبقي (SPECT)، فحص العظام والقلب والدماغ.",  
        "radiation_type": "Gamma (140 keV)",  
        "hazard_level": "متوسط"  
    },  
    "I-131": {  
        "name": "Iodine-131",  
        "half_life": "8.02 أيام",  
        "medical_use": "علاج سرطان الغدة الدرقية وفرط نشاط الغدة الدرقية.",  
        "radiation_type": "Beta & Gamma",  
        "hazard_level": "عالي"  
    },  
    "F-18": {  
        "name": "Fluorine-18",  
        "half_life": "110 دقيقة",  
        "medical_use": "تصوير الأورام والقلب بالانبعاث البوزيتروني (PET).",  
        "radiation_type": "Positron (511 keV)",  
        "hazard_level": "متوسط"  
    },  
    "Ga-68": {  
        "name": "Gallium-68",  
        "half_life": "68 دقيقة",  
        "medical_use": "تشخيص أورام الغدد الصماء العصبية عبر PET.",  
        "radiation_type": "Positron",  
        "hazard_level": "متوسط"  
    },  
    "Co-60": {  
        "name": "Cobalt-60",  
        "half_life": "5.27 سنوات",  
        "medical_use": "التعقيم الطبي والعلاج الإشعاعي الخارجي.",  
        "radiation_type": "High Energy Gamma",  
        "hazard_level": "حرج جداً"  
    }  
}  
  
# ---------------------------------------------------------  
# 3. تهيئة قاعدة بيانات الحاويات في الجلسة (Session State)  
# ---------------------------------------------------------  
if "containers" not in st.session_state:  
    st.session_state.containers = pd.DataFrame([  
        {  
            "Container_ID": "RW-001",  
            "Nuclide": "Tc-99m",  
            "Activity_MBq": 500.0,  
            "Volume_mL": 100.0,  
            "Date": "2026-09-20",  
            "Location": "Storage A",  
            "Status": "Stored"  
        },  
        {  
            "Container_ID": "RW-025",  
            "Nuclide": "I-131",  
            "Activity_MBq": 200.0,  
            "Volume_mL": 50.0,  
            "Date": "2026-09-24",  
            "Location": "Storage B",  
            "Status": "Stored"  
        },  
        {  
            "Container_ID": "RW-030",  
            "Nuclide": "I-131",  
            "Activity_MBq": 15000.0,  # نشاط عالي جدًا (للكشف)  
            "Volume_mL": None,        # بيان مفقود (للكشف)  
            "Date": "2026-08-01",     # تاريخ قديم (للكشف)  
            "Location": "Storage C",  
            "Status": "In-Transit"  
        }  
    ])  
  
# ---------------------------------------------------------  
# 4. الواجهة الرئيسية (Header & Disclaimer)  
# ---------------------------------------------------------  
st.title("☢️ RadTrack AI — نظام تتبع المخلفات الإشعاعية والنظائر المشعة")  
st.caption("نظام إدارة وتتبع تشغيلي ذكي يعتمد على تحليل السجلات واكتشاف البيانات الشاذة.")  
  
st.warning(  
    "⚠️ **تنبيه السلامة:** أي تنبيه أو توصية صادرة عن هذا النموذج هي لأغراض المتابعة والدعم التشغيلي فقط، "  
    "ولا تتخذ أي قرارات نهائية بشأن السلامة أو التخلص الإشعاعي إلا عبر القياسات المعتمدة والإجراءات الرسمية."  
)  
  
st.divider()  
  
# ---------------------------------------------------------  
# 5. التبويبات الرئيسية (Tabs Layout)  
# ---------------------------------------------------------  
tab1, tab2, tab3, tab4 = st.tabs([  
    "📦 سجل الحاويات والمدخلات",  
    "⚛️ قاعدة بيانات النظائر",  
    "🤖 تحليل الذكاء الاصطناعي والتنبيهات",  
    "📄 الملف التفصيلي للحاوية"  
])  
  
# --- TAB 1: إدارة وسجل الحاويات ---  
with tab1:  
    col_form, col_table = st.columns([1, 2])  
  
    with col_form:  
        st.subheader("📥 تسجيل حاوية جديدة")  
        with st.form("add_container_form", clear_on_submit=True):  
            c_id = st.text_input("معرف الحاوية (Container ID)", placeholder="مثال: RW-026")  
            nuclide = st.selectbox("النظير المشع", list(ISOTOPES_DB.keys()))  
            activity = st.number_input("النشاط الإشعاعي (MBq)", min_value=0.0, value=100.0)  
              
            # خيار ترك الحجم فارغاً للتجربة  
            has_volume = st.checkbox("تحديد الحجم (mL)", value=True)  
            volume = st.number_input("الحجم (mL)", min_value=0.0, value=50.0) if has_volume else None  
  
            date_val = st.date_input("تاريخ القياس", datetime.now())  
            location = st.text_input("الموقع", value="Storage A")  
            status = st.selectbox("الحالة التشغيلية", ["Stored", "In-Transit", "Under Review", "Disposed"])  
  
            submitted = st.form_submit_button("حفظ السجل في القاعدة")  
  
            if submitted and c_id:  
                # التحقق من عدم تكرار الـ ID  
                if c_id in st.session_state.containers["Container_ID"].values:  
                    st.error("معرف الحاوية موجود مسبقاً!")  
                else:  
                    new_entry = {  
                        "Container_ID": c_id,  
                        "Nuclide": nuclide,  
                        "Activity_MBq": activity,  
                        "Volume_mL": volume,  
                        "Date": str(date_val),  
                        "Location": location,  
                        "Status": status  
                    }  
                    st.session_state.containers = pd.concat(  
                        [st.session_state.containers, pd.DataFrame([new_entry])],  
                        ignore_index=True  
                    )  
                    st.success(f"تم تسجيل الحاوية {c_id} بنجاح!")  
                    st.rerun()  
  
    with col_table:  
        st.subheader("📋 جدول الحاويات المسجلة")  
        df = st.session_state.containers  
        st.dataframe(df, use_container_width=True)  
  
# --- TAB 2: المرجع النووي للنظائر ---  
with tab2:  
    st.subheader("📚 قاعدة البيانات المرجعية للنظائر المشعة")  
    iso_df = pd.DataFrame.from_dict(ISOTOPES_DB, orient='index')  
    iso_df.columns = ["الاسم الكامل", "عمر النصف", "الاستخدام الطبي", "نوع الإشعاع", "مستوى الخطورة"]  
    st.table(iso_df)  
  
# --- TAB 3: محرك الذكاء الاصطناعي والتنبيهات ---  
with tab3:  
    st.subheader("🤖 محرك الفحص الذكي واكتشاف البيانات الشاذة")  
  
    # 1. البحث والاستعلام باللغة الطبيعية  
    st.markdown("##### 🔍 البحث والاستعلام الذكي:")  
    query = st.text_input("اكتبي استفسارك (مثال: أظهر حاويات I-131 أو الحاويات في Storage B):")  
      
    if query:  
        df = st.session_state.containers  
        filtered = df[  
            df["Container_ID"].str.contains(query, case=False, na=False) |  
            df["Nuclide"].str.contains(query, case=False, na=False) |  
            df["Location"].str.contains(query, case=False, na=False)  
        ]  
        st.write(f"نتائج البحث عن: **{query}**")  
        st.dataframe(filtered)  
  
    st.divider()  
  
    # 2. الفحص التلقائي للشذوذ والبيانات الناقصة  
    st.markdown("##### 🚨 التنبيهات المكتشفة تلقائياً عبر النظام:")  
    alerts_found = False  
    df = st.session_state.containers  
  
    for _, row in df.iterrows():  
        # فحص الحجم المفقود  
        if pd.isna(row["Volume_mL"]) or row["Volume_mL"] is None:  
            st.error(f"🚨 **[بيانات ناقصة]** الحاوية `{row['Container_ID']}`: حجم الحاوية مفقود (Missing Volume).")  
            alerts_found = True  
  
        # فحص النشاط المرتفع جداً  
        if row["Activity_MBq"] > 10000:  
            st.error(f"🚨 **[نشاط مرتفع جداً]** الحاوية `{row['Container_ID']}`: النشاط الإشعاعي ({row['Activity_MBq']} MBq) عالي وغير معتاد.")  
            alerts_found = True  
  
        # فحص القدم الزمني  
        try:  
            rec_date = datetime.strptime(str(row["Date"]), "%Y-%m-%d")  
            days_diff = (datetime.now() - rec_date).days  
            if days_diff > 30 and row["Status"] != "Disposed":  
                st.warning(f"⚠️ **[تأخر تحديث]** الحاوية `{row['Container_ID']}`: لم يتم تحديث القياس منذ {days_diff} يومًا.")  
                alerts_found = True  
        except ValueError:  
            pass  
  
    if not alerts_found:  
        st.success("✅ جميع السجلات مكتملة ولا توجد أي تنبيهات أو قراءات شاذة.")  
  
# --- TAB 4: الملف التفصيلي للحاوية ---  
with tab4:  
    st.subheader("🔎 الملف التكاملي للحاوية والخصائص النووية")  
      
    df = st.session_state.containers  
    if not df.empty:  
        selected_c_id = st.selectbox("اختر الحاوية لعرض ملفها الكامل:", df["Container_ID"].unique())  
        c_data = df[df["Container_ID"] == selected_c_id].iloc[0]  
        iso_data = ISOTOPES_DB.get(c_data["Nuclide"], {})  
  
        col_a, col_b = st.columns(2)  
  
        with col_a:  
            st.markdown("### 📦 البيانات التشغيلية")  
            st.write(f"- **معرف الحاوية:** {c_data['Container_ID']}")  
            st.write(f"- **النظير:** {c_data['Nuclide']}")  
            st.write(f"- **النشاط الإشعاعي:** {c_data['Activity_MBq']} MBq")  
            st.write(f"- **الحجم:** {c_data['Volume_mL']} mL" if pd.notna(c_data['Volume_mL']) else "- **الحجم:** ❌ مفقود")  
            st.write(f"- **تاريخ القياس:** {c_data['Date']}")  
            st.write(f"- **الموقع:** {c_data['Location']}")  
            st.write(f"- **الحالة:** {c_data['Status']}")  
  
        with col_b:  
            st.markdown("### ⚛️ الخصائص النووية والطبية المرتبطة")  
            st.write(f"- **الاسم:** {iso_data.get('name', 'N/A')}")  
            st.write(f"- **عمر النصف:** {iso_data.get('half_life', 'N/A')}")  
            st.write(f"- **نوع الإشعاع:** {iso_data.get('radiation_type', 'N/A')}")  
            st.write(f"- **الاستخدام الطبي:** {iso_data.get('medical_use', 'N/A')}")  
            st.write(f"- **مستوى الخطورة المرجعي:** {iso_data.get('hazard_level', 'N/A')}")  

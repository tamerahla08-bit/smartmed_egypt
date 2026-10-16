import streamlit as st

# إعدادات الصفحة
st.set_page_config(page_title="SmartMed Egypt", page_icon="🏥", layout="centered")

st.markdown("""
    <style>
    html, body, [class*="css"]  {
        direction: rtl;
        text-align: right;
    }
    .main-header {
        color: #1A5276;
        text-align: center;
        font-size: 2.3rem;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .sub-header {
        color: #5D6D7E;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 25px;
    }
    .card {
        background-color: #F4F6F7;
        padding: 20px;
        border-radius: 10px;
        border-right: 5px solid #2980B9;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">SmartMed Egypt 🏥</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">النظام الخبير لتوصية التخصصات الطبية وترشيح المستشفيات في مصر</div>', unsafe_allow_html=True)

st.success("🎉 مرحباً بكِ! تم تشغيل المشروع بنجاح وتفعيل واجهة الويب الخاصة بمشروع التخرج.")

name = st.text_input("الاسم بالكامل:")
age = st.number_input("العمر:", min_value=1, max_value=120, value=25)
gov = st.selectbox("المحافظة:", ["القاهرة", "الجيزة", "الإسكندرية"])

symptom = st.selectbox("اختر العرض الرئيسي:", ["صداع شديد", "ألم في الصدر أو ضيق تنفس", "ألم في البطن", "ألم بالمفاصل"])

if st.button("تحليل الحالة وترشيح المستشفيات 🔍"):
    if name:
        st.markdown(f"""
        <div class="card">
            <h3>👤 تقرير الحالة للمستخدم: {name}</h3>
            <p><b>العمر:</b> {age} سنة | <b>المحافظة:</b> {gov}</p>
            <hr>
            <p><b>التخصص المقترح:</b> قسم الباطنة والتقييم الشامل</p>
            <p><b>المستشفيات المقترحة في محافظة {gov}:</b> مستشفيات جامعة القاهرة / مستشفيات المحافظة المركزية المعتمدة.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("يرجى إدخال الاسم أولاً.")

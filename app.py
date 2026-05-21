import streamlit as st
import pandas as pd
import pickle

# 1. Sahifa sozlamalari (eng tepada bo'lishi shart)
st.set_page_config(page_title="Kredit Skoring Tizimi", page_icon="🏦", layout="wide")

# 2. Modellarni xotiraga yuklash (tez ishlashi uchun keshlaymiz)
@st.cache_resource
def load_models():
    with open('rf_champion.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
    return model, scaler

# Fayllar borligini tekshirish
try:
    model, scaler = load_models()
except FileNotFoundError:
    st.error("Model yoki Scaler fayllari topilmadi! Iltimos, '.pkl' fayllar 'app.py' bilan bir papkada ekanligini tekshiring.")
    st.stop()

# 3. Dastur sarlavhasi
st.title("🏦 Bank Kredit Skoring Platformasi")
st.markdown("""
Ushbu dastur Sun'iy Intellekt (Random Forest) yordamida mijozning kredit tarixini tahlil qiladi va 
unga kredit ajratish xavfini (Probability of Default) baholaydi.
""")
st.divider()

# 4. Foydalanuvchi interfeysi (Ma'lumotlarni kiritish)
st.header("👤 Mijoz ma'lumotlarini kiriting:")

# Ekrandagi qutilarni 2 ta ustunga ajratamiz
col1, col2 = st.columns(2)

with col1:
    age = st.number_input("Mijozning yoshi (Age)", min_value=18, max_value=100, value=30)
    monthly_income = st.number_input("Oylik daromadi (MonthlyIncome)", min_value=0.0, value=5000.0, step=100.0)
    debt_ratio = st.number_input("Qarz yuki darajasi (DebtRatio)", min_value=0.0, value=0.3, step=0.1)
    revolving_util = st.number_input("Kredit karta ishlatish darajasi (RevolvingUtilization)", min_value=0.0, value=0.1, step=0.05)
    dependents = st.number_input("Qaramog'idagilar soni (NumberOfDependents)", min_value=0, max_value=20, value=1)

with col2:
    open_credit_lines = st.number_input("Ochiq kreditlar soni (OpenCreditLines)", min_value=0, value=3)
    real_estate_loans = st.number_input("Ko'chmas mulk kreditlari soni (RealEstateLoans)", min_value=0, value=1)
    past_due_30_59 = st.number_input("30-59 kun kechiktirganlar soni", min_value=0, value=0)
    past_due_60_89 = st.number_input("60-89 kun kechiktirganlar soni", min_value=0, value=0)
    past_due_90_plus = st.number_input("90+ kun kechiktirganlar soni", min_value=0, value=0)

st.divider()

# 5. Bashorat tugmasi va sun'iy intellekt mantig'i
submit_button = st.button("Kreditni baholash 🔍", type="primary", use_container_width=True)

if submit_button:
    # 1. Kiritilgan ma'lumotlarni model kutgan formatda (jadval qilib) yig'ib olamiz
    # DIQQAT: Ustunlar ketma-ketligi va nomlari model o'rgangan vaqtdagidek bo'lishi shart!
    input_df = pd.DataFrame({
    # 'Unnamed: 0' ni O'CHIRING — u feature emas
        'RevolvingUtilizationOfUnsecuredLines': [revolving_util],
        'age': [age],
        'NumberOfTime30-59DaysPastDueNotWorse': [past_due_30_59],
        'DebtRatio': [debt_ratio],
        'MonthlyIncome': [monthly_income],
        'NumberOfOpenCreditLinesAndLoans': [open_credit_lines],
        'NumberOfTimes90DaysLate': [past_due_90_plus],
        'NumberRealEstateLoansOrLines': [real_estate_loans],
        'NumberOfTime60-89DaysPastDueNotWorse': [past_due_60_89],
        'NumberOfDependents': [dependents]
    })

    try:
        # 2. Mijoz ma'lumotlarini qolipga tushiramiz (Masshtablash)
        scaled_data = scaler.transform(input_df)

        # 3. Model bashorati (Qallob bo'lish ehtimolligi)
        # predict_proba[0][1] - yomon mijoz bo'lish foizini ajratib oladi
        probability = model.predict_proba(scaled_data)[0][1]

        # 4. Natijani chiroyli qilib ekranga chiqarish
        st.divider()
        st.subheader("📊 Tahlil Natijasi:")

        # Agar mijozning xavflilik darajasi 50% dan yuqori bo'lsa:
        if probability > 0.50:
            st.error(f"❌ DIQQAT: XAVFLI MIJOZ! \n\nKreditni qaytarmaslik ehtimoli: **{probability * 100:.1f}%**")
            st.warning("💡 Bank uchun tavsiya: Kredit ajratish rad etilsin yoki juda kuchli kafillik talab qilinsin.")
        else:
            st.success(f"✅ ISHONCHLI MIJOZ! \n\nKreditni qaytarmaslik xatar darajasi bor-yo'g'i: **{probability * 100:.1f}%**")
            st.info("💡 Bank uchun tavsiya: Mijozga so'ralgan kredit miqdorini ajratish xavfsiz.")
            
    except Exception as e:
        st.error(f"Kechirasiz, hisoblashda xatolik yuz berdi. Xato kodi: {e}")
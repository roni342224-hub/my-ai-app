import os
import urllib.parse
from google import genai
import streamlit as st

# הגדרות עמוד בעיצוב נקי וכהה
st.set_page_config(
    page_title="AI Explorer", page_icon="🌐", layout="wide", initial_sidebar_state="collapsed"
)

# הזרקת עיצוב CSS מותאם אישית למראה המינימליסטי הכהה שבתמונה
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0b0b0b;
        color: #ffffff;
        direction: rtl;
    }
    /* הסתרת אלמנטים מיותרים של Streamlit למראה נקי */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* עיצוב תיבת הקלט המרכזית */
    .stChatInputContainer {
        max-width: 750px;
        margin: auto;
    }
    .stChatInput input {
        background-color: #161618 !important;
        color: #ffffff !important;
        border-radius: 28px !important;
        border: 1px solid #2d2d30 !important;
        padding: 12px 20px !important;
    }
    
    /* עיצוב כפתורי ההתחברות למעלה */
    .top-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px 30px;
        background-color: #0b0b0b;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# סרגל עליון (לוגו בצד שמאל/ימין וכפתורי התחברות)
col_logo, col_buttons = st.columns([8, 2])
with col_logo:
  st.markdown(
      "<h3 style='color: #ffffff; margin: 0;'>🌐 Explorer</h3>",
      unsafe_allow_html=True,
  )
with col_buttons:
  # כפתורי Sign in / Sign up דמויים
  b_col1, b_col2 = st.columns(2)
  with b_col1:
    if st.button("התחבר", use_container_width=True):
      st.info(
          "מצב התחברות פעיל (מחובר כמשתמש אורח עם מפתח API אישי)."
      )
  with b_col2:
    if st.button("הרשמה", use_container_width=True):
      st.success("ברוך הבא! האפליקציה מוכנה לשימוש.")

st.markdown("<br><br>", unsafe_allow_html=True)

# הכנס כאן את ה-API Key שלך בין המרכאות
API_KEY = "AQ.Ab8RN6LcJJnwnP6oGRNTlmlrUln79M4YcGejA-Um_awk3wSGYg"

# חיבור ללקוח ה-API
client = genai.Client(api_key=API_KEY)

# ניהול היסטוריית השיחה
if "messages" not in st.session_state:
  st.session_state.messages = []

# אם אין הודעות עדיין - נציג את המסך הראשי המרכזי כמו בתמונה
if len(st.session_state.messages) == 0:
  st.markdown(
      "<h1 style='text-align: center; color: #ffffff; font-size: 3rem;"
      " margin-bottom: 20px;'>מה נרצה לחקור?</h1>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='text-align: center; color: #8e918f; font-size: 1.1rem;'>שאל"
      " כל דבר או כתוב <b>'תמונה:'</b> ואחריה תיאור כדי ליצור תמונה"
      " מדהימה</p>",
      unsafe_allow_html=True,
  )
  st.markdown("<br>", unsafe_allow_html=True)

# הצגת היסטוריית ההודעות בצ'אט
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    if message.get("type") == "image":
      st.image(message["content"])
    else:
      st.markdown(message["content"])

# תיבת הקלט בתחתית העמוד
if prompt := st.chat_input("שאל את המודל או בקש תמונה..."):
  # הצגת הודעת המשתמש
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user"):
    st.markdown(prompt)

  # מענה של ה-AI עם טיפול בשגיאות עומס
  with st.chat_message("assistant"):
    try:
      if prompt.startswith("תמונה:"):
        hebrew_prompt = prompt.replace("תמונה:", "").strip()

        # תרגום חכם לאנגלית דרך המודל היציב
        translation_response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=(
                "Translate this image description to a detailed English prompt"
                f" for an AI image generator, return ONLY the translated prompt:"
                f" {hebrew_prompt}"
            ),
        )
        english_prompt = translation_response.text.strip()

        encoded_prompt = urllib.parse.quote(english_prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"

        st.image(image_url, caption=f"תמונה עבור: {hebrew_prompt}")
        st.session_state.messages.append(
            {"role": "assistant", "content": image_url, "type": "image"}
        )
      else:
        # מענה טקסטואלי רגיל
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
        )
        st.markdown(response.text)
        st.session_state.messages.append(
            {"role": "assistant", "content": response.text}
        )
    except Exception as e:
      error_message = (
          "⚠️ השרתים עמוסים כרגע (שגיאת עומס זמנית). המתן מספר שניות ונסח את"
          " הודעתך מחדש."
      )
      st.error(error_message)
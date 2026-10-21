import streamlit as st
from google import genai
from google.genai import types

# הגדרת עמוד
st.set_page_config(
    page_title="ChatGPT Style AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# עיצוב CSS מותאם אישית להשגת מראה מדויק כמו ChatGPT ותמיכה בעברית (RTL)
st.markdown("""
    <style>
    /* רקע כהה כללי ויישור לימין */
    .stApp {
        background-color: #212121;
        color: #ececec;
        direction: rtl;
        text-align: right;
    }
    
    /* הסתרת כותרות סטנדרטיות של סטרימליט לטובת עיצוב נקי */
    header {visibility: hidden;}
    
    /* סרגל צד (Sidebar) כהה */
    [data-testid="stSidebar"] {
        background-color: #171717;
        border-left: 1px solid #2f2f2f;
    }

    /* כותרת מרכזית בסגנון ChatGPT */
    .chatgpt-header {
        font-size: 2.2rem;
        font-weight: 600;
        text-align: center;
        color: #ececec;
        margin-top: 15vh;
        margin-bottom: 2rem;
    }

    /* עיצוב תיבת הקלט למטה */
    .stChatInputContainer {
        padding-bottom: 20px;
    }
    
    /* עיצוב אזור התשובות */
    .stChatMessage {
        background-color: #2f2f2f;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# סרגל צד (Sidebar)
with st.sidebar:
    st.markdown("### ⚙️ הגדרות מערכת")
    api_key = st.text_input("הכנס Google Gemini API Key:", type="password", placeholder="AIzaSy...")
    st.markdown("---")
    st.markdown("**תכונות המערכת:**")
    st.markdown("- מודל Gemini 2.5 Flash")
    st.markdown("- חיפוש בגוגל בזמן אמת (Grounding)")
    st.markdown("- ממשק עברי מלא (RTL)")

# ניהול היסטוריית צ'אט בזיכרון של Streamlit
if "messages" not in st.session_state:
    st.session_state.messages = []

# אם אין עדיין שיחות, הצג את מסך הפתיחה המרכזי בסגנון ChatGPT
if not st.session_state.messages:
    st.markdown('<div class="chatgpt-header">איפה נתחיל היום?</div>', unsafe_allow_html=True)

# הצגת היסטוריית ההודעות
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# תיבת הקלט של הצ'אט (יושבת אוטומטית למטה כמו ב-ChatGPT)
if prompt := st.chat_input("שאל את המודל או בקש חיפוש מהרשת..."):
    if not api_key:
        st.error("אנא הכנס את מפתח ה-API בסיידבר מצד שמאל כדי להתחיל לשוחח.")
    else:
        # הוספת הודעת המשתמש להיסטוריה
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # יצירת תשובה מהמודל עם חיפוש בגוגל
        with st.chat_message("assistant"):
            with st.spinner("חושב ומחפש בגוגל..."):
                try:
                    client = genai.Client(api_key=api_key)
                    
                    # בניית היסטוריית השיחה למודל
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            tools=[types.Tool(google_search=types.GoogleSearch())],
                            temperature=0.3,
                        ),
                    )
                    
                    answer = response.text
                    st.markdown(answer)
                    
                    # הוספת התשובה להיסטוריה
                    st.session_state.messages.append({"role": "assistant", "content": answer})

                except Exception as e:
                    error_msg = f"אירעה שגיאה: {e}"
                    st.error(error_msg)

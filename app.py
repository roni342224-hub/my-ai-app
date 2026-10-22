import streamlit as st
from google import genai
from google.genai import types

# הגדרת עמוד רחבה
st.set_page_config(
    page_title="ChatGPT Style AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# עיצוב CSS מתקדם בסגנון ChatGPT ומותאם לעברית (RTL)
st.markdown("""
    <style>
    .stApp {
        background-color: #212121;
        color: #ececec;
        direction: rtl;
        text-align: right;
    }
    header {visibility: hidden;}

    /* סרגל צד כהה בסגנון ChatGPT */
    [data-testid="stSidebar"] {
        background-color: #171717;
        border-left: 1px solid #2f2f2f;
        padding-top: 20px;
    }

    /* כרטיס התחברות מרכזי */
    .login-card {
        background: #2f2f2f;
        padding: 40px;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        border: 1px solid #3f3f3f;
        max-width: 420px;
        margin: 12vh auto;
        text-align: center;
    }

    .login-title {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 8px;
    }

    .login-subtitle {
        color: #9b9b9b;
        font-size: 0.95rem;
        margin-bottom: 25px;
    }

    /* כפתורים מודרניים */
    .stButton button {
        border-radius: 10px;
        font-weight: 600;
        background: #2f2f2f;
        color: white;
        border: 1px solid #4f4f4f;
        transition: 0.2s;
    }
    .stButton button:hover {
        background: #3f3f3f;
        border-color: #6f6f6f;
    }

    /* כותרת הצ'אט המרכזית */
    .chat-main-title {
        font-size: 2.2rem;
        font-weight: 600;
        text-align: center;
        margin-top: 15vh;
        margin-bottom: 2rem;
        color: #ececec;
    }

    /* בועות צ'אט */
    .stChatMessage {
        background-color: #2f2f2f;
        border-radius: 12px;
        padding: 16px;
        border: 1px solid #3f3f3f;
        margin-bottom: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# ניהול מצב התחברות (Session State)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

# ניהול היסטוריית צ'אטים מרובים
if "chats" not in st.session_state:
    st.session_state.chats = {"שיחה חדשה 1": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "שיחה חדשה 1"

# ---------------------------------------------------------
# מסך התחברות (Login Screen)
# ---------------------------------------------------------
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
            <div class="login-card">
                <div class="login-title">ברוך הבא ל-AI</div>
                <div class="login-subtitle">התחבר באמצעות חשבון Google כדי להמשיך</div>
            </div>
        """, unsafe_allow_html=True)
        
        email_input = st.text_input("כתובת אימייל", placeholder="name@example.com")
        pass_input = st.text_input("סיסמה", type="password", placeholder="••••••••")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("התחבר", use_container_width=True):
                if email_input.strip():
                    st.session_state.logged_in = True
                    st.session_state.user_email = email_input
                    st.rerun()
                else:
                    st.error("נא להזין אימייל")
        with c2:
            if st.button("🔵 התחבר עם Google", use_container_width=True):
                st.session_state.logged_in = True
                st.session_state.user_email = "user@gmail.com"
                st.rerun()

# ---------------------------------------------------------
# האפליקציה הראשית לאחר התחברות
# ---------------------------------------------------------
else:
    # סרגל צד (Sidebar) - ניהול שיחות והיסטוריה כמו ב-ChatGPT
    with st.sidebar:
        st.markdown(f"👤 **{st.session_state.user_email}**")
        st.markdown("---")
        
        # כפתור פתיחת צ'אט חדש
        if st.button("➕ צ'אט חדש", use_container_width=True):
            new_chat_name = f"שיחה {len(st.session_state.chats) + 1}"
            st.session_state.chats[new_chat_name] = []
            st.session_state.current_chat = new_chat_name
            st.rerun()

        st.markdown("### 💬 היסטוריית שיחות")
        
        # הצגת רשימת השיחות בסרגל הצד
        chat_names = list(st.session_state.chats.keys())
        for chat_name in chat_names:
            if st.button(chat_name, use_container_width=True, key=f"btn_{chat_name}"):
                st.session_state.current_chat = chat_name
                st.rerun()

        st.markdown("---")
        api_key = st.text_input("Gemini API Key:", type="password", placeholder="AIzaSy...")
        st.markdown("---")
        
        if st.button("🚪 התנתק", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.chats = {"שיחה חדשה 1": []}
            st.rerun()

    # שליפה של הודעות הצ'אט הנוכחי
    current_messages = st.session_state.chats[st.session_state.current_chat]

    # מסך פתיחה מרכזי אם אין הודעות בשיחה הנוכחית
    if not current_messages:
        st.markdown(f'<div class="chat-main-title">איפה נתחיל היום?</div>', unsafe_allow_html=True)

    # הצגת הודעות הצ'אט
    for message in current_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # תיבת הקלדת הודעה בתחתית המסך
    if prompt := st.chat_input("שאל את המודל או בקש חיפוש מהרשת..."):
        if not api_key:
            st.error("🔒 נא להזין את מפתח ה-API בסיידבר מצד שמאל.")
        else:
            # הוספת הודעת המשתמש לשיחה הנוכחית
            current_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # מענה מהמודל עם חיפוש בגוגל
            with st.chat_message("assistant"):
                with st.spinner("חושב ומחפש בגוגל..."):
                    try:
                        client = genai.Client(api_key=api_key)
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
                        # הוספת תשובת המודל לשיחה הנוכחית
                        current_messages.append({"role": "assistant", "content": answer})
                    except Exception as e:
                        st.error(f"שגיאה: {e}")

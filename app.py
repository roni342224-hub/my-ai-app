import streamlit as st
from google import genai
from google.genai import types

# ====================== הגדרת עמוד ======================
st.set_page_config(
    page_title="ChatGPT Style AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== עיצוב CSS (RTL + כהה) ======================
st.markdown("""
<style>
.stApp {
    background-color: #212121;
    color: #ececec;
    direction: rtl;
    text-align: right;
}
header {visibility: hidden;}
[data-testid="stSidebar"] {
    background-color: #171717;
    border-left: 1px solid #2f2f2f;
    padding-top: 20px;
}
</style>
""", unsafe_allow_html=True)

# ====================== הגדרות ======================
# הכנס כאן את ה-API Key שלך (או תשתמש ב-secrets)
API_KEY = st.secrets.get("GOOGLE_API_KEY", "הכנס-כאן-את-המפתח-שלך")

# הוראות מערכת – כאן אתה קובע איך ה-AI יתנהג
SYSTEM_INSTRUCTION = """
אתה עוזר AI ידידותי ומנומס שמדבר בעברית.
- אם מישהו כותב "שלום" או "היי" או "בוקר טוב" וכו' – תענה בצורה חמה כמו: "שלום! איך אוכל לעזור לך היום? 😊"
- תמיד תענה בעברית.
- תהיה קצר וברור אלא אם מבקשים הסבר ארוך.
- תזכור את כל מה שנאמר בשיחה ותשתמש בזה.
"""

# אתחול הלקוח
client = genai.Client(api_key=API_KEY)

# ====================== זיכרון השיחה ======================
if "messages" not in st.session_state:
    st.session_state.messages = []

# כותרת
st.title("🤖 הצ'אט שלי")

# הצגת היסטוריית השיחה
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# קלט מהמשתמש
if prompt := st.chat_input("כתוב הודעה..."):
    # הוספת הודעת המשתמש להיסטוריה
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    # בניית היסטוריה ל-Gemini
    history = []
    for msg in st.session_state.messages[:-1]:  # בלי ההודעה האחרונה
        role = "user" if msg["role"] == "user" else "model"
        history.append(
            types.Content(
                role=role, 
                parts=[types.Part(text=msg["content"])]
            )
        )

    # קריאה ל-Gemini עם זיכרון + System Instruction
    with st.chat_message("assistant"):
        with st.spinner("חושב..."):
            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash",  # אפשר גם gemini-1.5-flash או gemini-1.5-pro
                    contents=history + [
                        types.Content(
                            role="user", 
                            parts=[types.Part(text=prompt)]
                        )
                    ],
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.7,
                    )
                )
                
                answer = response.text
                st.markdown(answer)
                
                # שמירת התשובה בזיכרון
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer
                })
                
            except Exception as e:
                st.error(f"שגיאה: {e}")

# ====================== סיידבר ======================
with st.sidebar:
    st.header("הגדרות")
    
    if st.button("🗑️ נקה שיחה", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("**הוראות מערכת נוכחיות:**")
    st.code(SYSTEM_INSTRUCTION, language="text")

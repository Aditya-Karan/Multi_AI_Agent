import streamlit as st
import requests

from app.config.settings import settings
from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)

st.set_page_config(page_title="Multi AI Agent", layout="centered")
st.title("Multi AI Agent using Groq and Tavily")

# --- Session State Init ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = ""

if "model_name" not in st.session_state:
    st.session_state.model_name = settings.ALLOWED_MODEL_NAMES[0]

# --- Input Form ---
with st.form("chat_form"):
    st.session_state.system_prompt = st.text_area("Define your AI Agent:", value=st.session_state.system_prompt, height=70)
    st.session_state.model_name = st.selectbox("Select your AI model:", settings.ALLOWED_MODEL_NAMES, index=settings.ALLOWED_MODEL_NAMES.index(st.session_state.model_name))
    allow_web_search = st.checkbox("Allow web search")
    user_query = st.text_area("Enter your query:", height=150)
    submit_button = st.form_submit_button("Ask Agent")

API_URL = "https://multi-ai-agent-q9gd.onrender.com/chat"  # ✅ Deployed backend

# --- Handle Submission ---
if submit_button and user_query.strip():
    payload = {
        "model_name": st.session_state.model_name,
        "system_prompt": st.session_state.system_prompt,
        "messages": [msg["content"] for msg in st.session_state.messages if msg["role"] in ["user", "assistant"]] + [user_query],
        "allow_search": allow_web_search
    }

    try:
        logger.info("Sending request to backend")
        response = requests.post(API_URL, json=payload)

        if response.status_code == 200:
            agent_response = response.json().get("response", "")
            logger.info("Successfully received response from backend")

            # Append to chat history
            st.session_state.messages.append({"role": "user", "content": user_query})
            st.session_state.messages.append({"role": "assistant", "content": agent_response})

        else:
            logger.error("Backend error")
            st.error("Error with backend")

    except Exception as e:
        logger.error("Error occurred while sending request to backend")
        st.error(str(CustomException("Failed to communicate to backend")))

# --- Display Latest Response (on top) ---
if st.session_state.messages:
    if st.session_state.messages[-1]["role"] == "assistant":
        st.subheader("Agent Response")
        st.markdown(f"{st.session_state.messages[-1]['content'].replace(chr(10), '<br>')}", unsafe_allow_html=True)

# --- Display Full Conversation History Below ---
# --- Display Full Conversation History With "Show More" ---
if st.session_state.messages:
    st.markdown("---")
    st.subheader("Conversation History")
    
    for i in range(0, len(st.session_state.messages) - 1, 2):
        user_msg = st.session_state.messages[i]["content"]
        agent_msg = st.session_state.messages[i + 1]["content"]

        st.markdown(f"**You:** {user_msg}")

        # Split assistant message into preview and full
        words = agent_msg.split()
        preview = " ".join(words[:10]) + ("..." if len(words) > 10 else "")
        
        with st.expander(f"**Agent:** {preview}"):
            st.markdown(agent_msg.replace("\n", "<br>"), unsafe_allow_html=True)




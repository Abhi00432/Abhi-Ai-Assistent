import streamlit as st
import requests
import json
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Abhi's AI Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ADVANCED RGB & NEON CYBERPUNK CSS STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600&family=Inter:wght@300;400;600;700&display=swap');

    /* Global Base */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at 50% 10%, #16192b 0%, #0a0b10 100%);
        color: #e2e8f0;
    }

    /* Animated RGB Border Keyframes */
    @keyframes rgbGlow {
        0% { border-color: #ff0055; box-shadow: 0 0 15px rgba(255, 0, 85, 0.4); }
        25% { border-color: #7928ca; box-shadow: 0 0 15px rgba(121, 40, 202, 0.4); }
        50% { border-color: #0070f3; box-shadow: 0 0 15px rgba(0, 112, 243, 0.4); }
        75% { border-color: #00dfd8; box-shadow: 0 0 15px rgba(0, 223, 216, 0.4); }
        100% { border-color: #ff0055; box-shadow: 0 0 15px rgba(255, 0, 85, 0.4); }
    }

    @keyframes textShine {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* RGB Animated Gradient Header */
    .rgb-title {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 2.2rem;
        background: linear-gradient(90deg, #ff007f, #7928ca, #0070f3, #00dfd8, #ff007f);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: textShine 6s ease infinite;
        margin-bottom: 0.5rem;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0d0f17 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* RGB Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #1f1b2e, #16192e);
        color: #ffffff;
        border: 1px solid #7928ca;
        border-radius: 10px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        transition: all 0.3s ease-in-out;
    }

    .stButton > button:hover {
        border-color: #00dfd8;
        box-shadow: 0 0 18px rgba(0, 223, 216, 0.6);
        transform: translateY(-2px);
    }

    /* Chat Messages Container */
    .stChatMessage {
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        background-color: rgba(22, 27, 44, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(8px);
    }

    /* Chat Input Bar with Dynamic RGB Pulse */
    div[data-testid="stChatInput"] {
        border-radius: 15px;
        border: 2px solid #7928ca;
        animation: rgbGlow 8s linear infinite;
        background-color: #0f111a !important;
    }

    /* Code Blocks Customization */
    pre, code {
        font-family: 'Fira Code', monospace !important;
        background-color: #0b0c13 !important;
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

# --- BACKEND ENDPOINT CONFIGURATION ---
BACKEND_URL = "https://rachel-accommodate-hawaiian-penn.trycloudflare.com/v1/chat/completions"

# --- SESSION STATE INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_title" not in st.session_state:
    st.session_state.chat_title = "New Chat"

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown('<div class="rgb-title" style="font-size: 1.6rem;"> Ai Assistant </div>', unsafe_allow_html=True)
    
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_title = "New Chat"
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    new_title = st.text_input("✏️ Rename Session", value=st.session_state.chat_title)
    if new_title != st.session_state.chat_title:
        st.session_state.chat_title = new_title

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🧹 Clear Messages", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- MAIN CHAT INTERFACE ---
st.markdown(f'<div class="rgb-title">⚡ {st.session_state.chat_title}</div>', unsafe_allow_html=True)

# Render Chat History
for message in st.session_state.messages:
    role = message["role"]
    avatar = "🧑‍💻" if role == "user" else "🤖"
    with st.chat_message(role, avatar=avatar):
        st.markdown(message["content"])

# User Input & Handling
if user_prompt := st.chat_input("Ask code, queries, or ideas..."):
    # Store and display user message
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_prompt)

    # Assistant Response Generation
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        full_response = ""

        # Format message history payload for llama-server
        formatted_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]

        payload = {
    "model": "qwen2.5-coder-7b",
    "messages": formatted_messages,
    "temperature": 0.7,
    "max_tokens": 1024,
    "stop": ["<|im_end|>", "<|endoftext|>"],
    "stream": True
}
            )

            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode("utf-8")
                        if decoded_line.startswith("data: "):
                            data_str = decoded_line[6:].strip()
                            if data_str == "[DONE]":
                                break
                            try:
                                json_data = json.loads(data_str)
                                choices = json_data.get("choices", [])
                                if choices:
                                    delta = choices[0].get("delta", {})
                                    content = delta.get("content", "")
                                    full_response += content
                                    message_placeholder.markdown(full_response + "▌")
                            except json.JSONDecodeError:
                                pass

                # Final message without cursor
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            else:
                st.error(f"Backend Server Error: HTTP {response.status_code}")
                st.caption(response.text)

        except requests.exceptions.RequestException as e:
            st.error(f"Connection Error: Backend server is unreachable. Details: {e}")
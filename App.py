import streamlit as st
import requests
import json
import uuid

# --- Page Setup ---
st.set_page_config(
    page_title="AI Workspace Hub",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Samsung OneUI + Dynamic High-Contrast Chat Colors ---
st.markdown("""
<style>
    /* Dark Background */
    .stApp {
        background: radial-gradient(circle at 15% 15%, #0d1117 0%, #07090e 100%);
        color: #ffffff !important;
        font-family: 'Segoe UI', -apple-system, Roboto, sans-serif;
    }

    /* Animated RGB Gradient Title */
    @keyframes rgbGlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .rgb-header {
        background: linear-gradient(90deg, #ff007f, #7928ca, #0070f3, #00dfd8, #ff007f);
        background-size: 300% 300%;
        animation: rgbGlow 6s ease infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.4rem;
        font-weight: 800;
        margin-bottom: 20px;
    }

    /* Glassmorphism Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(15, 20, 32, 0.85) !important;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* Base Chat Message Box */
    [data-testid="stChatMessage"] {
        border-radius: 18px !important;
        padding: 16px 20px !important;
        margin-bottom: 14px !important;
        backdrop-filter: blur(12px);
    }

    /* User Prompt Bubble: Neon Cyan/Blue Border with Bright White/Cyan Text */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: linear-gradient(135deg, rgba(0, 112, 243, 0.2), rgba(121, 40, 202, 0.25)) !important;
        border: 1px solid rgba(0, 223, 216, 0.6) !important;
        box-shadow: 0 0 16px rgba(0, 223, 216, 0.25) !important;
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) p,
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) span,
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) div {
        color: #e0f2fe !important; /* Bright Cyan-White Text */
        font-size: 1.05rem !important;
        font-weight: 500 !important;
    }

    /* AI Response Bubble: Neon Pink/Purple Border with Bright Crisp White Text */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        background: linear-gradient(135deg, rgba(121, 40, 202, 0.25), rgba(255, 0, 127, 0.2)) !important;
        border: 1px solid rgba(255, 0, 127, 0.5) !important;
        box-shadow: 0 0 18px rgba(121, 40, 202, 0.3) !important;
    }

    /* AI Text High-Contrast Fix: Sabhi elements ko pure white/bright enforce karein */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) p,
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) span,
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) div,
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) li {
        color: #ffffff !important; /* Pure Crisp White */
        font-size: 1.02rem !important;
        line-height: 1.65 !important;
    }

    /* Code blocks inside AI responses */
    [data-testid="stChatMessage"] pre, [data-testid="stChatMessage"] code {
        background-color: #111827 !important;
        color: #38bdf8 !important; /* Bright Sky Blue */
        border-radius: 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    /* Fix Bottom Bar Background */
    [data-testid="stBottom"], [data-testid="stBottom"] > div {
        background: transparent !important;
    }

    /* Chat Input Container Styling */
    [data-testid="stChatInput"] {
        background: #111827 !important;
        border: 1.5px solid rgba(0, 223, 216, 0.5) !important;
        border-radius: 20px !important;
        box-shadow: 0 0 20px rgba(0, 112, 243, 0.25) !important;
    }

    [data-testid="stChatInput"]:focus-within {
        border: 1.5px solid rgba(255, 0, 127, 0.7) !important;
        box-shadow: 0 0 25px rgba(121, 40, 202, 0.4) !important;
    }

    /* Input Typing Box Text: Ab typing ke waqt crystal clear white dikhega */
    [data-testid="stChatInput"] textarea {
        background: transparent !important;
        color: #ffffff !important; /* Crystal White Typed Text */
        -webkit-text-fill-color: #ffffff !important;
        font-size: 1rem !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: #94a3b8 !important; /* Visible Grey Placeholder */
        -webkit-text-fill-color: #94a3b8 !important;
    }

    /* Custom Gradient Buttons */
    .stButton > button {
        border-radius: 12px !important;
        background: linear-gradient(135deg, #0070f3, #7928ca) !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 600 !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(121, 40, 202, 0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Multiple Chat State Management ---
if "chats" not in st.session_state:
    first_id = str(uuid.uuid4())
    st.session_state.chats = {first_id: {"name": "New Chat", "messages": []}}
    st.session_state.active_chat_id = first_id

if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = list(st.session_state.chats.keys())[0]

# --- Sidebar Controls ---
with st.sidebar:
    st.markdown('<div class="rgb-header" style="font-size: 1.6rem; margin-bottom: 10px;">⚡ Chats</div>', unsafe_allow_html=True)
    
    # New Chat Button
    if st.button("➕ New Chat", use_container_width=True):
        new_id = str(uuid.uuid4())
        chat_count = len(st.session_state.chats) + 1
        st.session_state.chats[new_id] = {"name": f"Chat {chat_count}", "messages": []}
        st.session_state.active_chat_id = new_id
        st.rerun()

    st.markdown("<hr style='border: 0.5px solid rgba(255,255,255,0.1); margin: 15px 0;'>", unsafe_allow_html=True)

    # Chat Sessions List
    chat_ids = list(st.session_state.chats.keys())
    chat_names = [st.session_state.chats[cid]["name"] for cid in chat_ids]
    current_index = chat_ids.index(st.session_state.active_chat_id)

    selected_name = st.radio(
        "Recent Conversations",
        chat_names,
        index=current_index,
        label_visibility="collapsed"
    )
    
    selected_id = chat_ids[chat_names.index(selected_name)]
    if selected_id != st.session_state.active_chat_id:
        st.session_state.active_chat_id = selected_id
        st.rerun()

    st.markdown("<hr style='border: 0.5px solid rgba(255,255,255,0.1); margin: 15px 0;'>", unsafe_allow_html=True)

    # Rename Current Chat Section
    current_chat = st.session_state.chats[st.session_state.active_chat_id]
    new_chat_name = st.text_input("✏️ Rename Chat", value=current_chat["name"])
    if new_chat_name and new_chat_name != current_chat["name"]:
        current_chat["name"] = new_chat_name
        st.rerun()

    # Clear Current Chat
    if st.button("🧹 Clear Messages", use_container_width=True):
        current_chat["messages"] = []
        st.rerun()

# --- Main Workspace Header ---
active_chat = st.session_state.chats[st.session_state.active_chat_id]
st.markdown(f'<h1 class="rgb-header">{active_chat["name"]}</h1>', unsafe_allow_html=True)

# Render Chat History
for msg in active_chat["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- User Input & Backend Execution ---
if prompt := st.chat_input("Ask code, queries, or ideas..."):
    active_chat["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_box = st.empty()
        full_text = ""

        payload = {
            "model": "qwen2.5-coder:1.5b",
            "messages": active_chat["messages"],
            "stream": True,
            "options": {
                "num_gpu": 99,
                "num_ctx": 1024,
                "low_vram": True,
                "num_thread": 4
            }
        }

        try:
            response = requests.post(
                url = "https://rachel-accommodate-hawaiian-penn.trycloudflare.com/api/chat",
                json=payload,
                stream=True,
                timeout=90
            )

            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        chunk_json = json.loads(line.decode("utf-8"))
                        text_chunk = chunk_json.get("message", {}).get("content", "")
                        full_text += text_chunk
                        response_box.markdown(full_text + "▌")
                        if chunk_json.get("done", False):
                            break
                response_box.markdown(full_text)
            else:
                st.error(f"Ollama API Error: HTTP {response.status_code}")

        except requests.exceptions.ConnectionError:
            st.error("⚠️ Ollama Server Offline. Start server using: ollama serve")
        except Exception as e:
            st.error(f"⚠️ Runtime Error: {str(e)}")

    if full_text:
        active_chat["messages"].append({"role": "assistant", "content": full_text})
import os
import streamlit as st

from core.transcript_loader import get_transcript
from core.embedding_vector_store import split_text, build_vectorstore
from core.retriever_augmentation import get_relevant_context
from core.llm_gen import get_answer

st.set_page_config(page_title="YouTube Chat", layout="wide")
st.title("💬 Chat with YouTube Video")

# --- SIDEBAR: API Key & YouTube URL ---
with st.sidebar:
    st.header("🔐 Configuration")
    google_api_key = st.text_input("Enter your Gemini API Key", type="password")
    if google_api_key:
        os.environ["GOOGLE_API_KEY"] = google_api_key
        st.success("API Key Set")

    st.header("📺 Video Setup")
    video_url = st.text_input("Enter YouTube Video URL")
    load_btn = st.button("🎬 Load Transcript & Video")

# --- SESSION STATE INIT ---
if "db" not in st.session_state:
    st.session_state.db = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "video_id" not in st.session_state:
    st.session_state.video_id = None

# --- LOAD VIDEO + TRANSCRIPT ---
if load_btn and video_url:
    try:
        transcript = get_transcript(video_url)
        st.session_state.chunks = split_text(transcript)
        st.session_state.db = build_vectorstore(st.session_state.chunks)

        # Extract video ID to embed
        st.session_state.video_id = video_url.split("v=")[-1].split("&")[0] if "v=" in video_url else video_url.split("/")[-1].split("?")[0]
        st.success("Transcript Loaded and Vectorstore Created")

    except Exception as e:
        st.error(f"Error: {e}")

# --- MAIN LAYOUT: 2 COLUMNS (Video+Transcript | Chat) ---
col1, col2 = st.columns([2, 2])

# --- COLUMN 1: Video + Transcript ---
with col1:
    if st.session_state.video_id:
        embed_url = f"https://www.youtube.com/embed/{st.session_state.video_id}"
        st.components.v1.iframe(embed_url, width=500, height=300)
        st.markdown("---")
    else:
        st.info("Load a video to watch here.")

    if "chunks" in st.session_state:
        st.subheader("📄 Transcript")
        st.text_area("Transcript", "\n\n".join(st.session_state.chunks[:10]), height=300)
    else:
        st.info("Transcript preview will appear here after loading.")

# --- COLUMN 2: Chatbot Interface ---
with col2:
    st.subheader("🤖 Chat with the Bot")

    if st.session_state.db:
        user_input = st.text_input("Ask your question")
        send = st.button("💬 Get Answer")

        if send and user_input:
            context = get_relevant_context(st.session_state.db, user_input)
            prompt = f"Use the following context to answer the question:\n\n{context}\n\nQuestion: {user_input}"
            answer = get_answer(prompt)

            st.session_state.chat_history.append(("You", user_input))
            st.session_state.chat_history.append(("Bot", answer))

        # Show chat history
        if st.session_state.chat_history:
            chat_container = st.container()
            with chat_container:
                for speaker, message in st.session_state.chat_history:
                    with st.chat_message("user" if speaker == "You" else "assistant"):
                        st.markdown(f"**{speaker}:** {message}")

                # Auto-scroll to bottom
                st.markdown("<div id='bottom-chat'></div>", unsafe_allow_html=True)
                st.markdown(
                    "<script>document.getElementById('bottom-chat').scrollIntoView({behavior: 'smooth'});</script>",
                    unsafe_allow_html=True,
                )

            if st.button("🧹 Clear Chat"):
                st.session_state.chat_history = []
    else:
        st.info("Chat will appear here after transcript is loaded.")
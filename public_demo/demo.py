import html

import streamlit as st
import streamlit.components.v1 as components
from huggingface_hub import InferenceClient


st.set_page_config(
    page_title="LENO — AI Assistant",
    page_icon="🤖",
    layout="centered"
)


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

CHAT_MODEL = "meta-llama/Llama-3.2-3B-Instruct"
ASR_MODEL = "openai/whisper-large-v3"

SYSTEM_PROMPT = """
You are LENO, a friendly, intelligent and natural AI personal assistant.

PERSONALITY:
- Friendly
- Confident
- Warm
- Slightly playful
- Natural and conversational
- Never robotic
- Do not use repetitive scripted dialogue
- Keep responses reasonably concise unless the user asks for detail

IDENTITY:
- You may naturally call the user "Boss".
- Do not claim that you can see the user in this public demo.
- Do not claim that you can access their camera.
- Do not claim that you can control their computer.
- Do not claim that you sent messages, made calls, shared locations,
  or performed external actions unless the interface actually provides
  that capability.

This is the public demonstration version of LENO.
"""


# --------------------------------------------------
# PAGE STYLE
# --------------------------------------------------

st.markdown(
    """
    <style>

    .main-title {
        text-align: center;
        font-size: 52px;
        font-weight: 750;
        margin-bottom: 0;
    }

    .subtitle {
        text-align: center;
        color: #777;
        font-size: 18px;
        margin-bottom: 25px;
    }

    .voice-box {
        padding: 18px;
        border-radius: 14px;
        background: #f4f5f7;
        margin-top: 10px;
        margin-bottom: 20px;
    }

    .demo-note {
        text-align: center;
        color: #777;
        font-size: 14px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    '<div class="main-title">🤖 LENO</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Multimodal AI personal assistant'
    '</div>',
    unsafe_allow_html=True
)


st.info(
    "🎤 Record your voice below and LENO will understand and respond."
)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]


if "last_audio_id" not in st.session_state:
    st.session_state.last_audio_id = None


# --------------------------------------------------
# HUGGING FACE CLIENT
# --------------------------------------------------

def get_client():

    token = st.secrets.get("HF_TOKEN")

    if not token:
        return None

    return InferenceClient(
        token=token
    )


# --------------------------------------------------
# ASK LENO
# --------------------------------------------------

def ask_leno(user_message):

    client = get_client()

    if client is None:
        return (
            "My AI connection has not been configured yet. "
            "The public demo needs its secure AI connection enabled."
        )

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    try:

        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=st.session_state.messages,
            max_tokens=300,
            temperature=0.7
        )

        answer = (
            response.choices[0]
            .message
            .content
            .strip()
        )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        return answer

   except Exception as error:
    return f"AI model error: {type(error).__name__}: {error}"
    

# --------------------------------------------------
# SPEECH TO TEXT
# --------------------------------------------------

def transcribe_audio(audio_file):

    client = get_client()

    if client is None:
        return None, "AI connection is not configured."

        try:
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=st.session_state.messages,
            max_tokens=300,
            temperature=0.7
        )

        answer = (
            response.choices[0]
            .message
            .content
            .strip()
        )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        return answer

    except Exception as error:
        return (
            f"AI model error: {type(error).__name__}: {error}"
        )


# --------------------------------------------------
# BROWSER TEXT TO SPEECH
# --------------------------------------------------

def speak_in_browser(text):

    safe_text = html.escape(
        text,
        quote=True
    )

    components.html(
        f"""
        <script>

        const text = {safe_text!r};

        if ("speechSynthesis" in window) {{

            window.speechSynthesis.cancel();

            const speech =
                new SpeechSynthesisUtterance(text);

            speech.rate = 1.0;
            speech.pitch = 1.0;
            speech.volume = 1.0;

            window.speechSynthesis.speak(speech);
        }}

        </script>
        """,
        height=0
    )


# --------------------------------------------------
# CHAT HISTORY
# --------------------------------------------------

for message in st.session_state.messages:

    if message["role"] == "system":
        continue

    with st.chat_message(
        message["role"]
    ):
        st.markdown(
            message["content"]
        )


# --------------------------------------------------
# VOICE INPUT
# --------------------------------------------------

st.markdown(
    '<div class="voice-box">',
    unsafe_allow_html=True
)

audio = st.audio_input(
    "🎤 Press the microphone and speak",
    sample_rate=16000
)

st.markdown(
    "</div>",
    unsafe_allow_html=True
)


# --------------------------------------------------
# PROCESS VOICE
# --------------------------------------------------

if audio is not None:

    audio_id = hash(
        audio.getvalue()
    )

    if audio_id != st.session_state.last_audio_id:

        st.session_state.last_audio_id = audio_id

        with st.spinner(
            "🎧 LENO is listening..."
        ):

            user_text, error = transcribe_audio(
                audio
            )

        if error:

            st.error(error)

        elif user_text:

            with st.chat_message("user"):
                st.markdown(user_text)

            with st.chat_message("assistant"):

                with st.spinner(
                    "🧠 LENO is thinking..."
                ):

                    answer = ask_leno(
                        user_text
                    )

                st.markdown(answer)

                speak_in_browser(
                    answer
                )


# --------------------------------------------------
# TEXT INPUT
# --------------------------------------------------

user_message = st.chat_input(
    "Or type a message..."
)


if user_message:

    with st.chat_message("user"):
        st.markdown(user_message)

    with st.chat_message("assistant"):

        with st.spinner(
            "🧠 LENO is thinking..."
        ):

            answer = ask_leno(
                user_message
            )

        st.markdown(answer)

        speak_in_browser(
            answer
        )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.markdown(
    '<div class="demo-note">'
    'LENO public voice demonstration • '
    'Experimental prototype'
    '</div>',
    unsafe_allow_html=True
)
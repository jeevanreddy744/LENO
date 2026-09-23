import streamlit as st
from huggingface_hub import InferenceClient


st.set_page_config(
    page_title="LENO — AI Assistant",
    page_icon="🤖",
    layout="centered"
)


# --------------------------------------------------
# PAGE STYLE
# --------------------------------------------------

st.markdown(
    """
    <style>
        .main-title {
            text-align: center;
            font-size: 48px;
            font-weight: 700;
            margin-bottom: 0;
        }

        .subtitle {
            text-align: center;
            color: #777;
            font-size: 18px;
            margin-bottom: 30px;
        }

        .status {
            text-align: center;
            padding: 10px;
            border-radius: 10px;
            background: #f0f2f6;
            margin-bottom: 20px;
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
    'Local-first multimodal AI personal assistant'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="status">🎤 Talk to LENO using the chat below</div>',
    unsafe_allow_html=True
)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": """
You are LENO, a friendly, intelligent and natural AI personal assistant.

Personality:
- Friendly
- Confident
- Slightly playful
- Natural and conversational
- Never robotic
- Keep responses reasonably concise

You may naturally call the user Boss when appropriate.

Do not claim that you can see the user, access their camera,
control their computer, send messages, make calls, or perform
external actions in this web demo unless the interface explicitly
provides that capability.
"""
        }
    ]


# --------------------------------------------------
# HUGGING FACE CONNECTION
# --------------------------------------------------

def get_client():

    if "HF_TOKEN" not in st.secrets:
        return None

    return InferenceClient(
        token=st.secrets["HF_TOKEN"]
    )


# --------------------------------------------------
# LENO RESPONSE
# --------------------------------------------------

def ask_leno(user_message):

    client = get_client()

    if client is None:
        return (
            "My online AI connection isn't configured yet. "
            "The full local LENO version runs with Ollama."
        )

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    try:

        response = client.chat.completions.create(
            model="meta-llama/Llama-3.2-3B-Instruct",
            messages=st.session_state.messages,
            max_tokens=300,
            temperature=0.7
        )

        answer = response.choices[0].message.content.strip()

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        return answer

    except Exception as error:

        return (
            "I couldn't reach my online AI service right now.\n\n"
            f"Technical details: {error}"
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
# USER INPUT
# --------------------------------------------------

user_message = st.chat_input(
    "Speak to LENO or type a message..."
)


if user_message:

    with st.chat_message("user"):
        st.markdown(user_message)

    with st.chat_message("assistant"):

        with st.spinner("LENO is thinking..."):

            answer = ask_leno(
                user_message
            )

        st.markdown(answer)


# --------------------------------------------------
# INFORMATION
# --------------------------------------------------

st.divider()

st.caption(
    "LENO is an experimental AI assistant. "
    "The public demo is separate from the full local LENO system."
)
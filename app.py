


import time, random, itertools
import streamlit as st


st.set_page_config(page_title="Mylle Chat", page_icon="💖", layout="centered")

def humanize_text(text: str) -> str:
    if not text:
        return text
    if random.random() < 0.15:
        idx = random.randint(0, len(text)-1)
        typo = text[:idx] + text[idx].upper() + text[idx+1:]
        return f"{typo}... ops, quis dizer: {text}"
    if random.random() < 0.1:
        return text + " kkk"
    return text

def show_typing_indicator(duration: float = 2.0):
    placeholder = st.empty()
    dots = itertools.cycle([".", "..", "..."])
    end_time = time.time() + duration
    while time.time() < end_time:
        placeholder.markdown(f"⏳ digitando{next(dots)}")
        time.sleep(0.5)
    placeholder.empty()

def show_recording_indicator(duration: float = 3.0):
    placeholder = st.empty()
    end_time = time.time() + duration
    toggle = True
    while time.time() < end_time:
        icon = "🔴 Gravando áudio..." if toggle else "⚪ Gravando áudio..."
        placeholder.markdown(f"<span style='color:red;font-weight:bold'>{icon}</span>", unsafe_allow_html=True)
        toggle = not toggle
        time.sleep(0.7)
    placeholder.empty()

NORMAL_AUDIOS = [
    "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/oi%20meu%20amor%20tudo%20bem.mp3",
    "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/Claro%20eu%20tenho%20amostra%20gr%C3%A1tis.mp3",
    "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/eu%20tenho%20uns%20conteudos%20aqui%20que%20vc%20vai%20amar.mp3"
]

st.title("💖 Chat da Mylle")

if "chat" not in st.session_state:
    st.session_state["chat"] = []

for role, content in st.session_state["chat"]:
    with st.chat_message(role):
        if isinstance(content, dict) and content.get("type") == "audio":
            st.audio(content["url"], format="audio/mp3")
        else:
            st.markdown(content if isinstance(content,str) else content.get("content",""))

if prompt := st.chat_input("Fala comigo, amor 💬"):
    st.session_state["chat"].append(("user", prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if random.random() < 0.3:
            show_recording_indicator(random.uniform(2.5, 4.5))
            if antifake.is_trigger(prompt):
                reply = antifake.reply()
                if reply["type"]=="audio":
                    st.audio(reply["url"], format="audio/mp3")
                else:
                    st.markdown(reply["content"])
                st.session_state["chat"].append(("assistant", reply))
            else:
                url = random.choice(NORMAL_AUDIOS)
                st.audio(url, format="audio/mp3")
                st.session_state["chat"].append(("assistant", {"type":"audio","url":url}))
        else:
            show_typing_indicator(random.uniform(1.5, 3.5))
            if antifake.is_trigger(prompt):
                reply = antifake.reply()
                if reply["type"]=="audio":
                    st.audio(reply["url"], format="audio/mp3")
                else:
                    st.markdown(reply["content"])
                st.session_state["chat"].append(("assistant", reply))
            else:
                fake_reply = f"Amor, adorei o que você falou: '{prompt}' 💕"
                fake_reply = humanize_text(fake_reply)
                st.markdown(fake_reply)
                st.session_state["chat"].append(("assistant", fake_reply))

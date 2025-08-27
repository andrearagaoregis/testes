import streamlit as st
import requests
import json
import time
import random
import logging
import uuid

from config import Config
from memory import conversation_memory
from mood_detector import mood_detector
from anti_fake import anti_fake_system
from typing_simulator import typing_simulator
from audio_manager import audio_manager
from personality_engine import personality_engine
from utils import get_user_id, init_db, detect_fake_question, save_message, load_messages, extract_user_info
from timing_simulator import timing_simulator
from ml_engine import ml_engine

logger = logging.getLogger(__name__)

# Estilos CSS aprimorados
hide_streamlit_style = """
<style>
    #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0rem;}
    div[data-testid="stToolbar"], div[data-testid="stDecoration"], 
    div[data-testid="stStatusWidget"], #MainMenu, header, footer, 
    .stDeployButton {display: none !important;}
    .block-container {padding-top: 0rem !important;}
    [data-testid="stVerticalBlock"], [data-testid="stHorizontalBlock"] {gap: 0.5rem !important;}
    .stApp {
        margin: 0 !important; 
        padding: 0 !important;
        background: radial-gradient(1200px 500px at -10% -10%, rgba(255, 0, 153, 0.25) 0%, transparent 60%) ,
                    radial-gradient(1400px 600px at 110% 10%, rgba(148, 0, 211, .25) 0%, transparent 55%),
                    linear-gradient(135deg, #140020 0%, #25003b 50%, #11001c 100%);
        color: white;
    }
    
    /* Melhorias no chat - texto branco para Mylle */
    .stChatMessage[data-testid="chat-message-assistant"] {
        background: rgba(255, 102, 179, 0.15) !important;
        border: 1px solid #ff66b3 !important;
        color: white !important;
    }
    
    .stChatMessage[data-testid="chat-message-assistant"] .stMarkdown {
        color: white !important;
    }
    
    .stChatMessage[data-testid="chat-message-assistant"] p {
        color: white !important;
    }
    
    .stChatMessage {
        padding: 12px !important; 
        border-radius: 15px !important; 
        margin: 8px 0 !important;
    }
    
    .stButton > button {
        transition: all 0.3s ease !important;
        background: linear-gradient(45deg, #ff1493, #9400d3) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important; 
        box-shadow: 0 4px 8px rgba(255, 20, 147, 0.4) !important;
    }
    .stTextInput > div > div > input {
        background: rgba(255, 102, 179, 0.1) !important;
        color: white !important;
        border: 1px solid #ff66b3 !important;
    }
    .social-buttons {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin: 15px 0;
    }
    .social-button {
        background: rgba(255, 102, 179, 0.2) !important;
        border: 1px solid #ff66b3 !important;
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.3s ease !important;
    }
    .social-button:hover {
        background: rgba(255, 102, 179, 0.4) !important;
        transform: scale(1.1) !important;
    }
    .cta-button {
        margin-top: 10px !important;
        background: linear-gradient(45deg, #ff1493, #9400d3) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 15px !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
    }
    .cta-button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(255, 20, 147, 0.4) !important;
    }
    .audio-message {
        background: rgba(255, 102, 179, 0.15) !important;
        padding: 15px !important;
        border-radius: 15px !important;
        margin: 10px 0 !important;
        border: 1px solid #ff66b3 !important;
        text-align: center !important;
    }
    .audio-icon {
        font-size: 24px !important;
        margin-right: 10px !important;
    }
    .recording-indicator {
        display: inline-block;
        padding: 8px 12px;
        background: rgba(255, 0, 0, 0.2);
        border-radius: 15px;
        color: #ff4444;
        margin: 5px 0;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    .typing-indicator {
        display: inline-block;
        padding: 12px;
        background: rgba(255,102,179,0.1);
        border-radius: 18px;
        margin: 5px 0;
        color: white;
    }
    .typing-indicator span {
        height: 8px;
        width: 8px;
        background: #ff66b3;
        border-radius: 50%;
        display: inline-block;
        margin: 0 2px;
        animation: typing 1.4s infinite;
    }
    .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
    .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes typing {
        0%, 60%, 100% { transform: translateY(0); }
        30% { transform: translateY(-5px); }
    }
    .donation-badge {
        background: linear-gradient(45deg, #ff6b35, #f7931e);
        color: white;
        padding: 3px 8px;
        border-radius: 10px;
        font-size: 0.7em;
        margin-left: 5px;
    }
    
    .user-typing-indicator {
        background: rgba(255, 255, 255, 0.1);
        padding: 8px 12px;
        border-radius: 15px;
        color: #aaa;
        font-style: italic;
        margin: 5px 0;
    }
    
    /* Melhorias responsivas e de acessibilidade */
    @media (max-width: 768px) {
        .stButton > button {
            padding: 12px 8px;
            font-size: 14px;
        }
        .stChatMessage {
            padding: 8px !important;
            margin: 5px 0 !important;
        }
        .audio-message {
            padding: 10px !important;
        }
    }
    
    .stButton > button:focus {
        outline: 2px solid #ff66b3;
        outline-offset: 2px;
    }
    
    .stChatMessage {
        transition: all 0.3s ease;
    }
    
    /* Indicador de digitação do usuário */
    .user-typing {
        background: rgba(255, 255, 255, 0.05);
        padding: 8px 15px;
        border-radius: 20px;
        color: #ccc;
        font-style: italic;
        margin: 10px 0;
        border-left: 3px solid #ff66b3;
    }
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.set_page_config(
    page_title="Mylle Alves Premium",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

class DonationSystem:
    def show_donation_modal(self):
        st.markdown("""
            <div style="
                background: rgba(255, 102, 179, 0.1);
                padding: 15px;
                border-radius: 15px;
                border: 1px solid #ff66b3;
                text-align: center;
                margin-bottom: 20px;
            ">
                <h3 style="color: #ff66b3; margin: 0;">💝 Apoie Meu Conteúdo</h3>
                <p style="color: #aaa; margin: 5px 0 0;">Sua doação me ajuda a criar mais conteúdo exclusivo!</p>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("### 🎯 Valores Sugeridos")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("R$ 30", key="donate_30", use_container_width=True):
                self._redirect_to_checkout(30)
        with col2:
            if st.button("R$ 50", key="donate_50", use_container_width=True):
                self._redirect_to_checkout(50)
        with col3:
            if st.button("R$ 100", key="donate_100", use_container_width=True):
                self._redirect_to_checkout(100)
        with col4:
            if st.button("R$ 150", key="donate_150", use_container_width=True):
                self._redirect_to_checkout(150)
    
    def _redirect_to_checkout(self, amount: float, is_custom: bool = False):
        user_id = get_user_id()
        
        if is_custom:
            checkout_url = Config.DONATION_CHECKOUT_LINKS["custom"]
        else:
            checkout_url = Config.DONATION_CHECKOUT_LINKS.get(amount, Config.DONATION_CHECKOUT_LINKS["custom"])
        
        st.markdown(f"""
        <script>
            window.open(\\'{checkout_url}\\', \'_blank\');
        </script>
        """, unsafe_allow_html=True)
        
        st.success(f"✅ Redirecionando para página de pagamento de R$ {amount:.2f}...")

donation_system = DonationSystem()

def call_gemini_api(prompt: str, user_id: str) -> dict:
    try:
        if Config.API_KEY == "sua_chave_api_gemini_aqui":
            return {
                "text": "⚠️ Sistema em configuração. Configure sua API Key do Gemini para usar o chat.",
                "audio": None,
                "cta": {"show": False},
                "typing_time": 2.0
            }
        
        mood = mood_detector.detect_mood(prompt)
        fake_analysis = anti_fake_system.analyze_user_behavior(user_id, prompt)
        
        fake_probability = detect_fake_question(prompt)
        if fake_probability > 0.7:
            audio_key = "nao_sou_fake_nao"
            return {
                "text": "Não sou fake não, amor! Ouça minha voz... 😘 Como posso provar que sou real pra você?",
                "audio": audio_key,
                "cta": {"show": False},
                "typing_time": typing_simulator.calculate_typing_time("Não sou fake não, amor! Ouça minha voz... 😘 Como posso provar que sou real pra você?")
            }
        
        # Simular delay de atividade real
        simulated_delay, delay_message = timing_simulator.get_simulated_delay(user_id)
        if simulated_delay > 0:
            st.session_state.messages.append({"role": "assistant", "content": delay_message, "metadata": {"is_delay_message": True}})
            time.sleep(simulated_delay)

        personality_prompt = personality_engine.generate_personality_prompt(prompt, user_id, mood)
        
        data = {
            "contents": [{
                "parts": [{"text": personality_prompt}]
            }]
        }
        
        response = requests.post(
            Config.API_URL,
            json=data,
            timeout=Config.REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            
            # Aplicar imperfeições humanas
            text = anti_fake_system.introduce_typing_error(text)
            text = anti_fake_system.simulate_forgetfulness(text)

            # Simular limitação humana
            limitation_message = anti_fake_system.simulate_limitation()
            if limitation_message:
                text = f"{limitation_message} {text}"

            if len(text) > 200:
                sentences = text.split(".")
                text = ". ".join(sentences[:2]) + "."
            
            user_profile = conversation_memory.get_user_profile(user_id)
            audio_key = audio_manager.get_contextual_audio(prompt, mood, user_profile)
            
            typing_time = typing_simulator.calculate_typing_time(text)
            
            conversation_memory.add_message(user_id, "user", prompt, {"mood": mood})
            conversation_memory.add_message(user_id, "assistant", text, {"audio": audio_key})
            
            extract_user_info(prompt, user_id)

            # Atualizar score de engajamento
            ml_engine.update_engagement_score(user_id, message_quality=1.0, cta_clicked=False) # CTA clicked será atualizado no show_chat_page
            
            return {
                "text": text,
                "audio": audio_key,
                "cta": {"show": True, "label": "📦 Ver Packs", "target": "offers"},
                "typing_time": typing_time
            }
        else:
            return {
                "text": "Estou com problemas técnicos agora, amor 😔 Tenta de novo em um minutinho?",
                "audio": None,
                "cta": {"show": False},
                "typing_time": 2.0
            }
            
    except Exception as e:
        logger.error(f"Erro na API: {e}")
        return {
            "text": "Oops! Algo deu errado... Me manda de novo? 😘",
            "audio": None,
            "cta": {"show": False},
            "typing_time": 1.5
        }

def show_typing_indicator():
    return st.markdown("""
    <div class="typing-indicator">
        <span></span>
        <span></span>
        <span></span>
        Mylle está digitando...
    </div>
    """, unsafe_allow_html=True)

def show_recording_indicator(duration: float):
    return st.markdown(f"""
    <div class="recording-indicator">
        🎤 Gravando áudio... ({duration:.1f}s)
    </div>
    """, unsafe_allow_html=True)

def show_user_typing_indicator():
    return st.markdown("""
    <div class="user-typing">
        Você está digitando...
    </div>
    """, unsafe_allow_html=True)

def show_home_page():
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <h1 style="color: #ff66b3; font-size: 2.5em; margin-bottom: 10px;">
            🔥 Mylle Alves Premium 🔥
        </h1>
        <p style="color: #aaa; font-size: 1.2em; margin-bottom: 30px;">
            Conteúdo exclusivo e muito quente te esperando...
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(Config.IMG_PROFILE, width=300, caption="Mylle Alves 💋")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💬 Conversar Comigo", use_container_width=True):
            st.session_state.current_page = "chat"
            st.rerun()
    
    with col2:
        if st.button("📦 Ver Meus Packs", use_container_width=True):
            st.session_state.current_page = "offers"
            st.rerun()
    
    with col3:
        if st.button("🖼️ Galeria", use_container_width=True):
            st.session_state.current_page = "gallery"
            st.rerun()
    
    st.markdown("### 🌟 Me siga nas redes:")
    social_cols = st.columns(4)
    
    for i, (platform, link) in enumerate(Config.SOCIAL_LINKS.items()):
        with social_cols[i]:
            icon = Config.SOCIAL_ICONS[platform]
            if st.button(icon, key=f"social_{platform}", use_container_width=True):
                st.markdown(f\'<script>window.open("{link}", "_blank");</script>\
', unsafe_allow_html=True)

def show_chat_page():
    st.markdown("### 💬 Chat com Mylle Alves")
    
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                
                if message["role"] == "assistant" and message.get("metadata", {}).get("audio"):
                    audio_key = message["metadata"]["audio"]
                    audio_url = Config.AUDIOS.get(audio_key, {}).get("url")
                    if audio_url:
                        st.audio(audio_url)
    
    if st.session_state.get("user_typing", False):
        show_user_typing_indicator()
    
    if prompt := st.chat_input("Digite sua mensagem..."):
        if st.session_state.request_count >= Config.MAX_REQUESTS_PER_SESSION:
            st.error("Limite de mensagens atingido para esta sessão.")
            return
        
        st.session_state.user_typing = True
        time.sleep(random.uniform(0.5, 1.5))
        st.session_state.user_typing = False
        
        user_message = {"role": "user", "content": prompt, "metadata": {}}
        st.session_state.messages.append(user_message)
        st.session_state.request_count += 1
        
        save_message(st.session_state.db_conn, get_user_id(), st.session_state.session_id, "user", prompt)
        
        with st.chat_message("user"):
            st.write(prompt)
        
        time.sleep(random.uniform(2.0, 5.0))
        
        with st.chat_message("assistant"):
            typing_placeholder = st.empty()
            typing_placeholder.markdown("""
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
                Mylle está digitando...
            </div>
            """, unsafe_allow_html=True)
            
            response = call_gemini_api(prompt, get_user_id())
            
            time.sleep(response.get("typing_time", 2.0))
            
            typing_placeholder.empty()
            
            st.write(response["text"])
            
            if response.get("audio"):
                audio_key = response["audio"]
                
                recording_time = audio_manager.simulate_recording_time(audio_key)
                recording_placeholder = st.empty()
                recording_placeholder.markdown(f"""
                <div class="recording-indicator">
                    🎤 Gravando áudio... ({recording_time:.1f}s)
                </div>
                """, unsafe_allow_html=True)
                
                time.sleep(recording_time)
                
                recording_placeholder.empty()
                
                audio_url = Config.AUDIOS.get(audio_key, {}).get("url")
                if audio_url:
                    st.audio(audio_url)
                    audio_manager.mark_audio_used(audio_key, get_user_id())
            
            if response.get("cta", {}).get("show"):
                if st.button(response["cta"]["label"], key=f"cta_button_{len(st.session_state.messages)}"):
                    st.session_state.current_page = response["cta"]["target"]
                    ml_engine.update_engagement_score(get_user_id(), cta_clicked=True) # Atualiza engajamento ao clicar no CTA
                    st.rerun()
        
        assistant_message = {
            "role": "assistant", 
            "content": response["text"],
            "metadata": {"audio": response.get("audio")}
        }
        st.session_state.messages.append(assistant_message)
        save_message(st.session_state.db_conn, get_user_id(), st.session_state.session_id, "assistant", response["text"], {"audio": response.get("audio")})

def show_offers_page():
    st.markdown("### 📦 Meus Packs Exclusivos")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(Config.PACK_IMAGES["TARADINHA"], width=200)
    with col2:
        st.markdown("""
        #### 🔥 Pack Taradinha - R$ 30
        - 50+ fotos sensuais
        - Conteúdo exclusivo
        - Acesso imediato
        """)
        if st.button("💳 Comprar Pack Taradinha", key="buy_taradinha"):
            st.markdown(f\'<script>window.open("{Config.CHECKOUT_TARADINHA}", "_blank");</script>\
', unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(Config.PACK_IMAGES["MOLHADINHA"], width=200)
    with col2:
        st.markdown("""
        #### 💦 Pack Molhadinha - R$ 50
        - 80+ fotos quentes
        - Vídeos exclusivos
        - Conteúdo premium
        """)
        if st.button("💳 Comprar Pack Molhadinha", key="buy_molhadinha"):
            st.markdown(f\'<script>window.open("{Config.CHECKOUT_MOLHADINHA}", "_blank");</script>\
', unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(Config.PACK_IMAGES["SAFADINHA"], width=200)
    with col2:
        st.markdown("""
        #### 😈 Pack Safadinha - R$ 80
        - 120+ fotos explícitas
        - Vídeos longos
        - Conteúdo mais ousado
        """)
        if st.button("💳 Comprar Pack Safadinha", key="buy_safadinha"):
            st.markdown(f\'<script>window.open("{Config.CHECKOUT_SAFADINHA}", "_blank");</script>\
', unsafe_allow_html=True)

def show_gallery_page():
    st.markdown("### 🖼️ Galeria de Fotos")
    
    st.info("🔒 Algumas fotos são apenas uma amostra. Para ver o conteúdo completo, adquira meus packs!")
    
    cols = st.columns(3)
    for i, img_url in enumerate(Config.IMG_GALLERY):
        with cols[i % 3]:
            st.image(img_url, caption=f"Foto {i+1}")
    
    st.markdown("---")
    if st.button("📦 Ver Todos os Packs", use_container_width=True):
        st.session_state.current_page = "offers"
        st.rerun()

def show_sidebar():
    with st.sidebar:
        st.markdown("### 🔥 Mylle Alves")
        st.image(Config.IMG_PROFILE, width=150)
        
        st.markdown("---")
        
        if st.button("🏠 Início", use_container_width=True):
            st.session_state.current_page = "home"
            st.rerun()
        
        if st.button("💬 Chat", use_container_width=True):
            st.session_state.current_page = "chat"
            st.rerun()
        
        if st.button("📦 Packs", use_container_width=True):
            st.session_state.current_page = "offers"
            st.rerun()
        
        if st.button("🖼️ Galeria", use_container_width=True):
            st.session_state.current_page = "gallery"
            st.rerun()
        
        st.markdown("---")
        
        donation_system.show_donation_modal()
        
        st.markdown("---")
        st.markdown("💋 **Mylle Alves Premium**")
        st.markdown("Conteúdo exclusivo para maiores de 18 anos")

def handle_age_verification():
    if not st.session_state.get("age_verified", False):
        st.markdown("""
        <div style="text-align: center; padding: 50px;">
            <h1 style="color: #ff66b3;">🔞 Verificação de Idade</h1>
            <p style="font-size: 1.2em; color: #aaa;">
                Este conteúdo é destinado apenas para maiores de 18 anos.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("✅ Sou maior de 18", use_container_width=True):
                st.session_state.age_verified = True
                st.rerun()
        
        with col3:
            if st.button("❌ Sou menor de 18", use_container_width=True):
                st.error("Você deve ser maior de 18 anos para acessar este conteúdo.")
                st.stop()
        
        return False
    return True

def main():
    if "db_conn" not in st.session_state:
        st.session_state.db_conn = init_db()
    
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(random.randint(100000, 999999))
    
    if "messages" not in st.session_state:
        loaded_messages = load_messages(
            st.session_state.db_conn, 
            get_user_id(), 
            st.session_state.session_id
        )
        st.session_state.messages = loaded_messages
        
        for msg in loaded_messages:
            conversation_memory.add_message(
                get_user_id(), 
                msg["role"], 
                msg["content"], 
                msg.get("metadata", {})
            )
    
    if "request_count" not in st.session_state:
        st.session_state.request_count = len([m for m in st.session_state.messages if m["role"] == "user"])
    
    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"
    
    if "user_typing" not in st.session_state:
        st.session_state.user_typing = False
    
    if not handle_age_verification():
        return
    
    show_sidebar()
    
    if st.session_state.current_page == "home":
        show_home_page()
    elif st.session_state.current_page == "chat":
        show_chat_page()
    elif st.session_state.current_page == "offers":
        show_offers_page()
    elif st.session_state.current_page == "gallery":
        show_gallery_page()

if __name__ == "__main__":
    main()



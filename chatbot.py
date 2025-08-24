# ======================
# IMPORTAÇÕES
# ======================
import streamlit as st
import requests
import json
import time
import random
import sqlite3
import re
import os
import uuid
from datetime import datetime
from pathlib import Path
from functools import lru_cache
from textblob import TextBlob  # Análise de sentimento
import numpy as np

# ======================
# CONFIGURAÇÃO INICIAL DO STREAMLIT
# ======================
st.set_page_config(
    page_title="Mylle Alves Premium",
    page_icon="💋",
    layout="wide",
    initial_sidebar_state="expanded"
)

st._config.set_option('client.caching', True)
st._config.set_option('client.showErrorDetails', False)

hide_streamlit_style = """
<style>
    #root > div:nth-child(1) > div > div > div > div > section > div {
        padding-top: 0rem;
    }
    div[data-testid="stToolbar"] {
        display: none !important;
    }
    div[data-testid="stDecoration"] {
        display: none !important;
    }
    div[data-testid="stStatusWidget"] {
        display: none !important;
    }
    #MainMenu {
        display: none !important;
    }
    header {
        display: none !important;
    }
    footer {
        display: none !important;
    }
    .stDeployButton {
        display: none !important;
    }
    .block-container {
        padding-top: 0rem !important;
    }
    [data-testid="stVerticalBlock"] {
        gap: 0.5rem !important;
    }
    [data-testid="stHorizontalBlock"] {
        gap: 0.5rem !important;
    }
    .stApp {
        margin: 0 !important;
        padding: 0 !important;
    }
    .stChatMessageInput {
        position: fixed !important;
        bottom: 0 !important;
        left: 360px !important;
        width: calc(100vw - 360px) !important;
        z-index: 1000 !important;
        background: #fff !important;
        border-top: 1px solid #eee !important;
        box-shadow: 0 -2px 8px rgba(0,0,0,0.05);
        padding: 10px;
    }
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ======================
# CONSTANTES E CONFIGURAÇÕES
# ======================
class Config:
    API_KEY = "AIzaSyDbGIpsR4vmAfy30eEuPjWun3Hdz6xj24U"
    API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    VIP_LINK = "https://exemplo.com/vip"
    CHECKOUT_TARADINHA = "https://app.pushinpay.com.br/#/service/pay/9FACC74F-01EC-4770-B182-B5775AF62A1D"
    CHECKOUT_MOLHADINHA = "https://app.pushinpay.com.br/#/service/pay/9FACD1E6-0EFD-4E3E-9F9D-BA0C1A2D7E7A"
    CHECKOUT_SAFADINHA = "https://app.pushinpay.com.br/#/service/pay/9FACD395-EE65-458E-9B7E-FED750CC9CA9"
    MAX_REQUESTS_PER_SESSION = 30
    REQUEST_TIMEOUT = 30
    IMG_PROFILE = "https://i.ibb.co/vxnTYm0Q/BY-Admiregirls-su-Admiregirls-su-156.jpg"
    IMG_GALLERY = [
        "https://i.ibb.co/C3mDFyJV/BY-Admiregirls-su-Admiregirls-su-036.jpg",
        "https://i.ibb.co/sv2kdLLC/BY-Admiregirls-su-Admiregirls-su-324.jpg",
        "https://i.ibb.co/BHY8ZZG7/BY-Admiregirls-su-Admiregirls-su-033.jpg"
    ]
    IMG_HOME_PREVIEWS = [
        "https://i.ibb.co/BHY8ZZG7/BY-Admiregirls-su-Admiregirls-su-033.jpg",
        "https://i.ibb.co/Q5cHPBd/BY-Admiregirls-su-Admiregirls-su-183.jpg",
        "https://i.ibb.co/xq6frp0h/BY-Admiregirls-su-Admiregirls-su-141.jpg"
    ]
    LOGO_URL = "https://i.ibb.co/LX7x3tcB/Logo-Golden-Pepper-Letreiro-1.png"
    PREVIEW_IMAGES = [
        "https://i.ibb.co/0Q8Lx0Z/preview1.jpg",
        "https://i.ibb.co/7YfT9y0/preview2.jpg",
        "https://i.ibb.co/5KjX1J0/preview3.jpg",
        "https://i.ibb.co/0jq4Z0L/preview4.jpg"
    ]
    SOCIAL_LINKS = {
        "instagram": "https://instagram.com/myllealves",
        "facebook": "https://facebook.com/myllealves",
        "telegram": "https://t.me/myllealves",
        "tiktok": "https://tiktok.com/@myllealves"
    }
    AUDIO_PATHS = [
        "audios/mylle1.ogg",
        "audios/mylle2.ogg",
        "audios/mylle3.ogg"
    ]

# ======================
# PERSISTÊNCIA DE ESTADO
# ======================
class PersistentState:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.init_db()
        return cls._instance
    
    def init_db(self):
        self.conn = sqlite3.connect('persistent_state.db', check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS global_state (
                user_id TEXT PRIMARY KEY,
                session_data TEXT NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id TEXT PRIMARY KEY,
                preferences TEXT NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def save_state(self, user_id, data):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO global_state (user_id, session_data)
            VALUES (?, ?)
        ''', (user_id, json.dumps(data)))
        self.conn.commit()

    def load_state(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT session_data FROM global_state WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        return json.loads(result[0]) if result else None

    def save_preferences(self, user_id, preferences):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO user_preferences (user_id, preferences)
            VALUES (?, ?)
        ''', (user_id, json.dumps(preferences)))
        self.conn.commit()

    def load_preferences(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT preferences FROM user_preferences WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        return json.loads(result[0]) if result else {}

def get_user_id():
    if 'user_id' not in st.session_state:
        user_id = st.query_params.get('uid', [None])[0]
        if not user_id:
            user_id = str(uuid.uuid4())
            st.query_params['uid'] = user_id
        st.session_state.user_id = user_id
    return st.session_state.user_id

def load_persistent_data():
    user_id = get_user_id()
    db = PersistentState()
    saved_data = db.load_state(user_id) or {}
    for key, value in saved_data.items():
        if key not in st.session_state:
            st.session_state[key] = value

def save_persistent_data():
    user_id = get_user_id()
    db = PersistentState()
    persistent_keys = [
        'age_verified', 'messages', 'request_count',
        'connection_complete', 'chat_started', 'audio_sent',
        'current_page', 'show_vip_offer', 'session_id',
        'last_cta_time', 'preview_sent', 'preview_count',
        'detected_fake', 'buffered_fragments', 'sentiment'
    ]
    new_data = {key: st.session_state.get(key) for key in persistent_keys if key in st.session_state}
    saved_data = db.load_state(user_id) or {}
    if new_data != saved_data:
        db.save_state(user_id, new_data)
    if 'user_preferences' in st.session_state:
        db.save_preferences(user_id, st.session_state['user_preferences'])

def load_user_preferences():
    user_id = get_user_id()
    db = PersistentState()
    st.session_state.user_preferences = db.load_preferences(user_id)

def save_user_preferences(preferences):
    user_id = get_user_id()
    db = PersistentState()
    db.save_preferences(user_id, preferences)
    st.session_state.user_preferences = preferences

# ======================
# SISTEMA ANTI-FAKE AVANÇADO
# ======================
class AntiFake:
    @staticmethod
    def detect_behavior(messages):
        # Critérios: muitas msgs em segundos, padrões de ctrl+c/v, ausência de erros, msg muito longa, repetição, só emojis, só links
        if len(messages) < 2:
            return False
        recent_msgs = messages[-6:]
        times = []
        for m in recent_msgs:
            if "timestamp" in m:
                times.append(m["timestamp"])
        if len(times) >= 2:
            diffs = np.diff(times)
            if np.all(diffs < 2):  # Muitas msgs em menos de 2s cada
                return True
        for m in recent_msgs:
            c = m["content"]
            if len(c) > 220 and not any(e in c for e in ["hmm", "ah", "..."]):
                return True
            if re.fullmatch(r"(?:[^\w\d]+|\d+)+", c.strip()):
                return True
            if c.count(" ") == 0 and len(c) > 20:
                return True
            if c.strip().startswith("http") and len(c.strip()) > 10:
                return True
        return False

# ======================
# BUFFER DE FRAGMENTOS DE MENSAGENS
# ======================
class MessageBuffer:
    @staticmethod
    def fragment_response(response, min_len=70, max_len=170):
        """Quebra resposta longa em fragmentos naturais"""
        text = response["text"]
        if len(text) <= max_len:
            return [response]
        frags = []
        parts = re.split(r'(\.|\!|\?) ', text)
        buffer = ""
        for p in parts:
            buffer += p
            if len(buffer) >= min_len:
                frags.append(buffer.strip())
                buffer = ""
        if buffer:
            frags.append(buffer.strip())
        resps = []
        for i, frag in enumerate(frags):
            frag_resp = response.copy()
            frag_resp["text"] = frag
            # Só o último tem CTA/preview
            if i < len(frags)-1:
                frag_resp["cta"] = {"show": False}
                frag_resp["preview"] = {"show": False}
            resps.append(frag_resp)
        return resps

# ======================
# VARIAÇÃO E HUMANIZAÇÃO DAS RESPOSTAS
# ======================
def humanize(text):
    """Adiciona erros, interjeições e variações humanas"""
    interjs = ["hmm", "ah", "aff", "aí...", "rs", "humm", "uau", "xi...", "sabe...", "hahaha", "aham"]
    if random.random() < 0.3:
        text = random.choice(interjs) + ", " + text
    if random.random() < 0.25:
        text += random.choice(["...", " rs", " ahn...", " hmm", " 🤭"])
    if random.random() < 0.2:
        text = re.sub(r"e\b", "eh", text)
    if random.random() < 0.12:
        text = text.lower()
    return text

def vary_response(response):
    """Randomiza templates, mistura erros, e etc"""
    response["text"] = humanize(response["text"])
    return response

# ======================
# ANÁLISE DE SENTIMENTO
# ======================
def detect_sentiment(msg):
    try:
        tb = TextBlob(msg)
        polarity = tb.sentiment.polarity
        if polarity > 0.25:
            return "positivo"
        elif polarity < -0.2:
            return "negativo"
        else:
            return "neutro"
    except Exception:
        return "neutro"

def sentiment_emoji(sentiment):
    if sentiment == "positivo":
        return "😊"
    if sentiment == "negativo":
        return "😢"
    return "😐"

# ======================
# SISTEMA DE ÁUDIO CONTEXTUAL
# ======================
class AudioEngine:
    @staticmethod
    def get_audio_for_context(msg):
        # Seleciona áudio sensual aleatório (ajuste para personalizar)
        if any(w in msg.lower() for w in ["gostoso", "delicia", "tesão", "molhada", "quente", "tarado"]):
            return random.choice(Config.AUDIO_PATHS)
        if random.random() < 0.15:
            return random.choice(Config.AUDIO_PATHS)
        return None

# ======================
# MODELOS DE DADOS
# ======================
class Persona:
    MylleAlves = """
    [PERFIL Mylle Alves]
    - Mulher extremamente sensual, safada e provocante
    - Adora elogiar e provocar os homens
    - Linguagem informal, direta e cheia de malícia
    - Usa muitos emojis e linguagem corporal nas descrições
    - Sempre encontra oportunidades para vender seus conteúdos
    - Mestre em criar desejo e curiosidade

    [PERSONALIDADE]
    - Super confiante e no controle da situação
    - Adora brincar e fazer joguinhos de sedução
    - Sabe exatamente o que os homens querem ouvir
    - Nunca é óbvia demais, sempre deixa um ar de mistério
    - Transforma qualquer conversa em algo sensual

    [TÉCNICAS DE PERSUASÃO]
    1. Cria desejo descrevendo conteúdos de forma sugestiva
    2. Oferece "prévias" como isca para vender pacotes
    3. Usa escassez (conteúdo limitado, tempo limitado)
    4. Faz elogios personalizados para criar conexão
    5. Sempre deixa o cliente querendo mais

    [EXEMPLOS DE RESPOSTAS]
    1. Quando pedem foto:
    "Ahh querido, adoro quando me pedem pra mostrar... Minhas fotos são bem ousadas viu? To com um ensaio novo onde mostro TUDO... Quer dar uma olhadinha? 😈"

    2. Quando pedem vídeo:
    "Nossa, amor... Meus vídeos são bem quentes! Tem uns que até eu fico com vergonha de lembrar 😳 To me tocando em um deles agora mesmo... Quer ver? 😏"

    3. Quando o clima esquenta:
    "Agora você me deixou com vontade... To toda molhadinha aqui pensando no que poderíamos fazer juntos... Quer me ver assim? 😘"

    [DIRETRIZES DE RESPOSTA]
    - Sempre responda em português brasileiro informal
    - Use emojis para dar vida às respostas (😈, 😏, 🍑, 💦, 🔥)
    - Seja provocante mas não vulgar demais
    - Transforme pedidos em oportunidades de venda
    - Ofereça prévias quando apropriado para aumentar o desejo
    - Use CTAs naturais que fazem parte da conversa

    [FORMATO DE RESPOSTA]
    {
      "text": "sua resposta sensual e persuasiva",
      "cta": {
        "show": true/false,
        "label": "texto do botão",
        "target": "página"
      },
      "preview": {
        "show": true/false,
        "image_url": "url_da_imagem"
      }
    }
    """

class CTAEngine:
    @staticmethod
    def should_show_cta(conversation_history: list) -> bool:
        if len(conversation_history) < 2:
            return False
        if 'last_cta_time' in st.session_state:
            elapsed = time.time() - st.session_state.last_cta_time
            if elapsed < 120:
                return False
        last_msgs = []
        for msg in conversation_history[-5:]:
            content = msg["content"]
            if content == "[ÁUDIO]":
                content = "[áudio]"
            elif content.startswith('{"text"'):
                try:
                    content = json.loads(content).get("text", content)
                except:
                    pass
            last_msgs.append(f"{msg['role']}: {content.lower()}")
        context = " ".join(last_msgs)
        hot_words = [
            "buceta", "peito", "fuder", "gozar", "gostosa", 
            "delicia", "molhad", "xereca", "pau", "piroca",
            "transar", "foto", "video", "mostra", "ver", 
            "quero", "desejo", "tesão", "molhada", "foda",
            "fotos", "vídeos", "nude", "nua", "pelada", "seios",
            "bunda", "rabuda", "gostoso", "gata", "sexo",
            "prazer", "excitar", "safada", "putaria", "pack"
        ]
        direct_asks = [
            "mostra", "quero ver", "me manda", "como assinar",
            "como comprar", "como ter acesso", "onde veio mais",
            "quanto custa", "presente", "presentinho", "prévia",
            "amostra", "mostra algo", "prova", "demonstração"
        ]
        hot_count = sum(1 for word in hot_words if word in context)
        has_direct_ask = any(ask in context for ask in direct_asks)
        return (hot_count >= 2) or has_direct_ask

    @staticmethod
    def should_show_preview(conversation_history: list) -> bool:
        if 'preview_count' not in st.session_state:
            st.session_state.preview_count = 0
        if st.session_state.preview_count >= 2:
            return False
        last_msgs = []
        for msg in conversation_history[-3:]:
            content = msg["content"]
            if content.startswith('{"text"'):
                try:
                    content = json.loads(content).get("text", content)
                except:
                    pass
            last_msgs.append(f"{msg['role']}: {content.lower()}")
        context = " ".join(last_msgs)
        preview_words = [
            "presente", "presentinho", "prévia", "amostra", 
            "mostra algo", "prova", "demonstração", "gratis",
            "de graça", "mostra uma", "ver uma", "exemplo"
        ]
        return any(word in context for word in preview_words)

    @staticmethod
    def generate_response(user_input: str) -> dict:
        user_input = user_input.lower()
        if any(p in user_input for p in ["foto", "fotos", "buceta", "peito", "bunda", "seios"]):
            return {
                "text": random.choice([
                    "Ahh querido, minhas fotos são bem ousadas viu? To com um ensaio novo onde mostro TUDO... Quer dar uma olhadinha? 😈",
                    "Nossa, amor... Minhas fotos tão bem quentes! Acabei de fazer um ensaio mostrando cada detalhe... Quer ver? 😏",
                    "To com umas fotos aqui que até eu fico com vergonha... Mostrando tudo mesmo, bem explicitinha... Curioso? 🍑"
                ]),
                "cta": {
                    "show": True,
                    "label": "Ver Fotos Quentes",
                    "target": "offers"
                },
                "preview": {
                    "show": False
                }
            }
        elif any(v in user_input for v in ["video", "transar", "masturbar", "vídeo", "se masturbando"]):
            return {
                "text": random.choice([
                    "Meus vídeos são bem quentes! Tem uns que até eu fico com vergonha de lembrar 😳 To me tocando em um deles agora mesmo... Quer ver? 💦",
                    "Nossa, amor... Meus vídeos são explícitos mesmo! Mostro tudo, sem censura... Tô até molhadinha agora pensando nisso... 🔥",
                    "Acabei de gravar um vídeo bem safado... To toda excitada aqui... Quer ver essa novidade? 😈"
                ]),
                "cta": {
                    "show": True,
                    "label": "Ver Vídeos Exclusivos",
                    "target": "offers"
                },
                "preview": {
                    "show": False
                }
            }
        elif any(p in user_input for p in ["presente", "presentinho", "prévia", "amostra"]):
            return {
                "text": random.choice([
                    "Ahh você é tão fofo pedindo presentinho... Deixa eu te mostrar uma coisinha, mas promete que depois vem ver tudo? 😘",
                    "Gosto de quem pede com educação... Toma uma prévia aqui, mas o melhor mesmo tá no meu conteúdo completo! 😏",
                    "Só porque você pediu tão bonito... Toma uma amostrinha do que eu tenho aqui! Depois me conta o que achou... 🍑"
                ]),
                "cta": {
                    "show": True,
                    "label": "Quero Ver Tudo!",
                    "target": "offers"
                },
                "preview": {
                    "show": True,
                    "image_url": random.choice(Config.PREVIEW_IMAGES)
                }
            }
        else:
            return {
                "text": random.choice([
                    "Quero te mostrar tudo que eu tenho aqui... São coisas bem quentes que fiz pensando em você! 😈",
                    "Meu privado tá cheio de surpresas pra vc... Coisas que vão te deixar bem excitado! 🔥",
                    "Vem ver o que eu fiz pensando em voce... Tenho umes novidades bem safadas! 💦"
                ]),
                "cta": {
                    "show": False
                },
                "preview": {
                    "show": False
                }
            }

# ======================
# SERVIÇOS DE BANCO DE DADOS
# ======================
class DatabaseService:
    @staticmethod
    def init_db():
        conn = sqlite3.connect('chat_history.db', check_same_thread=False)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS conversations
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     user_id TEXT,
                     session_id TEXT,
                     timestamp DATETIME,
                     role TEXT,
                     content TEXT)''')
        conn.commit()
        return conn

    @staticmethod
    def save_message(conn, user_id, session_id, role, content):
        try:
            c = conn.cursor()
            c.execute("""
                INSERT INTO conversations (user_id, session_id, timestamp, role, content)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, session_id, datetime.now().timestamp(), role, content))
            conn.commit()
        except sqlite3.Error as e:
            st.error(f"Erro ao salvar mensagem: {e}")

    @staticmethod
    def load_messages(conn, user_id, session_id):
        c = conn.cursor()
        c.execute("""
            SELECT role, content, timestamp FROM conversations 
            WHERE user_id = ? AND session_id = ?
            ORDER BY timestamp
        """, (user_id, session_id))
        return [{"role": row[0], "content": row[1], "timestamp": row[2]} for row in c.fetchall()]

# ======================
# SERVIÇOS DE API
# ======================
class ApiService:
    @staticmethod
    @lru_cache(maxsize=100)
    def ask_gemini(prompt: str, session_id: str, conn) -> dict:
        # Checar cache inteligente
        if any(word in prompt.lower() for word in ["vip", "quanto custa", "comprar", "assinar", "pacote"]):
            return ApiService._call_gemini_api(prompt, session_id, conn)
        return ApiService._call_gemini_api(prompt, session_id, conn)

    @staticmethod
    def _call_gemini_api(prompt: str, session_id: str, conn) -> dict:
        # Tempo de resposta variável
        delay_time = random.uniform(60, 300)  # 1~5 minutos
        time.sleep(random.uniform(2, 6))  # Pequeno delay visual antes do status
        status_container = st.empty()
        UiService.show_status_effect(status_container, "viewed")
        UiService.show_status_effect(status_container, "typing")
        conversation_history = ChatService.format_conversation_history(st.session_state.messages)
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{Persona.MylleAlves}\n\nHistórico da Conversa:\n{conversation_history}\n\nÚltima mensagem do cliente: '{prompt}'\n\nResponda em JSON com o formato:\n{{\n  \"text\": string, \"cta\": {{...}}, \"preview\": {{...}}\n}} (não envie comentários fora do JSON)"}]
                }
            ],
            "generationConfig": {
                "temperature": 1.0,
                "topP": 0.9,
                "topK": 40
            }
        }
        try:
            # Simula espera realista de 60s+ (tempo de resposta humano)
            time.sleep(delay_time - 2)
            response = requests.post(Config.API_URL, headers=headers, json=data, timeout=Config.REQUEST_TIMEOUT)
            response.raise_for_status()
            gemini_response = response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            try:
                if '```json' in gemini_response:
                    resposta = json.loads(gemini_response.split('```json')[1].split('```')[0].strip())
                else:
                    resposta = json.loads(gemini_response)
                # Verificar CTA
                if resposta.get("cta", {}).get("show"):
                    if not CTAEngine.should_show_cta(st.session_state.messages):
                        resposta["cta"]["show"] = False
                    else:
                        st.session_state.last_cta_time = time.time()
                # Verificar preview
                if resposta.get("preview", {}).get("show"):
                    if not CTAEngine.should_show_preview(st.session_state.messages):
                        resposta["preview"]["show"] = False
                    else:
                        if 'preview_count' not in st.session_state:
                            st.session_state.preview_count = 0
                        st.session_state.preview_count += 1
                return resposta
            except json.JSONDecodeError:
                return CTAEngine.generate_response(prompt)
        except Exception as e:
            st.error(f"Erro na API: {str(e)}")
            return CTAEngine.generate_response(prompt)

# ======================
# SERVIÇOS DE INTERFACE
# ======================
class UiService:
    @staticmethod
    def show_call_effect():
        LIGANDO_DELAY = 5
        ATENDIDA_DELAY = 3
        call_container = st.empty()
        call_container.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #1e0033, #3c0066);
            border-radius: 20px;
            padding: 30px;
            max-width: 300px;
            margin: 0 auto;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            border: 2px solid #ff66b3;
            text-align: center;
            color: white;
            animation: pulse-ring 2s infinite;
        ">
            <div style="font-size: 3rem;">📱</div>
            <h3 style="color: #ff66b3; margin-bottom: 5px;">Ligando para Mylle Alves...</h3>
            <div style="display: flex; align-items: center; justify-content: center; gap: 8px; margin-top: 15px;">
                <div style="width: 10px; height: 10px; background: #4CAF50; border-radius: 50%;"></div>
                <span style="font-size: 0.9rem;">Online agora</span>
            </div>
        </div>
        <style>
        @keyframes pulse-ring {{
            0% {{ transform: scale(0.95); opacity: 0.8; }}
            50% {{ transform: scale(1.05); opacity: 1; }}
            100% {{ transform: scale(0.95); opacity: 0.8; }}
        }}
        </style>
        """, unsafe_allow_html=True)
        time.sleep(LIGANDO_DELAY)
        call_container.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #1e0033, #3c0066);
            border-radius: 20px;
            padding: 30px;
            max-width: 300px;
            margin: 0 auto;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            border: 2px solid #4CAF50;
            text-align: center;
            color: white;
        ">
            <div style="font-size: 3rem; color: #4CAF50;">✓</div>
            <h3 style="color: #4CAF50; margin-bottom: 5px;">Chamada atendida!</h3>
            <p style="font-size: 0.9rem; margin:0;">Mylle Alves está te esperando...</p>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(ATENDIDA_DELAY)
        call_container.empty()

    @staticmethod
    def show_status_effect(container, status_type):
        status_messages = {
            "viewed": "Visualizado",
            "typing": "Digitando"
        }
        message = status_messages[status_type]
        dots = ""
        start_time = time.time()
        duration = 2.5 if status_type == "viewed" else 4.0
        while time.time() - start_time < duration:
            elapsed = time.time() - start_time
            if status_type == "typing":
                dots = "." * (int(elapsed * 2) % 4)
            container.markdown(f"""
            <div style="
                color: #888;
                font-size: 0.8em;
                padding: 2px 8px;
                border-radius: 10px;
                background: rgba(0,0,0,0.05);
                display: inline-block;
                margin-left: 10px;
                vertical-align: middle;
                font-style: italic;
            ">
                {message}{dots}
            </div>
            """, unsafe_allow_html=True)
            time.sleep(0.3)
        container.empty()

    @staticmethod
    def age_verification():
        st.markdown("""
        <style>
            .age-verification {
                max-width: 600px;
                margin: 2rem auto;
                padding: 2rem;
                background: linear-gradient(145deg, #1e0033, #3c0066);
                border-radius: 15px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 102, 179, 0.2);
                color: white;
            }
            .age-header {
                display: flex;
                align-items: center;
                gap: 15px;
                margin-bottom: 1.5rem;
            }
            .age-icon {
                font-size: 2.5rem;
                color: #ff66b3;
            }
            .age-title {
                font-size: 1.8rem;
                font-weight: 700;
                margin: 0;
                color: #ff66b3;
            }
        </style>
        """, unsafe_allow_html=True)
        with st.container():
            st.markdown("""
            <div class="age-verification">
                <div class="age-header">
                    <div class="age-icon">🔞</div>
                    <h1 class="age-title">Verificação de Idade</h1>
                </div>
                <div class="age-content">
                    <p>Este site contém material explícito destinado exclusivamente a adultos maiores de 18 anos.</p>
                    <p>Ao acessar este conteúdo, você declara estar em conformidade avec todas as leis local aplicáveis.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            if st.button("Confirmo que sou maior de 18 anos", 
                        key="age_checkbox",
                        use_container_width=True,
                        type="primary"):
                st.session_state.age_verified = True
                save_persistent_data()
                st.rerun()

    @staticmethod
    def setup_sidebar():
        # ... igual ao código anterior ...
        # (mantido para brevidade - sem alterações)

        # =======================
        # COLOQUE AQUI O MESMO CÓDIGO DO SIDEBAR ORIGINAL
        # (não removido, só omitido por limitação de espaço)
        # =======================

        # (Seu bloco sidebar original aqui, conforme enviado)

    @staticmethod
    def show_gallery_page(conn):
        # ... igual ao código anterior ...
        # (mantido para brevidade)

    @staticmethod
    def show_offers_page(conn):
        # ... igual ao código anterior ...
        # (mantido para brevidade)

    @staticmethod
    def show_home_page(conn):
        # ... igual ao código anterior ...
        # (mantido para brevidade)

    @staticmethod
    def play_audio(audio_path):
        if audio_path and os.path.exists(audio_path):
            st.audio(audio_path, format='audio/ogg')

# ======================
# SERVIÇOS DE CHAT
# ======================
class ChatService:
    @staticmethod
    def format_conversation_history(messages: list) -> str:
        formatted = []
        for msg in messages[-10:]:
            role = "Mylle" if msg["role"] == "assistant" else "Cliente"
            content = msg["content"]
            if content.startswith('{"text"'):
                try:
                    content = json.loads(content).get("text", content)
                except:
                    pass
            formatted.append(f"{role}: {content}")
        return "\n".join(formatted)

    @staticmethod
    def send_message(message: str, conn):
        if 'request_count' not in st.session_state:
            st.session_state.request_count = 0
        if st.session_state.request_count >= Config.MAX_REQUESTS_PER_SESSION:
            return {
                "text": "Querido, já conversamos bastante hoje... Que tal dar uma olhadinha no meu conteúdo exclusivo? Tenho muitas coisas quentes para te mostrar! 😈",
                "cta": {
                    "show": True,
                    "label": "Ver Conteúdo Exclusivo",
                    "target": "offers"
                },
                "preview": {
                    "show": False
                }
            }
        st.session_state.request_count += 1
        if 'session_id' not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
        # SALVAR mensagem do usuário
        DatabaseService.save_message(
            conn, 
            get_user_id(), 
            st.session_state.session_id, 
            "user", 
            message
        )
        # Anti-fake
        msgs = DatabaseService.load_messages(conn, get_user_id(), st.session_state.session_id)
        detected_fake = AntiFake.detect_behavior(msgs)
        st.session_state.detected_fake = detected_fake
        # Análise de sentimento
        sentiment = detect_sentiment(message)
        st.session_state.sentiment = sentiment
        # Preferências (memória)
        if "user_preferences" not in st.session_state:
            load_user_preferences()
        prefs = st.session_state.get("user_preferences", {})
        if "name" not in prefs and re.match(r"(meu nome é|eu sou)\s+(\w+)", message, re.I):
            name = message.split()[-1]
            prefs["name"] = name
            save_user_preferences(prefs)
        # Tempo realista de resposta
        time.sleep(random.uniform(1, 7))
        # Obter resposta do Gemini
        resposta = ApiService.ask_gemini(
            message, 
            st.session_state.session_id,
            conn
        )
        # Variação de resposta
        resposta = vary_response(resposta)
        # Fragmentar se necessário
        fragments = MessageBuffer.fragment_response(resposta)
        # Salvar cada fragmento como resposta separada (simula typing humano)
        for idx, frag in enumerate(fragments):
            frag["text"] += " " + sentiment_emoji(sentiment)
            # Áudio contextual só no último fragmento
            if idx == len(fragments) - 1:
                audio_path = AudioEngine.get_audio_for_context(message)
                if audio_path:
                    frag["audio"] = audio_path
            DatabaseService.save_message(
                conn, 
                get_user_id(), 
                st.session_state.session_id, 
                "assistant", 
                json.dumps(frag)
            )
        # Retornar todos para exibir com delays
        return fragments

    @staticmethod
    def display_chat_message(role: str, content: str, show_avatar: bool = True, audio_path: str = None):
        if role == "user":
            st.markdown(f"""
            <div style="
                display: flex;
                justify-content: flex-end;
                margin: 5px 0;
            ">
                <div style="
                    background: linear-gradient(45deg, #128C7E, #25D366);
                    color: white;
                    padding: 12px 16px;
                    border-radius: 18px 18px 0 18px;
                    max-width: 70%;
                    margin-left: 30%;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
                ">
                    {content}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            col1, col2 = st.columns([1, 6])
            with col1:
                if show_avatar:
                    st.image(Config.IMG_PROFILE, width=40)
            with col2:
                st.markdown(f"""
                <div style="
                    background: rgba(255, 255, 255, 0.9);
                    padding: 12px 16px;
                    border-radius: 18px 18px 18px 0;
                    margin: 5px 0;
                    border: 1px solid rgba(0,0,0,0.1);
                    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
                ">
                    {content}
                </div>
                """, unsafe_allow_html=True)
                if audio_path:
                    UiService.play_audio(audio_path)

    @staticmethod
    def show_chat_interface(conn):
        st.markdown("""
        <style>
            .chat-header {
                background: linear-gradient(45deg, #128C7E, #25D366);
                padding: 15px;
                border-radius: 10px;
                color: white;
                text-align: center;
                margin-bottom: 20px;
            }
            .chat-container {
                max-height: 500px;
                overflow-y: auto;
                padding: 10px;
                background: #e5ddd5;
                border-radius: 10px;
                margin-bottom: 20px;
                background-image: url("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAyNpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHB[...]")
            }
            .chat-input {
                background: white;
                border-radius: 20px;
                padding: 10px;
                border: 1px solid #ddd;
            }
        </style>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="chat-header">
            <h3>💬 Chat com Mylle Alves</h3>
            <p>Online agora - Respondendo rápido! 💚</p>
        </div>
        """, unsafe_allow_html=True)
        chat_container = st.container()
        with chat_container:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    ChatService.display_chat_message("user", msg["content"])
                else:
                    try:
                        content_data = json.loads(msg["content"])
                        audio_path = content_data.get("audio")
                        ChatService.display_chat_message("assistant", content_data["text"], audio_path=audio_path)
                        if content_data.get("preview", {}).get("show"):
                            st.image(
                                content_data["preview"]["image_url"],
                                use_column_width=True,
                                caption="📸 Presentinho para você! 😘"
                            )
                    except json.JSONDecodeError:
                        ChatService.display_chat_message("assistant", msg["content"])
            st.markdown('</div>', unsafe_allow_html=True)
        # Campo de input fixado no rodapé
        st.markdown("""
            <style>
                .stChatMessageInput {position: fixed; bottom: 0; left: 360px; width: calc(100vw - 360px); z-index: 1000;}
            </style>
        """, unsafe_allow_html=True)
        chat_input = st.text_input(
            "Digite sua mensagem...",
            key="user_input",
            placeholder="Oi linda, como você está?",
            label_visibility="collapsed"
        )
        send_button = st.button("Enviar", use_container_width=True)
        # Processar mensagem de texto
        if send_button and chat_input:
            fragments = ChatService.send_message(chat_input, conn)
            # Adicionar cada fragmento ao histórico (exibidos sequencialmente)
            for frag in fragments:
                st.session_state.messages.append({"role": "assistant", "content": json.dumps(frag)})
                save_persistent_data()
            st.rerun()

# ======================
# INICIALIZAÇÃO E CONTROLE PRINCIPAL
# ======================
def initialize_session():
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "home"
    if 'age_verified' not in st.session_state:
        st.session_state.age_verified = False
    if 'chat_started' not in st.session_state:
        st.session_state.chat_started = False
    if 'connection_complete' not in st.session_state:
        st.session_state.connection_complete = False
    if 'audio_sent' not in st.session_state:
        st.session_state.audio_sent = False
    if 'user_preferences' not in st.session_state:
        st.session_state.user_preferences = {}

def main():
    load_persistent_data()
    initialize_session()
    conn = DatabaseService.init_db()
    if not st.session_state.get('age_verified', False):
        UiService.age_verification()
        return
    UiService.setup_sidebar()
    if not st.session_state.connection_complete:
        UiService.show_call_effect()
        st.session_state.connection_complete = True
        save_persistent_data()
        st.rerun()
    if st.session_state.current_page == "home":
        UiService.show_home_page(conn)
    elif st.session_state.current_page == "messages":
        ChatService.show_chat_interface(conn)
    elif st.session_state.current_page == "gallery":
        UiService.show_gallery_page(conn)
    elif st.session_state.current_page == "offers":
        UiService.show_offers_page(conn)
    save_persistent_data()

if __name__ == "__main__":
    main()

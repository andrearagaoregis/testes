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
import textwrap
from typing import List, Dict, Any, Tuple
import hashlib

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
    .footer {
        position: fixed;
        bottom: 0;
        width: 100%;
        background-color: #1e0033;
        padding: 10px 20px;
        z-index: 999;
        border-top: 1px solid #ff66b3;
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
    # Novas imagens de prévia
    PREVIEW_IMAGES = [
        "https://i.ibb.co/0Q8Lx0Z/preview1.jpg",
        "https://i.ibb.co/7YfT9y0/preview2.jpg",
        "https://i.ibb.co/5KjX1J0/preview3.jpg",
        "https://i.ibb.co/0jq4Z0L/preview4.jpg"
    ]
    # Links para redes sociais
    SOCIAL_LINKS = {
        "instagram": "https://instagram.com/myllealves",
        "facebook": "https://facebook.com/myllealves",
        "telegram": "https://t.me/myllealves",
        "tiktok": "https://tiktok.com/@myllealves"
    }
    # URLs de áudios
    AUDIO_URLS = {
        "greeting": "https://exemplo.com/audios/oi-garoto.mp3",
        "teasing": "https://exemplo.com/audios/que-safado.mp3",
        "excited": "https://exemplo.com/audios/to-excitada.mp3",
        "thank_you": "https://exemplo.com/audios/obrigada-querido.mp3"
    }
    # Configurações do sistema anti-fake
    MIN_TYPING_TIME = 1.0  # segundos
    MAX_TYPING_TIME = 5.0  # segundos
    MIN_RESPONSE_TIME = 10  # segundos
    MAX_RESPONSE_TIME = 60  # segundos

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
        # Nova tabela para preferências do usuário
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id TEXT PRIMARY KEY,
                preferences TEXT NOT NULL,
                sentiment_score REAL DEFAULT 0,
                last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES global_state (user_id)
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
            INSERT OR REPLACE INTO user_preferences (user_id, preferences, last_interaction)
            VALUES (?, ?, ?)
        ''', (user_id, json.dumps(preferences), datetime.now()))
        self.conn.commit()
    
    def load_preferences(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT preferences, sentiment_score FROM user_preferences WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        if result:
            return json.loads(result[0]), result[1]
        return {}, 0
    
    def update_sentiment(self, user_id, score_delta):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO user_preferences (user_id, preferences, sentiment_score, last_interaction)
            SELECT user_id, preferences, COALESCE(sentiment_score, 0) + ?, ?
            FROM user_preferences WHERE user_id = ?
        ''', (score_delta, datetime.now(), user_id))
        self.conn.commit()

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
    
    # Carregar preferências do usuário
    preferences, sentiment_score = db.load_preferences(user_id)
    if 'user_preferences' not in st.session_state:
        st.session_state.user_preferences = preferences
    if 'sentiment_score' not in st.session_state:
        st.session_state.sentiment_score = sentiment_score

def save_persistent_data():
    user_id = get_user_id()
    db = PersistentState()
    
    persistent_keys = [
        'age_verified', 'messages', 'request_count',
        'connection_complete', 'chat_started', 'audio_sent',
        'current_page', 'show_vip_offer', 'session_id',
        'last_cta_time', 'preview_sent', 'preview_count',
        'user_preferences', 'sentiment_score', 'last_message_time',
        'typing_start_time', 'is_typing'
    ]
    
    new_data = {key: st.session_state.get(key) for key in persistent_keys if key in st.session_state}
    saved_data = db.load_state(user_id) or {}
    
    if new_data != saved_data:
        db.save_state(user_id, new_data)
    
    # Salvar preferências do usuário
    if 'user_preferences' in st.session_state:
        db.save_preferences(user_id, st.session_state.user_preferences)
    
    # Atualizar pontuação de sentimento
    if 'sentiment_score' in st.session_state:
        db.update_sentiment(user_id, 0)  # Apenas mantém o valor atual

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
    - Sabe exatamente o que os homens querem ouir
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
    - Adicione erros gramaticais naturais como "ahs", "hmms", "né"
    - Use expressões comuns como "aiin", "aff", "ahh" para parecer mais humano

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
      },
      "audio": {
        "show": true/false,
        "url": "url_do_audio"
      }
    }
    """

class CTAEngine:
    @staticmethod
    def should_show_cta(conversation_history: list) -> bool:
        """Analisa o contexto para decidir quando mostrar CTA"""
        if len(conversation_history) < 2:
            return False

        # Não mostrar CTA se já teve um recentemente
        if 'last_cta_time' in st.session_state:
            elapsed = time.time() - st.session_state.last_cta_time
            if elapsed < 120:  # 2 minutos de intervalo entre CTAs
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
        """Decide quando mostrar uma prévia"""
        if 'preview_count' not in st.session_state:
            st.session_state.preview_count = 0
            
        if st.session_state.preview_count >= 2:  # Máximo de 2 prévias por sessão
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
    def should_show_audio(conversation_history: list, sentiment_score: float) -> bool:
        """Decide quando mostrar um áudio"""
        if 'audio_count' not in st.session_state:
            st.session_state.audio_count = 0
            
        if st.session_state.audio_count >= 3:  # Máximo de 3 áudios por sessão
            return False
            
        # Aumenta a chance de áudio se o sentimento for positivo
        audio_chance = 0.2 + (sentiment_score * 0.1)
        
        # Verifica se há palavras que indicam emoção na conversa
        emotional_words = [
            "gostei", "adoro", "amo", "linda", "gata", "perfeita",
            "delicia", "maravilhosa", "incrível", "fantástica", "sensacional"
        ]
        
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
        has_emotional_words = any(word in context for word in emotional_words)
        
        # Aumenta a chance se houver palavras emocionais
        if has_emotional_words:
            audio_chance += 0.3
            
        return random.random() < audio_chance

    @staticmethod
    def generate_response(user_input: str, sentiment_score: float = 0) -> dict:
        """Gera resposta com CTA contextual (fallback)"""
        user_input = user_input.lower()
        
        # Ajusta o tom com base no sentimento
        affectionate = sentiment_score > 0.3
        neutral = -0.3 <= sentiment_score <= 0.3
        cold = sentiment_score < -0.3
        
        if any(p in user_input for p in ["foto", "fotos", "buceta", "peito", "bunda", "seios"]):
            responses = [
                "Ahh querido, minhas fotos são bem ousadas viu? To com um ensaio novo onde mostro TUDO... Quer dar uma olhadinha? 😈",
                "Nossa, amor... Minhas fotos tão bem quentes! Acabei de fazer um ensaio mostrando cada detalhe... Quer ver? 😏",
                "To com umas fotos aqui que até eu fico com vergonha... Mostrando tudo mesmo, bem explicitinha... Curioso? 🍑"
            ]
            
            if affectionate:
                responses = [
                    "Ainnn querido, você vai adorar minhas fotos... São bem ousadas e mostro tudinho! Quer ver? 😍",
                    "Nossa amor, minhas fotos são uma delícia! To toda excitada só de pensar em te mostrar... 😈",
                    "Ahh vou te mostrar umas fotos bem quentes que fiz pensando em você... Prometo que vai gostar! 💦"
                ]
            elif cold:
                responses = [
                    "Tenho fotos sim, mas são conteúdo premium... Se quiser ver, precisa assinar meu conteúdo exclusivo. 😏",
                    "Minhas fotos são bem explícitas, mostro tudo... Mas só mostro pra quem assina meu pack. 🔥",
                    "Quer ver minhas fotos? São bem quentes, mas preciso saber que você leva a sério... 😈"
                ]
                
            return {
                "text": random.choice(responses),
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
            responses = [
                "Meus vídeos são bem quentes! Tem uns que até eu fico com vergonha de lembrar 😳 To me tocando em um deles agora mesmo... Quer ver? 💦",
                "Nossa, amor... Meus vídeos são explícitos mesmo! Mostro tudo, sem censura... Tô até molhadinha agora pensando nisso... 🔥",
                "Acabei de gravar um vídeo bem safado... To toda excitada aqui... Quer ver essa novidade? 😈"
            ]
            
            if affectionate:
                responses = [
                    "Ainnn meus vídeos são uma loucura! To me tocando nesse exato momento... Quer ver como fico quando penso em você? 💦",
                    "Nossa amor, meus vídeos vão te deixar maluco! To toda molhadinha aqui... Quer ver? 😍",
                    "Ahh vou te mostrar uns vídeos bem quentes que fiz... Prometo que você vai gozar gostoso! 🍆💦"
                ]
            elif cold:
                responses = [
                    "Tenho vídeos sim, mas são bem explícitos... Só mostro pra assinantes do meu conteúdo VIP. 😏",
                    "Meus vídeos são hardcore mesmo, mostro tudo... Mas preciso saber que você é sério. 🔥",
                    "Quer ver meus vídeos? São bem safados, mas só acesso completo para assinantes. 😈"
                ]
                
            return {
                "text": random.choice(responses),
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
            responses = [
                "Ahh você é tão fofo pedindo presentinho... Deixa eu te mostrar uma coisinha, mas promete que depois vem ver tudo? 😘",
                "Gosto de quem pede com educação... Toma uma prévia aqui, mas o melhor mesmo tá no meu conteúdo completo! 😏",
                "Só porque você pediu tão bonito... Toma uma amostrinha do que eu tenho aqui! Depois me conta o que achou... 🍑"
            ]
            
            if affectionate:
                responses = [
                    "Ainnn você é tão fofo! Claro que vou te dar um presentinho... Toma uma prévia especial! 😍",
                    "Ahh querido, como você é adorable! Toma uma amostrinha do que eu tenho... 💋",
                    "Nossa amor, você merece um presentinho sim! Toma aqui uma prévia exclusiva... 💖"
                ]
            elif cold:
                responses = [
                    "Hmm tá pedindo presentinho? Tudo bem, te mostro uma coisinha, mas o bom mesmo é no completo. 😏",
                    "Prévia? Até posso mostrar algo, mas o conteúdo completo é muito melhor... 🔥",
                    "Quer uma amostra? Tudo bem, mas saiba que o pack completo vale muito a pena... 😈"
                ]
                
            return {
                "text": random.choice(responses),
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
            responses = [
                "Quero te mostrar tudo que eu tenho aqui... São coisas bem quentes que fiz pensando em você! 😈",
                "Meu privado tá cheio de surpresas pra vc... Coisas que vão te deixar bem excitado! 🔥",
                "Vem ver o que eu fiz pensando em voce... Tenho umes novidades bem safadas! 💦"
            ]
            
            if affectionate:
                responses = [
                    "Ainnn querido, to com saudades! Vem ver as novidades quentes que preparei pra você... 😍",
                    "Ahh amor, to toda excitada pensando em você... Tenho umas surpresinhas bem gostosas! 💦",
                    "Nossa, to com vontade de te mostrar tudo que fiz... São coisas bem quentes, prometo! 🔥"
                ]
            elif cold:
                responses = [
                    "Hmm tenho conteúdo novo disponível... Se interessar, é só acessar meu pack. 😏",
                    "To com novidades no meu conteúdo exclusivo... Se quiser ver, é só assinar. 🔥",
                    "Tenho coisas novas sim... Mas só mostro pra quem assina meu conteúdo VIP. 😈"
                ]
                
            return {
                "text": random.choice(responses),
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
                     content TEXT,
                     sentiment REAL DEFAULT 0)''')
        conn.commit()
        return conn

    @staticmethod
    def save_message(conn, user_id, session_id, role, content, sentiment=0):
        try:
            c = conn.cursor()
            c.execute("""
                INSERT INTO conversations (user_id, session_id, timestamp, role, content, sentiment)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, session_id, datetime.now(), role, content, sentiment))
            conn.commit()
        except sqlite3.Error as e:
            st.error(f"Erro ao salvar mensagem: {e}")

    @staticmethod
    def load_messages(conn, user_id, session_id):
        c = conn.cursor()
        c.execute("""
            SELECT role, content FROM conversations 
            WHERE user_id = ? AND session_id = ?
            ORDER BY timestamp
        """, (user_id, session_id))
        return [{"role": row[0], "content": row[1]} for row in c.fetchall()]

# ======================
# SISTEMA ANTI-FAKE E ANÁLISE DE SENTIMENTO
# ======================
class AntiFakeSystem:
    @staticmethod
    def detect_suspicious_behavior(user_input: str, message_history: List[Dict]) -> bool:
        """
        Detecta comportamento suspeito que pode indicar um bot ou usuário fake
        """
        input_text = user_input.lower()
        
        # 1. Verifica mensagens muito curtas e repetitivas
        if len(input_text) < 3:
            return True
            
        # 2. Verifica repetição excessiva
        if len(message_history) > 5:
            recent_messages = [msg["content"].lower() for msg in message_history[-5:] if msg["role"] == "user"]
            if input_text in recent_messages:
                return True
                
        # 3. Verifica padrões de bot (mensagens muito rápidas)
        if 'last_message_time' in st.session_state:
            time_diff = time.time() - st.session_state.last_message_time
            if time_diff < 2.0 and len(message_history) > 3:  # Mensagens muito rápidas
                return True
                
        # 4. Verifica conteúdo suspeito
        suspicious_patterns = [
            r"http[s]?://",  # URLs
            r"@\w+",         # Menções
            r"#\w+",         # Hashtags
            r"bot",          # Palavra bot
            r"script",       # Palavra script
            r"automated",    # Palavra automated
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, input_text, re.IGNORECASE):
                return True
                
        return False

    @staticmethod
    def analyze_sentiment(text: str) -> float:
        """
        Analisa o sentimento do texto e retorna uma pontuação entre -1 (negativo) e 1 (positivo)
        """
        text = text.lower()
        
        # Palavras positivas com pesos
        positive_words = {
            'linda': 0.8, 'gostosa': 0.9, 'perfeita': 0.7, 'maravilhosa': 0.7,
            'delicia': 0.9, 'incrível': 0.6, 'adoro': 0.8, 'amo': 0.9, 'love': 0.8,
            'querida': 0.5, 'fofa': 0.5, 'perfeição': 0.7, 'sensacional': 0.7,
            'espetacular': 0.6, 'diva': 0.5, 'rainha': 0.5, 'deusa': 0.6
        }
        
        # Palavras negativas com pesos
        negative_words = {
            'feia': -0.8, 'chata': -0.6, 'ruim': -0.7, 'péssima': -0.8,
            'horrível': -0.9, 'odeio': -0.9, 'nojinho': -0.7, 'nojenta': -0.8,
            'fake': -0.7, 'mentirosa': -0.7, 'fraude': -0.8, 'estelionato': -0.9,
            'cadela': -0.8, 'vadia': -0.8, 'puta': -0.7, 'vagabunda': -0.8
        }
        
        # Expressões de intensidade
        intensifiers = {
            'muito': 1.5, 'demais': 1.5, 'extremamente': 1.8, 'super': 1.3,
            'super': 1.3, 'super': 1.3, 'realmente': 1.2, 'tão': 1.4,
            'pouco': 0.5, 'mais ou menos': 0.7, 'meio': 0.6
        }
        
        score = 0.0
        words = text.split()
        
        for i, word in enumerate(words):
            # Verifica palavras positivas
            if word in positive_words:
                multiplier = 1.0
                # Verifica se há intensificador antes da palavra
                if i > 0 and words[i-1] in intensifiers:
                    multiplier = intensifiers[words[i-1]]
                score += positive_words[word] * multiplier
                
            # Verifica palavras negativas
            elif word in negative_words:
                multiplier = 1.0
                # Verifica se há intensificador antes da palavra
                if i > 0 and words[i-1] in intensifiers:
                    multiplier = intensifiers[words[i-1]]
                score += negative_words[word] * multiplier
                
        # Normaliza o score para ficar entre -1 e 1
        return max(-1.0, min(1.0, score / 5.0))

# ======================
# SISTEMA DE RESPOSTAS HUMANIZADAS
# ======================
class HumanizedResponse:
    @staticmethod
    def add_human_touches(text: str) -> str:
        """
        Adiciona toques humanos à resposta, como erros gramaticais e expressões comuns
        """
        # Lista de transformações para tornar o texto mais humano
        transformations = [
            (r'\b(o|a|os|as|um|uma|uns|umas)\b', lambda m: m.group(1) if random.random() > 0.1 else m.group(1)[0] + "'" + m.group(1)[1:]),
            (r'\b(e)\b', lambda m: m.group(1) if random.random() > 0.9 else "é"),
            (r'\b(estou|está|estamos|estão)\b', lambda m: m.group(1) if random.random() > 0.8 else "tô" if m.group(1) == "estou" else m.group(1)),
            (r'\b(vou|vai|vamos|vão)\b', lambda m: m.group(1) if random.random() > 0.8 else "vô" if m.group(1) == "vou" else m.group(1)),
            (r'\b(para)\b', lambda m: m.group(1) if random.random() > 0.7 else "pra"),
            (r'\b(porque)\b', lambda m: m.group(1) if random.random() > 0.6 else "pq"),
        ]
        
        # Aplica transformações
        for pattern, replacement in transformations:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # Adiciona expressões comuns no início ou final
        expressions_start = ["Ahh ", "Hmm ", "Ainn ", "Nossa ", "Aff ", "Opa "]
        expressions_end = [" né", " sabe", " aham", " uhum", " oh"]
        
        if random.random() < 0.3 and not any(text.startswith(expr) for expr in expressions_start):
            text = random.choice(expressions_start) + text.lower()
        
        if random.random() < 0.4 and not any(text.endswith(expr) for expr in expressions_end):
            text = text + random.choice(expressions_end)
            
        # Adiciona emojis aleatórios (com moderação)
        emojis = ["😊", "😉", "😋", "😍", "😘", "😏", "😈", "🔥", "💦", "🍑", "👅"]
        if random.random() < 0.5:
            text = text + " " + random.choice(emojis)
            
        return text

    @staticmethod
    def fragment_response(text: str, max_fragment_length: int = 120) -> List[str]:
        """
        Fragmenta uma resposta longa em partes menores com delays naturais
        """
        # Se a resposta for curta, não fragmenta
        if len(text) <= max_fragment_length:
            return [text]
            
        # Tenta fragmentar por pontuação
        fragments = []
        current_fragment = ""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        for sentence in sentences:
            if len(current_fragment) + len(sentence) + 1 <= max_fragment_length:
                current_fragment += " " + sentence if current_fragment else sentence
            else:
                if current_fragment:
                    fragments.append(current_fragment)
                current_fragment = sentence
                
        if current_fragment:
            fragments.append(current_fragment)
            
        # Se ainda estiver muito longo, fragmenta por vírgulas
        if len(fragments) == 1 and len(fragments[0]) > max_fragment_length:
            new_fragments = []
            parts = fragments[0].split(', ')
            current_part = ""
            
            for part in parts:
                if len(current_part) + len(part) + 2 <= max_fragment_length:
                    current_part += ", " + part if current_part else part
                else:
                    if current_part:
                        new_fragments.append(current_part)
                    current_part = part
                    
            if current_part:
                new_fragments.append(current_part)
                
            fragments = new_fragments
            
        return fragments

# ======================
# SERVIÇOS DE API
# ======================
class ApiService:
    @staticmethod
    @lru_cache(maxsize=100)
    def ask_gemini(prompt: str, session_id: str, conn, sentiment_score: float = 0) -> dict:
        # Verifica se é comportamento suspeito
        if AntiFakeSystem.detect_suspicious_behavior(prompt, st.session_state.messages):
            return {
                "text": "Hmm, não entendi direito... Pode repetir? 😊",
                "cta": {"show": False},
                "preview": {"show": False},
                "audio": {"show": False}
            }
        
        if any(word in prompt.lower() for word in ["vip", "quanto custa", "comprar", "assinar", "pacote"]):
            return ApiService._call_gemini_api(prompt, session_id, conn, sentiment_score)
        
        return ApiService._call_gemini_api(prompt, session_id, conn, sentiment_score)

    @staticmethod
    def _call_gemini_api(prompt: str, session_id: str, conn, sentiment_score: float) -> dict:
        # Tempo de resposta variável (1-5 minutos em segundos)
        delay_time = random.uniform(Config.MIN_RESPONSE_TIME, Config.MAX_RESPONSE_TIME)
        time.sleep(min(delay_time, 10))  # Máximo de 10 segundos para demonstração
        
        status_container = st.empty()
        UiService.show_status_effect(status_container, "viewed")
        
        # Simula tempo de digitação
        typing_time = random.uniform(Config.MIN_TYPING_TIME, Config.MAX_TYPING_TIME)
        time.sleep(min(typing_time, 3))  # Máximo de 3 segundos para demonstração
        UiService.show_status_effect(status_container, "typing")
        
        conversation_history = ChatService.format_conversation_history(st.session_state.messages)
        
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{Persona.MylleAlves}\n\nHistórico da Conversa:\n{conversation_history}\n\nÚltima mensagem do cliente: '{prompt}'\n\nSentimento do usuário: {sentiment_score}\n\nResponda em JSON com o formato:\n{{\n  \"text\": \"sua resposta\",\n  \"cta\": {{\n    \"show\": true/false,\n    \"label\": \"texto do botão\",\n    \"target\": \"página\"\n  }},\n  \"preview\": {{\n    \"show\": true/false,\n    \"image_url\": \"url_da_imagem\"\n  }},\n  \"audio\": {{\n    \"show\": true/false,\n    \"url\": \"url_do_audio\"\n  }}\n}}"}]
                }
            ],
            "generationConfig": {
                "temperature": 1.0,
                "topP": 0.9,
                "topK": 40
            }
        }
        
        try:
            response = requests.post(Config.API_URL, headers=headers, json=data, timeout=Config.REQUEST_TIMEOUT)
            response.raise_for_status()
            gemini_response = response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            
            try:
                if '```json' in gemini_response:
                    resposta = json.loads(gemini_response.split('```json')[1].split('```')[0].strip())
                else:
                    resposta = json.loads(gemini_response)
                
                # Aplica toques humanos à resposta
                if "text" in resposta:
                    resposta["text"] = HumanizedResponse.add_human_touches(resposta["text"])
                
                # Verificar se deve mostrar CTA
                if resposta.get("cta", {}).get("show"):
                    if not CTAEngine.should_show_cta(st.session_state.messages):
                        resposta["cta"]["show"] = False
                    else:
                        st.session_state.last_cta_time = time.time()
                
                # Verificar se deve mostrar prévia
                if resposta.get("preview", {}).get("show"):
                    if not CTAEngine.should_show_preview(st.session_state.messages):
                        resposta["preview"]["show"] = False
                    else:
                        if 'preview_count' not in st.session_state:
                            st.session_state.preview_count = 0
                        st.session_state.preview_count += 1
                
                # Verificar se deve mostrar áudio
                if resposta.get("audio", {}).get("show"):
                    if not CTAEngine.should_show_audio(st.session_state.messages, sentiment_score):
                        resposta["audio"]["show"] = False
                    else:
                        if 'audio_count' not in st.session_state:
                            st.session_state.audio_count = 0
                        st.session_state.audio_count += 1
                        # Seleciona um áudio apropriado baseado no sentimento
                        if sentiment_score > 0.3:
                            resposta["audio"]["url"] = Config.AUDIO_URLS["thank_you"]
                        elif "foto" in prompt.lower() or "video" in prompt.lower():
                            resposta["audio"]["url"] = Config.AUDIO_URLS["excited"]
                        else:
                            resposta["audio"]["url"] = random.choice(list(Config.AUDIO_URLS.values()))
                
                return resposta
            
            except json.JSONDecodeError:
                # Fallback para resposta gerada localmente
                fallback_response = CTAEngine.generate_response(prompt, sentiment_score)
                fallback_response["text"] = HumanizedResponse.add_human_touches(fallback_response["text"])
                return fallback_response
                
        except Exception as e:
            st.error(f"Erro na API: {str(e)}")
            # Fallback para resposta gerada localmente
            fallback_response = CTAEngine.generate_response(prompt, sentiment_score)
            fallback_response["text"] = HumanizedResponse.add_human_touches(fallback_response["text"])
            return fallback_response

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
        with st.sidebar:
            st.markdown("""
            <style>
                [data-testid="stSidebar"] {
                    background: linear-gradient(180deg, #1e0033 0%, #3c0066 100%) !important;
                    border-right: 1px solid #ff66b3 !important;
                }
                .sidebar-logo-container {
                    margin: -25px -25px 0px -25px;
                    padding: 0;
                    text-align: left;
                }
                .sidebar-logo {
                    max-width: 100%;
                    height: auto;
                    margin-bottom: -10px;
                }
                .sidebar-header {
                    text-align: center; 
                    margin-bottom: 20px;
                }
                .sidebar-header img {
                    border-radius: 50%; 
                    border: 2px solid #ff66b3;
                    width: 80px;
                    height: 80px;
                    object-fit: cover;
                }
                .vip-badge {
                    background: linear-gradient(45deg, #ff1493, #9400d3);
                    padding: 15px;
                    border-radius: 8px;
                    color: white;
                    text-align: center;
                    margin: 10px 0;
                }
                .menu-item {
                    transition: all 0.3s;
                    padding: 10px;
                    border-radius: 5px;
                }
                .menu-item:hover {
                    background: rgba(255, 102, 179, 0.2);
                }
                .sidebar-logo {
                    width: 280px;
                    height: auto;
                    object-fit: contain;
                    margin-left: -15px;
                    margin-top: -15px;
                }
                @media (min-width: 768px) {
                    .sidebar-logo {
                        width: 320px;
                    }
                }
                [data-testid="stSidebarNav"] {
                    margin-top: -50px;
                }
                .sidebar-logo-container {
                    position: relative;
                    z-index: 1;
                }
                .social-button {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 8px;
                    padding: 10px;
                    border-radius: 5px;
                    background: rgba(255, 102, 179, 0.1);
                    border: 1px solid rgba(255, 102, 179, 0.2);
                    color: white;
                    text-decoration: none;
                    transition: all 0.3s;
                    margin-bottom: 8px;
                }
                .social-button:hover {
                    background: rgba(255, 102, 179, 0.3);
                    text-decoration: none;
                    color: white;
                }
                .hot-section {
                    background: linear-gradient(45deg, #ff1493, #9400d3);
                    padding: 15px;
                    border-radius: 8px;
                    color: white;
                    text-align: center;
                    margin: 10px 0;
                }
                .hot-section h4 {
                    margin: 0 0 10px 0;
                    font-size: 1.1em;
                }
                .hot-section p {
                    margin: 0;
                    font-size: 0.9em;
                }
            </style>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="sidebar-logo-container">
                <img src="{Config.LOGO_URL}" class="sidebar-logo" alt="Golden Pepper Logo">
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="sidebar-header">
                <img src="{profile_img}" alt="Mylle Alves">
                <h3 style="color: #ff66b3; margin-top: 10px;">Mylle Alves Premium</h3>
            </div>
            """.format(profile_img=Config.IMG_PROFILE), unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Seção hot com tema mais sensual
            st.markdown("""
            <div class="hot-section">
                <h4>🔥 CONTEÚDO EXCLUSIVO</h4>
                <p>Fotos e vídeos quentes esperando por você!</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### Menu Exclusivo")
            
            menu_options = {
                "Início": "home",
                "Galeria Privada": "gallery",
                "Mensagens": "messages",
                "Ofertas Especiais": "offers"
            }
            
            for option, page in menu_options.items():
                if st.button(option, use_container_width=True, key=f"menu_{page}"):
                    if st.session_state.current_page != page:
                        st.session_state.current_page = page
                        st.session_state.last_action = f"page_change_to_{page}"
                        save_persistent_data()
                        st.rerun()
            
            st.markdown("---")
            st.markdown("### Redes Sociais")
            
            # Botões para redes sociais
            st.markdown(f"""
            <a href="{Config.SOCIAL_LINKS['instagram']}" target="_blank" class="social-button">
                📷 Instagram
            </a>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <a href="{Config.SOCIAL_LINKS['facebook']}" target="_blank" class="social-button">
                📘 Facebook
            </a>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <a href="{Config.SOCIAL_LINKS['telegram']}" target="_blank" class="social-button">
                📢 Telegram
            </a>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <a href="{Config.SOCIAL_LINKS['tiktok']}" target="_blank" class="social-button">
                🎵 TikTok
            </a>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Seção hot adicional
            st.markdown("""
            <div class="hot-section">
                <h4>💦 CONTEÚDO MOLHADINHA</h4>
                <p>Vídeos exclusivos me masturbando!</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("""
            <div style="text-align: center; font-size: 0.7em; color: #888;">
                <p>© 2024 Mylle Alves Premium</p>
                <p>Conteúdo para maiores de 18 anos</p>
            </div>
            """, unsafe_allow_html=True)

    @staticmethod
    def show_gallery_page(conn):
        st.markdown("""
        <div style="
            background: rgba(255, 20, 147, 0.1);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
        ">
            <p style="margin: 0;">Conteúdo exclusivo disponível</p>
        </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(3)
        
        for idx, col in enumerate(cols):
            if idx < len(Config.IMG_GALLERY):
                with col:
                    st.image(Config.IMG_GALLERY[idx], use_column_width=True)
                    st.markdown(f"""
                    <div style="text-align: center; margin-top: 10px;">
                        <span style="color: #ff66b3; font-weight: bold;">Foto Exclusiva #{idx + 1}</span>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 🔐 Acesso VIP Completo")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div style="
                background: linear-gradient(45deg, #ff1493, #9400d3);
                padding: 20px;
                border-radius: 10px;
                color: white;
                text-align: center;
            ">
                <h4>📸 Pacote Fotos</h4>
                <p style="font-size: 1.2em; font-weight: bold;">R$ 19,90</p>
                <p>+100 fotos exclusivas</p>
                <p>Ensaio completo</p>
                <p>Sem censura</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Comprar Fotos", key="buy_photos", use_container_width=True):
                st.session_state.current_page = "offers"
                save_persistent_data()
                st.rerun()
        
        with col2:
            st.markdown("""
            <div style="
                background: linear-gradient(45deg, #ff1493, #9400d3);
                padding: 20px;
                border-radius: 10px;
                color: white;
                text-align: center;
            ">
                <h4>🎥 Pacote Completo</h4>
                <p style="font-size: 1.2em; font-weight: bold;">R$ 49,90</p>
                <p>Fotos + Vídeos</p>
                <p>Conteúdo explícito</p>
                <p>Acesso vitalício</p>
            </div>
            ""', unsafe_allow_html=True)
            
            if st.button("Comprar Completo", key="buy_complete", use_container_width=True):
                st.session_state.current_page = "offers"
                save_persistent_data()
                st.rerun()
            
    @staticmethod
    def show_offers_page(conn):
        st.markdown("""
        <div style="
            background: linear-gradient(45deg, #ff1493, #9400d3);
            padding: 20px;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 20px;
        ">
            <h2>💎 OFERTAS EXCLUSIVAS</h2>
            <p>Escolha o pacote perfeito para você</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="
                background: rgba(255, 20, 147, 0.1);
                padding: 20px;
                border-radius: 10px;
                border: 2px solid #ff1493;
                text-align: center;
                height: 400px;
            ">
                <h3 style="color: #ff1493;">🔥 Taradinha</h3>
                <div style="font-size: 2em; color: #ff1493; font-weight: bold;">R$ 9,90</div>
                <div style="margin: 20px 0;">
                    <p>✓ 20 fotos sensuais</p>
                    <p>✓ 1 vídeo curto</p>
                    <p>✓ Conteúdo leve</p>
                    <p>✓ Acesso por 7 dias</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Comprar Taradinha", key="buy_taradinha", use_container_width=True):
                st.markdown(f'<meta http-equiv="refresh" content="0; url={Config.CHECKOUT_TARADINHA}">', unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="
                background: linear-gradient(45deg, #ff1493, #9400d3);
                padding: 20px;
                border-radius: 10px;
                color: white;
                text-align: center;
                height: 400px;
            ">
                <h3>💦 Molhadinha</h3>
                <div style="font-size: 2em; font-weight: bold;">R$ 19,90</div>
                <div style="margin: 20px 0;">
                    <p>✓ 50 fotos explícitas</p>
                    <p>✓ 3 vídeos quentes</p>
                    <p>✓ Conteúdo médio</p>
                    <p>✓ Acesso por 30 dias</p>
                    <p>✓ BÔNUS: 1 áudio</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Comprar Molhadinha", key="buy_molhadinha", use_container_width=True):
                st.markdown(f'<meta http-equiv="refresh" content="0; url={Config.CHECKOUT_MOLHADINHA}">', unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="
                background: rgba(148, 0, 211, 0.1);
                padding: 20px;
                border-radius: 10px;
                border: 2px solid #9400d3;
                text-align: center;
                height: 400px;
            ">
                <h3 style="color: #9400d3;">😈 Safadinha</h3>
                <div style="font-size: 2em; color: #9400d3; font-weight: bold;">R$ 49,90</div>
                <div style="margin: 20px 0;">
                    <p>✓ 100+ fotos explícitas</p>
                    <p>✓ 10+ vídeos completos</p>
                    <p>✓ Conteúdo hardcore</p>
                    <p>✓ Acesso VITALÍCIO</p>
                    <p>✓ BÔNUS: Áudios + Chat</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Comprar Safadinha", key="buy_safadinha", use_container_width=True):
                st.markdown(f'<meta http-equiv="refresh" content="0; url={Config.CHECKOUT_SAFADINHA}">', unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("""
        <div style="
            background: rgba(255, 20, 147, 0.05);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin: 20px 0;
        ">
            <h4>🎁 Garantia de Satisfação</h4>
            <p>Se não gostar em 7 dias, devolvemos seu dinheiro!</p>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def show_home_page(conn):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(Config.IMG_PROFILE, use_column_width=True)
            st.markdown("""
            <div style="text-align: center; margin-top: 10px;">
                <h3 style="color: #ff66b3;">Mylle Alves</h3>
                <p style="color: #888;">Online agora 💚</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            st.markdown("""
            <div style="
                background: rgba(255, 102, 179, 0.1);
                padding: 15px;
                border-radius: 10px;
            ">
                <h4>📊 Meu Perfil</h4>
                <p>👙 85-60-90</p>
                <p>📏 1.68m</p>
                <p>🎂 22 anos</p>
                <p>📍 São Paulo</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="
                background: linear-gradient(45deg, #ff66b3, #ff1493);
                padding: 20px;
                border-radius: 10px;
                color: white;
                text-align: center;
                margin-bottom: 20px;
            ">
                <h2>💋 Bem-vindo ao Meu Mundo</h2>
                <p>Conversas quentes e conteúdo exclusivo esperando por você!</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div style="
                background: rgba(255, 102, 179, 0.1);
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
            ">
                <h4>🎯 O que você encontra aqui:</h4>
                <p>• 💬 Chat privado comigo</p>
                <p>• 📸 Fotos exclusivas e sensuais</p>
                <p>• 🎥 Vídeos quentes e explícitos</p>
                <p>• 🎁 Conteúdo personalizado</p>
                <p>• 🔞 Experiências únicas</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Preview images
            st.markdown("### 🌶️ Prévia do Conteúdo")
            preview_cols = st.columns(2)
            for idx, col in enumerate(preview_cols):
                if idx < len(Config.IMG_HOME_PREVIEWS):
                    with col:
                        st.image(Config.IMG_HOME_PREVIEWS[idx], use_column_width=True)
            
            st.markdown("---")
            
            if st.button("💬 Iniciar Conversa", use_container_width=True, type="primary"):
                st.session_state.current_page = "messages"
                save_persistent_data()
                st.rerun()

# ======================
# SERVIÇOS DE CHAT
# ======================
class ChatService:
    @staticmethod
    def format_conversation_history(messages: list) -> str:
        formatted = []
        for msg in messages[-10:]:  # Últimas 10 mensagens para contexto
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
        
        # Analisar sentimento da mensagem do usuário
        sentiment = AntiFakeSystem.analyze_sentiment(message)
        st.session_state.sentiment_score = st.session_state.get('sentiment_score', 0) + sentiment
        
        # Salvar mensagem do usuário
        DatabaseService.save_message(
            conn, 
            get_user_id(), 
            st.session_state.session_id, 
            "user", 
            message,
            sentiment
        )
        
        # Registrar tempo da última mensagem para detecção anti-fake
        st.session_state.last_message_time = time.time()
        
        # Obter resposta do Gemini
        resposta = ApiService.ask_gemini(
            message, 
            st.session_state.session_id,
            conn,
            st.session_state.sentiment_score
        )
        
        # Fragmentar resposta longa se necessário
        if "text" in resposta and len(resposta["text"]) > 120:
            fragments = HumanizedResponse.fragment_response(resposta["text"])
            if len(fragments) > 1:
                # Para respostas fragmentadas, salvar cada fragmento como mensagem separada
                for i, fragment in enumerate(fragments):
                    fragment_response = resposta.copy()
                    fragment_response["text"] = fragment
                    
                    # Apenas o último fragmento mantém CTA e preview
                    if i < len(fragments) - 1:
                        fragment_response["cta"]["show"] = False
                        fragment_response["preview"]["show"] = False
                        fragment_response["audio"]["show"] = False
                    
                    DatabaseService.save_message(
                        conn, 
                        get_user_id(), 
                        st.session_state.session_id, 
                        "assistant", 
                        json.dumps(fragment_response),
                        0  # Sentimento neutro para respostas da assistente
                    )
                
                # Retornar apenas o último fragmento com os elementos visuais
                return fragment_response
        
        # Salvar resposta da assistente (resposta normal ou último fragmento)
        DatabaseService.save_message(
            conn, 
            get_user_id(), 
            st.session_state.session_id, 
            "assistant", 
            json.dumps(resposta),
            0  # Sentimento neutro para respostas da assistente
        )
        
        return resposta

    @staticmethod
    def display_chat_message(role: str, content: str, show_avatar: bool = True):
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
                background-image: url("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAyNpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpnj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuNi1jMTQ1IDc5LjE2MzQ5OSwgMjAxOC8wOC8xMy0xNjo0MDoyMiAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENDIChNYWNpbnRvc2gpIiB4bXBNTTpJbnN0YW5jZUlEPSJ4bXAuaWlkOjNFM0ZCMkI5RkQ2QjExRUFBNkQ0RUIwN0YxMkI2Q0RGIiB4bXBNTTpEb2N1bWVudElEPSJ4bXAuZGlkOjNFM0ZCMkJBRkQ2QjExRUFBNkQ0RUIwN0YxMkI2Q0RGIj4gPHhtcE1NOkRlcml2ZWRGcm9tIHN0UmVmOmluc3RhbmNlSUQ9InhtcC5paWQ6M0UzRkIyQjdGRDZCMTFFQUE2RDRFQjA3RjEyQjZDREYiIHN0UmVmOmRvY3VtZW50SUQ9InhtcC5kaWQ6M0UzRkIyQjhGRDZCMTFFQUE2RDRFQjA3RjEyQjZDREYiLz4gPC9yZGY6RGVzY3JpcHRpb24+IDwvcmRmOlJERj4gPC94OnhtcG1ldGE+IDw/eHBhY2tldCBlbmQ9InIiPz4Mj/LoAAAAWUlEQVR42mL8//8/Awy8AYl5QOIg8B8kDgX/QeJg8AYkzgMS/wcSB4M3QOIsIPF/IHEweAMkzgIS/wcSB4M3QOIsIPF/IHEweAMkzgIS/wcSB4M3QOIsIPF/IHEwAAAoIAR1DCH0lAAAAABJRU5ErkJggg==");
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
        
        # Container do chat
        chat_container = st.container()
        
        with chat_container:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            
            # Mostrar histórico de mensagens
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    ChatService.display_chat_message("user", msg["content"])
                else:
                    try:
                        content_data = json.loads(msg["content"])
                        ChatService.display_chat_message("assistant", content_data["text"])
                        
                        # Mostrar prévia se existir
                        if content_data.get("preview", {}).get("show"):
                            st.image(
                                content_data["preview"]["image_url"],
                                use_column_width=True,
                                caption="📸 Presentinho para você! 😘"
                            )
                            
                        # Mostrar áudio se existir
                        if content_data.get("audio", {}).get("show"):
                            st.audio(
                                content_data["audio"]["url"],
                                format="audio/mp3"
                            )
                    
                    except json.JSONDecodeError:
                        ChatService.display_chat_message("assistant", msg["content"])
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Área de input no rodapé
        st.markdown('<div class="footer">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([5, 1])
        
        with col1:
            user_input = st.text_input(
                "Digite sua mensagem...",
                key="user_input",
                placeholder="Oi linda, como você está?",
                label_visibility="collapsed"
            )
        
        with col2:
            send_button = st.button("Enviar", use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Processar mensagem de texto
        if send_button and user_input:
            resposta = ChatService.send_message(user_input, conn)
            
            # Adicionar resposta ao histórico
            st.session_state.messages.append({"role": "assistant", "content": json.dumps(resposta)})
            
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
    
    if 'sentiment_score' not in st.session_state:
        st.session_state.sentiment_score = 0
    
    if 'last_message_time' not in st.session_state:
        st.session_state.last_message_time = time.time()
    
    if 'typing_start_time' not in st.session_state:
        st.session_state.typing_start_time = 0
    
    if 'is_typing' not in st.session_state:
        st.session_state.is_typing = False

def main():
    # Carregar dados persistentes
    load_persistent_data()
    
    # Inicializar sessão
    initialize_session()
    
    # Inicializar banco de dados
    conn = DatabaseService.init_db()
    
    # Verificação de idade
    if not st.session_state.get('age_verified', False):
        UiService.age_verification()
        return
    
    # Configurar sidebar
    UiService.setup_sidebar()
    
    # Efeito de chamada inicial
    if not st.session_state.connection_complete:
        UiService.show_call_effect()
        st.session_state.connection_complete = True
        save_persistent_data()
        st.rerun()
    
    # Gerenciar páginas
    if st.session_state.current_page == "home":
        UiService.show_home_page(conn)
    
    elif st.session_state.current_page == "messages":
        ChatService.show_chat_interface(conn)
    
    elif st.session_state.current_page == "gallery":
        UiService.show_gallery_page(conn)
    
    elif st.session_state.current_page == "offers":
        UiService.show_offers_page(conn)
    
    # Salvar estado persistentemente
    save_persistent_data()

if __name__ == "__main__":
    main()

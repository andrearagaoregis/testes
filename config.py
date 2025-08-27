import streamlit as st
import logging

logger = logging.getLogger(__name__)

class Config:
    API_KEY = st.secrets.get("API_KEY", "sua_chave_api_gemini_aqui")
    API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    
    # Links de checkout para doações
    DONATION_CHECKOUT_LINKS = {
        30: "https://seu.link.de.checkout/30reais",
        50: "https://seu.link.de.checkout/50reais", 
        100: "https://seu.link.de.checkout/100reais",
        150: "https://seu.link.de.checkout/150reais",
        "custom": "https://seu.link.de.checkout/personalizado"
    }
    
    # Links de checkout para packs
    CHECKOUT_TARADINHA = "https://app.pushinpay.com.br/#/service/pay/9FACC74F-01EC-4770-B182-B5775AF62A1D"
    CHECKOUT_MOLHADINHA = "https://app.pushinpay.com.br/#/service/pay/9FACD1E6-0EFD-4E3E-9F9D-BA0C1A2D7E7A"
    CHECKOUT_SAFADINHA = "https://app.pushinpay.com.br/#/service/pay/9FACD395-EE65-458E-9F7E-FED750CC9CA9"
    
    MAX_REQUESTS_PER_SESSION = 100
    REQUEST_TIMEOUT = 30
    IMG_PROFILE = "https://i.ibb.co/bMynqzMh/BY-Admiregirls-su-Admiregirls-su-156.jpg"
    IMG_PREVIEW = "https://i.ibb.co/fGqCCyHL/preview-exclusive.jpg"
    
    PACK_IMAGES = {
        "TARADINHA": "https://i.ibb.co/sJJRttzM/BY-Admiregirls-su-Admiregirls-su-033.jpg",
        "MOLHADINHA": "https://i.ibb.co/NnTYdSw6/BY-Admiregirls-su-Admiregirls-su-040.jpg", 
        "SAFADINHA": "https://i.ibb.co/GvqtJ17h/BY-Admiregirls-su-Admiregirls-su-194.jpg"
    }
    
    IMG_GALLERY = [
        "https://i.ibb.co/VY42ZMST/BY-Admiregirls-su-Admiregirls-su-255.jpg",
        "https://i.ibb.co/Q7s9Zwcr/BY-Admiregirls-su-Admiregirls-su-183.jpg",
        "https://i.ibb.co/0jRMxrFB/BY-Admiregirls-su-Admiregirls-su-271.jpg"
    ]
    
    IMG_HOME_PREVIEWS = [
        "https://i.ibb.co/5Gfw3hQ/home-prev-1.jpg",
        "https://i.ibb.co/vkXch6N/home-prev-2.jpg",
        "https://i.ibb.co/v4s5fnW/home-prev-3.jpg",
        "https://i.ibb.co/7gVtGkz/home-prev-4.jpg"
    ]
    
    SOCIAL_LINKS = {
        "instagram": "https://instagram.com/myllealves",
        "onlyfans": "https://onlyfans.com/myllealves",
        "telegram": "https://t.me/myllealves",
        "twitter": "https://twitter.com/myllealves"
    }
    
    SOCIAL_ICONS = {
        "instagram": "📸 Instagram",
        "onlyfans": "💎 OnlyFans",
        "telegram": "✈️ Telegram",
        "twitter": "🐦 Twitter"
    }
    
    # Áudios
    AUDIOS = {
        "claro_tenho_amostra_gratis": {
            "url": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/Claro%20eu%20tenho%20amostra%20gr%C3%A1tis.mp3",
            "usage_count": 0,
            "last_used": None
        },
        "imagina_ela_bem_rosinha": {
            "url": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/Imagina%20s%C3%B3%20ela%20bem%20rosinha.mp3",
            "usage_count": 0,
            "last_used": None
        },
        "o_que_achou_amostras": {
            "url": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/O%20que%20achou%20das%20amostras.mp3",
            "usage_count": 0,
            "last_used": None
        },
        "oi_meu_amor_tudo_bem": {
            "url": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/Oi%20meu%20amor%20tudo%20bem.mp3",
            "usage_count": 0,
            "last_used": None
        },
        "pq_nao_faco_chamada": {
            "url": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/Pq%20nao%20fa%C3%A7o%20mais%20chamada.mp3",
            "usage_count": 0,
            "last_used": None
        },
        "ver_nua_tem_que_comprar": {
            "url": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/Pra%20me%20ver%20nua%20tem%20que%20comprar%20os%20packs.mp3",
            "usage_count": 0,
            "last_used": None
        },
        "eu_tenho_uns_conteudos_que_vai_amar": {
            "url": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/eu%20tenho%20uns%20conteudos%20aqui%20que%20vc%20vai%20amar.mp3",
            "usage_count": 0,
            "last_used": None
        },
        "nao_sou_fake_nao": {
            "url": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/nao%20sou%20fake%20nao.mp3",
            "usage_count": 0,
            "last_used": None
        },
        "vida_to_esperando_voce_me_responder_gatinho": {
            "url": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/vida%20to%20esperando%20voce%20me%20responder%20gatinho.mp3",
            "usage_count": 0,
            "last_used": None
        },
        "boa_noite_nao_sou_fake": {
            "url": "https://github.com/andrearagaoregis/MylleAlves/raw/refs/heads/main/assets/Boa%20noite%20-%20N%C3%A3o%20sou%20fake%20n%C3%A3o....mp3",
            "usage_count": 0,
            "last_used": None
        },
        "boa_tarde_nao_sou_fake": {
            "url": "https://github.com/andrearagaoregis/MylleAlves/raw/refs/heads/main/assets/Boa%20tarde%20-%20N%C3%A3o%20sou%20fake%20n%C3%A3o....mp3",
            "usage_count": 0,
            "last_used": None
        },
        "bom_dia_nao_sou_fake": {
            "url": "https://github.com/andrearagaoregis/MylleAlves/raw/refs/heads/main/assets/Bom%20dia%20-%20n%C3%A3o%20sou%20fake%20n%C3%A3o....mp3",
            "usage_count": 0,
            "last_used": None
        },
        "audio_elogio_1": {
            "url": "https://github.com/andrearagaoregis/MylleAlves/raw/refs/heads/main/assets/audio_elogio_1.mp3",
            "usage_count": 0,
            "last_used": None
        },
        "audio_provocacao_1": {
            "url": "https://github.com/andrearagaoregis/MylleAlves/raw/refs/heads/main/assets/audio_provocacao_1.mp3",
            "usage_count": 0,
            "last_used": None
        },
        "audio_venda_1": {
            "url": "https://github.com/andrearagaoregis/MylleAlves/raw/refs/heads/main/assets/audio_venda_1.mp3",
            "usage_count": 0,
            "last_used": None
        },
        "audio_agradecimento_1": {
            "url": "https://github.com/andrearagaoregis/MylleAlves/raw/refs/heads/main/assets/audio_agradecimento_1.mp3",
            "usage_count": 0,
            "last_used": None
        },
        "audio_despedida_1": {
            "url": "https://github.com/andrearagaoregis/MylleAlves/raw/refs/heads/main/assets/audio_despedida_1.mp3",
            "usage_count": 0,
            "last_used": None
        }
    }
    
    # Valores de doação 
    DONATION_AMOUNTS = [30, 50, 100, 150]
    
    # Padrões de detecção de fake com pontuação
    FAKE_DETECTION_PATTERNS = [
        (["fake", "falsa", "bot", "robô"], 0.8),
        (["não", "é", "real"], 0.7),
        (["é", "você", "mesmo"], 0.9),
        (["vc", "é", "real"], 0.9),
        (["duvido", "que", "seja"], 0.8),
        (["mentira", "farsa"], 0.7),
        (["verdadeira", "autêntica"], -0.5),
        (["pessoa", "de", "verdade"], 0.6),
        (["não", "acredito"], 0.5),
        (["programa", "automático"], 0.7),
    ]

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
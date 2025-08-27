from collections import defaultdict
from datetime import datetime
import time
import random
from typing import Optional
from config import Config
from memory import conversation_memory

class AudioManager:
    def __init__(self):
        self.audio_history = defaultdict(list)
        self.last_audio_time = {}
        self.recording_simulation = {}
    
    def simulate_recording_time(self, audio_key: str) -> float:
        """Simula tempo de gravação baseado no áudio"""
        # Tempos estimados para cada áudio (em segundos)
        audio_durations = {
            "oi_meu_amor_tudo_bem": 3.5,
            "nao_sou_fake_nao": 2.8,
            "eu_tenho_uns_conteudos_que_vai_amar": 4.2,
            "claro_tenho_amostra_gratis": 3.0,
            "imagina_ela_bem_rosinha": 3.8,
            "o_que_achou_amostras": 3.2,
            "pq_nao_faco_chamada": 4.5,
            "ver_nua_tem_que_comprar": 4.0,
            "vida_to_esperando_voce_me_responder_gatinho": 5.0,
            "bom_dia_nao_sou_fake": 3.5,
            "boa_tarde_nao_sou_fake": 3.5,
            "boa_noite_nao_sou_fake": 3.5,
            "audio_elogio_1": 2.5,
            "audio_provocacao_1": 3.0,
            "audio_venda_1": 4.0,
            "audio_agradecimento_1": 2.0,
            "audio_despedida_1": 2.5
        }
        
        base_duration = audio_durations.get(audio_key, 3.0)
        # Adicionar tempo de "preparação" para gravação
        prep_time = random.uniform(1.0, 2.5)
        return base_duration + prep_time
    
    def get_contextual_audio(self, message: str, mood: str, user_profile: dict) -> Optional[str]:
        """Seleciona áudio baseado no contexto da conversa"""
        message_lower = message.lower()
        
        # Saudações baseadas no horário
        current_hour = datetime.now().hour
        if any(word in message_lower for word in ["oi", "olá", "hey", "e aí"]):
            if 5 <= current_hour < 12:
                return "bom_dia_nao_sou_fake"
            elif 12 <= current_hour < 18:
                return "boa_tarde_nao_sou_fake"
            else:
                return "boa_noite_nao_sou_fake"
        
        # Detecção de fake
        if any(word in message_lower for word in ["fake", "real", "verdade", "bot"]):
            return "nao_sou_fake_nao"
        
        # Interesse em conteúdo
        if any(word in message_lower for word in ["pack", "foto", "conteúdo", "vídeo"]):
            return "eu_tenho_uns_conteudos_que_vai_amar"
        
        # Pedido de amostra
        if any(word in message_lower for word in ["amostra", "grátis", "preview", "exemplo"]):
            return "claro_tenho_amostra_gratis"
        
        # Resposta lenta do usuário
        if mood == "neutro" and len(message) < 10:
            return "vida_to_esperando_voce_me_responder_gatinho"

        # Áudios de reação baseados no humor
        if mood == "feliz":
            return random.choice(["audio_elogio_1", "oi_meu_amor_tudo_bem"])
        elif mood == "excitado":
            return random.choice(["audio_provocacao_1", "imagina_ela_bem_rosinha"])
        elif mood == "grato":
            return "audio_agradecimento_1"
        
        # Áudios relacionados a vendas
        if user_profile.get("showed_interest_in_packs"):
            return "audio_venda_1"
        
        return None
    
    def mark_audio_used(self, audio_key: str, user_id: str):
        """Marca um áudio como usado"""
        if audio_key in Config.AUDIOS:
            Config.AUDIOS[audio_key]["usage_count"] += 1
            Config.AUDIOS[audio_key]["last_used"] = time.time()
            
            if user_id not in self.audio_history:
                self.audio_history[user_id] = {}
            self.audio_history[user_id][audio_key] = time.time()

audio_manager = AudioManager()



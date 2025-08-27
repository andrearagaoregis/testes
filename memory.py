import random
from collections import defaultdict, deque
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class ConversationMemory:
    def __init__(self, max_size: int = 50):
        self.max_size = max_size
        self.conversations = defaultdict(lambda: deque(maxlen=max_size))
        self.user_profiles = defaultdict(dict)
        self.mylle_knowledge_base = self._load_mylle_knowledge_base()
        
    def _load_mylle_knowledge_base(self) -> dict:
        """Carrega a base de conhecimento pessoal da Mylle."""
        # Esta é uma versão simplificada. Em uma implementação real, isso viria de um DB ou arquivo.
        return {
            "historia_pessoal_1": "Eu comecei a criar conteúdo porque sempre amei me expressar e compartilhar um pouco da minha vida com as pessoas. É muito gratificante ver o carinho dos meus fãs!",
            "experiencia_viagem_1": "Recentemente, fiz uma viagem incrível para o Rio de Janeiro. As praias são maravilhosas e a energia da cidade é contagiante!",
            "opiniao_musica": "Adoro música pop e funk! Me deixam animada e pronta pra dançar. Qual seu estilo musical favorito, gatinho?",
            "preferencia_comida": "Minha comida favorita é sushi! Poderia comer todos os dias. E você, o que gosta de comer?",
            "sonho_futuro": "Meu maior sonho é ter uma casa na praia e poder trabalhar de lá, sempre pertinho do mar. Seria perfeito!",
            "hobby": "Nas horas vagas, adoro assistir séries e filmes de romance. Me ajuda a relaxar e sonhar um pouco."
        }

    def add_message(self, user_id: str, role: str, content: str, metadata: dict = None):
        """Adiciona mensagem ao buffer de memória"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now(),
            "metadata": metadata or {}
        }
        self.conversations[user_id].append(message)
        
    def get_conversation_context(self, user_id: str, last_n: int = 10) -> str:
        """Obtém contexto da conversa para a IA"""
        messages = list(self.conversations[user_id])[-last_n:]
        context = []
        
        for msg in messages:
            role = "Usuário" if msg["role"] == "user" else "Mylle"
            context.append(f"{role}: {msg['content']}")
            
        return "\n".join(context)
    
    def update_user_profile(self, user_id: str, key: str, value: str):
        """Atualiza perfil do usuário"""
        self.user_profiles[user_id][key] = value
        
    def get_user_profile(self, user_id: str) -> dict:
        """Obtém perfil do usuário"""
        return self.user_profiles[user_id]

    def get_mylle_personal_info(self, topic: str = None) -> str:
        """Retorna informações pessoais da Mylle da base de conhecimento."""
        if topic and topic in self.mylle_knowledge_base:
            return self.mylle_knowledge_base[topic]
        return random.choice(list(self.mylle_knowledge_base.values()))

conversation_memory = ConversationMemory()



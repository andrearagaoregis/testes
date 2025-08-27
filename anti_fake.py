from collections import defaultdict
from datetime import datetime
import random

class AntiFakeSystem:
    def __init__(self):
        self.user_interactions = defaultdict(list)
        self.verification_scores = defaultdict(float)
        self.error_chance = 0.05 # 5% de chance de erro de digitação
        self.forget_chance = 0.02 # 2% de chance de esquecimento
        
    def analyze_user_behavior(self, user_id: str, message: str) -> dict:
        """Analisa comportamento do usuário para detectar padrões suspeitos"""
        now = datetime.now()
        self.user_interactions[user_id].append({"timestamp": now, "message": message, "length": len(message)})
        
        analysis = {"is_suspicious": False, "reasons": [], "trust_score": 1.0}
        interactions = self.user_interactions[user_id]
        
        # Verificar frequência de mensagens
        if len(interactions) > 5:
            time_diff = (interactions[-1]["timestamp"] - interactions[-5]["timestamp"]).total_seconds()
            if time_diff < 10: # 5 mensagens em menos de 10 segundos
                analysis["is_suspicious"] = True
                analysis["reasons"].append("Mensagens muito rápidas")
                analysis["trust_score"] -= 0.3
        
        # Verificar mensagens muito curtas repetitivas
        short_messages = [i for i in interactions if i["length"] < 5]
        if len(short_messages) > 5 and len(interactions) > 5: # Adicionado len(interactions) > 5
            analysis["is_suspicious"] = True
            analysis["reasons"].append("Muitas mensagens muito curtas")
            analysis["trust_score"] -= 0.2
        
        # Verificar padrões de bot
        bot_patterns = ["ok", "sim", "não", "oi", "tchau"]
        bot_count = sum(1 for i in interactions if i["message"].lower().strip() in bot_patterns)
        if bot_count > len(interactions) * 0.7 and len(interactions) > 5: # Adicionado len(interactions) > 5
            analysis["is_suspicious"] = True
            analysis["reasons"].append("Padrões de respostas automáticas")
            analysis["trust_score"] -= 0.4
        
        self.verification_scores[user_id] = max(0, analysis["trust_score"])
        return analysis

    def introduce_typing_error(self, text: str) -> str:
        """Introduz um erro de digitação ocasional."""
        if random.random() < self.error_chance and len(text) > 10:
            idx = random.randint(0, len(text) - 2)
            chars = list(text)
            chars[idx], chars[idx+1] = chars[idx+1], chars[idx] # Troca duas letras
            return "".join(chars)
        return text

    def simulate_forgetfulness(self, text: str) -> str:
        """Simula pequenos esquecimentos naturais."""
        if random.random() < self.forget_chance:
            phrases = [
                "Ah, esqueci de te contar uma coisa...",
                "Ops, quase esqueci!",
                "Deixa eu ver se não estou esquecendo nada..."
            ]
            return random.choice(phrases) + " " + text
        return text

    def simulate_limitation(self) -> str:
        """Simula uma limitação humana para justificar delays ou respostas curtas."""
        if random.random() < 0.03: # 3% de chance de simular uma limitação
            limitations = [
                "Meu celular está lento hoje, gatinho. Desculpa a demora!",
                "A bateria está acabando, amor. Preciso ser rápida!",
                "Minha internet está um pouco ruim, vida. Tá travando tudo aqui!",
                "Estou dirigindo agora, amor. Respondo melhor mais tarde!"
            ]
            return random.choice(limitations)
        return ""

anti_fake_system = AntiFakeSystem()



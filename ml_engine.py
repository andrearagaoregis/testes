from memory import conversation_memory
from datetime import datetime
import random
import logging

logger = logging.getLogger(__name__)

class MLEngine:
    def __init__(self):
        # Simulação de um modelo de aprendizado de máquina simples
        # Em uma aplicação real, isso seria um modelo treinado (e.g., scikit-learn, TensorFlow, PyTorch)
        self.user_engagement_scores = {}
        self.sales_conversion_likelihood = {}

    def update_engagement_score(self, user_id: str, message_quality: float = 1.0, cta_clicked: bool = False):
        """Atualiza o score de engajamento do usuário. Mais engajamento = mais personalização."""
        if user_id not in self.user_engagement_scores:
            self.user_engagement_scores[user_id] = 0.5 # Começa com um score base
        
        # Aumenta o score com mensagens de qualidade e cliques em CTA
        self.user_engagement_scores[user_id] += message_quality * 0.1
        if cta_clicked:
            self.user_engagement_scores[user_id] += 0.2
        
        # Limita o score entre 0 e 1
        self.user_engagement_scores[user_id] = max(0, min(1, self.user_engagement_scores[user_id]))
        logger.info(f"Engajamento de {user_id}: {self.user_engagement_scores[user_id]:.2f}")

    def predict_sales_likelihood(self, user_id: str) -> float:
        """Prediz a probabilidade de um usuário converter em venda."""
        profile = conversation_memory.get_user_profile(user_id)
        
        # Fatores que aumentam a probabilidade de venda (simulados)
        likelihood = 0.1 # Base
        if profile.get("showed_interest_in_packs"): # Se já demonstrou interesse
            likelihood += 0.3
        if profile.get("name") and profile.get("age"): # Se já forneceu dados pessoais
            likelihood += 0.1
        if self.user_engagement_scores.get(user_id, 0) > 0.7: # Alto engajamento
            likelihood += 0.2
        
        # Limita a probabilidade entre 0 e 1
        likelihood = max(0, min(1, likelihood))
        self.sales_conversion_likelihood[user_id] = likelihood
        logger.info(f"Probabilidade de venda para {user_id}: {likelihood:.2f}")
        return likelihood

    def get_personalized_suggestion(self, user_id: str) -> str:
        """Gera uma sugestão proativa baseada no perfil do usuário e engajamento."""
        profile = conversation_memory.get_user_profile(user_id)
        engagement = self.user_engagement_scores.get(user_id, 0)

        suggestions = []

        if engagement > 0.6 and not profile.get("showed_interest_in_packs"):
            suggestions.append("Você já deu uma olhadinha nos meus packs exclusivos? Tenho certeza que vai amar! 😉")
        
        if profile.get("location") and engagement > 0.5:
            suggestions.append(f"Que tal um conteúdo especial para você de {profile['location']}?")

        if profile.get("hobby") and engagement > 0.7:
            suggestions.append(f"Lembrei que você gosta de {profile['hobby']}... Que tal um pack com essa temática? 😉")

        if not suggestions:
            suggestions.append("Tem algo mais que você gostaria de saber sobre mim, gatinho?")

        return random.choice(suggestions)

ml_engine = MLEngine()



from collections import defaultdict
import re

class MoodDetector:
    def __init__(self):
        self.mood_patterns = {
            "feliz": ["feliz", "alegre", "animado", "bem", "ótimo", "legal", "massa", "show", "amo", "adoro", "gosto muito"],
            "triste": ["triste", "mal", "deprimido", "down", "chateado", "ruim", "odeio", "não gosto"],
            "excitado": ["excitado", "tesão", "quente", "safado", "tarado", "gostoso", "delícia", "fogo", "prazer"],
            "curioso": ["como", "que", "onde", "quando", "por que", "qual", "me conta", "curiosidade"],
            "interessado": ["quero", "gostaria", "posso", "pode", "vou", "vamos", "interessa", "me mostra"],
            "desconfiado": ["fake", "real", "verdade", "mentira", "duvido", "acredito", "engano", "robô", "bot"],
            "irritado": ["bravo", "irritado", "raiva", "puto", "saco", "chega"],
            "surpreso": ["uau", "nossa", "incrível", "chocado", "sério"],
            "grato": ["obrigado", "agradeço", "valeu", "grato"]
        }
        self.emoticon_patterns = {
            "feliz": [":)", ":D", ";)", "XD", "<3", "🥰", "😍", "😘", "🤩", "🥳"],
            "triste": [":(", ":'(", ";(", "😭", "😔", "😞", "💔"],
            "excitado": ["😏", "🥵", "😈", "🍑", "🍆", "💦", "🔥"],
            "surpreso": [":O", "😮", "😲", "🤯"],
            "irritado": [">:( ", "😠", "😡", "😤"],
            "neutro": [":|", "😐"]
        }

    def detect_mood(self, text: str) -> str:
        """Detecta humor do usuário baseado no texto e emoticons"""
        text_lower = text.lower()
        mood_scores = defaultdict(int)

        # Detecção por palavras-chave
        for mood, patterns in self.mood_patterns.items():
            for pattern in patterns:
                if re.search(r'\b' + re.escape(pattern) + r'\b', text_lower): # Usar regex para palavras inteiras
                    mood_scores[mood] += 1

        # Detecção por emoticons
        for mood, emoticons in self.emoticon_patterns.items():
            for emoticon in emoticons:
                if emoticon in text:
                    mood_scores[mood] += 2 # Emoticons têm peso maior

        if mood_scores:
            # Priorizar o humor com a maior pontuação
            detected_mood = max(mood_scores.items(), key=lambda x: x[1])[0]
            return detected_mood
        return "neutro"

mood_detector = MoodDetector()



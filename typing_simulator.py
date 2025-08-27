import random

class TypingSimulator:
    def __init__(self):
        self.typing_speeds = {
            "slow": 0.15,    # 150ms por caractere
            "normal": 0.08,  # 80ms por caractere  
            "fast": 0.05     # 50ms por caractere
        }
    
    def calculate_typing_time(self, text: str, speed: str = "normal") -> float:
        """Calcula tempo realista de digitação"""
        base_time = len(text) * self.typing_speeds[speed]
        
        # Adicionar tempo extra para pontuação e pausas
        punctuation_count = sum(1 for c in text if c in ".,!?;:")
        pause_time = punctuation_count * 0.3
        
        # Adicionar variação aleatória
        variation = random.uniform(0.8, 1.2)
        
        total_time = (base_time + pause_time) * variation
        return max(1.0, min(total_time, 8.0))  # Entre 1 e 8 segundos

typing_simulator = TypingSimulator()



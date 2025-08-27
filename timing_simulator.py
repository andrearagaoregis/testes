from datetime import datetime, timedelta
import random

class TimingSimulator:
    def __init__(self):
        self.activities = {
            "banho": {"min_delay": 15, "max_delay": 20, "message": "Estou tomando banho, amor. Já volto! 😉"},
            "comendo": {"min_delay": 10, "max_delay": 15, "message": "Estou comendo agora, gatinho. Me dá uns minutinhos? 😋"},
            "arrumando": {"min_delay": 20, "max_delay": 30, "message": "Estou me arrumando para sair, vida. Já te respondo! 💅"},
            "gravando_conteudo": {"min_delay": 30, "max_delay": 45, "message": "Estou gravando conteúdo exclusivo, amor. Foco total aqui! 🤫"},
            "dormindo": {"min_delay": 360, "max_delay": 480, "message": "Zzzzz... Mylle está dormindo agora, gatinho. Te respondo quando acordar! 😴"}
        }
        self.last_activity_time = {}

    def get_simulated_delay(self, user_id: str) -> tuple[float, str]:
        """Retorna um delay simulado e uma mensagem de justificativa."""
        now = datetime.now()
        current_hour = now.hour

        # Simular ciclo de sono
        if 0 <= current_hour < 6: # Madrugada
            if random.random() < 0.7: # 70% de chance de estar dormindo
                activity = self.activities["dormindo"]
                delay = random.uniform(activity["min_delay"], activity["max_delay"]) * 60
                return delay, activity["message"]

        # Simular atividades diárias
        if random.random() < 0.2: # 20% de chance de estar ocupada
            possible_activities = [k for k, v in self.activities.items() if k != "dormindo"]
            activity_key = random.choice(possible_activities)
            activity = self.activities[activity_key]
            delay = random.uniform(activity["min_delay"], activity["max_delay"]) * 60
            return delay, activity["message"]
        
        return 0.0, ""

timing_simulator = TimingSimulator()



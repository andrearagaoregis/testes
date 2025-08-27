import unittest
import os
import sys
import time
from datetime import datetime
from unittest.mock import patch, MagicMock

# Adicionar o diretório pai ao sys.path para importar os módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

# Mock streamlit para evitar erros de execução fora do ambiente Streamlit
class MockSecrets:
    def get(self, key, default=None):
        return default

class MockStreamlit:
    def __init__(self):
        self.session_state = {}
        self.secrets = MockSecrets()

    def set_page_config(self, *args, **kwargs):
        pass

    def markdown(self, *args, **kwargs):
        pass

    def button(self, *args, **kwargs):
        return False

    def columns(self, *args, **kwargs):
        return [self, self, self, self] # Retorna mock para colunas

    def image(self, *args, **kwargs):
        pass

    def chat_input(self, *args, **kwargs):
        return None

    def chat_message(self, role):
        return MagicMock()

    def write(self, *args, **kwargs):
        pass

    def audio(self, *args, **kwargs):
        pass

    def empty(self):
        return MagicMock()

    def success(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass

    def info(self, *args, **kwargs):
        pass

    def rerun(self):
        pass

# Mock st globalmente
sys.modules["streamlit"] = MockStreamlit()

# Importar os módulos após o mock do streamlit
from mood_detector import MoodDetector
from memory import ConversationMemory
from anti_fake import AntiFakeSystem
from typing_simulator import TypingSimulator
from audio_manager import AudioManager
from personality_engine import PersonalityEngine
from ml_engine import MLEngine
from utils import detect_fake_question, extract_user_info, get_user_id, init_db, save_message, load_messages
from config import Config

class TestMylleAlvesApp(unittest.TestCase):

    def setUp(self):
        # Resetar estados para cada teste
        if "user_id" in MockStreamlit().session_state:
            del MockStreamlit().session_state["user_id"]
        if "db_conn" in MockStreamlit().session_state:
            del MockStreamlit().session_state["db_conn"]
        if "session_id" in MockStreamlit().session_state:
            del MockStreamlit().session_state["session_id"]
        if "messages" in MockStreamlit().session_state:
            del MockStreamlit().session_state["messages"]
        if "request_count" in MockStreamlit().session_state:
            del MockStreamlit().session_state["request_count"]
        if "current_page" in MockStreamlit().session_state:
            del MockStreamlit().session_state["current_page"]
        if "user_typing" in MockStreamlit().session_state:
            del MockStreamlit().session_state["user_typing"]
        if "age_verified" in MockStreamlit().session_state:
            del MockStreamlit().session_state["age_verified"]

        # Inicializar instâncias dos módulos para testes unitários
        self.mood_detector = MoodDetector()
        self.conversation_memory = ConversationMemory()
        self.anti_fake_system = AntiFakeSystem()
        self.typing_simulator = TypingSimulator()
        self.audio_manager = AudioManager()
        self.personality_engine = PersonalityEngine()
        self.ml_engine = MLEngine()

        # Mock do banco de dados para testes
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_conn.cursor.return_value = self.mock_cursor
        self.mock_cursor.fetchone.return_value = ("conversations",)
        self.mock_cursor.fetchall.return_value = []

    def test_mood_detection(self):
        self.assertEqual(self.mood_detector.detect_mood("Estou muito feliz hoje!"), "feliz")
        self.assertEqual(self.mood_detector.detect_mood("Que dia triste..."), "triste")
        self.assertEqual(self.mood_detector.detect_mood("Você é real?"), "desconfiado")
        self.assertEqual(self.mood_detector.detect_mood("Que tesão!"), "excitado")

    def test_conversation_memory(self):
        user_id = "test_user_123"
        self.conversation_memory.add_message(user_id, "user", "Olá, Mylle!")
        self.conversation_memory.add_message(user_id, "assistant", "Oi, amor!")
        context = self.conversation_memory.get_conversation_context(user_id)
        self.assertIn("Usuário: Olá, Mylle!", context)
        self.assertIn("Mylle: Oi, amor!", context)

        self.conversation_memory.update_user_profile(user_id, "name", "João")
        profile = self.conversation_memory.get_user_profile(user_id)
        self.assertEqual(profile["name"], "João")

    def test_anti_fake_system(self):
        user_id = "test_user_456"
        analysis = self.anti_fake_system.analyze_user_behavior(user_id, "oi")
        self.assertFalse(analysis["is_suspicious"])

        for _ in range(6):
            self.anti_fake_system.analyze_user_behavior(user_id, "ok")
        analysis = self.anti_fake_system.analyze_user_behavior(user_id, "sim")
        self.assertTrue(analysis["is_suspicious"])
        self.assertIn("Padrões de respostas automáticas", analysis["reasons"])

        # Teste de imperfeições
        original_text = "Olá, como você está?"
        error_text = self.anti_fake_system.introduce_typing_error(original_text)
        self.assertIsInstance(error_text, str)
        # A chance de erro é pequena, então não podemos garantir que haverá um erro
        # self.assertNotEqual(original_text, error_text) # Isso pode falhar ocasionalmente

        forget_text = self.anti_fake_system.simulate_forgetfulness(original_text)
        self.assertIsInstance(forget_text, str)

        limitation_message = self.anti_fake_system.simulate_limitation()
        self.assertIsInstance(limitation_message, str)

    def test_typing_simulator(self):
        text = "Olá, como vai?"
        typing_time = self.typing_simulator.calculate_typing_time(text)
        self.assertGreaterEqual(typing_time, 1.0)
        self.assertLessEqual(typing_time, 8.0)

    @patch('audio_manager.datetime')
    def test_audio_manager(self, mock_datetime):
        user_id = "test_user_789"
        # Mock para simular que é noite
        mock_datetime.now.return_value = datetime(2025, 1, 1, 20, 0, 0)
        audio_key = self.audio_manager.get_contextual_audio("oi", "neutro", {})
        self.assertEqual(audio_key, "boa_noite_nao_sou_fake")

        # Mock para simular que é dia
        mock_datetime.now.return_value = datetime(2025, 1, 1, 8, 0, 0)
        audio_key = self.audio_manager.get_contextual_audio("oi", "neutro", {})
        self.assertEqual(audio_key, "bom_dia_nao_sou_fake")

        self.audio_manager.mark_audio_used("oi_meu_amor_tudo_bem", user_id)
        self.assertEqual(Config.AUDIOS["oi_meu_amor_tudo_bem"]["usage_count"], 1)
    def test_personality_engine(self):
        user_id = "test_user_101"
        prompt = self.personality_engine.generate_personality_prompt("Oi", user_id, "neutro")
        self.assertIn("Você é Mylle Alves", prompt)
        self.assertIn("REGRAS IMPORTANTES", prompt)

    def test_ml_engine(self):
        user_id = "test_user_ml"
        self.ml_engine.update_engagement_score(user_id)
        self.assertGreater(self.ml_engine.user_engagement_scores[user_id], 0.5)

        likelihood = self.ml_engine.predict_sales_likelihood(user_id)
        self.assertGreaterEqual(likelihood, 0.0)
        self.assertLessEqual(likelihood, 1.0)

        suggestion = self.ml_engine.get_personalized_suggestion(user_id)
        self.assertIsInstance(suggestion, str)

    @patch("utils.sqlite3.connect")
    def test_db_functions(self, mock_connect):
        mock_connect.return_value = self.mock_conn
        conn = init_db()
        self.assertIsNotNone(conn)

        user_id = "db_test_user"
        session_id = "db_test_session"
        save_message(conn, user_id, session_id, "user", "Hello DB")
        self.mock_cursor.execute.assert_called()
        self.mock_conn.commit.assert_called()

        # Mock para load_messages
        self.mock_cursor.fetchall.return_value = [("user", "Hello DB", "2023-01-01 10:00:00", None)]
        messages = load_messages(conn, user_id, session_id)
        self.assertEqual(len(messages), 1)

    def test_extract_user_info(self):
        user_id = "info_test_user"
        from memory import conversation_memory as global_conversation_memory
        extract_user_info("Meu nome é Ana e tenho 25 anos. Moro em São Paulo.", user_id)
        profile = global_conversation_memory.get_user_profile(user_id)
        self.assertEqual(profile["name"], "Ana")
        self.assertEqual(profile["age"], 25)
        self.assertEqual(profile["location"], "São Paulo")

        extract_user_info("Quero ver seus packs, Mylle!", user_id)
        profile = global_conversation_memory.get_user_profile(user_id)
        self.assertTrue(profile["showed_interest_in_packs"])

    def test_detect_fake_question(self):
        self.assertGreater(detect_fake_question("Você é um bot?"), 0.7)
        self.assertLess(detect_fake_question("Olá, tudo bem?"), 0.5)

if __name__ == "__main__":
    unittest.main()



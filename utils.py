import sqlite3
import uuid
import json
import re
import logging
from typing import Dict, List
from config import Config
from memory import conversation_memory

logger = logging.getLogger(__name__)

def get_user_id() -> str:
    """Gera ID único do usuário"""
    import streamlit as st # Import local para evitar circular dependency
    if 'user_id' not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    return st.session_state.user_id

def init_db() -> sqlite3.Connection:
    """Inicializa banco de dados"""
    conn = sqlite3.connect('chat_history.db', check_same_thread=False)
    c = conn.cursor()
    
    # Verificar se a tabela existe
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='conversations'")
    table_exists = c.fetchone()
    
    if not table_exists:
        # Criar tabela nova
        c.execute('''
            CREATE TABLE conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        ''')
    else:
        # Verificar se coluna metadata existe
        c.execute("PRAGMA table_info(conversations)")
        columns = [column[1] for column in c.fetchall()]
        if 'metadata' not in columns:
            # Adicionar coluna metadata
            c.execute("ALTER TABLE conversations ADD COLUMN metadata TEXT")
    
    conn.commit()
    return conn

def detect_fake_question(text: str) -> float:
    """Detecta se a mensagem é uma pergunta sobre fake"""
    text_lower = text.lower()
    total_score = 0.0
    
    for patterns, score in Config.FAKE_DETECTION_PATTERNS:
        if all(pattern in text_lower for pattern in patterns):
            total_score += score
        elif any(pattern in text_lower for pattern in patterns):
            total_score += score * 0.5
    
    return min(1.0, max(0.0, total_score))

def save_message(conn: sqlite3.Connection, user_id: str, session_id: str, role: str, content: str, metadata: dict = None):
    """Salva mensagem no banco de dados"""
    try:
        c = conn.cursor()
        metadata_json = json.dumps(metadata) if metadata else None
        c.execute('''
            INSERT INTO conversations (user_id, session_id, role, content, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, session_id, role, content, metadata_json))
        conn.commit()
    except Exception as e:
        logger.error(f"Erro ao salvar mensagem: {e}")

def load_messages(conn: sqlite3.Connection, user_id: str, session_id: str, limit: int = 50) -> List[Dict]:
    """Carrega mensagens do banco de dados"""
    try:
        c = conn.cursor()
        c.execute('''
            SELECT role, content, timestamp, metadata FROM conversations 
            WHERE user_id = ? AND session_id = ?
            ORDER BY timestamp DESC LIMIT ?
        ''', (user_id, session_id, limit))
        
        messages = []
        for row in reversed(c.fetchall()):
            metadata = json.loads(row[3]) if row[3] else {}
            messages.append({
                "role": row[0],
                "content": row[1],
                "timestamp": row[2],
                "metadata": metadata
            })
        return messages
    except Exception as e:
        logger.error(f"Erro ao carregar mensagens: {e}")
        return []

def extract_user_info(message: str, user_id: str):
    """Extrai informações do usuário da mensagem"""
    message_lower = message.lower()
    
    # Extrair nome
    name_patterns = [
        r"meu nome é ([A-Za-zÀ-ÿ\s]+?)(?=\s*e tenho|\.|\,|\s*$)",
        r"me chamo ([A-Za-zÀ-ÿ\s]+?)(?=\s*e tenho|\.|\,|\s*$)",
        r"sou o ([A-Za-zÀ-ÿ\s]+?)(?=\s*e tenho|\.|\,|\s*$)",
        r"eu sou ([A-Za-zÀ-ÿ\s]+?)(?=\s*e tenho|\.|\,|\s*$)"
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, message_lower)
        if match:
            name = match.group(1).strip().title()
            conversation_memory.update_user_profile(user_id, "name", name)
            logger.info(f"Nome do usuário extraído: {name}")
            break

    # Extrair idade
    age_patterns = [
        r"tenho (\d+) anos",
        r"minha idade é (\d+)"
    ]
    for pattern in age_patterns:
        match = re.search(pattern, message_lower)
        if match:
            age = int(match.group(1))
            conversation_memory.update_user_profile(user_id, "age", age)
            logger.info(f"Idade do usuário extraída: {age}")
            break

    # Extrair localização
    location_patterns = [
        r"sou de ([A-Za-zÀ-ÿ\s]+?)(?=\.|\,|\s*$)",
        r"moro em ([A-Za-zÀ-ÿ\s]+?)(?=\.|\,|\s*$)"
    ]
    for pattern in location_patterns:
        match = re.search(pattern, message_lower)
        if match:
            location = match.group(1).strip().title()
            conversation_memory.update_user_profile(user_id, "location", location)
            logger.info(f"Localização do usuário extraída: {location}")
            break

    # Extrair interesse em packs
    pack_interest_patterns = [
        "quero ver seus packs", "interesso nos packs", "comprar pack", "preço dos packs"
    ]
    for pattern in pack_interest_patterns:
        if pattern in message_lower:
            conversation_memory.update_user_profile(user_id, "showed_interest_in_packs", True)
            logger.info("Usuário demonstrou interesse em packs.")
            break



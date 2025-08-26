
from __future__ import annotations
import random

TRIGGERS = ["fake","falsa","bot","robô","robo","é você mesmo","vc é real","duvido"]

RESPONSES = [
    "Não sou fake não 😘 tô aqui de verdade contigo, amor.",
    "Claro que sou eu mesma, vida 💖 pode confiar.",
    "Eii, para com isso 😂 tô aqui de carne e osso contigo.",
    "Kkk duvida de mim? Então fica e sente minha energia 💋",
    "Tô aqui de verdade, bem pertinho de você 😏",
    "Ô amor, não sou robô não… sou todinha sua 😍"
]

AUDIO_URLS = [
    "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/nao%20sou%20fake%20nao.mp3",
    "https://github.com/andrearagaoregis/MylleAlves/raw/refs/heads/main/assets/Bom%20dia%20-%20n%C3%A3o%20sou%20fake%20n%C3%A3o....mp3",
    "https://github.com/andrearagaoregis/MylleAlves/raw/refs/heads/main/assets/Boa%20tarde%20-%20N%C3%A3o%20sou%20fake%20n%C3%A3o....mp3",
    "https://github.com/andrearagaoregis/MylleAlves/raw/refs/heads/main/assets/Boa%20noite%20-%20N%C3%A3o%20sou%20fake%20n%C3%A3o....mp3"
]

def is_trigger(text: str) -> bool:
    t = (text or "").lower()
    return any(x in t for x in TRIGGERS)

def reply() -> dict:
    if random.random() < 0.5:
        return {"type":"audio","url":random.choice(AUDIO_URLS)}
    return {"type":"text","content":random.choice(RESPONSES)}

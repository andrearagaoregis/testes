import streamlit as st
import requests
import json
import time
import random
import sqlite3
import re
import os
import uuid
from datetime import datetime
from pathlib import Path
from functools import lru_cache

# ======================
# CONFIGURAÇÃO INICIAL DO STREAMLIT
# ======================
st.set_page_config(
    page_title="Mylle Alves Premium",
    page_icon="💋",
    layout="wide",
    initial_sidebar_state="expanded"
)

st._config.set_option('client.caching', True)
st._config.set_option('client.showErrorDetails', False)

# ======================
# ESTILO GLOBAL
# ======================
hide_streamlit_style = """
<style>
    div[data-testid="stToolbar"] {display: none !important;}
    div[data-testid="stDecoration"] {display: none !important;}
    div[data-testid="stStatusWidget"] {display: none !important;}
    #MainMenu {display: none !important;}
    header {display: none !important;}
    footer {display: none !important;}

    body {background: #0d001a;}
    .main-content {
        background: linear-gradient(135deg, #1e0033, #3c0066);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 0 25px rgba(255,20,147,0.3);
        color: white;
    }
    .section-box {
        background: rgba(255, 20, 147, 0.1);
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid rgba(255, 20, 147, 0.2);
    }
    h2, h3, h4 {color: #ff66b3 !important;}
    a {color: #ff66b3; text-decoration:none;}
    a:hover {color:#fff;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ======================
# CONFIGURAÇÕES E LINKS
# ======================
class Config:
    LOGO_URL = "https://i.ibb.co/LX7x3tcB/Logo-Golden-Pepper-Letreiro-1.png"
    IMG_PROFILE = "https://i.ibb.co/vxnTYm0Q/BY-Admiregirls-su-Admiregirls-su-156.jpg"
    SOCIAL_LINKS = {
        "instagram": "https://instagram.com/myllealves",
        "facebook": "https://facebook.com/myllealves",
        "telegram": "https://t.me/myllealves",
        "tiktok": "https://tiktok.com/@myllealves"
    }

# ======================
# SIDEBAR HOT
# ======================
def setup_sidebar():
    with st.sidebar:
        st.markdown("""
        <style>
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #1e0033 0%, #3c0066 100%) !important;
                border-right: 2px solid #ff1493 !important;
            }
            .sidebar-logo {width: 100%; margin-bottom: 10px;}
            .sidebar-header {text-align: center; margin-bottom: 20px;}
            .sidebar-header img {
                border-radius: 50%;
                border: 3px solid #ff1493;
                width: 90px;
                height: 90px;
                object-fit: cover;
            }
            .menu-button {
                display: block;
                width: 100%;
                padding: 12px;
                margin: 5px 0;
                border-radius: 8px;
                background: rgba(255, 20, 147, 0.15);
                color: white;
                border: 1px solid rgba(255, 20, 147, 0.4);
                text-align: center;
                font-weight: bold;
                transition: 0.3s;
                cursor: pointer;
                text-decoration: none;
            }
            .menu-button:hover {
                background: rgba(255, 20, 147, 0.4);
                text-decoration: none;
                color: white;
            }
            .social-button {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                padding: 10px;
                border-radius: 5px;
                background: rgba(255, 102, 179, 0.1);
                border: 1px solid rgba(255, 102, 179, 0.2);
                color: white;
                text-decoration: none;
                transition: all 0.3s;
                margin-bottom: 8px;
            }
            .social-button:hover {
                background: rgba(255, 102, 179, 0.3);
            }
        </style>
        """, unsafe_allow_html=True)

        # LOGO
        st.markdown(f"""
        <div style='text-align:center;'>
            <img src="{Config.LOGO_URL}" class="sidebar-logo">
        </div>
        """, unsafe_allow_html=True)

        # FOTO PERFIL
        st.markdown(f"""
        <div class="sidebar-header">
            <img src="{Config.IMG_PROFILE}" alt="Mylle Alves">
            <h3 style="color:#ff66b3; margin-top:10px;">Mylle Alves Premium</h3>
        </div>
        """, unsafe_allow_html=True)

        # MENU
        st.markdown("---")
        st.markdown("### 🔥 Menu Hot")

        menu_items = {
            "Início": "home",
            "Galeria Privada": "gallery",
            "Mensagens": "messages",
            "Ofertas": "offers"
        }
        for label, page in menu_items.items():
            if st.button(label, use_container_width=True):
                st.session_state.current_page = page

        # REDES SOCIAIS
        st.markdown("---")
        st.markdown("### 🌐 Redes Sociais")
        st.markdown(f"""
        <a href="{Config.SOCIAL_LINKS['instagram']}" target="_blank" class="social-button">📷 Instagram</a>
        <a href="{Config.SOCIAL_LINKS['facebook']}" target="_blank" class="social-button">📘 Facebook</a>
        <a href="{Config.SOCIAL_LINKS['telegram']}" target="_blank" class="social-button">📢 Telegram</a>
        <a href="{Config.SOCIAL_LINKS['tiktok']}" target="_blank" class="social-button">🎵 TikTok</a>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("<p style='text-align:center; font-size:0.8em; color:#aaa;'>© 2024 Mylle Alves Premium 🔞</p>", unsafe_allow_html=True)

# ======================
# PÁGINAS HOT
# ======================
def show_home():
    st.markdown("<div class='main-content'><h2>💋 Bem-vindo ao Meu Mundo</h2><p>Conteúdos quentes e exclusivos esperando por você!</p></div>", unsafe_allow_html=True)

def show_gallery():
    st.markdown("<div class='main-content'><h2>📸 Galeria Privada</h2><p>Veja minhas fotos mais ousadas...</p></div>", unsafe_allow_html=True)

def show_messages():
    st.markdown("<div class='main-content'><h2>💬 Mensagens</h2><p>Bate-papo íntimo e exclusivo comigo...</p></div>", unsafe_allow_html=True)

def show_offers():
    st.markdown("<div class='main-content'><h2>💎 Ofertas Especiais</h2><p>Escolha o pacote que vai te enlouquecer 🔥</p></div>", unsafe_allow_html=True)

# ======================
# APP PRINCIPAL
# ======================
def main():
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'

    setup_sidebar()

    if st.session_state.current_page == "home":
        show_home()
    elif st.session_state.current_page == "gallery":
        show_gallery()
    elif st.session_state.current_page == "messages":
        show_messages()
    elif st.session_state.current_page == "offers":
        show_offers()

if __name__ == "__main__":
    main()

                text-align: center;
                margin-bottom: 20px;
            ">
                <h3 style="color: #ff66b3; margin: 0;">💝 Apoie Meu Conteúdo</h3>
                <p style="color: #aaa; margin: 5px 0 0;">Sua doação me ajuda a criar mais conteúdo exclusivo!</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Botões de valor rápido com links de checkout
            st.markdown("### 🎯 Valores Sugeridos")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("R$ 30", key="donate_30", use_container_width=True):
                    self._redirect_to_checkout(30)
            with col2:
                if st.button("R$ 50", key="donate_50", use_container_width=True):
                    self._redirect_to_checkout(50)
            with col3:
                if st.button("R$ 100", key="donate_100", use_container_width=True):
                    self._redirect_to_checkout(100)
            with col4:
                if st.button("R$ 150", key="donate_150", use_container_width=True):
                    self._redirect_to_checkout(150)
    
    def _redirect_to_checkout(self, amount: float, is_custom: bool = False):
        """Redireciona para página de checkout"""
        user_id = get_user_id()
        
        # Obter link de checkout apropriado
        if is_custom:
            checkout_url = Config.DONATION_CHECKOUT_LINKS["custom"]
        else:
            checkout_url = Config.DONATION_CHECKOUT_LINKS.get(amount, Config.DONATION_CHECKOUT_LINKS["custom"])
        
        # Redirecionar para checkout
        st.markdown(f"""
        <script>
            window.open('{checkout_url}', '_blank');
        </script>
        """, unsafe_allow_html=True)
        
        st.success(f"✅ Redirecionando para página de pagamento de R$ {amount:.2f}...")

# Instância global do sistema de doação
donation_system = DonationSystem()

# ======================
# INTERFACE DO USUÁRIO APRIMORADA
# ======================
def show_typing_indicator():
    """Mostra indicador de digitação"""
    return st.markdown("""
    <div class="typing-indicator">
        <span></span>
        <span></span>
        <span></span>
        Mylle está digitando...
    </div>
    """, unsafe_allow_html=True)

def show_recording_indicator(duration: float):
    """Mostra indicador de gravação de áudio"""
    return st.markdown(f"""
    <div class="recording-indicator">
        🎤 Gravando áudio... ({duration:.1f}s)
    </div>
    """, unsafe_allow_html=True)

def show_user_typing_indicator():
    """Mostra que o usuário está digitando"""
    return st.markdown("""
    <div class="user-typing">
        Você está digitando...
    </div>
    """, unsafe_allow_html=True)

def show_home_page():
    """Mostra página inicial"""
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <h1 style="color: #ff66b3; font-size: 2.5em; margin-bottom: 10px;">
            🔥 Mylle Alves Premium 🔥
        </h1>
        <p style="color: #aaa; font-size: 1.2em; margin-bottom: 30px;">
            Conteúdo exclusivo e muito quente te esperando...
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Imagem de perfil
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(Config.IMG_PROFILE, width=300, caption="Mylle Alves 💋")
    
    # Botões de ação
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💬 Conversar Comigo", use_container_width=True):
            st.session_state.current_page = "chat"
            st.rerun()
    
    with col2:
        if st.button("📦 Ver Meus Packs", use_container_width=True):
            st.session_state.current_page = "offers"
            st.rerun()
    
    with col3:
        if st.button("🖼️ Galeria", use_container_width=True):
            st.session_state.current_page = "gallery"
            st.rerun()
    
    # Links sociais
    st.markdown("### 🌟 Me siga nas redes:")
    social_cols = st.columns(4)
    
    for i, (platform, link) in enumerate(Config.SOCIAL_LINKS.items()):
        with social_cols[i]:
            icon = Config.SOCIAL_ICONS[platform]
            if st.button(icon, key=f"social_{platform}", use_container_width=True):
                st.markdown(f'<script>window.open("{link}", "_blank");</script>', unsafe_allow_html=True)

def show_chat_page():
    """Mostra página de chat aprimorada"""
    st.markdown("### 💬 Chat com Mylle Alves")
    
    # Área de mensagens
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                
                # Mostrar áudio se disponível
                if message["role"] == "assistant" and message.get("metadata", {}).get("audio"):
                    audio_key = message["metadata"]["audio"]
                    audio_url = Config.AUDIOS.get(audio_key, {}).get("url")
                    if audio_url:
                        st.audio(audio_url)
    
    # Mostrar indicador se usuário está digitando
    if st.session_state.get('user_typing', False):
        show_user_typing_indicator()
    
    # Input do usuário
    if prompt := st.chat_input("Digite sua mensagem..."):
        # Verificar limite de requests
        if st.session_state.request_count >= Config.MAX_REQUESTS_PER_SESSION:
            st.error("Limite de mensagens atingido para esta sessão.")
            return
        
        # Simular delay de digitação do usuário
        st.session_state.user_typing = True
        time.sleep(random.uniform(0.5, 1.5))
        st.session_state.user_typing = False
        
        # Adicionar mensagem do usuário
        user_message = {"role": "user", "content": prompt, "metadata": {}}
        st.session_state.messages.append(user_message)
        st.session_state.request_count += 1
        
        # Salvar no banco
        save_message(st.session_state.db_conn, get_user_id(), st.session_state.session_id, "user", prompt)
        
        # Mostrar mensagem do usuário
        with st.chat_message("user"):
            st.write(prompt)
        
        # Simular delay antes da resposta (usuário parou de digitar)
        time.sleep(random.uniform(2.0, 5.0))
        
        # Gerar resposta
        with st.chat_message("assistant"):
            # Mostrar indicador de digitação
            typing_placeholder = st.empty()
            typing_placeholder.markdown("""
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
                Mylle está digitando...
            </div>
            """, unsafe_allow_html=True)
            
            # Gerar resposta da API
            response = call_gemini_api(prompt, get_user_id())
            
            # Simular tempo de digitação
            time.sleep(response.get("typing_time", 2.0))
            
            # Limpar indicador de digitação
            typing_placeholder.empty()
            
            # Mostrar resposta
            st.write(response["text"])
            
            # Simular gravação e reproduzir áudio se disponível
            if response.get("audio"):
                audio_key = response["audio"]
                
                # Mostrar indicador de gravação
                recording_time = audio_manager.simulate_recording_time(audio_key)
                recording_placeholder = st.empty()
                recording_placeholder.markdown(f"""
                <div class="recording-indicator">
                    🎤 Gravando áudio... ({recording_time:.1f}s)
                </div>
                """, unsafe_allow_html=True)
                
                # Simular tempo de gravação
                time.sleep(recording_time)
                
                # Limpar indicador de gravação
                recording_placeholder.empty()
                
                # Reproduzir áudio
                audio_url = Config.AUDIOS.get(audio_key, {}).get("url")
                if audio_url:
                    st.audio(audio_url)
                    audio_manager.mark_audio_used(audio_key, get_user_id())
            
            # Mostrar CTA se necessário
            if response.get("cta", {}).get("show"):
                if st.button(response["cta"]["label"], key=f"cta_button_{len(st.session_state.messages)}"):
                    st.session_state.current_page = response["cta"]["target"]
                    st.rerun()
        
        # Salvar resposta no banco
        assistant_message = {
            "role": "assistant", 
            "content": response["text"],
            "metadata": {"audio": response.get("audio")}
        }
        st.session_state.messages.append(assistant_message)
        save_message(st.session_state.db_conn, get_user_id(), st.session_state.session_id, "assistant", response["text"], {"audio": response.get("audio")})

def show_offers_page():
    """Mostra página de ofertas"""
    st.markdown("### 📦 Meus Packs Exclusivos")
    
    # Pack Taradinha
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(Config.PACK_IMAGES["TARADINHA"], width=200)
    with col2:
        st.markdown("""
        #### 🔥 Pack Taradinha - R$ 30
        - 50+ fotos sensuais
        - Conteúdo exclusivo
        - Acesso imediato
        """)
        if st.button("💳 Comprar Pack Taradinha", key="buy_taradinha"):
            st.markdown(f'<script>window.open("{Config.CHECKOUT_TARADINHA}", "_blank");</script>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Pack Molhadinha
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(Config.PACK_IMAGES["MOLHADINHA"], width=200)
    with col2:
        st.markdown("""
        #### 💦 Pack Molhadinha - R$ 50
        - 80+ fotos quentes
        - Vídeos exclusivos
        - Conteúdo premium
        """)
        if st.button("💳 Comprar Pack Molhadinha", key="buy_molhadinha"):
            st.markdown(f'<script>window.open("{Config.CHECKOUT_MOLHADINHA}", "_blank");</script>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Pack Safadinha
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(Config.PACK_IMAGES["SAFADINHA"], width=200)
    with col2:
        st.markdown("""
        #### 😈 Pack Safadinha - R$ 80
        - 120+ fotos explícitas
        - Vídeos longos
        - Conteúdo mais ousado
        """)
        if st.button("💳 Comprar Pack Safadinha", key="buy_safadinha"):
            st.markdown(f'<script>window.open("{Config.CHECKOUT_SAFADINHA}", "_blank");</script>', unsafe_allow_html=True)

def show_gallery_page():
    """Mostra galeria de fotos"""
    st.markdown("### 🖼️ Galeria de Fotos")
    
    st.info("🔒 Algumas fotos são apenas uma amostra. Para ver o conteúdo completo, adquira meus packs!")
    
    cols = st.columns(3)
    for i, img_url in enumerate(Config.IMG_GALLERY):
        with cols[i % 3]:
            st.image(img_url, caption=f"Foto {i+1}")
    
    st.markdown("---")
    if st.button("📦 Ver Todos os Packs", use_container_width=True):
        st.session_state.current_page = "offers"
        st.rerun()

def show_sidebar():
    """Mostra sidebar com navegação"""
    with st.sidebar:
        st.markdown("### 🔥 Mylle Alves")
        st.image(Config.IMG_PROFILE, width=150)
        
        st.markdown("---")
        
        # Navegação
        if st.button("🏠 Início", use_container_width=True):
            st.session_state.current_page = "home"
            st.rerun()
        
        if st.button("💬 Chat", use_container_width=True):
            st.session_state.current_page = "chat"
            st.rerun()
        
        if st.button("📦 Packs", use_container_width=True):
            st.session_state.current_page = "offers"
            st.rerun()
        
        if st.button("🖼️ Galeria", use_container_width=True):
            st.session_state.current_page = "gallery"
            st.rerun()
        
        st.markdown("---")
        
        # Sistema de doação
        donation_system.show_donation_modal()
        
        st.markdown("---")
        st.markdown("💋 **Mylle Alves Premium**")
        st.markdown("Conteúdo exclusivo para maiores de 18 anos")

def handle_age_verification():
    """Verifica idade do usuário"""
    if not st.session_state.get('age_verified', False):
        st.markdown("""
        <div style="text-align: center; padding: 50px;">
            <h1 style="color: #ff66b3;">🔞 Verificação de Idade</h1>
            <p style="font-size: 1.2em; color: #aaa;">
                Este conteúdo é destinado apenas para maiores de 18 anos.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("✅ Sou maior de 18", use_container_width=True):
                st.session_state.age_verified = True
                st.rerun()
        
        with col3:
            if st.button("❌ Sou menor de 18", use_container_width=True):
                st.error("Você deve ser maior de 18 anos para acessar este conteúdo.")
                st.stop()
        
        return False
    return True

# ======================
# FUNÇÃO PRINCIPAL
# ======================
def main():
    # Inicializar sessão
    if 'db_conn' not in st.session_state:
        st.session_state.db_conn = init_db()
    
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(random.randint(100000, 999999))
    
    if 'messages' not in st.session_state:
        loaded_messages = load_messages(
            st.session_state.db_conn, 
            get_user_id(), 
            st.session_state.session_id
        )
        st.session_state.messages = loaded_messages
        
        # Carregar mensagens na memória
        for msg in loaded_messages:
            conversation_memory.add_message(
                get_user_id(), 
                msg["role"], 
                msg["content"], 
                msg.get("metadata", {})
            )
    
    if 'request_count' not in st.session_state:
        st.session_state.request_count = len([m for m in st.session_state.messages if m["role"] == "user"])
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "home"
    
    if 'user_typing' not in st.session_state:
        st.session_state.user_typing = False
    
    # Verificação de idade
    if not handle_age_verification():
        return
    
    # Mostrar sidebar
    show_sidebar()
    
    # Roteamento de páginas
    if st.session_state.current_page == "home":
        show_home_page()
    elif st.session_state.current_page == "chat":
        show_chat_page()
    elif st.session_state.current_page == "offers":
        show_offers_page()
    elif st.session_state.current_page == "gallery":
        show_gallery_page()

if __name__ == "__main__":
    main()


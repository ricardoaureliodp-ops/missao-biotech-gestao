import streamlit as st
import requests

# --- FUNÇÃO AUTOSSUFICIENTE (BUSCA O MODELO CORRETO SOZINHA) ---
def chamar_gemini(prompt, api_key):
    # PASSO 1: O código pergunta pro Google qual modelo a sua chave tem permissão para usar
    url_list = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    modelo_escolhido = "models/gemini-1.5-flash" # Padrão de segurança
    
    try:
        res_list = requests.get(url_list, timeout=10)
        if res_list.status_code == 200:
            modelos_disponiveis = res_list.json().get('models', [])
            for m in modelos_disponiveis:
                # Pega o primeiro modelo da família Gemini que faz geração de texto
                if 'generateContent' in m.get('supportedGenerationMethods', []) and 'gemini' in m.get('name'):
                    modelo_escolhido = m['name']
                    break
    except:
        pass # Se a busca falhar, tenta com o padrão

    # PASSO 2: Faz a chamada usando o modelo exato que o Google autorizou
    url_chat = f"https://generativelanguage.googleapis.com/v1beta/{modelo_escolhido}:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        response = requests.post(url_chat, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Erro Final. Modelo que o Google mandou usar: {modelo_escolhido}. Motivo da recusa: {response.text}"
    except Exception as e:
        return f"Erro de conexão com a internet. Detalhe: {e}"

# --- FUNÇÃO PARA A PLANILHA ---
def enviar_planilha(n, t, r):
    url_form = "https://docs.google.com/forms/d/e/1FAIpQLSf971GsVen1ehIuhMLQGdLjp7qTkM0GCcF7xik4AUdeoRM6AA/formResponse"
    dados = {"entry.2033090623": n, "entry.449784386": t, "entry.474665496": r}
    try: requests.post(url_form, data=dados, timeout=5)
    except: pass

st.set_page_config(page_title="Missão BioTech", page_icon="🏗️")
st.title("🏗️ Desafio: Gestão de Projetos")
st.markdown("---")

api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("🚨 Chave API não encontrada nos Secrets.")
    st.stop()

with st.sidebar:
    st.header("📋 Identificação")
    nome = st.text_input("Seu Nome:")
    turma = st.text_input("Sua Turma:")
    if st.button("Reiniciar"):
        st.session_state.clear()
        st.rerun()

if nome and turma:
    if "chat" not in st.session_state:
        st.session_state.chat = []
        st.session_state.enviado = False
        msg_inicial = f"Olá {nome}, sou a Diretora da BioTech. Nosso projeto está atrasado e 30% mais caro. Como gerente, qual sua primeira ação? (Ao final darei nota e direi RELATORIO_FINAL)"
        st.session_state.chat.append({"role": "assistant", "content": msg_inicial})

    for m in st.session_state.chat:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if p := st.chat_input("Digite sua resposta aqui..."):
        st.session_state.chat.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        
        contexto = f"Você é a Diretora da BioTech. O aluno {nome} respondeu: '{p}'. Continue o desafio de forma curta. Se ele resolver, dê nota 0-10 e escreva RELATORIO_FINAL."
        resposta_ia = chamar_gemini(contexto, api_key)
        
        st.session_state.chat.append({"role": "assistant", "content": resposta_ia})
        with st.chat_message("assistant"): st.markdown(resposta_ia)
        
        if "RELATORIO_FINAL" in resposta_ia and not st.session_state.enviado:
            enviar_planilha(nome, turma, resposta_ia)
            st.session_state.enviado = True
            st.success("✅ Nota registrada na planilha!")
else:
    st.info("👈 Preencha os dados ao lado para começar.")

import streamlit as st
import requests
import json

# --- FUNÇÃO PARA FALAR COM O GOOGLE (USANDO MODELO 1.0 PRO) ---
def chamar_gemini(prompt, api_key):
    # Mudamos para o gemini-1.0-pro. Ele é universal e não dá erro 404 em chaves novas!
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.0-pro:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Erro na Diretoria: {response.status_code}"
    except Exception as e:
        return "Erro de conexão. Tente novamente em instantes."

# --- FUNÇÃO PARA ENVIAR NOTA PARA A PLANILHA ---
def enviar_planilha(n, t, r):
    url_form = "https://docs.google.com/forms/d/e/1FAIpQLSf971GsVen1ehIuhMLQGdLjp7qTkM0GCcF7xik4AUdeoRM6AA/formResponse"
    dados = {"entry.2033090623": n, "entry.449784386": t, "entry.474665496": r}
    try: requests.post(url_form, data=dados, timeout=5)
    except: pass

# --- CONFIGURAÇÃO DA TELA ---
st.set_page_config(page_title="Missão BioTech", page_icon="🏗️")
st.title("🏗️ Desafio: Gestão de Projetos")
st.markdown("---")

api_key = st.secrets.get("GEMINI_API_KEY")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("📋 Identificação")
    nome = st.text_input("Seu Nome Completo:")
    turma = st.text_input("Sua Turma:")
    if st.button("Reiniciar Atividade"):
        st.session_state.clear()
        st.rerun()

if "chat" not in st.session_state:
    st.session_state.chat = []
    st.session_state.enviado = False

# --- LÓGICA DO JOGO ---
if nome and turma:
    if not st.session_state.chat:
        msg_inicial = f"Olá {nome}, sou a Diretora da BioTech. Nosso projeto está atrasado e 30% mais caro. Como gerente, qual sua primeira ação? (Ao final darei nota e direi RELATORIO_FINAL)"
        st.session_state.chat.append({"role": "assistant", "content": msg_inicial})

    for m in st.session_state.chat:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if p := st.chat_input("Digite sua resposta aqui..."):
        st.session_state.chat.append({"role": "user", "content": p})
        with st.chat_message("user"):
            st.markdown(p)
        
        prompt_full = f"Você é a Diretora da BioTech. O aluno {nome} é o gerente do projeto. Responda à fala dele: '{p}'. Continue o desafio de gestão. Se ele resolver o problema satisfatoriamente, dê uma nota de 0 a 10 e escreva obrigatoriamente a palavra RELATORIO_FINAL no fim."
        
        resposta_ia = chamar_gemini(prompt_full, api_key)
        
        st.session_state.chat.append({"role": "assistant", "content": resposta_ia})
        with st.chat_message("assistant"):
            st.markdown(resposta_ia)
        
        if "RELATORIO_FINAL" in resposta_ia and not st.session_state.enviado:
            enviar_planilha(nome, turma, resposta_ia)
            st.session_state.enviado = True
            st.success("✅ Seu desempenho foi registrado na planilha do professor!")
else:
    st.info("👈 Por favor, preencha seu Nome e Turma na barra lateral para começar.")

import streamlit as st
import requests
import json

# --- FUNÇÃO PARA FALAR COM O GOOGLE (SEM BIBLIOTECA) ---
def chamar_gemini(prompt, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    else:
        return f"Erro na Diretoria: {response.status_code}"

# --- FUNÇÃO PARA A PLANILHA ---
def enviar_planilha(n, t, r):
    url_form = "https://docs.google.com/forms/d/e/1FAIpQLSf971GsVen1ehIuhMLQGdLjp7qTkM0GCcF7xik4AUdeoRM6AA/formResponse"
    dados = {"entry.2033090623": n, "entry.449784386": t, "entry.474665496": r}
    try: requests.post(url_form, data=dados, timeout=5)
    except: pass

st.set_page_config(page_title="Missão BioTech", page_icon="🏗️")
st.title("🏗️ Desafio: Gestão de Projetos")

api_key = st.secrets.get("GEMINI_API_KEY")

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
        # Primeira fala da Diretora
        msg_inicial = f"Olá {nome}, sou a Diretora da BioTech. Nosso projeto está atrasado e 30% mais caro. Como gerente, qual sua primeira ação? (Ao final darei nota e direi RELATORIO_FINAL)"
        st.session_state.chat.append({"role": "assistant", "content": msg_inicial})

    for m in st.session_state.chat:
        with st.chat_message(m["role"]): st.write(m["content"])

    if p := st.chat_input("Responda aqui..."):
        st.session_state.chat.append({"role": "user", "content": p})
        with st.chat_message("user"): st.write(p)
        
        # Chama a IA no modo "Raiz"
        resposta_ia = chamar_gemini(f"Você é a Diretora BioTech. O aluno {nome} disse: {p}. Responda e continue o desafio.", api_key)
        
        st.session_state.chat.append({"role": "assistant", "content": resposta_ia})
        with st.chat_message("assistant"): st.write(resposta_ia)
        
        if "RELATORIO_FINAL" in resposta_ia:
            enviar_planilha(nome, turma, resposta_ia)
            st.success("✅ Nota enviada!")
else:
    st.info("👈 Identifique-se para começar.")

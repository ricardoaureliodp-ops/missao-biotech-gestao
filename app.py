import streamlit as st
import google.generativeai as genai
import requests

# Função simples para a planilha
def salvar_dados(n, t, r):
    url = "https://docs.google.com/forms/d/e/1FAIpQLSf971GsVen1ehIuhMLQGdLjp7qTkM0GCcF7xik4AUdeoRM6AA/formResponse"
    d = {"entry.2033090623": n, "entry.449784386": t, "entry.474665496": r}
    try: requests.post(url, data=d, timeout=5)
    except: pass

st.set_page_config(page_title="Missão BioTech", page_icon="🏗️")
st.title("🏗️ Desafio: Gestão de Projetos")

# Configuração da Chave
try:
    key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("🚨 Chave API não configurada corretamente nos Secrets.")
    st.stop()

with st.sidebar:
    st.header("📋 Identificação")
    nome = st.text_input("Seu Nome:")
    turma = st.text_input("Sua Turma:")
    if st.button("Reiniciar Jogo"):
        st.session_state.chat_history = []
        st.rerun()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if nome and turma:
    # Início do jogo
    if not st.session_state.chat_history:
        try:
            prompt_inicial = f"Você é a Diretora da BioTech. O aluno {nome} é o novo Gerente. Peça ajuda com o projeto atrasado. No final, dê nota e escreva RELATORIO_FINAL."
            res = model.generate_content(prompt_inicial)
            st.session_state.chat_history.append({"role": "assistant", "content": res.text})
        except Exception as e:
            st.error(f"Erro ao iniciar IA: {e}")

    # Exibe histórico
    for m in st.session_state.chat_history:
        with st.chat_message(m["role"]): st.write(m["content"])

    # Entrada do aluno
    if p := st.chat_input("Sua resposta..."):
        st.session_state.chat_history.append({"role": "user", "content": p})
        with st.chat_message("user"): st.write(p)
        
        try:
            # Resposta simples para evitar erros de histórico longo
            resposta = model.generate_content(f"Diretora BioTech respondendo a {nome}. Histórico recente: {p}")
            st.session_state.chat_history.append({"role": "assistant", "content": resposta.text})
            with st.chat_message("assistant"): st.write(resposta.text)
            
            if "RELATORIO_FINAL" in resposta.text:
                salvar_dados(nome, turma, resposta.text)
                st.success("✅ Nota enviada para a planilha!")
        except:
            st.error("Erro na resposta da IA.")
else:
    st.info("👈 Por favor, informe seu Nome e Turma na barra lateral.")

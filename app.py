import streamlit as st
import google.generativeai as genai
import requests

# --- ENVIO PARA PLANILHA ---
def enviar_para_planilha(nome, turma, relatorio):
    url = "https://docs.google.com/forms/d/e/1FAIpQLSf971GsVen1ehIuhMLQGdLjp7qTkM0GCcF7xik4AUdeoRM6AA/formResponse"
    dados = {
        "entry.2033090623": nome,
        "entry.449784386": turma,
        "entry.474665496": relatorio
    }
    try: requests.post(url, data=dados, timeout=5)
    except: pass

st.set_page_config(page_title="Missão: BioTech", page_icon="🏗️")
st.title("🏗️ Desafio: Gestão de Projetos e Processos")
st.markdown("---")

api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("🚨 Chave API não configurada.")
    st.stop()

genai.configure(api_key=api_key)

# Testando o nome mais simples possível
model = genai.GenerativeModel('gemini-1.5-flash')

with st.sidebar:
    st.header("📋 Identificação")
    nome_aluno = st.text_input("Seu Nome Completo:")
    turma_aluno = st.text_input("Sua Turma/Grupo:")
    if st.button("Reiniciar Atividade"):
        st.session_state.messages = []
        st.session_state.enviado = False
        st.rerun()

if nome_aluno and turma_aluno:
    if "messages" not in st.session_state or len(st.session_state.messages) == 0:
        st.session_state.messages = []
        st.session_state.enviado = False
        try:
            res = model.generate_content("Olá, apresente-se como Diretora da BioTech.")
            st.session_state.messages.append({"role": "assistant", "content": res.text})
        except Exception as e:
            st.error(f"Erro na IA: {e}")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Digite aqui..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        hist = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
        try:
            resp = model.generate_content(f"Diretora BioTech. Histórico:\n{hist}")
            with st.chat_message("assistant"): st.markdown(resp.text)
            st.session_state.messages.append({"role": "assistant", "content": resp.text})
            if "RELATORIO_FINAL" in resp.text and not st.session_state.enviado:
                enviar_para_planilha(nome_aluno, turma_aluno, resp.text)
                st.session_state.enviado = True
        except: pass
else:
    st.info("👈 Digite Nome e Turma para começar!")

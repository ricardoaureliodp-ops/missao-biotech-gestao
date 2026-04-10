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
    st.error("🚨 Chave API não encontrada.")
    st.stop()

genai.configure(api_key=api_key)

# NOME PURO. É assim que o Google gosta em 2026.
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
            # Chamada super simples para testar
            res = model.generate_content(f"Olá! Sou a diretora da BioTech. O aluno {nome_aluno} está aqui. Inicie a simulação.")
            st.session_state.messages.append({"role": "assistant", "content": res.text})
        except Exception as e:
            st.error(f"Erro ao acordar a IA: {e}")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Digite sua resposta aqui..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        hist = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
        
        try:
            resp = model.generate_content(f"Contexto: BioTech. Aluno: {nome_aluno}. Histórico:\n{hist}")
            with st.chat_message("assistant"): st.markdown(resp.text)
            st.session_state.messages.append({"role": "assistant", "content": resp.text})
            
            if "RELATORIO_FINAL" in resp.text and not st.session_state.enviado:
                enviar_para_planilha(nome_aluno, turma_aluno, resp.text)
                st.session_state.enviado = True
                st.success("✅ Nota enviada para a planilha!")
        except Exception as e:
            st.error(f"Erro na resposta: {e}")
else:
    st.info("👈 Digite seu Nome e Turma ali na esquerda para a IA aparecer!")

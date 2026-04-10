import streamlit as st
import google.generativeai as genai
import requests

# --- ENVIO PARA PLANILHA ---
def enviar_para_planilha(nome, turma, relatorio):
    url = "https://docs.google.com/forms/d/e/1FAIpQLSf971GsVen1ehIuhMLQGdLjp7qTkM0GCcF7xik4AUdeoRM6AA/formResponse"
    dados = {
        "entry.2033090623": nome, "entry.449784386": turma, "entry.474665496": relatorio
    }
    try: requests.post(url, data=dados, timeout=5)
    except: pass

st.set_page_config(page_title="Missão: BioTech", page_icon="🏗️")
st.title("🏗️ Desafio: Gestão de Projetos e Processos")

api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("🚨 Chave API não configurada.")
    st.stop()

genai.configure(api_key=api_key)

# TROCAMOS PARA O PRO QUE É MAIS ESTÁVEL EM ALGUNS SERVIDORES
model = genai.GenerativeModel('gemini-1.5-pro')

with st.sidebar:
    st.header("📋 Identificação")
    n = st.text_input("Nome:")
    t = st.text_input("Turma:")
    if st.button("Reiniciar"):
        st.session_state.messages = []
        st.session_state.enviado = False
        st.rerun()

if n and t:
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.enviado = False
        try:
            res = model.generate_content("Olá, sou a Diretora da BioTech. Vamos iniciar o desafio de Gestão de Projetos.")
            st.session_state.messages.append({"role": "assistant", "content": res.text})
        except Exception as e:
            st.error(f"Erro na conexão: {e}")

    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if p := st.chat_input("Digite aqui..."):
        st.session_state.messages.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        try:
            r = model.generate_content(p)
            st.session_state.messages.append({"role": "assistant", "content": r.text})
            with st.chat_message("assistant"): st.markdown(r.text)
            if "RELATORIO_FINAL" in r.text and not st.session_state.enviado:
                enviar_para_planilha(n, t, r.text)
                st.session_state.enviado = True
                st.success("✅ Nota registrada!")
        except: st.error("Erro ao responder.")
else:
    st.info("👈 Preencha Nome e Turma para começar!")

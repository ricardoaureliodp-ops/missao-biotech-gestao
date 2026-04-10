import streamlit as st
import google.generativeai as genai
import requests

# --- FUNÇÃO DE ENVIO PARA A PLANILHA ---
def enviar_para_planilha(nome, turma, relatorio):
    url = "https://docs.google.com/forms/d/e/1FAIpQLSf971GsVen1ehIuhMLQGdLjp7qTkM0GCcF7xik4AUdeoRM6AA/formResponse"
    dados = {
        "entry.2033090623": nome,
        "entry.449784386": turma,
        "entry.474665496": relatorio
    }
    try: requests.post(url, data=dados)
    except: pass

st.set_page_config(page_title="Missão: BioTech", page_icon="🏗️")
st.title("🏗️ Desafio: Gestão de Projetos e Processos")
st.markdown("---")

api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("🚨 Configure a chave GEMINI_API_KEY no Streamlit.")
    st.stop()

genai.configure(api_key=api_key)

# USANDO O NOME DE MODELO MAIS ESTÁVEL DO PLANETA
model = genai.GenerativeModel('models/gemini-1.5-flash')

with st.sidebar:
    st.header("📋 Identificação")
    nome = st.text_input("Seu Nome Completo:")
    turma = st.text_input("Sua Turma/Grupo:")
    if st.button("Reiniciar Atividade"):
        st.session_state.messages = []
        st.session_state.enviado = False
        st.rerun()

instrucao = f"Você é a Diretora da BioTech. O aluno {nome} é o Gerente. Avalie-o em 3 fases. No fim diga RELATORIO_FINAL e dê nota 0-10."

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.enviado = False
    try:
        res = model.generate_content(f"{instrucao}\n\nApresente-se e peça ajuda com o projeto BioTech.")
        st.session_state.messages.append({"role": "assistant", "content": res.text})
    except Exception as e:
        st.error(f"Erro na IA: {e}")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if nome and turma:
    if prompt := st.chat_input("Responda aqui..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        hist = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
        resp = model.generate_content(f"{instrucao}\n\nHistórico:\n{hist}")
        
        with st.chat_message("assistant"): st.markdown(resp.text)
        st.session_state.messages.append({"role": "assistant", "content": resp.text})
        
        if "RELATORIO_FINAL" in resp.text and not st.session_state.enviado:
            enviar_para_planilha(nome, turma, resp.text)
            st.session_state.enviado = True
            st.success("✅ Nota registrada na planilha!")
else:
    st.warning("👈 Preencha Nome e Turma para começar.")

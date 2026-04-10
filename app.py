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
    try: requests.post(url, data=dados)
    except: pass

st.set_page_config(page_title="Missão: Gestão de Projetos", page_icon="🏗️")
st.title("🏗️ Desafio: Gestão de Projetos e Processos")
st.markdown("---")

api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("🚨 Erro: Chave API não configurada.")
    st.stop()

# Voltando para o padrão estável de conexão
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

with st.sidebar:
    st.header("📋 Identificação")
    nome_aluno = st.text_input("Seu Nome Completo:")
    turma_aluno = st.text_input("Sua Turma/Grupo:")
    if st.button("Reiniciar Atividade"):
        st.session_state.messages = []
        st.session_state.enviado = False
        st.rerun()

instrucao = f"Você é a Diretora da BioTech. O aluno {nome_aluno} é o Gerente. Avalie-o em 3 fases. No fim diga RELATORIO_FINAL e dê nota 0-10."

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.enviado = False
    # Chamada de texto simples (sem erro de protocolo)
    res = model.generate_content(f"{instrucao}\n\nApresente-se e peça ajuda.")
    st.session_state.messages.append({"role": "assistant", "content": res.text})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if nome_aluno and turma_aluno:
    if prompt := st.chat_input("Digite sua resposta..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        historico = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
        resposta = model.generate_content(f"{instrucao}\n\nHistórico:\n{historico}")
        
        with st.chat_message("assistant"): st.markdown(resposta.text)
        st.session_state.messages.append({"role": "assistant", "content": resposta.text})
        
        if "RELATORIO_FINAL" in resposta.text and not st.session_state.enviado:
            enviar_para_planilha(nome_aluno, turma_aluno, resposta.text)
            st.session_state.enviado = True
            st.success("✅ Registrado na planilha!")
else:
    st.warning("👈 Preencha Nome e Turma ao lado.")

import streamlit as st
import google.generativeai as genai
import requests

# Função para a planilha
def enviar_para_planilha(nome, turma, relatorio):
    url = "https://docs.google.com/forms/d/e/1FAIpQLSf971GsVen1ehIuhMLQGdLjp7qTkM0GCcF7xik4AUdeoRM6AA/formResponse"
    dados = {"entry.2033090623": nome, "entry.449784386": turma, "entry.474665496": relatorio}
    try: requests.post(url, data=dados, timeout=5)
    except: pass

st.set_page_config(page_title="Missão BioTech")
st.title("🏗️ Desafio: Gestão de Projetos")

# Configuração da Chave
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("🚨 Configure a chave no Streamlit!")
    st.stop()

genai.configure(api_key=api_key)

# SIDEBAR PARA IDENTIFICAÇÃO
with st.sidebar:
    st.header("📋 Identificação")
    nome = st.text_input("Seu Nome:")
    turma = st.text_input("Sua Turma:")
    if st.button("Reiniciar"):
        st.session_state.clear()
        st.rerun()

# JOGO SÓ COMEÇA COM NOME E TURMA
if nome and turma:
    if "chat" not in st.session_state:
        # USANDO O MODELO MAIS COMPATÍVEL DE TODOS
        model = genai.GenerativeModel('gemini-1.5-flash')
        st.session_state.chat = model.start_chat(history=[])
        st.session_state.enviado = False
        
        # Mensagem inicial
        instrucao = f"Você é a Diretora da BioTech. O aluno {nome} é o Gerente. Peça ajuda com o projeto BioTech atrasado. No final de tudo, dê uma nota e escreva RELATORIO_FINAL."
        res = st.session_state.chat.send_message(instrucao)
        st.session_state.mensagens = [{"role": "assistant", "content": res.text}]

    # Mostrar histórico
    for m in st.session_state.mensagens:
        with st.chat_message(m["role"]): st.write(m["content"])

    # Entrada do aluno
    if prompt := st.chat_input("Sua resposta..."):
        st.session_state.mensagens.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        
        # Resposta da IA
        resposta = st.session_state.chat.send_message(prompt)
        st.session_state.mensagens.append({"role": "assistant", "content": resposta.text})
        with st.chat_message("assistant"): st.write(resposta.text)

        # Automação da Planilha
        if "RELATORIO_FINAL" in resposta.text and not st.session_state.enviado:
            enviar_para_planilha(nome, turma, resposta.text)
            st.session_state.enviado = True
            st.success("✅ Nota registrada na planilha!")
else:
    st.info("👈 Digite seu Nome e Turma ao lado para começar!")

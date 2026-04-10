import streamlit as st
import google.generativeai as genai
import requests

# Função para a planilha
def enviar_dados(n, t, r):
    url = "https://docs.google.com/forms/d/e/1FAIpQLSf971GsVen1ehIuhMLQGdLjp7qTkM0GCcF7xik4AUdeoRM6AA/formResponse"
    d = {"entry.2033090623": n, "entry.449784386": t, "entry.474665496": r}
    try: requests.post(url, data=d, timeout=5)
    except: pass

st.set_page_config(page_title="Missão BioTech", page_icon="🏗️")
st.title("🏗️ Desafio: Gestão de Projetos")

api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("🚨 Chave API não configurada.")
    st.stop()

genai.configure(api_key=api_key)

# TENTA ENCONTRAR UM MODELO QUE FUNCIONE (SISTEMA ANTI-404)
if "model_name" not in st.session_state:
    modelos_para_testar = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-1.0-pro']
    sucesso = False
    for m in modelos_para_testar:
        try:
            teste = genai.GenerativeModel(m)
            teste.generate_content("oi", generation_config={"max_output_tokens": 1})
            st.session_state.model_name = m
            sucesso = True
            break
        except:
            continue
    if not sucesso:
        st.error("🚨 O Google está instável hoje. Tente dar Reboot no Streamlit.")
        st.stop()

model = genai.GenerativeModel(st.session_state.model_name)

with st.sidebar:
    st.header("📋 Identificação")
    nome = st.text_input("Seu Nome:")
    turma = st.text_input("Sua Turma:")
    if st.button("Reiniciar Atividade"):
        st.session_state.chat = []
        st.rerun()

if "chat" not in st.session_state: st.session_state.chat = []

if nome and turma:
    if not st.session_state.chat:
        instrucao = f"Você é a Diretora da BioTech. O aluno {nome} é o Gerente. Peça ajuda com o projeto. No final escreva RELATORIO_FINAL."
        res = model.generate_content(instrucao)
        st.session_state.chat.append({"role": "assistant", "content": res.text})

    for m in st.session_state.chat:
        with st.chat_message(m["role"]): st.write(m["content"])

    if p := st.chat_input("Responda aqui..."):
        st.session_state.chat.append({"role": "user", "content": p})
        with st.chat_message("user"): st.write(p)
        res_ia = model.generate_content(f"Diretora BioTech. Aluno: {nome}. Fala: {p}")
        st.session_state.chat.append({"role": "assistant", "content": res_ia.text})
        with st.chat_message("assistant"): st.write(res_ia.text)
        
        if "RELATORIO_FINAL" in res_ia.text:
            enviar_dados(nome, turma, res_ia.text)
            st.success("✅ Nota enviada!")
else:
    st.info("👈 Digite Nome e Turma ao lado.")

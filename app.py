import streamlit as st
from google import genai
from google.genai import types
import requests

# --- CONFIGURAÇÃO AUTOMÁTICA DA PLANILHA ---
def enviar_para_planilha(nome, turma, relatorio):
    # Link de resposta do seu formulário específico
    url = "https://docs.google.com/forms/d/e/1FAIpQLSf971GsVen1ehIuhMLQGdLjp7qTkM0GCcF7xik4AUdeoRM6AA/formResponse"
    
    # IDs das suas perguntas que eu extraí do seu link
    dados = {
        "entry.2033090623": nome,
        "entry.449784386": turma,
        "entry.474665496": relatorio
    }
    try:
        requests.post(url, data=dados)
    except:
        pass

st.set_page_config(page_title="Missão: Gestão de Projetos", page_icon="🏗️")
st.title("🏗️ Desafio: Gestão de Projetos e Processos")
st.markdown("---")

api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("🚨 Chave API não encontrada! Verifique os Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

with st.sidebar:
    st.header("📋 Identificação")
    nome_aluno = st.text_input("Seu Nome Completo:")
    turma_aluno = st.text_input("Sua Turma/Grupo:")
    st.write("---")
    if st.button("Reiniciar Atividade"):
        st.session_state.messages = []
        st.session_state.enviado = False
        st.rerun()

instrucao_mestre = f"""
Você é a Diretora de Operações da BioTech. O aluno {nome_aluno} é o novo Gerente de Projetos.
CENÁRIO: O lançamento do 'Eco-Filtro' está atrasado e os custos subiram 30%.
MISSÃO: Guie o aluno por 3 fases (Diagnóstico, Planejamento e Solução). No final, dê uma NOTA de 0 a 10.
REGRA: Ao terminar a avaliação, escreva a palavra RELATORIO_FINAL.
"""

configuracao = types.GenerateContentConfig(system_instruction=instrucao_mestre)

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.enviado = False
    res = client.models.generate_content(model='gemini-1.5-flash', contents="Apresente-se e peça ajuda com o projeto.", config=configuracao)
    st.session_state.messages.append({"role": "assistant", "content": res.text})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if nome_aluno and turma_aluno:
    if prompt := st.chat_input("Digite sua resposta aqui..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        contexto = "\n\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
        resposta_ia = client.models.generate_content(model='gemini-1.5-flash', contents=contexto, config=configuracao)
        
        with st.chat_message("assistant"): st.markdown(resposta_ia.text)
        st.session_state.messages.append({"role": "assistant", "content": resposta_ia.text})
        
        # O MOMENTO DA AUTOMAÇÃO
        if "RELATORIO_FINAL" in resposta_ia.text and not st.session_state.get('enviado', False):
            enviar_para_planilha(nome_aluno, turma_aluno, resposta_ia.text)
            st.session_state.enviado = True
            st.success("✅ Seu desempenho foi registrado automaticamente na planilha do professor!")
else:
    st.warning("👈 Preencha Nome e Turma ao lado para começar.")

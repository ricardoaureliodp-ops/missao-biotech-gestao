import streamlit as st
import google.generativeai as genai
import requests

# --- FUNÇÃO PARA A PLANILHA ---
def enviar_planilha(n, t, r):
    url_form = "https://docs.google.com/forms/d/e/1FAIpQLSf971GsVen1ehIuhMLQGdLjp7qTkM0GCcF7xik4AUdeoRM6AA/formResponse"
    dados = {"entry.2033090623": n, "entry.449784386": t, "entry.474665496": r}
    try: requests.post(url_form, data=dados, timeout=5)
    except: pass

st.set_page_config(page_title="Missão BioTech", page_icon="🏗️")
st.title("🏗️ Desafio: Gestão de Projetos")
st.markdown("---")

# PUXA A CHAVE NOVA DOS SECRETS
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("🚨 Chave API não encontrada nos Secrets.")
    st.stop()

# CONFIGURA A BIBLIOTECA OFICIAL DO GOOGLE
genai.configure(api_key=api_key)

# A MUDANÇA SALVADORA: Usando o modelo 1.0 Pro que é universal e imune ao erro 404
model = genai.GenerativeModel('gemini-1.0-pro')

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
        st.session_state.enviado = False
        msg_inicial = f"Olá {nome}, sou a Diretora da BioTech. Nosso projeto está atrasado e 30% mais caro. Como gerente, qual sua primeira ação? (Ao final darei nota e direi RELATORIO_FINAL)"
        st.session_state.chat.append({"role": "assistant", "content": msg_inicial})

    for m in st.session_state.chat:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if p := st.chat_input("Digite sua resposta aqui..."):
        st.session_state.chat.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        
        try:
            # Chama a IA de forma oficial e segura
            contexto = f"Você é a Diretora da BioTech. O aluno {nome} respondeu: '{p}'. Continue o desafio de forma curta e direta. Se ele resolver, dê nota 0-10 e escreva RELATORIO_FINAL."
            resposta_ia = model.generate_content(contexto)
            
            st.session_state.chat.append({"role": "assistant", "content": resposta_ia.text})
            with st.chat_message("assistant"): st.markdown(resposta_ia.text)
            
            if "RELATORIO_FINAL" in resposta_ia.text and not st.session_state.enviado:
                enviar_planilha(nome, turma, resposta_ia.text)
                st.session_state.enviado = True
                st.success("✅ Nota registrada na planilha!")
        except Exception as e:
            st.error(f"Ocorreu um erro. Tente novamente. Detalhe: {e}")
else:
    st.info("👈 Preencha os dados ao lado para começar.")

import streamlit as st
import requests

# --- FUNÇÃO RAIZ PARA FALAR COM O GOOGLE (MODELO CLÁSSICO INFALÍVEL) ---
def chamar_gemini(prompt, api_key):
    # Mudamos para 'gemini-pro', o modelo universal que nunca dá 404
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Erro do Google: {response.status_code}. Detalhe: {response.text}"
    except Exception as e:
        return f"Erro de conexão com a internet. Detalhe: {e}"

# --- FUNÇÃO PARA A PLANILHA ---
def enviar_planilha(n, t, r):
    url_form = "https://docs.google.com/forms/d/e/1FAIpQLSf971GsVen1ehIuhMLQGdLjp7qTkM0GCcF7xik4AUdeoRM6AA/formResponse"
    dados = {"entry.2033090623": n, "entry.449784386": t, "entry.474665496": r}
    try: requests.post(url_form, data=dados, timeout=5)
    except: pass

st.set_page_config(page_title="Missão BioTech", page_icon="🏗️")
st.title("🏗️ Desafio: Gestão de Projetos")
st.markdown("---")

# PUXA A CHAVE DOS SECRETS
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("🚨 Chave API não encontrada nos Secrets.")
    st.stop()

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
        
        # Chama a IA usando a nossa função direta
        contexto = f"Você é a Diretora da BioTech. O aluno {nome} respondeu: '{p}'. Continue o desafio de forma curta e direta. Se ele resolver, dê nota 0-10 e escreva RELATORIO_FINAL."
        resposta_ia = chamar_gemini(contexto, api_key)
        
        st.session_state.chat.append({"role": "assistant", "content": resposta_ia})
        with st.chat_message("assistant"): st.markdown(resposta_ia)
        
        if "RELATORIO_FINAL" in resposta_ia and not st.session_state.enviado:
            enviar_planilha(nome, turma, resposta_ia)
            st.session_state.enviado = True
            st.success("✅ Nota registrada na planilha!")
else:
    st.info("👈 Preencha os dados ao lado para começar.")

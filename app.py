import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Missão: Gestão de Projetos", page_icon="🏗️")

# --- INTERFACE INICIAL ---
st.title("🏗️ Desafio: Gestão de Projetos e Processos")
st.markdown("---")

# Puxa a chave do cofre
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("🚨 Atenção: Chave API não encontrada! O professor precisa configurar o cofre (Secrets).")
    st.stop()

genai.configure(api_key=api_key)
# Usando o modelo Flash que agora está turbinado no seu cartão!
model = genai.GenerativeModel('gemini-1.5-flash')

# --- IDENTIFICAÇÃO DO ALUNO ---
with st.sidebar:
    st.header("📋 Identificação")
    nome_aluno = st.text_input("Seu Nome Completo:")
    turma_aluno = st.text_input("Sua Turma/Grupo:")
    st.write("---")
    if st.button("Reiniciar Atividade"):
        st.session_state.messages = []
        st.session_state.fase = 1
        st.rerun()

# --- LÓGICA DO JOGO ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.fase = 1
    
    # PROMPT MESTRE (O Cérebro da Atividade)
    instrucao_mestre = f"""
    Você é a Diretora de Operações da BioTech. O aluno {nome_aluno} é o novo Gerente de Projetos.
    CENÁRIO: O lançamento do novo 'Eco-Filtro' está atrasado, a equipe está brigando e os custos subiram 30%.
    
    SUA MISSÃO: Guiar o aluno por 3 fases:
    FASE 1 (Diagnóstico): Ele deve te fazer perguntas para entender o problema (gargalos, falta de processos). 
    Só passe para a Fase 2 quando ele identificar pelo menos 2 problemas reais.
    
    FASE 2 (Planejamento): Ele deve propor uma ferramenta (Ex: Kanban, 5W2H ou PDCA) para organizar o caos.
    
    FASE 3 (Relatório Final): Ele entrega a solução. Você avalia e dá uma NOTA de 0 a 10.
    
    REGRAS: 
    - Seja profissional e um pouco pressionada pelo tempo. 
    - No final da Fase 3, escreva exatamente a palavra 'RELATORIO_FINAL' e resuma o desempenho dele.
    """
    
    # Mensagem inicial da IA
    chat = model.start_chat(history=[])
    res = chat.send_message(instrucao_mestre + "\n\n Comece se apresentando e pedindo ajuda para o projeto.")
    st.session_state.messages.append({"role": "assistant", "content": res.text})

# Exibir mensagens
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

# Entrada do Aluno
if nome_aluno and turma_aluno:
    if prompt := st.chat_input("Digite sua resposta ou plano de ação aqui..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        # Envia para a IA
        chat = model.start_chat(history=[]) 
        contexto = "\n".join([m["content"] for m in st.session_state.messages])
        response = chat.send_message(contexto)
        
        with st.chat_message("assistant"): st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        
        # --- VERIFICAÇÃO DE CONCLUSÃO ---
        if "RELATORIO_FINAL" in response.text:
            st.success("🏁 Atividade Concluída! Copie a nota acima e cole no link do formulário que o professor enviou.")
else:
    st.warning("👈 Por favor, preencha seu Nome e Turma na barra lateral esquerda para começar a atividade.")

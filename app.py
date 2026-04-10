import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="Missão: Gestão de Projetos", page_icon="🏗️")

st.title("🏗️ Desafio: Gestão de Projetos e Processos")
st.markdown("---")

api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("🚨 Atenção: Chave API não encontrada! O professor precisa configurar o cofre (Secrets).")
    st.stop()

# Cliente da API
client = genai.Client(api_key=api_key)

with st.sidebar:
    st.header("📋 Identificação")
    nome_aluno = st.text_input("Seu Nome Completo:")
    turma_aluno = st.text_input("Sua Turma/Grupo:")
    st.write("---")
    if st.button("Reiniciar Atividade"):
        st.session_state.messages = []
        st.rerun()

# A Regra do Jogo
instrucao_mestre = f"""
Você é a Diretora de Operações da BioTech. O aluno {nome_aluno if nome_aluno else 'que está falando com você'} é o novo Gerente de Projetos.
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

# Configuração blindada para evitar erros no servidor
configuracao = types.GenerateContentConfig(
    system_instruction=instrucao_mestre,
)

if "messages" not in st.session_state:
    st.session_state.messages = []
    
    # Primeira mensagem da Diretora (Usando o motor 1.5 Flash)
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents="Comece a simulação se apresentando como Diretora da BioTech e pedindo ajuda para o projeto. Seja breve.",
        config=configuracao
    )
    st.session_state.messages.append({"role": "assistant", "content": response.text})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if nome_aluno and turma_aluno:
    if prompt := st.chat_input("Digite sua resposta ou plano de ação aqui..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        # Junta o histórico da conversa
        contexto = "\n\n".join([f"{'ALUNO' if m['role']=='user' else 'DIRETORA'}: {m['content']}" for m in st.session_state.messages])
        
        # Resposta da IA (Usando o motor 1.5 Flash)
        resposta_ia = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=contexto,
            config=configuracao
        )
        
        with st.chat_message("assistant"): st.markdown(resposta_ia.text)
        st.session_state.messages.append({"role": "assistant", "content": resposta_ia.text})
        
        if "RELATORIO_FINAL" in resposta_ia.text:
            st.success("🏁 Atividade Concluída! Copie a nota acima e cole no link do formulário que o professor enviou.")
else:
    st.warning("👈 Por favor, preencha seu Nome e Turma na barra lateral esquerda para começar a atividade.")

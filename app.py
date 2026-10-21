import os
from dotenv import load_dotenv
from groq import Groq
import streamlit as st

# ==============================================================================
# 1. CONFIGURAÇÃO E AMBIENTE (.env / GROQ)
# ==============================================================================
load_dotenv()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Inicializa o cliente Groq se a chave estiver presente
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# ==============================================================================
# 2. CONFIGURAÇÃO DA INTERFACE DO STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="Cockpit Virtual - Assistente de Voo",
    page_icon="✈️",
    layout="centered",
)

st.title("👨‍✈️ Cockpit Virtual - Assistente de Voo")
st.markdown(
    "Demonstração técnica de Agente de IA com **Memória de Curto Prazo**,"
    " integração **Groq** e persona de Comandante Sênior."
)

# Inicializa o histórico de mensagens na sessão para garantir a memória contínua
if "mensagens_historico" not in st.session_state:
  st.session_state.mensagens_historico = []

# Exibe o histórico de conversas na tela
for mensagem in st.session_state.mensagens_historico:
  with st.chat_message(mensagem["role"]):
    st.markdown(mensagem["content"])

# ==============================================================================
# 3. LÓGICA DE EXECUÇÃO E COMUNICAÇÃO COM A API
# ==============================================================================
prompt_usuario = st.chat_input(
    "Digite sua dúvida técnica ou altere a rota da conversa..."
)

if prompt_usuario:
  # Salva e exibe a mensagem do usuário
  st.session_state.mensagens_historico.append(
      {"role": "user", "content": prompt_usuario}
  )
  with st.chat_message("user"):
    st.markdown(prompt_usuario)

  # Processa a resposta do assistente
  with st.chat_message("assistant"):
    if not GROQ_API_KEY:
      resposta_erro = (
          "⚠️ **Atenção:** A `GROQ_API_KEY` não foi encontrada. Configure-a no"
          " arquivo `.env` ou nas variáveis de ambiente do Render."
      )
      st.error(resposta_erro)
      st.session_state.mensagens_historico.append(
          {"role": "assistant", "content": resposta_erro}
      )
    else:
      with st.spinner(
          "Estabelecendo comunicação de bordo... Processando dados..."
      ):
        try:
          # System Prompt incorporando a persona e regras de mudança de assunto
          system_prompt = {
              "role": "system",
              "content": (
                  "Você é um comandante e piloto de aviação comercial sênior"
                  " com mais de 15 anos de experiência em voos internacionais."
                  " Responda com precisão técnica, clareza didática, tom"
                  " calmo, confiante e profissional. Use termos técnicos da"
                  " aviação explicados de maneira acessível. Se o usuário mudar"
                  " bruscamente de tópico, reconheça e adapte a conversa"
                  " naturalmente (ex: 'Entendido, alterando nossa rota para"
                  " falar sobre...')."
              ),
          }

          # Monta o payload unindo o system prompt e o histórico do Streamlit
          payload_mensagens = [system_prompt] + [
              {"role": m["role"], "content": m["content"]}
              for m in st.session_state.mensagens_historico
          ]

          # Chamada à API da Groq
          chat_completion = client.chat.completions.create(
              model='openai/gpt-oss-120b',
              messages=payload_mensagens,
              temperature=0.7,
              max_tokens=1024,
          )

          resposta_ia = chat_completion.choices[0].message.content

          st.markdown(resposta_ia)
          st.session_state.mensagens_historico.append(
              {"role": "assistant", "content": resposta_ia}
          )

        except Exception as e:
          resposta_erro = f"❌ Erro de comunicação com a API Groq: {e}"
          st.error(resposta_erro)
          st.session_state.mensagens_historico.append(
              {"role": "assistant", "content": resposta_erro}
          )
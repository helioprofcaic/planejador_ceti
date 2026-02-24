import pandas as pd
import streamlit as st
import utils
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Menu", layout="wide")

# --- INICIALIZAÇÃO DE ESTADO (SESSION STATE) ---
# Garante que as configurações persistam entre as páginas
# Tenta carregar do arquivo primeiro para consistência
utils.garantir_perfil_visitante()
perfil_prof = utils.carregar_perfil_professor_db("Visitante")

if 'escola' not in st.session_state:
    st.session_state['escola'] = "CETI PROFESSOR RALDIR CAVALCANTE BASTOS"
if 'professor' not in st.session_state:
    st.session_state['professor'] = "Visitante"
if 'tema' not in st.session_state:
    st.session_state['tema'] = "Padrão"
if 'tamanho_fonte' not in st.session_state:
    st.session_state['tamanho_fonte'] = 14
if 'municipio' not in st.session_state:
    st.session_state['municipio'] = perfil_prof.get("municipio", "")

# --- BARRA LATERAL DE CONFIGURAÇÃO ---
with st.sidebar:
    st.header("⚙️ Configuração Central")
    st.session_state['escola'] = st.text_input("Escola", st.session_state['escola'])
    
    # Exibe os dados do perfil (Edição apenas na página de Configuração)
    st.markdown(f"**Professor(a):** {st.session_state['professor']}")
    st.markdown(f"**Município:** {st.session_state['municipio']}")
    
    st.info("Para alterar Professor ou Município, acesse a página **⚙️ Configuração**.")
    
    st.divider()
    st.header("🎨 Aparência Global")
    st.session_state['tema'] = st.selectbox(
        "Tema Visual", 
        ["Padrão", "Compacto", "Foco no Conteúdo"], 
        index=["Padrão", "Compacto", "Foco no Conteúdo"].index(st.session_state['tema'])
    )
    st.session_state['tamanho_fonte'] = st.slider(
        "Tamanho da Fonte (px)", 12, 24, st.session_state['tamanho_fonte']
    )

# --- APLICAÇÃO DO ESTILO ---
utils.aplicar_estilo()

# --- CONTEÚDO DA HOME ---
st.title("🏠 Menu Principal")

# --- STATUS DA CONEXÃO ---
st.divider()
if utils.USE_CLOUD_STORAGE:
    st.success("☁️ **Modo Nuvem Ativado:** Os dados estão sendo lidos e salvos no seu Google Drive.")
else:
    st.info("📂 **Modo Local Ativado:** Os dados estão sendo lidos e salvos na pasta `data/` do projeto.")
st.divider()

st.subheader(f"{st.session_state['escola']}")
st.caption(f"Bem-vindo(a), Prof. {st.session_state['professor']}")

st.markdown("""
### 🧭 Navegação Rápida
Clique em um dos links abaixo ou utilize o menu lateral para acessar os módulos:

- **[📅 Planejamento](Planejamento)**: Geração de planos de aula semanais, mensais e trimestrais.
- **[📊 Ficha Qualitativa](Ficha_Qualitativa)**: Registro de avaliação socioemocional.
- **[📝 Frequência](Frequencia)**: Controle de presença diária.
- **[📈 Dashboard](Dashboard)**: Visualização gráfica da assiduidade das turmas.
- **[🤖 Gerador de Aulas (IA)](Gerador_Aulas)**: Crie roteiros de aula completos com Inteligência Artificial.
- **[📚 Repositório de Aulas](Repositorio_Aulas)**: Gerencie e visualize os roteiros de aula salvos.
- **[⚙️ Configuração de Perfil](Configuracao)**: Personalização de turmas e disciplinas do professor.
- **[🛠️ Config. Componentes](Config_Componentes)**: Ajuste de regras de carga horária e currículo.
- **[☁️ Status da Nuvem](Status_Nuvem)**: Verifique a conexão com o Google Drive.
""")

st.info("As configurações definidas aqui (Escola, Professor, Tema) serão aplicadas automaticamente em todas as páginas.")

# --- HORÁRIO SEMANAL ---
st.divider()
st.subheader("📅 Grade Horária Semanal")

caminho_horario = os.path.join("data", "horario_professor.json")
df_horario = utils.carregar_dados_json(caminho_horario)

if df_horario is None:
    horario_data = [
        {"Horário": "07:20 - 08:20", "Período": "1ª Aula", "Segunda": "", "Terça": "", "Quarta": "", "Quinta": "", "Sexta": ""},
        {"Horário": "08:20 - 09:20", "Período": "2ª Aula", "Segunda": "", "Terça": "", "Quarta": "", "Quinta": "", "Sexta": ""},
        {"Horário": "09:20 - 09:40", "Período": "☕ Lanche", "Segunda": "---", "Terça": "---", "Quarta": "---", "Quinta": "---", "Sexta": "---"},
        {"Horário": "09:40 - 10:40", "Período": "3ª Aula", "Segunda": "", "Terça": "", "Quarta": "", "Quinta": "", "Sexta": ""},
        {"Horário": "10:40 - 11:40", "Período": "4ª Aula", "Segunda": "", "Terça": "", "Quarta": "", "Quinta": "", "Sexta": ""},
        {"Horário": "11:40 - 12:40", "Período": "🍽️ Almoço", "Segunda": "---", "Terça": "---", "Quarta": "---", "Quinta": "---", "Sexta": "---"},
        {"Horário": "12:40 - 13:40", "Período": "5ª Aula", "Segunda": "", "Terça": "", "Quarta": "", "Quinta": "", "Sexta": ""},
        {"Horário": "13:40 - 14:40", "Período": "6ª Aula", "Segunda": "", "Terça": "", "Quarta": "", "Quinta": "", "Sexta": ""},
        {"Horário": "14:40 - 14:50", "Período": "☕ Lanche", "Segunda": "---", "Terça": "---", "Quarta": "---", "Quinta": "---", "Sexta": "---"},
        {"Horário": "14:50 - 15:50", "Período": "7ª Aula", "Segunda": "", "Terça": "", "Quarta": "", "Quinta": "", "Sexta": ""},
        {"Horário": "15:50 - 16:50", "Período": "8ª Aula", "Segunda": "", "Terça": "", "Quarta": "", "Quinta": "", "Sexta": ""},
    ]
    df_horario = pd.DataFrame(horario_data)

def highlight_aulas(val):
    """Destaca células que não estão vazias e não são '---'."""
    if isinstance(val, str) and val.strip() and val.strip() != '---':
        return 'background-color: #60a5fa'  # Azul mais escuro
    return ''

# Calcula altura para remover barra de rolagem: (linhas + cabeçalho) * 35px
altura_tabela = (len(df_horario) + 1) * 33 + 3

st.dataframe(
    df_horario.style.apply(
        lambda x: x.map(highlight_aulas), 
        subset=['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']
    ),
    hide_index=True,
    width='stretch',
    height=altura_tabela
)

with st.expander("_            ✏️ Editar Horário"):
    df_editado = st.data_editor(
        df_horario, 
        hide_index=True, 
        width='stretch', 
        key="grade_horaria_editor",
        row_height=33
    )

    if st.button("💾 Salvar Alterações do Horário"):
        utils.salvar_dados_json(caminho_horario, df_editado)
        st.success("✅ Grade horária salva com sucesso!")
        st.rerun()
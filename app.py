import pandas as pd
import streamlit as st
import utils
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Menu", layout="wide")

# --- SELETOR DE FONTE DE DADOS ---
with st.sidebar:
    st.header("💾 Fonte de Dados")
    modo_atual = st.session_state.get('storage_mode', "Automático")
    opcoes = ["Automático", "Local (data/)", "Google Drive (Nuvem)", "Supabase (Banco)"]
    
    modo_selecionado = st.selectbox(
        "Carregar dados de:",
        opcoes,
        index=opcoes.index(modo_atual) if modo_atual in opcoes else 0,
        help="Se os dados não carregarem na Nuvem, force o modo 'Local' para usar os arquivos do repositório."
    )
    if modo_selecionado != modo_atual:
        st.session_state['storage_mode'] = modo_selecionado
        utils.configurar_modo_armazenamento()
        # Limpa o professor logado para forçar recarregamento do perfil da nova fonte
        if 'professor' in st.session_state: del st.session_state['professor']
        st.rerun()

# --- INICIALIZAÇÃO DE ESTADO (SESSION STATE) ---
# Mantém o estado da sessão entre atualizações de página
# Só executa se a sessão for nova (ex: F5, primeira visita)
if 'professor' not in st.session_state:
    # 1. Tenta carregar o último perfil de professor logado
    perfil = utils.carregar_perfil_professor()

    # 2. Se não houver perfil, usa o de "Visitante" como padrão
    if not perfil or not perfil.get("professor"):
        utils.garantir_perfil_visitante()
        # O perfil do visitante é um arquivo separado, então carregamos ele
        perfil = utils.carregar_perfil_professor_db("Visitante")

    # 3. Popula o st.session_state com os dados do perfil
    st.session_state['professor'] = perfil.get("professor", "Visitante")
    st.session_state['escola'] = perfil.get("escola", "CETI PROFESSOR RALDIR CAVALCANTE BASTOS")
    st.session_state['municipio'] = perfil.get("municipio", "")
    st.session_state['tema'] = perfil.get("tema", "Padrão")
    st.session_state['tamanho_fonte'] = perfil.get("tamanho_fonte", 14)

# --- BARRA LATERAL DE CONFIGURAÇÃO ---
with st.sidebar:
    st.header("⚙️ Configuração Central")
    st.session_state['escola'] = st.text_input("Escola", st.session_state['escola'])
    
    # --- LÓGICA DE LOGIN/LOGOUT ---
    if st.session_state.get("professor", "Visitante") == "Visitante":
        st.subheader("Login de Perfil")
        professores = ["Visitante"] + utils.listar_professores_db()
        professores = sorted(list(set(professores))) # Garante lista única e ordenada

        perfil_selecionado = st.selectbox("Selecione seu perfil", options=professores)
        senha = st.text_input("Senha", type="password", help="A senha de professor é definida pelo administrador.")

        if st.button("➡️ Entrar"):
            if perfil_selecionado == "Visitante":
                perfil = utils.carregar_perfil_professor_db("Visitante")
                utils.salvar_perfil_professor(perfil)
                st.session_state['professor'] = "Visitante"
                st.session_state['municipio'] = ""
                st.rerun()
            elif utils.verificar_senha(senha, tipo="professor"):
                perfil = utils.carregar_perfil_professor_db(perfil_selecionado)
                utils.salvar_perfil_professor(perfil) # Salva como último perfil logado
                # Atualiza a sessão com os dados do perfil
                st.session_state['professor'] = perfil.get("professor", "Visitante")
                st.session_state['municipio'] = perfil.get("municipio", "")
                st.session_state['tema'] = perfil.get("tema", "Padrão")
                st.session_state['tamanho_fonte'] = perfil.get("tamanho_fonte", 14)
                st.rerun()
            else:
                st.error("Senha incorreta. Tente novamente.")
    else:
        # Usuário já logado
        st.markdown(f"**Professor(a):** `{st.session_state['professor']}`")
        st.markdown(f"**Município:** `{st.session_state.get('municipio', '')}`")
        if st.button("⬅️ Sair (Logout)"):
            perfil_visitante = utils.carregar_perfil_professor_db("Visitante")
            utils.salvar_perfil_professor(perfil_visitante)
            st.session_state['professor'] = "Visitante"
            st.session_state['municipio'] = ""
            st.rerun()
    
    st.info("Para criar um novo perfil ou editar vínculos, acesse a página **⚙️ Configuração de Perfil**.")
    
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
elif utils.USE_SUPABASE:
    st.success("🛰️ **Modo Banco de Dados Ativado:** Os dados estão sendo lidos e salvos via Supabase.")
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
- **[🕒 Quadro de Horários](Quadro_Horario)**: Visualização da grade horária pessoal e global.
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

# Carrega o perfil específico do professor logado
professor_logado_nome = st.session_state.get('professor', 'Visitante')
perfil_logado = utils.carregar_perfil_professor_db(professor_logado_nome)

# Tenta carregar a grade horária do perfil
grade_data = perfil_logado.get("grade_horaria", None)

# Se a grade existir no perfil, converte para DataFrame. Senão, cria uma padrão.
if grade_data is not None:
    df_horario = pd.DataFrame(grade_data)
else:
    horario_data = [
        {"Horário": "07:20 - 08:20", "Período": "1ª Aula", "Segunda": "", "Terça": "", "Quarta": "", "Quinta": "", "Sexta": ""},
        {"Horário": "08:20 - 09:20", "Período": "2ª Aula", "Segunda": "", "Terça": "", "Quarta": "", "Quinta": "", "Sexta": ""},
        {"Horário": "09:20 - 09:40", "Período": "☕", "Segunda": "---", "Terça": "---", "Quarta": "---", "Quinta": "---", "Sexta": "---"},
        {"Horário": "09:40 - 10:40", "Período": "3ª Aula", "Segunda": "", "Terça": "", "Quarta": "", "Quinta": "", "Sexta": ""},
        {"Horário": "10:40 - 11:40", "Período": "4ª Aula", "Segunda": "", "Terça": "", "Quarta": "", "Quinta": "", "Sexta": ""},
        {"Horário": "11:40 - 12:40", "Período": "🍽️", "Segunda": "---", "Terça": "---", "Quarta": "---", "Quinta": "---", "Sexta": "---"},
        {"Horário": "12:40 - 13:40", "Período": "5ª Aula", "Segunda": "", "Terça": "", "Quarta": "", "Quinta": "", "Sexta": ""},
        {"Horário": "13:40 - 14:40", "Período": "6ª Aula", "Segunda": "", "Terça": "", "Quarta": "", "Quinta": "", "Sexta": ""},
        {"Horário": "14:40 - 14:50", "Período": "☕", "Segunda": "---", "Terça": "---", "Quarta": "---", "Quinta": "---", "Sexta": "---"},
        {"Horário": "14:50 - 15:50", "Período": "7ª Aula", "Segunda": "", "Terça": "", "Quarta": "", "Quinta": "", "Sexta": ""},
        {"Horário": "15:50 - 16:50", "Período": "8ª Aula", "Segunda": "", "Terça": "", "Quarta": "", "Quinta": "", "Sexta": ""},
    ]
    df_horario = pd.DataFrame(horario_data)

def highlight_aulas(val):
    """Destaca células que não estão vazias e não são '---'."""
    if isinstance(val, str) and val.strip() and val.strip() != '---':
        return 'background-color: #6495ed'  # Azul mais escuro #3381e2 #60a5fa #6495ed
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

with st.expander(" ✏️ Editar Horário"):
    df_editado = st.data_editor(
        df_horario, 
        hide_index=True, 
        width='stretch', 
        key="grade_horaria_editor",
        row_height=33
    )

    if st.button("💾 Salvar Alterações do Horário"):
        if professor_logado_nome != "Visitante":
            # Carrega o perfil completo para não sobrescrever outros dados
            perfil_completo = utils.carregar_perfil_professor_db(professor_logado_nome)

            # Atualiza a grade horária no dicionário do perfil
            perfil_completo['grade_horaria'] = df_editado.to_dict(orient='records')

            # Salva no arquivo específico do professor (data/perfis/perfil_...json)
            utils.salvar_professor_config_db(
                professor_logado_nome,
                perfil_completo.get('email', ''),
                perfil_completo.get('municipio', ''),
                perfil_completo
            )

            # Salva também no perfil ativo (data/professor_config.json)
            utils.salvar_perfil_professor(perfil_completo)

            st.success("✅ Grade horária salva com sucesso!")
            st.rerun()
        else:
            st.warning("Não é possível salvar o horário para o perfil 'Visitante'.")
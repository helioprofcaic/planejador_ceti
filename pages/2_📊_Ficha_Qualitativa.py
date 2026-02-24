import streamlit as st
import pandas as pd
import os
import utils

st.set_page_config(page_title="Ficha Qualitativa", layout="wide")

# --- CONFIGURAÇÕES GLOBAIS ---
utils.aplicar_estilo()

# --- DADOS ---
perfil_prof = utils.carregar_perfil_professor()

escola = st.session_state.get('escola', "CETI PROFESSOR RALDIR CAVALCANTE BASTOS")
professor = perfil_prof.get("professor", st.session_state.get('professor', "Helio Lima"))

# --- DADOS GLOBAIS ---
escola_db = utils.carregar_escola_db()
turmas_disponiveis = []
mapa_componentes = {}

# Tenta carregar as turmas do perfil do professor
if perfil_prof and "vinculos" in perfil_prof and perfil_prof["vinculos"]:
    for v in perfil_prof["vinculos"]:
        t = v["turma"]
        turmas_disponiveis.append(t)
        mapa_componentes[t] = v["componentes"]
# Se o perfil não tiver turmas, carrega todas as turmas e seus componentes
else:
    turmas_disponiveis = utils.listar_turmas_db()
    for t in turmas_disponiveis:
        mapa_componentes[t] = escola_db.get("turmas", {}).get(t, {}).get("componentes", [])

st.header("📊 Ficha de Acompanhamento Qualitativo")
st.info("Registre o desempenho socioemocional e técnico dos estudantes por projeto, aula ou período.")

# --- DIAGNÓSTICO DE ARQUIVOS ---
if not turmas_disponiveis:
    st.error("❌ Nenhuma turma encontrada.")
    with st.expander("🕵️ Diagnóstico de Arquivos"):
        if utils.USE_CLOUD_STORAGE:
            st.info("☁️ Modo Nuvem: Arquivos na pasta 'data':")
            try:
                st.write(utils.listar_arquivos_dados(""))
            except:
                st.error("Erro ao conectar no Drive.")
        else:
            st.info("💻 Modo Local: Arquivos em data/:")
            if os.path.exists("data"):
                st.write(os.listdir("data"))

# Seleção
turma_sel = st.selectbox("Selecione a Turma", turmas_disponiveis if turmas_disponiveis else ["Nenhuma turma encontrada"])

# Seleção de Contexto (Componente e Tipo)
comps_turma = mapa_componentes.get(turma_sel, [])
if not comps_turma: comps_turma = ["Geral"]

col_sel1, col_sel2 = st.columns(2)
with col_sel1:
    comp_sel = st.selectbox("Componente Curricular", comps_turma)
with col_sel2:
    contexto_sel = st.text_input("Contexto da Avaliação (Pode ser alterado)", value="1º Trimestre", placeholder="Ex: Projeto Robótica, Aula 15/03...", help="Você pode alterar este texto para criar avaliações específicas (ex: 'Projeto Robótica', 'Seminário').")

st.write(f"### Avaliação: {turma_sel} | {comp_sel}")

# Caminho do arquivo para persistência
safe_filename = f"{turma_sel}_{comp_sel}_{contexto_sel}".replace(" ", "_").replace("/", "-").replace("\\", "-")
caminho_arquivo = os.path.join("data", f"qualitativo_{safe_filename}.json")

# Tenta carregar dados salvos, senão cria um novo DataFrame
df_qualitativo = utils.carregar_dados_json(caminho_arquivo)

if df_qualitativo is None:
    lista_alunos = utils.listar_alunos_turma_db(turma_sel)
    df_qualitativo = pd.DataFrame({
        "Nº": range(1, len(lista_alunos) + 1),
        "Nome do Estudante": [aluno["nome"] for aluno in lista_alunos],
        "Participação": [""] * len(lista_alunos),
        "Entrega": [""] * len(lista_alunos),
        "Autonomia": [""] * len(lista_alunos),
        "NM1": [None] * len(lista_alunos),
        "NM2": [None] * len(lista_alunos),
        "NM3": [None] * len(lista_alunos),
        "MT": [None] * len(lista_alunos),
        "Recuperação": [None] * len(lista_alunos),
        "Nota Final": [None] * len(lista_alunos)
    })

# Configuração das colunas com Selectbox
column_config = {
    "Participação": st.column_config.SelectboxColumn(options=["Ótimo", "Bom", "Regular", "Insuficiente"], required=True),
    "Entrega": st.column_config.SelectboxColumn(options=["Em dia", "Atrasada", "Não entregou"], required=True),
    "Autonomia": st.column_config.SelectboxColumn(options=["Sim", "Não", "Em desenvolvimento"], required=True),
    "NM1": st.column_config.NumberColumn(min_value=0, max_value=10, step=0.1, format="%.1f"),
    "NM2": st.column_config.NumberColumn(min_value=0, max_value=10, step=0.1, format="%.1f"),
    "NM3": st.column_config.NumberColumn(min_value=0, max_value=10, step=0.1, format="%.1f"),
    "MT": st.column_config.NumberColumn(min_value=0, max_value=10, step=0.1, format="%.1f"),
    "Recuperação": st.column_config.NumberColumn(min_value=0, max_value=10, step=0.1, format="%.1f"),
    "Nota Final": st.column_config.NumberColumn(min_value=0, max_value=10, step=0.1, format="%.1f")
}

# Editor de dados
df_editado = st.data_editor(df_qualitativo, num_rows="dynamic", width='stretch', column_config=column_config)

st.divider()
c1, c2 = st.columns(2)

with c1:
    if st.button("💾 Salvar Registro Qualitativo"):
        if not df_editado.empty:
            utils.salvar_dados_json(caminho_arquivo, df_editado)
            st.success(f"Avaliação '{contexto_sel}' salva com sucesso!")
        else:
            st.warning("Não há dados para salvar.")

with c2:
    pdf_bytes = utils.gerar_pdf_qualitativo(escola, professor, turma_sel, df_editado, comp_sel, contexto_sel)
    st.download_button(
        label="🖨️ Baixar Ficha Qualitativa (PDF)",
        data=pdf_bytes,
        file_name=f"qualitativo_{safe_filename}.pdf",
        mime="application/pdf"
    )
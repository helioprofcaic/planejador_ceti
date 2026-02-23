import streamlit as st
import pandas as pd
from datetime import date
import os
import utils

st.set_page_config(page_title="Frequência", layout="wide")

# --- CONFIGURAÇÕES GLOBAIS ---
utils.aplicar_estilo()
# Recupera dados da sessão
escola = st.session_state.get('escola', "CETI PROFESSOR RALDIR CAVALCANTE BASTOS")
professor = st.session_state.get('professor', "Helio Lima")

st.header("📝 Lista de Frequência Diária")

# Carregar turmas para o selectbox
perfil_prof = utils.carregar_perfil_professor()
if perfil_prof:
    turmas = [v["turma"] for v in perfil_prof["vinculos"]]
else:
    turmas = utils.listar_turmas_db()

col1, col2 = st.columns(2)
with col1:
    turma_sel = st.selectbox("Turma", turmas if turmas else ["Turma A", "Turma B"])
with col2:
    data_aula = st.date_input("Data da Aula", date.today())

st.write("### Chamada")

# Caminho do arquivo para persistência
caminho_arquivo = os.path.join("data", f"frequencia_{turma_sel}_{data_aula.strftime('%Y-%m-%d')}.json")

# Tenta carregar dados salvos, senão cria um novo DataFrame
df_chamada = utils.carregar_dados_json(caminho_arquivo)

if df_chamada is None:
    lista_alunos = utils.listar_alunos_turma_db(turma_sel)
    if lista_alunos:
        df_chamada = pd.DataFrame({
            "Nº": [aluno["n"] for aluno in lista_alunos],
            "Nome do Aluno": [aluno["nome"] for aluno in lista_alunos],
            "Presença": [True] * len(lista_alunos)
        })
    else:
        df_chamada = pd.DataFrame(columns=["Nº", "Nome do Aluno", "Presença"])

df_editado = st.data_editor(df_chamada, width='stretch', height=600, key=f"editor_{turma_sel}_{data_aula}")

c1, c2, c3 = st.columns(3)

with c1:
    if st.button("💾 Salvar Frequência"):
        utils.salvar_dados_json(caminho_arquivo, df_editado)
        st.success(f"Frequência de {data_aula.strftime('%d/%m/%Y')} salva.")

with c2:
    pdf_bytes = utils.gerar_pdf_frequencia(escola, professor, turma_sel, data_aula, df_editado)
    st.download_button(
        label="🖨️ Baixar Lista de Presença (PDF)",
        data=pdf_bytes,
        file_name=f"frequencia_{turma_sel}_{data_aula}.pdf",
        mime="application/pdf"
    )

with c3:
    docx_bytes = utils.gerar_docx_frequencia(turma_sel, data_aula, df_editado)
    st.download_button(
        label="📄 Baixar Lista de Presença (DOCX)",
        data=docx_bytes,
        file_name=f"frequencia_{turma_sel}_{data_aula}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
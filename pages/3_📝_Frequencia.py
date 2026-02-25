import streamlit as st
import pandas as pd
from datetime import date
import os
import utils

st.set_page_config(page_title="Frequência", layout="wide")

# --- CONFIGURAÇÕES GLOBAIS ---
utils.aplicar_estilo()

# Carregar perfil do professor
perfil_prof = utils.carregar_perfil_professor()

# Recupera dados da sessão
escola = st.session_state.get('escola', "CETI PROFESSOR RALDIR CAVALCANTE BASTOS")
professor = perfil_prof.get("professor", st.session_state.get('professor', "Helio Lima"))

st.header("📝 Lista de Frequência Diária")

turmas = []
# Tenta carregar as turmas do perfil do professor
if perfil_prof and "vinculos" in perfil_prof and perfil_prof["vinculos"]:
    turmas = [v["turma"] for v in perfil_prof["vinculos"]]

# Se o perfil não tiver turmas, carrega todas as turmas do banco de dados
if not turmas:
    turmas = utils.listar_turmas_db()

# --- DIAGNÓSTICO DE ARQUIVOS (Se não houver turmas) ---
if not turmas:
    st.error("❌ Nenhuma turma encontrada. O sistema não conseguiu ler o arquivo de alunos.")
    
    with st.expander("🕵️ Diagnóstico de Arquivos (Clique aqui)"):
        st.write("O sistema está procurando o arquivo `alunos.json`.")
        st.write(f"**Modo Atual:** {'☁️ Nuvem (Google Drive)' if utils.USE_CLOUD_STORAGE else '💻 Local (Pasta data/)'}")
        
        if utils.USE_CLOUD_STORAGE:
            st.info("☁️ Modo Nuvem Ativo: Listando arquivos na pasta 'data' do Drive...")
            try:
                arquivos_drive = utils.listar_arquivos_dados("") 
                st.write("Arquivos encontrados:", arquivos_drive)
            except Exception as e:
                st.error(f"Erro ao listar Drive: {e}")
        else:
            st.info("💻 Modo Local Ativo: Verificando pasta data/...")
            if os.path.exists("data"):
                st.write("Arquivos locais:", os.listdir("data"))
            else:
                st.error("Pasta `data/` não existe.")

col1, col2 = st.columns(2)
with col1:
    turma_sel = st.selectbox("Turma", turmas if turmas else ["Nenhuma turma encontrada"])
with col2:
    data_aula = st.date_input("Data da Aula", date.today())

st.write("### Chamada")

# Tenta carregar dados salvos do arquivo acumulado do professor
df_total_prof = utils.carregar_frequencia_professor(professor)
df_chamada = pd.DataFrame()

if df_total_prof is not None and not df_total_prof.empty:
    # Filtra para o dia e turma selecionados
    data_str = data_aula.strftime('%Y-%m-%d')
    mask = (df_total_prof.get("Turma") == turma_sel) & (df_total_prof.get("Data") == data_str)
    if not df_total_prof[mask].empty:
        df_chamada = df_total_prof[mask][["Nº", "Nome do Aluno", "Presença"]]

if df_chamada is None or df_chamada.empty:
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
        utils.salvar_frequencia_dia(professor, turma_sel, data_aula, df_editado)
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
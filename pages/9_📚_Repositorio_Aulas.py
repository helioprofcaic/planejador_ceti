import streamlit as st
import os
import utils

st.set_page_config(page_title="Repositório de Aulas", layout="wide")
utils.aplicar_estilo()

st.title("📚 Repositório de Planos de Aula")
st.markdown("Gerencie e visualize os roteiros de aula salvos no sistema.")

# --- FUNÇÃO DE FORMATAÇÃO ---
def formatar_nome_aula(filename):
    """Formata o nome de um arquivo de aula para uma exibição mais amigável."""
    try:
        # Limpa o nome do arquivo para ser o título da aula
        nome_formatado = filename.replace(".md", "")
        if nome_formatado.startswith("Plano_Aula_"):
            nome_formatado = nome_formatado.replace("Plano_Aula_", "", 1)

        # Substituições para legibilidade
        nome_formatado = nome_formatado.replace("__", ": ").replace("_-_", " - ").replace("_", " ")

        return nome_formatado
    except Exception:
        return filename  # Fallback para o nome original em caso de erro

# --- BARRA LATERAL: NAVEGAÇÃO ---
pasta_aulas = os.path.join("data", "aulas")
arquivo_selecionado = None

with st.sidebar:
    st.header("🗂️ Navegar no Repositório")
    
    if not os.path.exists(pasta_aulas):
        os.makedirs(pasta_aulas, exist_ok=True)
        st.warning("Pasta 'data/aulas' não encontrada. Ela foi criada agora.")
        st.info("Crie subpastas para Turmas e Disciplinas para organizar seus planos.")
        st.stop()

    # 1. Selecionar Turma
    try:
        turmas = sorted([d for d in os.listdir(pasta_aulas) if os.path.isdir(os.path.join(pasta_aulas, d))])
    except FileNotFoundError:
        turmas = []

    if not turmas:
        st.warning("Nenhuma pasta de turma encontrada em 'data/aulas'.")
        st.stop()

    turma_selecionada = st.selectbox("Selecione a Turma:", ["Selecione..."] + turmas)

    # 2. Selecionar Disciplina
    disciplinas = []
    if turma_selecionada and turma_selecionada != "Selecione...":
        caminho_turma = os.path.join(pasta_aulas, turma_selecionada)
        try:
            disciplinas = sorted([d for d in os.listdir(caminho_turma) if os.path.isdir(os.path.join(caminho_turma, d))])
        except FileNotFoundError:
            disciplinas = []
    
    disciplina_selecionada = st.selectbox("Selecione a Disciplina:", ["Selecione..."] + disciplinas, disabled=(not disciplinas))

    # 3. Listar Aulas
    if disciplina_selecionada and disciplina_selecionada != "Selecione...":
        caminho_disciplina = os.path.join(pasta_aulas, turma_selecionada, disciplina_selecionada)
        try:
            aulas_arquivos = sorted([f for f in os.listdir(caminho_disciplina) if f.endswith(".md")])
            
            if aulas_arquivos:
                # O radio retorna o nome do arquivo, não o nome formatado
                aula_escolhida = st.radio(
                    "Selecione uma aula:",
                    aulas_arquivos,
                    format_func=formatar_nome_aula
                )
                
                # Reconstroi o caminho relativo para o resto do script
                if aula_escolhida:
                    arquivo_selecionado = os.path.join(turma_selecionada, disciplina_selecionada, aula_escolhida)
            else:
                st.info("Nenhum plano de aula (.md) encontrado nesta disciplina.")

        except FileNotFoundError:
            st.error("Pasta da disciplina não encontrada.")

# --- ÁREA PRINCIPAL ---
if arquivo_selecionado:
    caminho_completo = os.path.join(pasta_aulas, arquivo_selecionado)
    
    with open(caminho_completo, "r", encoding="utf-8") as f:
        conteudo_atual = f.read()
    
    # Abas para Visualização e Edição
    tab1, tab2 = st.tabs(["👁️ Visualizar", "✏️ Editar"])
    
    with tab1:
        st.markdown(conteudo_atual)
        
        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            # Botão para baixar PDF (usando a função existente no utils)
            pdf_bytes = utils.gerar_pdf_aula_ia(conteudo_atual)
            st.download_button(
                label="📄 Baixar PDF",
                data=pdf_bytes,
                file_name=os.path.basename(arquivo_selecionado).replace(".md", ".pdf"),
                mime="application/pdf"
            )
            
    with tab2:
        novo_conteudo = st.text_area("Editor Markdown", value=conteudo_atual, height=600)
        
        if st.button("💾 Salvar Alterações"):
            with open(caminho_completo, "w", encoding="utf-8") as f:
                f.write(novo_conteudo)
            st.success("Arquivo atualizado com sucesso!")
            st.rerun()

else:
    st.info("👈 Selecione uma turma e disciplina no menu lateral para listar e visualizar as aulas.")
    
    # Estatísticas
    st.divider()
    # Recalcular total de arquivos para estatísticas
    total_arquivos = 0
    if os.path.exists(pasta_aulas):
        for root, dirs, files in os.walk(pasta_aulas):
            for file in files:
                if file.endswith(".md"):
                    total_arquivos += 1
    
    st.metric("Total de Aulas no Repositório", total_arquivos)

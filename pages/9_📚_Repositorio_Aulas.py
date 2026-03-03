import streamlit as st
import os
import utils

st.set_page_config(page_title="Repositório de Aulas", layout="wide")
utils.aplicar_estilo()

st.title("📚 Repositório de Planos de Aula")
st.markdown("Gerencie e visualize os roteiros de aula salvos no sistema.")

# --- FUNÇÃO DE FORMATAÇÃO ---
def formatar_nome_aula(filepath):
    """Formata o caminho de um arquivo de aula para uma exibição mais amigável."""
    try:
        # Normaliza as barras para o SO atual e divide o caminho
        filepath = os.path.normpath(filepath)
        parts = filepath.split(os.sep)

        # Limpa o nome do arquivo para ser o título da aula
        filename = parts[-1]
        filename = filename.replace(".md", "")
        if filename.startswith("Plano_Aula_"):
            filename = filename.replace("Plano_Aula_", "", 1)

        # Substituições para legibilidade
        filename = filename.replace("__", ": ").replace("_-_", " - ").replace("_", " ")

        # Monta a string final com a estrutura de pastas (Turma/Componente)
        if len(parts) > 1:
            caminho_formatado = " | ".join(parts[:-1])
            return f"[{caminho_formatado}] {filename}"
        return filename
    except Exception:
        return filepath  # Fallback para o caminho original em caso de erro

# --- BARRA LATERAL: LISTAGEM ---
pasta_aulas = os.path.join("data", "aulas")
if not os.path.exists(pasta_aulas):
    os.makedirs(pasta_aulas, exist_ok=True)

arquivos = []
for root, dirs, files in os.walk(pasta_aulas):
    for file in files:
        if file.endswith(".md"):
            arquivos.append(os.path.relpath(os.path.join(root, file), pasta_aulas))
arquivos.sort()

with st.sidebar:
    st.header("🗂️ Arquivos Disponíveis")
    if not arquivos:
        st.warning("Nenhum plano de aula encontrado.")
        st.info("Execute o script `gerar_aulas_iniciais.py` para criar os modelos iniciais.")
    
    # Filtros
    filtro_turma = st.text_input("Filtrar por Turma/Ano", placeholder="Ex: 2ano")
    
    arquivos_filtrados = [f for f in arquivos if filtro_turma.lower() in f.lower()]
    
    arquivo_selecionado = st.radio(
        "Selecione uma aula:",
        arquivos_filtrados,
        format_func=formatar_nome_aula
    )

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
    st.info("👈 Selecione um plano de aula no menu lateral para visualizar.")
    
    # Estatísticas
    st.divider()
    col1, col2 = st.columns(2)
    col1.metric("Total de Aulas", len(arquivos))
    col2.metric("Disciplinas Identificadas", len(set([os.path.basename(f).split('_')[1] for f in arquivos if '_' in os.path.basename(f)])))

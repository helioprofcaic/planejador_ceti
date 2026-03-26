import streamlit as st
import os
import utils
import random

st.set_page_config(page_title="Repositório de Aulas", layout="wide")
utils.aplicar_estilo() # Isso sincroniza o modo de armazenamento

# --- Integração com Supabase (Abaixo do aplicar_estilo) ---
if utils.USE_SUPABASE:
    from tools import database as db

st.title("📚 Repositório de Aulas")
st.markdown("Gerencie e visualize os roteiros de aula salvos no sistema.")

# --- INICIALIZAÇÃO DE ESTADO ---
if 'simulado_gerado' not in st.session_state:
    st.session_state.simulado_gerado = None

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

# Variáveis para armazenar a seleção, seja de arquivo ou de objeto do DB
arquivo_selecionado_path = None
aula_selecionada_obj = None

with st.sidebar:
    st.header("🗂️ Navegar no Repositório")
    
    if utils.USE_SUPABASE:
        # Se um simulado estiver ativo, mostra apenas a opção de voltar
        if st.session_state.get('simulado_gerado'):
            st.info("Visualizando um simulado.")
            if st.button("⬅️ Voltar para Aulas"):
                st.session_state.simulado_gerado = None
                st.rerun()
        else:
            # --- MODO SUPABASE (Navegação Padrão) ---
            st.info("🛰️ Conectado ao Banco de Dados.")
            # 1. Selecionar Turma
            turmas_obj = db.get_classes()
            if not turmas_obj:
                st.warning("Nenhuma turma encontrada no banco de dados.")
                st.stop()
            
            turmas_nomes = [t['name'] for t in turmas_obj]
            turma_selecionada_nome = st.selectbox("Selecione a Turma:", ["Selecione..."] + turmas_nomes)

            # 2. Selecionar Disciplina
            disciplinas_obj = []
            if turma_selecionada_nome != "Selecione...":
                turma_id = next((t['id'] for t in turmas_obj if t['name'] == turma_selecionada_nome), None)
                if turma_id:
                    disciplinas_obj = db.get_subjects_for_class(turma_id)
            
            disciplinas_nomes = [d['name'] for d in disciplinas_obj]
            disciplina_selecionada_nome = st.selectbox("Selecione a Disciplina:", ["Selecione..."] + disciplinas_nomes, disabled=(not disciplinas_obj))

            # --- NOVA FUNCIONALIDADE: GERADOR DE SIMULADO ---
            if disciplina_selecionada_nome != "Selecione...":
                disciplina_id = next((d['id'] for d in disciplinas_obj if d['name'] == disciplina_selecionada_nome), None)
                if disciplina_id:
                    if st.button("🎲 Gerar Simulado da Disciplina"):
                        with st.spinner("Buscando questões no banco de dados..."):
                            todas_questoes = db.get_all_quiz_questions_for_subject(disciplina_id)
                            if len(todas_questoes) > 0:
                                num_questoes = min(10, len(todas_questoes))
                                questoes_selecionadas = random.sample(todas_questoes, num_questoes)
                                
                                st.session_state['simulado_gerado'] = {
                                    "questoes": questoes_selecionadas,
                                    "disciplina": disciplina_selecionada_nome,
                                    "turma": turma_selecionada_nome
                                }
                                st.rerun()
                            else:
                                st.warning("Nenhuma questão de quiz encontrada para esta disciplina.")

            # 3. Listar Aulas
            aulas_obj = []
            if disciplina_selecionada_nome != "Selecione...":
                disciplina_id = next((d['id'] for d in disciplinas_obj if d['name'] == disciplina_selecionada_nome), None)
                if disciplina_id:
                    aulas_obj = db.get_lessons_for_subject(disciplina_id)

            if aulas_obj:
                aulas_map = {aula['title']: aula for aula in aulas_obj}
                aula_escolhida_titulo = st.radio(
                    "Selecione uma aula:",
                    list(aulas_map.keys()),
                    format_func=formatar_nome_aula
                )
                aula_selecionada_obj = aulas_map.get(aula_escolhida_titulo)
            else:
                if disciplina_selecionada_nome != "Selecione...":
                    st.info("Nenhuma aula encontrada para esta disciplina.")
            
            st.divider()
            with st.expander("🛠️ Ferramentas de Sincronização"):
                st.caption("Use para sincronizar o ambiente local com o banco de dados.")

                if st.button("Sincronizar Pastas (DB -> Local)"):
                    with st.spinner("Lendo a estrutura do banco de dados e criando pastas locais..."):
                        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
                        turmas_path = os.path.join(project_root, 'data', 'Turmas')
                        logs = db.sync_local_folders_from_db(turmas_path)
                        st.session_state['sync_logs'] = logs
                
                if 'sync_logs' in st.session_state and st.session_state['sync_logs']:
                    st.code(st.session_state['sync_logs'], language='text')

                if st.button("Importar Aulas (Local -> DB)"):
                    with st.spinner("Lendo arquivos .md locais e importando para o banco de dados..."):
                        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
                        turmas_path = os.path.join(project_root, 'data', 'Turmas')
                        logs = db.import_lessons_from_files(turmas_path)
                        st.session_state['import_logs'] = logs
                
                if 'import_logs' in st.session_state and st.session_state['import_logs']:
                    st.code(st.session_state['import_logs'], language='text')

    else:
        # --- MODO ARQUIVO (LOCAL/DRIVE) ---
        # Garante que a pasta base exista (para modo local)
        if not utils.USE_CLOUD_STORAGE and not os.path.exists(pasta_aulas):
            try:
                os.makedirs(pasta_aulas, exist_ok=True)
                st.warning("Pasta 'data/aulas' não encontrada. Ela foi criada agora.")
                st.info("Crie subpastas para Turmas e Disciplinas para organizar seus planos.")
            except OSError:
                st.error("Não foi possível criar a pasta 'data/aulas'. Verifique as permissões.")
            st.stop()

        # 1. Selecionar Turma
        turmas = utils.listar_subpastas(['data', 'aulas'])

        if not turmas:
            st.warning("Nenhuma pasta de turma encontrada em `data/aulas`.")
            st.info("Para organizar, crie uma pasta para cada turma dentro de `data/aulas` (Ex: `3Ano_A_DS`).")
            st.stop()

        turma_selecionada = st.selectbox("Selecione a Turma:", ["Selecione..."] + turmas)

        # 2. Selecionar Disciplina
        disciplinas = []
        if turma_selecionada and turma_selecionada != "Selecione...":
            disciplinas = utils.listar_subpastas(['data', 'aulas', turma_selecionada])
        
        disciplina_selecionada = st.selectbox("Selecione a Disciplina:", ["Selecione..."] + disciplinas, disabled=(not disciplinas))

        # 3. Listar Aulas
        if disciplina_selecionada and disciplina_selecionada != "Selecione...":
            aulas_arquivos = utils.listar_arquivos_md(['data', 'aulas', turma_selecionada, disciplina_selecionada])
            
            if aulas_arquivos:
                aula_escolhida = st.radio(
                    "Selecione uma aula:",
                    aulas_arquivos,
                    format_func=formatar_nome_aula
                )
                if aula_escolhida:
                    arquivo_selecionado_path = os.path.join("data", "aulas", turma_selecionada, disciplina_selecionada, aula_escolhida)
            else:
                st.info("Nenhum plano de aula (.md) encontrado nesta disciplina.")

# --- ÁREA PRINCIPAL ---

# Define qual conteúdo e qual ID/path usar
conteudo_atual = None
is_db_mode = utils.USE_SUPABASE and aula_selecionada_obj is not None
is_file_mode = not utils.USE_SUPABASE and arquivo_selecionado_path is not None
simulado_gerado = st.session_state.get('simulado_gerado')

if simulado_gerado:
    st.subheader(f"🎲 Simulado: {simulado_gerado['disciplina']}")
    st.caption(f"Turma: {simulado_gerado['turma']} | Número de Questões: {len(simulado_gerado['questoes'])}")

    with st.container(border=True):
        for i, q in enumerate(simulado_gerado['questoes'], 1):
            st.markdown(f"**{i}. {q['question_text']}**")
            opcoes = q.get('options', [])
            # Apenas exibe as opções, sem input
            for j, opt in enumerate(opcoes):
                letra = chr(ord('a') + j)
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{letra}) {opt}")
            if i < len(simulado_gerado['questoes']):
                st.markdown("---")

    st.divider()
    
    # Botão para baixar PDF
    perfil = utils.carregar_perfil_professor()
    professor_nome = perfil.get("professor", "Professor")
    
    pdf_bytes = utils.gerar_pdf_simulado(
        disciplina_nome=simulado_gerado['disciplina'],
        turma_nome=simulado_gerado['turma'],
        professor_nome=professor_nome,
        questoes=simulado_gerado['questoes']
    )
    
    st.download_button(
        label="🖨️ Baixar Simulado em PDF",
        data=pdf_bytes,
        file_name=f"simulado_{simulado_gerado['disciplina'].replace(' ', '_')}.pdf",
        mime="application/pdf"
    )

elif is_db_mode:
    conteudo_atual = aula_selecionada_obj.get('description', '# Erro\n\nConteúdo da aula não encontrado no banco de dados.')
elif is_file_mode:
    conteudo_atual = utils.carregar_arquivo_texto(arquivo_selecionado_path)

if conteudo_atual:
    
    # Abas para Visualização e Edição
    tab1, tab2 = st.tabs(["👁️ Visualizar", "✏️ Editar"])
    
    with tab1:
        st.markdown(conteudo_atual)
        
        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            # Botão para baixar PDF (usando a função existente no utils)
            pdf_bytes = utils.gerar_pdf_aula_ia(conteudo_atual)
            
            # Define o nome do arquivo com base no modo
            file_name_base = ""
            if is_db_mode:
                file_name_base = aula_selecionada_obj.get('title', 'aula_sem_titulo')
            elif is_file_mode:
                file_name_base = os.path.basename(arquivo_selecionado_path)

            st.download_button(
                label="📄 Baixar como PDF",
                data=pdf_bytes,
                file_name=file_name_base.replace(".md", ".pdf"),
                mime="application/pdf"
            )
            
    with tab2:
        key = f"editor_{aula_selecionada_obj['id']}" if is_db_mode else f"editor_{arquivo_selecionado_path}"
        novo_conteudo = st.text_area("Editor Markdown", value=conteudo_atual, height=600, key=key)
        
        if st.button("💾 Salvar Alterações"):
            if is_db_mode:
                _, error = db.update_lesson_content(aula_selecionada_obj['id'], novo_conteudo)
                if not error:
                    st.success("Aula atualizada com sucesso no banco de dados!")
                    st.rerun()
                else:
                    st.error(f"Falha ao salvar no banco de dados: {error}")
            else:
                if utils.salvar_arquivo_texto(arquivo_selecionado_path, novo_conteudo):
                    st.success("Arquivo atualizado com sucesso!")
                    st.rerun()
                else:
                    st.error("Falha ao salvar o arquivo.")

else:
    st.info("👈 Selecione uma turma e disciplina no menu lateral para listar e visualizar as aulas.")
    
    # Estatísticas
    st.divider()
    # Recalcular total de arquivos para estatísticas
    total_arquivos = 0
    if utils.USE_SUPABASE:
        # TODO: Implementar contagem de aulas no Supabase se necessário
        pass
    elif not utils.USE_CLOUD_STORAGE: # Modo Local
        if os.path.exists(pasta_aulas):
            for root, dirs, files in os.walk(pasta_aulas):
                for file in files:
                    if file.endswith(".md"):
                        total_arquivos += 1
    
    # Exibe a métrica apenas se for relevante
    if total_arquivos > 0 or not utils.USE_CLOUD_STORAGE and not utils.USE_SUPABASE:
        st.metric("Total de Aulas no Repositório (Modo Local)", total_arquivos)

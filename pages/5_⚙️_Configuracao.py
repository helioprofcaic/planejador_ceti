import streamlit as st
import pandas as pd
import utils

st.set_page_config(page_title="Configuração", layout="wide")

# --- CONFIGURAÇÕES GLOBAIS ---
utils.aplicar_estilo()

st.title("⚙️ Configuração do Sistema")

# Definição das abas para organizar as funcionalidades
tab_perfil, tab_alunos = st.tabs(["👤 Perfil e Vínculos", "👥 Gerenciar Alunos"])

with tab_perfil:
    st.header("Configuração de Perfil")
    st.info("Utilize esta aba para configurar seus dados pessoais e vínculos com disciplinas.")
    # A lógica de perfil (como a que existe no sidebar do app.py) pode ser expandida aqui

with tab_alunos:
    st.header("Gerenciamento de Alunos por Turma")
    st.markdown("Nesta aba você pode adicionar novos alunos ou remover alunos existentes de cada turma.")

    # Carrega o banco de dados de alunos (alunos.json)
    alunos_db = utils.carregar_alunos()
    
    # Verifica permissão: Visitantes são bloqueados por padrão na função carregar_alunos do utils
    if st.session_state.get("professor") == "Visitante":
        st.warning("⚠️ O perfil 'Visitante' não possui permissão para alterar a lista de alunos.")
    else:
        if not alunos_db:
            st.info("Nenhuma turma com alunos encontrada no sistema.")
            nova_turma_nome = st.text_input("Nome da nova turma (ex: 1º Ano A)")
            if st.button("➕ Criar Turma"):
                if nova_turma_nome:
                    alunos_db[nova_turma_nome] = []
                    utils.salvar_alunos(alunos_db)
                    st.success(f"Turma '{nova_turma_nome}' criada com sucesso!")
                    st.rerun()
        else:
            # Seleção da Turma para edição
            turmas_disponiveis = sorted(list(alunos_db.keys()))
            turma_selecionada = st.selectbox("Selecione a Turma para gerenciar", turmas_disponiveis)
            
            lista_alunos = alunos_db.get(turma_selecionada, [])
            
            # Layout em duas colunas para facilitar a visualização e ação
            col_lista, col_acoes = st.columns([2, 1])
            
            with col_lista:
                st.subheader(f"Lista de Alunos: {turma_selecionada}")
                if lista_alunos:
                    # Exibe os alunos em um DataFrame para conferência
                    df_alunos = pd.DataFrame(lista_alunos)
                    df_alunos.index = range(1, len(df_alunos) + 1)
                    st.dataframe(df_alunos, use_container_width=True)
                else:
                    st.info("Esta turma ainda não possui alunos cadastrados.")
            
            with col_acoes:
                st.subheader("Ações")
                
                # --- SEÇÃO ADICIONAR ALUNO ---
                with st.expander("➕ Adicionar Aluno", expanded=True):
                    novo_nome = st.text_input("Nome Completo do Estudante")
                    if st.button("Confirmar Adição", use_container_width=True):
                        if novo_nome.strip():
                            # Evita duplicatas na mesma turma
                            if any(a['nome'].lower() == novo_nome.strip().lower() for a in lista_alunos):
                                st.error("Este aluno já está cadastrado nesta turma.")
                            else:
                                lista_alunos.append({"nome": novo_nome.strip()})
                                # Ordena a lista alfabeticamente para manter o padrão
                                lista_alunos = sorted(lista_alunos, key=lambda x: x['nome'])
                                alunos_db[turma_selecionada] = lista_alunos
                                if utils.salvar_alunos(alunos_db):
                                    st.success(f"Aluno {novo_nome} adicionado!")
                                    st.rerun()
                        else:
                            st.error("O nome não pode estar vazio.")
                
                # --- SEÇÃO REMOVER ALUNO ---
                if lista_alunos:
                    with st.expander("🗑️ Remover Aluno"):
                        aluno_para_remover = st.selectbox("Selecione o aluno para excluir", [a['nome'] for a in lista_alunos])
                        if st.button("🗑️ Confirmar Remoção", type="secondary", use_container_width=True):
                            lista_alunos = [a for a in lista_alunos if a['nome'] != aluno_para_remover]
                            alunos_db[turma_selecionada] = lista_alunos
                            if utils.salvar_alunos(alunos_db):
                                st.warning(f"Aluno {aluno_para_remover} removido da turma.")
                                st.rerun()

utils.criar_botao_voltar()
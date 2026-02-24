import streamlit as st
import json
import os
import utils

st.set_page_config(page_title="Configuração do Perfil", layout="wide")

# --- ESTILO ---
utils.aplicar_estilo()

st.header("⚙️ Configuração de Perfil Docente")
st.info("Selecione suas turmas e componentes para personalizar seu planejamento e diário.")

# Carregar dados globais do Novo Banco de Dados
escola_db = utils.carregar_escola_db()
turmas_db = escola_db.get("turmas", {})

# Definir a lista oficial de turmas
todas_turmas = list(turmas_db.keys())

# --- SELEÇÃO DE PERFIL ---
professores_db = utils.listar_professores_db()
opcoes_perfis = ["Visitante", "➕ Novo Perfil"] + [p for p in professores_db if p != "Visitante"]

# Identifica perfil ativo atual (do JSON local) para pré-selecionar
perfil_ativo_local = utils.carregar_perfil_professor()
nome_ativo_local = perfil_ativo_local.get("professor", "")

index_sel = 0
if nome_ativo_local in professores_db:
    index_sel = professores_db.index(nome_ativo_local) + 1

perfil_selecionado = st.selectbox("Selecione o Perfil para Editar", opcoes_perfis, index=index_sel)

# --- PROTEÇÃO POR SENHA ---
if perfil_selecionado != "Visitante":
    st.info("🔒 Este perfil é protegido.")
    senha_input = st.text_input("Digite a senha de administrador para acessar/trocar:", type="password")
    
    if senha_input != utils.SENHA_ADMIN:
        st.warning("Senha incorreta ou não informada. Acesso restrito.")
        st.stop()

if perfil_selecionado == "➕ Novo Perfil":
    config_atual = {}
    nome_atual = ""
    email_atual = ""
    municipio_atual = ""
    vinculos_atuais = []
else:
    config_atual = utils.carregar_perfil_professor_db(perfil_selecionado)
    nome_atual = config_atual.get("professor", perfil_selecionado)
    email_atual = config_atual.get("email", "")
    municipio_atual = config_atual.get("municipio", "")
    vinculos_atuais = config_atual.get("vinculos", [])

# --- FORMULÁRIO DE PERFIL ---
nome = st.text_input("Seu Nome Completo (Como sairá no Plano)", value=nome_atual, key=f"nome_{perfil_selecionado}")
email = st.text_input("E-mail Institucional", value=email_atual, key=f"email_{perfil_selecionado}")
municipio = st.text_input("Município", value=municipio_atual, key=f"mun_{perfil_selecionado}")

st.write("---")
st.subheader("Minha Carga Horária")

# Pré-selecionar turmas se já houver configuração
turmas_pre_sel = [v["turma"] for v in vinculos_atuais if v["turma"] in todas_turmas]

# Seleção múltipla de turmas
turmas_selecionadas = st.multiselect("Quais turmas você leciona?", todas_turmas, default=turmas_pre_sel, key=f"turmas_{perfil_selecionado}")

config_vínculos = []

for turma in turmas_selecionadas:
    st.write(f"**Componentes para {turma}:**")
    # Busca os componentes disponíveis no catálogo geral
    opcoes_comp = turmas_db.get(turma, {}).get("componentes", [])
    
    if not opcoes_comp:
        opcoes_comp = ["INTELIGÊNCIA ARTIFICIAL", "PROGRAMAÇÃO", "COMPUTAÇÃO", "OUTRO"]
    
    # Tentar recuperar seleção anterior
    comps_pre_sel = []
    for v in vinculos_atuais:
        if v["turma"] == turma:
            comps_pre_sel = [c for c in v["componentes"] if c in opcoes_comp]
            break
        
    selecionados = st.multiselect(f"Disciplinas em {turma}", opcoes_comp, default=comps_pre_sel, key=f"sel_{turma}_{perfil_selecionado}")
    config_vínculos.append({"turma": turma, "componentes": selecionados})

    # --- ADIÇÃO MANUAL DE COMPONENTE ---
    with st.container(border=True):
        add_component = st.checkbox(f"➕ Adicionar Componente em {turma}", key=f"add_check_{turma}")

        if add_component:
            col_add1, col_add2 = st.columns([3, 1])
            with col_add1:
                novo_comp = st.text_input(f"Nome do Componente (Oficial)", key=f"new_{turma}", placeholder="Ex: Marketing Digital")
            with col_add2:
                st.write("")  # Espaçamento
                st.write("")
                if st.button("Adicionar", key=f"btn_{turma}"):
                    if novo_comp:
                        if turma in turmas_db:
                            # Faz a verificação case-insensitive para evitar duplicatas
                            if novo_comp.upper() not in [c.upper() for c in turmas_db[turma]["componentes"]]:
                                turmas_db[turma]["componentes"].append(novo_comp)
                                utils.salvar_escola_db(escola_db)
                                st.success(f"Componente '{novo_comp}' adicionado com sucesso!")
                                st.rerun()
                            else:
                                st.warning(f"O componente '{novo_comp}' já existe para esta turma.")
st.divider()
if st.button("💾 Salvar Minha Configuração"):
    # --- VALIDAÇÃO DE NOME DUPLICADO ---
    nome_input = nome.strip()
    
    if not nome_input:
        st.error("❌ O nome do professor é obrigatório.")
        st.stop()

    # Normaliza lista existente para comparação (maiúsculas)
    nomes_existentes_upper = [p.upper() for p in professores_db]
    
    # Cenário 1: Criando Novo Perfil -> Nome não pode existir
    if perfil_selecionado == "➕ Novo Perfil":
        if nome_input.upper() in nomes_existentes_upper:
            st.error(f"❌ Já existe um professor cadastrado com o nome '{nome_input}'. Por favor, diferencie (ex: adicione o sobrenome).")
            st.stop()
            
    # Cenário 2: Editando Perfil -> Se mudou o nome, o novo nome não pode conflitar com outro
    elif nome_input.upper() != perfil_selecionado.upper():
        if nome_input.upper() in nomes_existentes_upper:
            st.error(f"❌ O nome '{nome_input}' já está em uso por outro professor.")
            st.stop()

    perfil = {
        "professor": nome_input,
        "email": email,
        "municipio": municipio,
        "vinculos": config_vínculos
    }

    

    utils.salvar_perfil_professor(perfil)
    utils.salvar_professor_config_db(nome_input, email, municipio, perfil)
    
    # --- CORREÇÃO: Atualizar a lista geral de professores no escola_db ---
    utils.atualizar_lista_professores_db(nome_input)
    
    # Atualizar estado da sessão para refletir mudanças imediatamente
    st.session_state['professor'] = nome_input
    st.session_state['municipio'] = municipio
    st.success("Configuração salva com sucesso! Agora o sistema está personalizado para você.")

st.divider()

st.subheader("🛠️ Manutenção de Dados")
st.caption("Ferramentas para ajuste e correção do banco de dados.")

if st.button("🔄 Corrigir Terminologia (Neurodivergência)"):
    caminho_alunos = os.path.join("data", "alunos.json")
    if os.path.exists(caminho_alunos):
        with open(caminho_alunos, "r", encoding="utf-8-sig") as f:
            dados = json.load(f)
        
        for turma, lista in dados.items():
            for aluno in lista:
                if "deficiencia" in aluno:
                    aluno["neurodivergencia"] = aluno.pop("deficiencia")
        
        with open(caminho_alunos, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
        
        st.success("✅ Banco de dados atualizado! Termo ajustado para 'neurodivergencia'.")
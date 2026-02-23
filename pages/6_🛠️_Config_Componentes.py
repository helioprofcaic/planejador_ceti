import streamlit as st
import pandas as pd
import utils

st.set_page_config(page_title="Configuração de Componentes", layout="wide")
utils.aplicar_estilo()

st.title("🛠️ Configuração de Componentes Curriculares")
st.info("Gerencie as regras de carga horária e associe os componentes da escola a elas.")

# Carregar a configuração atual
config = utils.carregar_config_componentes()
escola_db = utils.carregar_escola_db()

# Extrair todos os componentes únicos da escola para facilitar a seleção
todos_componentes = set()
for turma in escola_db.get("turmas", {}).values():
    for comp in turma.get("componentes", []):
        todos_componentes.add(comp)
todos_componentes = sorted(list(todos_componentes))

# --- Seção de Mapeamento por Palavra-chave ---
st.subheader("1. Regras de Carga Horária")
st.caption("Defina os tipos de carga horária (Ex: 40h, 80h, 120h). Adicione novas linhas se necessário.")

# Converter o dicionário para um DataFrame para usar no data_editor
mapeamento_lista = []
if config and "MAPEAMENTO_POR_CHAVE" in config:
    for chave, valor in config.get("MAPEAMENTO_POR_CHAVE", {}).items():
        mapeamento_lista.append({
            "ID da Regra": chave,
            "Tipo de Curso (Descrição)": valor["tipo_curso"],
            "Duração (Semanas)": valor["duracao_semanas"],
            "Aulas por Semana": valor.get("aulas_por_semana", 1),
            "Palavras-Chave (separadas por vírgula)": ", ".join(valor["palavras_chave"])
        })

df_mapeamento = pd.DataFrame(mapeamento_lista)

# Usar o data_editor para uma interface de edição poderosa
edited_df = st.data_editor(
    df_mapeamento,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "ID da Regra": st.column_config.TextColumn(
            "ID da Regra (Ex: ANUAL_40H)",
            help="Um identificador único para a regra. Não pode ter espaços ou caracteres especiais.",
            required=True,
        ),
        "Duração (Semanas)": st.column_config.NumberColumn(
            "Duração (Semanas)",
            help="Número de semanas para o planejamento trimestral.",
            min_value=1,
            max_value=15,
            step=1,
            format="%d",
            required=True,
        ),
        "Aulas por Semana": st.column_config.NumberColumn(
            "Aulas por Semana",
            help="Número de aulas (encontros) por semana para este componente.",
            min_value=1,
            max_value=8,
            step=1,
            required=True,
        ),
        "Palavras-Chave (separadas por vírgula)": st.column_config.TextColumn(
            "Palavras-Chave / Componentes",
            help="Lista de termos que identificam esta regra. Você pode editar aqui ou usar o classificador abaixo.",
            disabled=False
        )
    }
)

# --- Classificador Visual ---
st.divider()
st.subheader("2. Classificador de Componentes")
st.caption("Selecione os componentes da escola e atribua-os às regras criadas acima.")

regras_ids = [row["ID da Regra"] for _, row in edited_df.iterrows() if row["ID da Regra"]]

if regras_ids:
    tabs = st.tabs(regras_ids)
    
    # Dicionário para armazenar as seleções
    selecoes_por_regra = {}
    
    for i, regra in enumerate(regras_ids):
        with tabs[i]:
            # Recuperar keywords atuais dessa regra do DataFrame editado
            row = edited_df[edited_df["ID da Regra"] == regra].iloc[0]
            keywords_str = row["Palavras-Chave (separadas por vírgula)"]
            keywords_atuais = [k.strip() for k in keywords_str.split(",") if k.strip()]
            
            # Filtrar quais componentes da escola dão match com essas keywords para pré-popular
            pre_selecionados = []
            for comp in todos_componentes:
                if comp.upper() in [k.upper() for k in keywords_atuais]:
                    pre_selecionados.append(comp)
            
            st.write(f"**Componentes associados a: {regra}**")
            selecao = st.multiselect(
                f"Selecione os componentes para {regra}",
                options=todos_componentes,
                default=pre_selecionados,
                key=f"sel_{regra}"
            )
            selecoes_por_regra[regra] = selecao
else:
    st.warning("Crie regras na tabela acima primeiro.")

st.divider()

# --- Seção de Regras Padrão ---
st.subheader("3. Regras Padrão (Fallback)")
st.caption("Estas regras são aplicadas quando nenhuma palavra-chave das regras acima é encontrada no nome do componente.")

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.write("**Padrão Geral (Ensino Regular)**")
        padrao_geral = config.get("PADRAO_GERAL", {})
        pg_tipo = st.text_input("Descrição do Padrão Geral", value=padrao_geral.get("tipo_curso", "Anual / Regular"), key="pg_tipo")
        pg_duracao = st.number_input("Duração (Semanas)", value=padrao_geral.get("duracao_semanas", 13), min_value=1, max_value=15, step=1, key="pg_duracao")
        pg_aulas = st.number_input("Aulas por Semana", value=padrao_geral.get("aulas_por_semana", 1), min_value=1, max_value=8, step=1, key="pg_aulas")

with col2:
    with st.container(border=True):
        st.write("**Padrão Técnico Modular**")
        padrao_tecnico = config.get("PADRAO_TECNICO_MODULAR", {})
        pt_tipo = st.text_input("Descrição do Padrão Técnico", value=padrao_tecnico.get("tipo_curso", "Modular Mensal (40h)"), key="pt_tipo")
        pt_duracao = st.number_input("Duração (Semanas)", value=padrao_tecnico.get("duracao_semanas", 4), min_value=1, max_value=15, step=1, key="pt_duracao")
        pt_aulas = st.number_input("Aulas por Semana", value=padrao_tecnico.get("aulas_por_semana", 5), min_value=1, max_value=8, step=1, key="pt_aulas")

st.divider()

# --- Botão de Salvar ---
if st.button("💾 Salvar Todas as Configurações", type="primary"):
    novo_mapeamento = {}
    
    for _, row in edited_df.iterrows():
        if not row["ID da Regra"]: continue
        
        r_id = row["ID da Regra"]
        
        # Combina keywords digitadas com componentes selecionados
        keywords_originais = [k.strip().upper() for k in row["Palavras-Chave (separadas por vírgula)"].split(",") if k.strip()]
        componentes_selecionados = [c.upper() for c in selecoes_por_regra.get(r_id, [])]
        
        # União única
        todas_keywords = list(set(keywords_originais + componentes_selecionados))
        
        novo_mapeamento[r_id] = {
            "tipo_curso": row["Tipo de Curso (Descrição)"],
            "duracao_semanas": int(row["Duração (Semanas)"]),
            "aulas_por_semana": int(row["Aulas por Semana"]),
            "palavras_chave": todas_keywords
        }

    config_final = {
        "MAPEAMENTO_POR_CHAVE": novo_mapeamento,
        "PADRAO_GERAL": {"tipo_curso": pg_tipo, "duracao_semanas": pg_duracao, "aulas_por_semana": pg_aulas},
        "PADRAO_TECNICO_MODULAR": {"tipo_curso": pt_tipo, "duracao_semanas": pt_duracao, "aulas_por_semana": pt_aulas}
    }

    utils.salvar_config_componentes(config_final)
    st.success("✅ Configurações salvas com sucesso!")
    st.balloons()
    st.rerun()
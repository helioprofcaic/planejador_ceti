import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date
import utils
import uuid

st.set_page_config(page_title="Agenda do Professor", page_icon="📅", layout="wide")
utils.aplicar_estilo()

st.title("📅 Agenda e Cronograma")

# --- DADOS DO PROFESSOR ---
professor = st.session_state.get('professor', "Visitante")
st.caption(f"Agenda para: {professor}")

# --- CAMINHOS ---
EVENTOS_FILE = "eventos_anuais.json"
safe_prof_name = professor.replace(" ", "_").lower()
COMPROMISSOS_FILE = f"compromissos_{safe_prof_name}.json"

# =================================================================
# 1. GUIA DE COMPROMISSOS
# =================================================================
st.header("🎯 Guia de Compromissos")
st.caption("Registre e acompanhe seus acordos e tarefas com alunos, coordenação e outros.")

# Carregar compromissos existentes
caminho_compromissos = os.path.join("data", "compromissos", COMPROMISSOS_FILE)
df_compromissos = utils.carregar_dados_json(caminho_compromissos)

# Se o arquivo não existe ou está vazio, cria um DataFrame vazio
if df_compromissos is None:
    df_compromissos = pd.DataFrame(columns=["id", "Descrição", "Categoria", "Data do Prazo", "Status", "Data de Criação"])

# Formulário para adicionar novo compromisso
with st.expander("➕ Adicionar Novo Compromisso"):
    with st.form("novo_compromisso_form", clear_on_submit=True):
        nova_descricao = st.text_area("Descrição do Compromisso")
        col_form1, col_form2 = st.columns(2)
        with col_form1:
            nova_categoria = st.selectbox("Categoria", ["Alunos", "Coordenação", "Matriz do Curso", "Pessoal"])
        with col_form2:
            nova_data_prazo = st.date_input("Data do Prazo (Opcional)", value=None)
        
        submitted = st.form_submit_button("Adicionar Compromisso")
        if submitted and nova_descricao.strip():
            novo_item = pd.DataFrame([{
                "id": str(uuid.uuid4()),
                "Descrição": nova_descricao,
                "Categoria": nova_categoria,
                "Data do Prazo": str(nova_data_prazo) if nova_data_prazo else None,
                "Status": "Pendente",
                "Data de Criação": str(date.today())
            }])
            df_compromissos = pd.concat([df_compromissos, novo_item], ignore_index=True)
            utils.salvar_dados_json(caminho_compromissos, df_compromissos)
            st.success("Compromisso adicionado!")
            st.rerun()

# Editor para os compromissos
if not df_compromissos.empty:
    # Garantir que as colunas existam para o editor
    colunas_necessarias = ["id", "Descrição", "Categoria", "Data do Prazo", "Status", "Data de Criação"]
    for col in colunas_necessarias:
        if col not in df_compromissos.columns:
            df_compromissos[col] = None
    
    # Converter colunas de data para o formato correto para o editor
    df_compromissos['Data do Prazo'] = pd.to_datetime(df_compromissos['Data do Prazo'], errors='coerce').dt.date
    df_compromissos['Data de Criação'] = pd.to_datetime(df_compromissos['Data de Criação'], errors='coerce').dt.date
    
    # Ordenar por Status e Data do Prazo
    df_compromissos = df_compromissos.sort_values(by=["Status", "Data do Prazo"], ascending=[True, True])

    df_editado = st.data_editor(
        df_compromissos,
        column_config={
            "id": None, # Ocultar ID
            "Descrição": st.column_config.TextColumn("Descrição", width="large", help="O que precisa ser feito?"),
            "Categoria": st.column_config.SelectboxColumn("Categoria", options=["Alunos", "Coordenação", "Matriz do Curso", "Pessoal"], required=True),
            "Data do Prazo": st.column_config.DateColumn("Prazo", format="DD/MM/YYYY"),
            "Status": st.column_config.SelectboxColumn("Status", options=["Pendente", "Em Andamento", "Concluído", "Cancelado"], required=True),
            "Data de Criação": st.column_config.DateColumn("Criado em", format="DD/MM/YYYY", disabled=True),
        },
        use_container_width=True, 
        hide_index=True,
        num_rows="dynamic" # Allow deleting
    )
    
    if st.button("💾 Salvar Alterações nos Compromissos"):
        utils.salvar_dados_json(caminho_compromissos, df_editado)
        st.success("Compromissos atualizados com sucesso!")
        st.rerun()
else:
    st.info("Nenhum compromisso registrado ainda. Use o formulário acima para adicionar o primeiro.")

# =================================================================
# 2. CALENDÁRIO ANUAL (GRID 3x4)
# =================================================================
st.divider()
st.header("🗓️ Calendário Anual de Eventos")

caminho_eventos = os.path.join("data", EVENTOS_FILE)
eventos_data = utils.carregar_dados_json(caminho_eventos) # Usando utils para consistência

if eventos_data is not None and not eventos_data.empty:
    df_eventos = eventos_data
    df_eventos['data'] = pd.to_datetime(df_eventos['data'])
    df_eventos = df_eventos.sort_values('data')
    
    # Criar colunas auxiliares para agrupamento
    df_eventos['Mes_Num'] = df_eventos['data'].dt.month
    
    # Obter meses únicos ordenados
    meses_unicos = df_eventos[['Mes_Num']].drop_duplicates().sort_values('Mes_Num')
    
    # Mapeamento de meses para Português
    meses_pt = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho",
        7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }
    
    # Layout em Grid (3 colunas)
    cols = st.columns(3)
    
    for index, row in enumerate(meses_unicos.itertuples()):
        mes_num = row.Mes_Num
        mes_nome = meses_pt.get(mes_num, "Mês")
        
        # Distribui os meses nas 3 colunas
        with cols[index % 3]:
            with st.container(border=True):
                st.markdown(f"**{mes_nome.upper()}**")
                
                eventos_mes = df_eventos[df_eventos['Mes_Num'] == mes_num]
                for _, evento in eventos_mes.iterrows():
                    dia = evento['data'].day
                    tipo = evento['tipo']
                    desc = evento['descricao']
                    
                    # Cores por tipo de evento
                    cor_tipo = {
                        "Feriado Nacional": "red", "Ponto Facultativo": "orange",
                        "Sábado Letivo": "blue", "Projeto Escolar": "green",
                        "Reunião Pedagógica": "violet"
                    }
                    cor = cor_tipo.get(tipo, "gray")
                    
                    # Exibição compacta: Dia - Descrição [Tipo]
                    st.markdown(f"<span style='font-size:0.9em'><b>{dia:02d}</b> - {desc} <span style='color:{cor}'>[{tipo}]</span></span>", unsafe_allow_html=True)
else:
    st.info(f"Arquivo `{EVENTOS_FILE}` não encontrado ou vazio. Execute o processamento de horários para gerar.")

# =================================================================
# 3. DISTRIBUIÇÃO MENSAL DE DIAS LETIVOS
# =================================================================
st.divider()
st.header("📊 Distribuição Mensal de Dias Letivos")

# Dados estimados de dias letivos para 2026 (Baseado no calendário padrão)
dias_letivos_data = {
    "Mês": ["Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"],
    "Dias": [7, 24, 20, 20, 22, 10, 22, 22, 21, 20, 14]
}
df_dias = pd.DataFrame(dias_letivos_data)

col_graf, col_info = st.columns([3, 1])

with col_graf:
    st.bar_chart(df_dias.set_index("Mês"), color="#2E7D32", height=250)

with col_info:
    total_dias = df_dias["Dias"].sum()
    st.metric("Total de Dias Letivos", total_dias, delta="200 dias (Meta)")
    st.caption("Estimativa baseada no calendário padrão.")
    with st.expander("Ver Tabela"):
        st.dataframe(df_dias, hide_index=True, use_container_width=True)

# =================================================================
# 4. CRONOGRAMA TRIMESTRAL
# =================================================================
st.divider()
st.header("📆 Cronograma Trimestral")

calendario_data = utils.carregar_calendario_letivo()

if calendario_data and "trimestres" in calendario_data:
    cols = st.columns(3)
    trimestres = calendario_data["trimestres"]
    
    # Ordenar chaves para garantir 1º, 2º, 3º
    for i, chave in enumerate(sorted(trimestres.keys())):
        t_data = trimestres[chave]
        with cols[i % 3]:
            with st.container(border=True):
                st.subheader(f"{chave} Trimestre")
                st.caption(f"📅 {t_data.get('inicio', '')} até {t_data.get('fim', '')}")
                
                try:
                    inicio = datetime.strptime(t_data['inicio'], "%Y-%m-%d")
                    fim = datetime.strptime(t_data['fim'], "%Y-%m-%d")
                    hoje = datetime.now()
                    
                    if hoje < inicio:
                        st.info("⏳ Não iniciado")
                    elif hoje > fim:
                        st.success("✅ Concluído")
                    else:
                        total_dias = (fim - inicio).days
                        if total_dias > 0:
                            dias_passados = (hoje - inicio).days
                            progresso = max(0.0, min(1.0, dias_passados / total_dias))
                            st.progress(progresso, text="Em andamento")
                        else:
                            st.progress(1.0, text="Concluído")
                except (ValueError, TypeError, KeyError):
                    st.error("Erro nas datas do calendário.")
else:
    st.info("Dados do calendário letivo não disponíveis.")

utils.criar_botao_voltar()
import streamlit as st
import pandas as pd
import os
import utils
import sqlite3

st.set_page_config(page_title="Dashboard", layout="wide")

# --- CONFIGURAÇÕES GLOBAIS ---
utils.aplicar_estilo()

st.title("📈 Dashboard de Frequência")
st.markdown("Visualização gráfica da assiduidade das turmas.")

# --- CARREGAMENTO DE DADOS ---
db_path = os.path.join("data", "backup_sistema.db")
df_dash = pd.DataFrame()
df_alunos = pd.DataFrame()

if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        # Lê apenas os dados necessários do banco
        query = "SELECT turma as Turma, data as Data, presenca FROM frequencia"
        df_raw = pd.read_sql_query(query, conn)
        
        # Query para análise por aluno
        query_alunos = "SELECT aluno_nome, COUNT(*) as total, SUM(presenca) as presentes FROM frequencia GROUP BY aluno_nome"
        df_alunos = pd.read_sql_query(query_alunos, conn)
        conn.close()

        if not df_raw.empty:
            # Agrupa por Turma e Data para calcular o percentual
            df_dash = df_raw.groupby(['Turma', 'Data']).agg(
                Total=('presenca', 'count'),
                Presentes=('presenca', 'sum')
            ).reset_index()
            
            df_dash['Percentual'] = (df_dash['Presentes'] / df_dash['Total']) * 100
            df_dash['Data'] = pd.to_datetime(df_dash['Data'])

        if not df_alunos.empty:
            df_alunos['Percentual'] = (df_alunos['presentes'] / df_alunos['total']) * 100

    except Exception as e:
        st.error(f"Erro ao ler banco de dados: {e}")

# --- VISUALIZAÇÃO ---
if df_dash.empty:
    st.info("Nenhum registro encontrado. Vá na página inicial e clique em 'Sincronizar Banco de Dados' ou salve novas frequências.")
else:
    # Métricas Gerais
    col1, col2, col3 = st.columns(3)
    media_geral = df_dash["Percentual"].mean()
    total_aulas = len(df_dash)
    # Turma com maior média
    turma_melhor_freq = df_dash.groupby("Turma")["Percentual"].mean().idxmax()
    
    col1.metric("Média Geral de Presença", f"{media_geral:.1f}%")
    col2.metric("Total de Chamadas Realizadas", total_aulas)
    col3.metric("Turma Mais Assídua", turma_melhor_freq)
    
    st.divider()
    
    # Gráfico 1: Média por Turma
    st.subheader("📊 Média de Presença por Turma")
    df_por_turma = df_dash.groupby("Turma")["Percentual"].mean().sort_values()
    st.bar_chart(df_por_turma, color="#007bff")
    
    # Gráfico 2: Evolução Temporal
    st.subheader("📈 Evolução da Frequência no Tempo")
    turmas_disponiveis = df_dash["Turma"].unique()
    turma_filtro = st.selectbox("Filtrar por Turma", turmas_disponiveis)
    
    df_evolucao = df_dash[df_dash["Turma"] == turma_filtro].sort_values("Data")
    
    # Exibe gráfico de linha (Data no eixo X, Percentual no eixo Y)
    st.line_chart(df_evolucao.set_index("Data")["Percentual"], color="#28a745")

    # Análise de Risco (Alunos)
    if not df_alunos.empty:
        st.divider()
        st.subheader("👥 Situação dos Alunos (Frequência)")
        aprovados = len(df_alunos[df_alunos['Percentual'] >= 75])
        risco = len(df_alunos) - aprovados
        
        kpi1, kpi2 = st.columns(2)
        kpi1.metric("Alunos com Frequência ≥ 75%", aprovados)
        kpi2.metric("Alunos em Risco (< 75%)", risco, delta=f"-{risco}" if risco > 0 else "0", delta_color="inverse")

    st.divider()

    # Tabela de Dados Brutos
    if st.checkbox("🔍 Ver Dados Detalhados"):
        st.dataframe(df_dash.style.format({"Percentual": "{:.1f}%", "Data": "{:%d/%m/%Y}"}))
        
        st.download_button(
            label="📥 Baixar Dados (CSV)",
            data=df_dash.to_csv(index=False).encode('utf-8'),
            file_name="dados_dashboard.csv",
            mime="text/csv"
        )
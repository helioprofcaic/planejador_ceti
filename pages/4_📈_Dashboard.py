import streamlit as st
import pandas as pd
import os
import utils

st.set_page_config(page_title="Dashboard", layout="wide")

# --- CONFIGURAÇÕES GLOBAIS ---
utils.aplicar_estilo()

st.title("📈 Dashboard de Frequência")
st.markdown("Visualização gráfica da assiduidade das turmas.")

# --- CARREGAMENTO DE DADOS ---
df_dash = pd.DataFrame()
df_alunos = pd.DataFrame()

# Lista todos os arquivos de frequência disponíveis
arquivos_freq = utils.listar_arquivos_dados("frequencia_")

if arquivos_freq:
    lista_dfs = []
    
    with st.spinner("Consolidando dados de frequência..."):
        for arquivo in arquivos_freq:
            # Extrai metadados do nome do arquivo: frequencia_{turma}_{data}.json
            try:
                # Remove extensão e prefixo
                nome_limpo = arquivo.replace("frequencia_", "").replace(".json", "")
                # Assume formato turma_data (data são os últimos 10 chars: YYYY-MM-DD)
                data_str = nome_limpo[-10:]
                turma_str = nome_limpo[:-11]
                
                df_temp = utils.carregar_dados_json(os.path.join("data", arquivo))
                if df_temp is not None and not df_temp.empty:
                    df_temp["Turma"] = turma_str
                    df_temp["Data"] = data_str
                    # Normaliza coluna de presença
                    df_temp["presenca_bool"] = df_temp["Presença"].apply(lambda x: 1 if x else 0)
                    lista_dfs.append(df_temp)
            except Exception as e:
                print(f"Erro ao processar {arquivo}: {e}")

    if lista_dfs:
        df_completo = pd.concat(lista_dfs, ignore_index=True)
        
        # Agrupa por Turma e Data para o gráfico temporal
        df_dash = df_completo.groupby(['Turma', 'Data']).agg(
            Total=('presenca_bool', 'count'),
            Presentes=('presenca_bool', 'sum')
        ).reset_index()
        
        df_dash['Percentual'] = (df_dash['Presentes'] / df_dash['Total']) * 100
        df_dash['Data'] = pd.to_datetime(df_dash['Data'])
        
        # Agrupa por Aluno para análise de risco
        df_alunos = df_completo.groupby(['Nome do Aluno', 'Turma']).agg(
            total=('presenca_bool', 'count'),
            presentes=('presenca_bool', 'sum')
        ).reset_index()
        df_alunos['Percentual'] = (df_alunos['presentes'] / df_alunos['total']) * 100

# --- VISUALIZAÇÃO ---
if df_dash.empty:
    st.info("Nenhum registro de frequência encontrado.")
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
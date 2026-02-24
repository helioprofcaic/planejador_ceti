import streamlit as st
import pandas as pd
import utils
import os

st.set_page_config(page_title="Quadro de Horários", layout="wide")
utils.aplicar_estilo()

# --- DADOS DO USUÁRIO ---
professor_logado = st.session_state.get('professor', "Professor Visitante")
perfil = utils.carregar_perfil_professor()

st.title("🕒 Quadro de Horários")
st.caption(f"Visualização para: {professor_logado}")

# --- CONTROLES ---
col_opt1, col_opt2 = st.columns([1, 3])
with col_opt1:
    modo_visualizacao = st.radio("Modo de Visualização", ["Meu Horário", "Quadro Global (Escola)"])

# --- LÓGICA DE DADOS ---
horario_global = utils.carregar_horario_global()

if not horario_global:
    st.warning("⚠️ O arquivo de horário global (`data/horario_global.json`) não foi encontrado.")
    st.info("Execute o script `tools/processar_horario.py` para gerar a base de dados a partir do documento oficial.")
else:
    # --- VISUALIZAÇÃO: MEU HORÁRIO ---
    if modo_visualizacao == "Meu Horário":
        st.subheader(f"📅 Agenda Semanal - {professor_logado}")
        
        dados_globais_filtrados = utils.obter_horario_professor_do_global(professor_logado)
        
        if dados_globais_filtrados:
            df = pd.DataFrame(dados_globais_filtrados)
            
            # Remove coluna auxiliar de ordenação para exibição
            if "OrdemDia" in df.columns:
                df = df.drop(columns=["OrdemDia"])
                
            # Edição
            st.info("💡 Você pode editar os detalhes abaixo para seu controle pessoal.")
            df_editado = st.data_editor(
                df, 
                use_container_width=True, 
                num_rows="dynamic",
                column_config={
                    "Dia": st.column_config.SelectboxColumn(
                        "Dia da Semana",
                        options=["SEGUNDA-FEIRA", "TERÇA-FEIRA", "QUARTA-FEIRA", "QUINTA-FEIRA", "SEXTA-FEIRA"],
                        required=True
                    ),
                    "Período": st.column_config.TextColumn("Aula/Período"),
                    "Sala": st.column_config.TextColumn("Turma/Sala"),
                },
                hide_index=True
            )
            
            if st.button("💾 Salvar Meu Horário Personalizado"):
                # Salva em um JSON específico do professor para persistência
                caminho_prof = os.path.join("data", "perfis", f"{professor_logado.replace(' ', '_')}.json")
                utils.salvar_dados_json(caminho_prof, df_editado)
                st.success("✅ Horário personalizado salvo com sucesso!")
                
        else:
            st.warning(f"Não foram encontradas aulas vinculadas ao nome '{professor_logado}' no quadro global.")
            st.markdown("""
            **Possíveis motivos:**
            1. Seu nome no cadastro está diferente do quadro de horários (Ex: "Helio" vs "Hélio").
            2. O quadro global ainda não foi importado.
            
            *Você pode adicionar aulas manualmente abaixo:*
            """)
            
            df_vazio = pd.DataFrame(columns=["Dia", "Período", "Horário", "Sala", "Disciplina"])
            st.data_editor(df_vazio, num_rows="dynamic", use_container_width=True)

    # --- VISUALIZAÇÃO: QUADRO GLOBAL ---
    else:
        st.subheader("🏫 Quadro Geral de Aulas (Todas as Salas)")
        
        dias_disponiveis = list(horario_global.keys())
        dia_selecionado = st.selectbox("Selecione o Dia", dias_disponiveis)
        
        if dia_selecionado:
            dados_dia = horario_global[dia_selecionado]
            
            # Transforma o JSON hierárquico em uma Tabela (DataFrame)
            # Linhas: Períodos
            # Colunas: Salas
            
            # 1. Coletar todas as salas únicas neste dia
            todas_salas = set()
            for periodo, salas in dados_dia.items():
                todas_salas.update(salas.keys())
            lista_salas = sorted(list(todas_salas))
            
            # 2. Construir linhas
            linhas_tabela = []
            periodos_ordenados = sorted(dados_dia.keys()) 
            
            for per in periodos_ordenados:
                linha = {"Período": per}
                # Adiciona horário se disponível na primeira sala encontrada (aproximação)
                horario_ref = next(iter(dados_dia[per].values()))["horario"] if dados_dia[per] else ""
                linha["Horário"] = horario_ref
                
                for sala in lista_salas:
                    info = dados_dia[per].get(sala, {})
                    linha[sala] = f"{info.get('professor', '')}\n{info.get('disciplina', '')}" if info else "-"
                linhas_tabela.append(linha)
                
            df_global = pd.DataFrame(linhas_tabela)
            st.dataframe(df_global, use_container_width=True, height=600, hide_index=True)

utils.criar_botao_voltar()
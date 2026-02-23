import streamlit as st
import pandas as pd
import utils
import math
from datetime import date, timedelta

st.set_page_config(page_title="Planejamento", layout="wide")

# --- RECUPERA CONFIGURAÇÕES GLOBAIS ---
escola = st.session_state.get('escola', "CETI PROFESSOR RALDIR CAVALCANTE BASTOS")
professor = st.session_state.get('professor', "Helio Lima")

# --- ESTILO ---
utils.aplicar_estilo()

# --- DADOS ---
escola_db = utils.carregar_escola_db()
curriculo_db = utils.carregar_curriculo_db()
perfil_prof = utils.carregar_perfil_professor()
habilidades_csv = utils.carregar_habilidades_csv()
config_componentes = utils.carregar_config_componentes() # Carrega as novas configurações de carga horária
calendario_letivo = utils.carregar_calendario_letivo() # Carrega a bússola do tempo

# --- INICIALIZAÇÃO DA CESTA DE PLANOS ---
if 'cesta_planos' not in st.session_state:
    st.session_state['cesta_planos'] = []

# --- FUNÇÕES AUXILIARES ---
def get_component_config(nome_comp, config):
    """Retorna a configuração de carga horária para um componente."""
    nome_upper = nome_comp.upper()
    mapeamento = config.get("MAPEAMENTO_POR_CHAVE", {})
    
    # Busca por palavra-chave
    for cfg in mapeamento.values():
        if any(k in nome_upper for k in cfg["palavras_chave"]):
            return cfg
            
    # Retorna padrão se não encontrar
    return config.get("PADRAO_GERAL", {"tipo_curso": "Anual", "duracao_semanas": 13, "aulas_por_semana": 1})

def calcular_cronograma_turma(turma, escola_db, config_componentes):
    """Calcula a semana de início e fim de cada componente na fila anual."""
    cronograma = {}
    acumulado_semanas = 0
    
    # Pega a lista ordenada de componentes (A ordem no JSON importa!)
    componentes_ordenados = escola_db.get("turmas", {}).get(turma, {}).get("componentes", [])
    
    for comp in componentes_ordenados:
        cfg = get_component_config(comp, config_componentes)
        tipo = cfg.get("tipo_curso", "")
        duracao = cfg.get("duracao_semanas", 13)
        
        if "Anual" in tipo or "Técnico Anual" in tipo:
            # Disciplinas anuais rodam em paralelo o ano todo (0 a 40 semanas)
            cronograma[comp] = {"inicio": 0, "fim": 40, "tipo": "Anual", "duracao": duracao, "cfg": cfg}
        else:
            # Disciplinas modulares entram na fila
            inicio = acumulado_semanas
            fim = inicio + duracao
            cronograma[comp] = {"inicio": inicio, "fim": fim, "tipo": "Modular", "duracao": duracao, "cfg": cfg}
            acumulado_semanas = fim # O próximo começa quando este termina
            
    return cronograma

# --- INTERFACE ---
st.title("🚀 Planejamento Escolar")
st.caption(f"Unidade: {escola} | Professor: {professor}")

# --- SELEÇÃO (LINHA 1) ---
col1, col2 = st.columns(2)

with col1:
    # Lista de turmas (Prioriza perfil do professor, mas permite ver todas se necessário)
    if perfil_prof:
        turma_lista = [v["turma"] for v in perfil_prof["vinculos"]]
        # Adiciona opção para ver todas caso o professor queira explorar
        turma_lista += [t for t in escola_db.get("turmas", {}).keys() if t not in turma_lista]
    else:
        turma_lista = list(escola_db.get("turmas", {}).keys())
        
    turma_sel = st.selectbox("Selecione a Turma", turma_lista)

with col2:
    trimestre_sel = st.selectbox("Trimestre", ["1º", "2º", "3º"])
    
    # Define intervalo de semanas e datas usando a bússola do tempo
    dados_tri = calendario_letivo.get("trimestres", {}).get(trimestre_sel, {})
    tri_inicio = dados_tri.get("semana_inicio", 0)
    tri_fim = dados_tri.get("semana_fim", 13)
    try:
        data_inicio_trimestre = date.fromisoformat(dados_tri.get("inicio", "2026-02-19"))
    except ValueError:
        data_inicio_trimestre = date(2026, 2, 19)

# --- CÁLCULO E FILTRAGEM ---
cronograma_turma = calcular_cronograma_turma(turma_sel, escola_db, config_componentes)
componentes_disponiveis = []
info_cronograma = {} # Para guardar dados de deslocamento

if turma_sel:
    # Filtra componentes que acontecem neste trimestre
    for comp, dados in cronograma_turma.items():
        # Verifica se há sobreposição entre o tempo da disciplina e o trimestre
        # (Inicio da disciplina < Fim do Trimestre) E (Fim da disciplina > Inicio do Trimestre)
        if dados["inicio"] < tri_fim and dados["fim"] > tri_inicio:
            componentes_disponiveis.append(comp)
            info_cronograma[comp] = dados

    # Se o professor tem perfil, filtra apenas os dele que estão disponíveis neste trimestre
    if perfil_prof:
        comps_prof = []
        for v in perfil_prof["vinculos"]:
            if v["turma"] == turma_sel:
                comps_prof = v["componentes"]
                break
        if comps_prof:
            # Interseção: Só mostra o que é do professor E está disponível no trimestre
            componentes_disponiveis = [c for c in componentes_disponiveis if c in comps_prof]

# --- SELEÇÃO (LINHA 2) ---
col3, col4 = st.columns(2)

with col3:
    if not componentes_disponiveis:
        st.warning(f"Nenhum componente curricular previsto para o {trimestre_sel} Trimestre nesta turma.")
        comp_sel = None
    else:
        comp_sel = st.selectbox("Componente Curricular", componentes_disponiveis)

with col4:
    escala = st.radio("Escala", ["Semanal", "Mensal", "Trimestral"], horizontal=True)

# Conteúdo
if turma_sel and comp_sel:
    # Recupera dados do cronograma calculado
    dados_agendamento = info_cronograma.get(comp_sel, {})
    cfg_comp = dados_agendamento.get("cfg", {})
    
    # Calcula o deslocamento (offset) para a data correta
    offset_semanas = max(0, dados_agendamento["inicio"] - tri_inicio)

    # Busca dados no Curriculo DB (Hierarquia: EPT -> Aprofundamento -> Básico)
    conteudo_db = {}
    
    # Normalização simples para busca (ex: POO -> POO)
    chave_busca = comp_sel
    if "POO" in comp_sel: chave_busca = "PROGRAMAÇÃO ORIENTADA À OBJETOS - POO"
    elif "IOT" in comp_sel: chave_busca = "IOT - INTERNET DAS COISAS"
    elif "WEB" in comp_sel: chave_busca = "PROGRAMAÇÃO WEB FRONT-END"
    elif "INTELIGÊNCIA ARTIFICIAL" in comp_sel and "AUTOMAÇÃO" not in comp_sel: chave_busca = "INTELIGÊNCIA ARTIFICIAL"
    elif "SISTEMAS INTELIGENTES" in comp_sel: chave_busca = "SISTEMAS INTELIGENTES E AUTÔNOMOS"
    
    # Tenta encontrar em cada seção
    if chave_busca in curriculo_db.get("EPT", {}):
        conteudo_db = curriculo_db["EPT"][chave_busca]
    elif chave_busca in curriculo_db.get("APROFUNDAMENTO", {}):
        conteudo_db = curriculo_db["APROFUNDAMENTO"][chave_busca]
    elif chave_busca in curriculo_db.get("BASICO", {}):
        conteudo_db = curriculo_db["BASICO"][chave_busca]
    # Tenta busca direta
    elif comp_sel in curriculo_db.get("EPT", {}): conteudo_db = curriculo_db["EPT"][comp_sel]
    elif comp_sel in curriculo_db.get("APROFUNDAMENTO", {}): conteudo_db = curriculo_db["APROFUNDAMENTO"][comp_sel]
    elif comp_sel in curriculo_db.get("BASICO", {}): conteudo_db = curriculo_db["BASICO"][comp_sel]
    
    # Tenta buscar do CSV (Prioridade Máxima)
    conteudo_csv = habilidades_csv.get(comp_sel, {})
    
    # Consolidação dos dados (Prioridade: CSV > Novo JSON > Oficial Antigo > Básico)
    competencia = conteudo_csv.get("competencia") or conteudo_db.get("competencia", "")
    objetos = conteudo_csv.get("objetos") or conteudo_db.get("objetos", [])
    habilidades_raw = conteudo_csv.get("habilidades") or conteudo_db.get("habilidades", [])
    referencias = conteudo_db.get("referencias", "")
    
    # Tenta carregar um planejamento já salvo para não perder edições
    plano_salvo = utils.carregar_planejamento(turma_sel, comp_sel, escala, trimestre_sel)
    
    st.divider()
    st.write("### 🏗️ Elementos Estruturantes")
    
    # Se houver plano salvo, usa a competência salva, senão usa a padrão
    valor_competencia = plano_salvo.get("competencia_geral", competencia) if plano_salvo else competencia
    comp_geral = st.text_area("Competência Geral", value=valor_competencia, height=80)
    
    if referencias:
        st.info(f"📚 **Referências Bibliográficas:** {referencias}")
    
    st.write(f"### 📅 Detalhamento {escala}")
    
    linhas = []
    
    # Se já existe um plano salvo, carregamos ele diretamente
    if plano_salvo and "planilha" in plano_salvo:
        linhas = plano_salvo["planilha"]
        st.info("📂 Carregado planejamento salvo anteriormente. Edite conforme necessário.")
        if st.button("🔄 Regenerar (Descartar alterações salvas)"):
            utils.salvar_planejamento({"turma": turma_sel, "componente": comp_sel, "escala": escala, "trimestre": trimestre_sel}) # Salva vazio para limpar
            st.rerun()
            
    else:
        # --- LÓGICA DE GERAÇÃO (Só roda se não tiver salvo) ---
        
        # Lógica de Sugestão Automática (Se houver dados oficiais)
        if (conteudo_csv or conteudo_db) and escala == "Semanal":
            if conteudo_csv:
                st.success("✅ Sugestão automática carregada de arquivo CSV.")
            else:
                st.success("✅ Sugestão automática carregada com base no Currículo Oficial.")
                
            items_para_planejar = objetos if objetos else ["Conteúdo a definir"]
            
            for i, item in enumerate(items_para_planejar):
                # Formata habilidade
                hab_texto = ""
                if habilidades_raw:
                    hab_item = habilidades_raw[i % len(habilidades_raw)]
                    if isinstance(hab_item, dict):
                        hab_texto = f"{hab_item.get('codigo', '')} - {hab_item.get('descricao', '')}"
                    else:
                        hab_texto = str(hab_item)
                
                linhas.append({
                    "Semana": f"Semana {i+1}",
                    "Habilidade": hab_texto,
                    "Objetivos": f"Compreender e aplicar {item}",
                    "Conteúdo": item,
                    "Metodologia": "Aula Prática / Hands-on",
                    "Avaliação": "Entrega de artefatos técnicos"
                })
                
        elif escala == "Mensal":
            # ... (Lógica Mensal mantida simplificada) ...
            mes_sel = st.selectbox("Mês", ["Fevereiro", "Março", "Abril", "Maio"])
            linhas.append({
                "Período": mes_sel,
                "Objetivos": "Desenvolver as competências técnicas do mês",
                "Conteúdo": " / ".join(objetos[:2]),
                "Metodologia": "PBL - Aprendizagem Baseada em Projetos",
                "Avaliação": "Atividade Prática e Teórica"
            })
            
        else:  # Trimestral (Lógica Principal)
            tipo_curso = cfg_comp.get("tipo_curso", "Regular")
            duracao_semanas = cfg_comp.get("duracao_semanas", 13)
            aulas_semana = cfg_comp.get("aulas_por_semana", 1)

            total_aulas_trimestre = duracao_semanas * aulas_semana
            
            col_info1, col_info2 = st.columns([3, 1])
            col_info1.info(f"📅 **{tipo_curso}** | Início: Semana {offset_semanas + 1} do Trimestre | Duração: {duracao_semanas} semanas.")
            col_info2.metric("Aulas Previstas", total_aulas_trimestre)
            
            # Data real de início das aulas deste componente
            inicio_efetivo = data_inicio_trimestre + timedelta(weeks=offset_semanas)
            # Ajusta para a segunda-feira
            inicio_efetivo = inicio_efetivo - timedelta(days=inicio_efetivo.weekday())
            
            meses_pt = {1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"}
            
            # Garante que há objetos para distribuir
            if not objetos: objetos = ["Conteúdo Programático a definir"]
            
            # Define habilidade base para fallback caso não haja específicas
            habilidade_base = competencia if competencia else "Habilidade a desenvolver"

            for sem in range(1, duracao_semanas + 1): # Loop das semanas
                for aula_num in range(1, aulas_semana + 1): # Loop das aulas dentro da semana
                    # Calcula as datas da semana de planejamento (Segunda a Sexta)
                    data_inicio_semana = inicio_efetivo + timedelta(weeks=sem - 1)
                    data_fim_semana = data_inicio_semana + timedelta(days=4)
                    
                    # Determina o mês com base no início da semana
                    mes_nome = meses_pt.get(data_inicio_semana.month, "")
                    if data_inicio_semana.month != data_fim_semana.month:
                        mes_nome = f"{meses_pt.get(data_inicio_semana.month, '')}/{meses_pt.get(data_fim_semana.month, '')}"

                    # Distribuição proporcional do conteúdo pelo total de AULAS, não de semanas
                    aula_indice_geral = (sem - 1) * aulas_semana + (aula_num - 1)
                    idx_obj = math.floor(aula_indice_geral * len(objetos) / total_aulas_trimestre)
                    idx_obj = min(idx_obj, len(objetos) - 1)
                    obj_atual = objetos[idx_obj]

                    # Seleção da Habilidade correspondente
                    hab_texto = habilidade_base
                    if habilidades_raw:
                        hab_item = habilidades_raw[idx_obj % len(habilidades_raw)]
                        if isinstance(hab_item, dict):
                            hab_texto = f"{hab_item.get('codigo', '')} - {hab_item.get('descricao', '')}"
                        else:
                            hab_texto = str(hab_item)
                    
                    # Fallback para habilidade base se não encontrou específica
                    if not hab_texto: hab_texto = habilidade_base
                    
                    linhas.append({
                        "Mês": mes_nome,
                        "Semana": f"Semana {sem}",
                        "Aula": f"Aula {aula_num}",
                        "Habilidade": hab_texto,
                        "Objetivos": f"Compreender e aplicar {obj_atual}",
                        "Conteúdo": obj_atual,
                        "Metodologia": "Projetos Práticos" if "Modular" in tipo_curso else "Ensino Híbrido",
                        "Avaliação": "Avaliação Contínua"
                    })

    df_plano = pd.DataFrame(linhas)
    df_editado = st.data_editor(df_plano, num_rows="dynamic", width='stretch')

    # Botões
    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("💾 Salvar Planejamento"):
            plano_save = {
                "escola": escola,
                "professor": professor,
                "turma": turma_sel,
                "componente": comp_sel,
               "escala": escala,
                "trimestre": trimestre_sel,
                "competencia_geral": comp_geral,
                "planilha": df_editado.to_dict(orient="records")
            }
            utils.salvar_planejamento(plano_save)
            st.success("✅ Planejamento salvo com sucesso! Você pode fechar e voltar depois.")
    with c2:
        docx_bytes = utils.gerar_docx_planejamento(escola, professor, turma_sel, comp_sel, escala, comp_geral, df_editado, trimestre_sel, st.session_state.get('municipio', ""))
        if 'municipio' not in st.session_state:
           st.session_state['municipio'] = ""
        st.download_button(
            label="📄 Baixar DOCX",
            data=docx_bytes,
            file_name=f"planejamento_{turma_sel}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    with c3:
        pdf_bytes = utils.gerar_pdf_planejamento(escola, professor, turma_sel, comp_sel, escala, comp_geral, df_editado, trimestre_sel, st.session_state.get('municipio', ""))
        st.download_button(
            label="🖨️ Baixar PDF",
            data=pdf_bytes,
            file_name=f"planejamento_{turma_sel}.pdf",
            mime="application/pdf"
        )
    with c4:
        if st.button("🛒 Adicionar à Cesta"):
            plano_data = {
                "escola": escola,
                "professor": professor,
                "turma": turma_sel,
                "componente": comp_sel,
                "escala": escala,
                "trimestre": trimestre_sel,
                "comp_geral": comp_geral,
                "df": df_editado
            }
            st.session_state['cesta_planos'].append(plano_data)
            st.success(f"Adicionado! Cesta tem {len(st.session_state['cesta_planos'])} planos.")

# --- ÁREA DA CESTA DE PLANOS ---
if st.session_state['cesta_planos']:
    st.divider()
    st.subheader(f"📦 Cesta de Planos ({len(st.session_state['cesta_planos'])})")
    
    # Listar itens na cesta
    for i, p in enumerate(st.session_state['cesta_planos']):
        st.text(f"{i+1}. {p['turma']} - {p['componente']} ({p['escala']} - {p.get('trimestre', '1º')} Trimestre)")
    
    col_cesta1, col_cesta2 = st.columns(2)
    with col_cesta1:
        if st.button("🗑️ Limpar Cesta"):
            st.session_state['cesta_planos'] = []
            st.rerun()
    with col_cesta2:
        pdf_consolidado = utils.consolidar_planos(st.session_state['cesta_planos'])
        st.download_button(
            label="🗂️ Baixar Todos (PDF Único)",
            data=pdf_consolidado,
            file_name="Cesta_de_Planos_Consolidada.pdf",
            mime="application/pdf"
        )


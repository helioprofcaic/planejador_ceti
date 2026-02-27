import streamlit as st
import pandas as pd
import utils
import math
from datetime import date, timedelta
import unicodedata
import os

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
def normalizar_texto(texto):
    """Remove acentos e padroniza para maiúsculas."""
    if not texto: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', str(texto))
                  if unicodedata.category(c) != 'Mn').upper()

def buscar_dados_curriculo(nome_comp, curriculo_db):
    """Busca dados do componente no currículo. Prioriza EPT > Aprofundamento > Basico."""
    if not curriculo_db or not nome_comp:
        return {}

    nome_norm = normalizar_texto(nome_comp)
    
    partial_match_with_content = None
    exact_match_empty = None
    partial_match_empty = None

    # Percorre as seções na ordem de prioridade
    for secao in ["EPT", "APROFUNDAMENTO", "BASICO"]:
        secao_data = curriculo_db.get(secao, {})
        for db_key, db_val in secao_data.items():
            db_key_norm = normalizar_texto(db_key)
            
            has_content = bool(db_val.get("competencia"))

            if nome_norm == db_key_norm:
                if has_content:
                    # Prioridade máxima, pode retornar imediatamente
                    return db_val
                elif not exact_match_empty:
                    exact_match_empty = db_val
            elif (nome_norm in db_key_norm or db_key_norm in nome_norm):
                if has_content:
                    if not partial_match_with_content:
                        partial_match_with_content = db_val
                elif not partial_match_empty:
                    partial_match_empty = db_val
    
    # Retorna na ordem de prioridade
    if partial_match_with_content:
        return partial_match_with_content
    if exact_match_empty:
        return exact_match_empty
    if partial_match_empty:
        return partial_match_empty
    
    return {}

def get_component_config(nome_comp, turma, config, curriculo_db=None):
    """Retorna a configuração de carga horária para um componente."""
    nome_upper = normalizar_texto(nome_comp)
    
    # 1. Regras fixas de negócio que rodam o ano todo
    if "PENSAMENTO" in nome_upper or "MENTORIA" in nome_upper:
        return {"tipo_curso": "Contínuo", "duracao_semanas": 40, "aulas_por_semana": 1}
    if "9" in turma and ("COMPUTACAO" in nome_upper or "INTELIGENCIA" in nome_upper):
        return {"tipo_curso": "Anual", "duracao_semanas": 40, "aulas_por_semana": 1}

    # 2. Busca a regra no arquivo de configuração do usuário (config_componentes.json)
    # Esta é a fonte de verdade para a duração das disciplinas modulares.
    mapeamento = config.get("MAPEAMENTO_POR_CHAVE", {})
    for cfg in mapeamento.values():
        palavras_chave = [normalizar_texto(k) for k in cfg.get("palavras_chave", [])]
        if any(k in nome_upper for k in palavras_chave):
            cfg_copy = cfg.copy()
            # Para turmas DS, a carga horária semanal é fixa, então sobrescrevemos apenas este valor.
            # A duração em semanas vem da regra que o usuário criou.
            if "DS" in turma:
                # Garante que Mentoria/Pensamento não sejam afetados pela regra de 8h/10h
                if "MENTORIA" not in nome_upper and "PENSAMENTO" not in nome_upper:
                    cfg_copy['aulas_por_semana'] = 8 if "2" in turma else 10
            return cfg_copy
            
    # 3. Se nenhuma regra específica foi encontrada, usa um padrão.
    if "DS" in turma:
        padrao = config.get("PADRAO_TECNICO_MODULAR", {}).copy()
        padrao['aulas_por_semana'] = 8 if "2" in turma else 10
        return padrao
        
    return config.get("PADRAO_GERAL", {"tipo_curso": "Anual", "duracao_semanas": 40, "aulas_por_semana": 1})

def calcular_cronograma_turma(turma, componentes_ordenados, config_componentes, curriculo_db=None):
    """Calcula a semana de início e fim de cada componente, tratando DS de forma especial."""
    cronograma = {}
    acumulado_semanas_modular = 0
    
    is_ds_turma = "DS" in turma

    for comp in componentes_ordenados:
        cfg = get_component_config(comp, turma, config_componentes, curriculo_db)
        duracao = cfg.get("duracao_semanas", 40)
        
        # Lógica de Agendamento:
        # - Para turmas que não são de DS (ex: 9º ano), todos componentes rodam em paralelo (anual).
        # - Para turmas de DS, "Pensamento Computacional" e "Mentoria Tec" rodam em paralelo (anual).
        # - Para turmas de DS, os demais componentes são modulares e sequenciais.
        is_parallel = False
        if not is_ds_turma:
            is_parallel = True
        elif is_ds_turma and ("PENSAMENTO" in normalizar_texto(comp) or "MENTORIA" in normalizar_texto(comp)):
            is_parallel = True

        if is_parallel:
            # Disciplinas anuais rodam em paralelo o ano todo (0 a 40 semanas)
            cronograma[comp] = {"inicio": 0, "fim": 40, "tipo": "Anual", "duracao": 40, "cfg": cfg}
        else:
            # Disciplinas modulares entram na fila
            inicio = acumulado_semanas_modular
            fim = inicio + duracao
            cronograma[comp] = {"inicio": inicio, "fim": fim, "tipo": "Modular", "duracao": duracao, "cfg": cfg}
            acumulado_semanas_modular = fim # O próximo começa quando este termina
            
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
# 1. A fonte da verdade para a lista e ORDEM dos componentes é o PERFIL DO PROFESSOR (se existir).
lista_para_calcular = []
if perfil_prof:
    for v in perfil_prof.get("vinculos", []):
        if v.get("turma") == turma_sel:
            lista_para_calcular = v.get("componentes", [])
            break

# Se não achou no perfil (ou perfil vazio), usa o escola_db
if not lista_para_calcular:
    lista_para_calcular = escola_db.get("turmas", {}).get(turma_sel, {}).get("componentes", [])

# 3. Calculamos o cronograma com a lista ordenada e filtrada.
cronograma_turma = calcular_cronograma_turma(turma_sel, lista_para_calcular, config_componentes, curriculo_db)
componentes_disponiveis = []
info_cronograma = {} # Para guardar dados de deslocamento

if turma_sel:
    # 4. Filtra componentes do cronograma que acontecem neste trimestre
    for comp, dados in cronograma_turma.items():
        if dados["inicio"] < tri_fim and dados["fim"] > tri_inicio:
            componentes_disponiveis.append(comp)
            info_cronograma[comp] = dados

    # 5. Garante que a ordem da lista suspensa seja a mesma da lista original da escola.
    if componentes_disponiveis:
        componentes_disponiveis.sort(key=lambda c: lista_para_calcular.index(c) if c in lista_para_calcular else -1)

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
    conteudo_db = buscar_dados_curriculo(comp_sel, curriculo_db)
    
    # Tenta buscar do CSV (Prioridade Máxima)
    conteudo_csv = habilidades_csv.get(comp_sel, {})
    
    # Consolidação dos dados (Prioridade: CSV > Novo JSON > Oficial Antigo > Básico)
    competencia_especifica_db = conteudo_csv.get("competencia") or conteudo_db.get("competencia", "")
    objetos = conteudo_csv.get("objetos") or conteudo_db.get("objetos", [])
    habilidades_raw = conteudo_csv.get("habilidades") or conteudo_db.get("habilidades", [])
    referencias = conteudo_db.get("referencias", "")
    
    # Tenta carregar um planejamento já salvo para não perder edições
    plano_salvo = utils.carregar_planejamento(turma_sel, comp_sel, escala, trimestre_sel)
    
    # Garante que o município venha do perfil carregado (mais confiável que a sessão)
    municipio_atual = perfil_prof.get("municipio", st.session_state.get("municipio", ""))
    
    # --- LÓGICA DE IMPORTAÇÃO DE AULAS DO CSV ---
    aulas_sugeridas = ""
    csv_aulas_path = os.path.join("data", "aulas", "lista_geral_de_aulas.csv")
    if os.path.exists(csv_aulas_path):
        try:
            df_aulas = pd.read_csv(csv_aulas_path)
            if 'Componente' in df_aulas.columns and 'Nome da Aula' in df_aulas.columns:
                comp_sel_norm = normalizar_texto(comp_sel)
                
                def match_componente(comp_csv):
                    if pd.isna(comp_csv): return False
                    c_norm = normalizar_texto(str(comp_csv))
                    
                    # 1. Busca exata ou substring (Bidirecional)
                    if c_norm in comp_sel_norm or comp_sel_norm in c_norm:
                        return True
                        
                    # 2. Tratamento de Plurais e Variações (Tokenização)
                    tokens_csv = [t.rstrip('S') for t in c_norm.split()]
                    tokens_sel = [t.rstrip('S') for t in comp_sel_norm.split()]
                    
                    if not tokens_csv: return False
                    return all(t in tokens_sel for t in tokens_csv)
                
                df_filtrado = df_aulas[df_aulas['Componente'].apply(match_componente)]
                
                if not df_filtrado.empty:
                    aulas_unicas = df_filtrado['Nome da Aula'].unique()
                    aulas_sugeridas = "\n".join(aulas_unicas)
        except Exception as e:
            print(f"Erro ao carregar lista de aulas: {e}")

    st.divider()
    st.write("### 🏗️ Elementos Estruturantes")
    
    # Se houver plano salvo, usa a competência salva, senão usa a padrão
    valor_comp_especifica = plano_salvo.get("competencia_especifica", competencia_especifica_db) if plano_salvo else competencia_especifica_db
    # Tenta recuperar competência geral se existir, senão deixa vazio para preenchimento
    valor_comp_geral = plano_salvo.get("competencia_geral", "") if plano_salvo else ""

    col_struc1, col_struc2 = st.columns(2)
    with col_struc1:
        comp_geral = st.text_area("Competência Geral (BNCC)", value=valor_comp_geral, height=150, placeholder="Insira as Competências Gerais da BNCC...")
    with col_struc2:
        comp_especifica = st.text_area("Competência Específica", value=valor_comp_especifica, height=150)
    
    # Campo opcional para lista de aulas
    valor_lista_aulas = ""
    if plano_salvo and plano_salvo.get("lista_aulas"):
        valor_lista_aulas = plano_salvo.get("lista_aulas")
    elif aulas_sugeridas:
        valor_lista_aulas = aulas_sugeridas
        st.info(f"📂 Encontrei {len(aulas_sugeridas.splitlines())} aulas no repositório para **{comp_sel}**. Elas foram listadas abaixo.")

    lista_aulas = st.text_area("Lista de Aulas (Opcional)", value=valor_lista_aulas, height=120, placeholder="Cole aqui uma lista de aulas ou tópicos, um por linha. Se preenchido, isso substituirá os conteúdos do currículo para gerar o detalhamento abaixo.")

    # Se o usuário preencheu a lista de aulas, usa ela como "objetos de conhecimento"
    if lista_aulas.strip():
        objetos = [linha.strip() for linha in lista_aulas.strip().split('\n') if linha.strip()]

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

        # --- Bloco Comum de Cálculo de Janela de Visualização ---
        tipo_curso = cfg_comp.get("tipo_curso", "Regular")
        duracao_semanas_componente = dados_agendamento.get("duracao", 40)
        aulas_semana = cfg_comp.get("aulas_por_semana", 1)

        # Define a semana de início e fim da visualização (absolutas, base 0)
        view_start_week = max(dados_agendamento.get("inicio", 0), tri_inicio)
        view_end_week = min(dados_agendamento.get("fim", 40), tri_fim)

        # Calcula a duração em semanas a ser exibida
        duracao_view = view_end_week - view_start_week
        total_aulas_no_trimestre = duracao_view * aulas_semana
        total_aulas_componente = duracao_semanas_componente * aulas_semana
        
        col_info1, col_info2 = st.columns([3, 1])
        col_info1.info(f"📅 **{tipo_curso}** | Duração no trimestre: {duracao_view} semanas.")
        col_info2.metric("Aulas Previstas no Trimestre", total_aulas_no_trimestre)
        
        # Calcula a data de início da primeira semana a ser exibida
        offset_view_weeks = view_start_week - tri_inicio
        data_inicio_view = data_inicio_trimestre + timedelta(weeks=offset_view_weeks)
        data_inicio_view = data_inicio_view - timedelta(days=data_inicio_view.weekday())
        
        meses_pt = {1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"}
        
        if not objetos: objetos = ["Conteúdo Programático a definir"]
        habilidade_base = competencia_especifica_db if competencia_especifica_db else "Habilidade a desenvolver"

        # --- Lógica Específica da Escala ---
        if escala == "Semanal":
            if conteudo_csv: st.success("✅ Sugestão automática carregada de arquivo CSV.")
            elif conteudo_db: st.success("✅ Sugestão automática carregada com base no Currículo Oficial.")
            
            for i in range(duracao_view):
                sem = (view_start_week + i) - dados_agendamento.get("inicio", 0) + 1

                data_inicio_semana = data_inicio_view + timedelta(weeks=i)
                data_fim_semana = data_inicio_semana + timedelta(days=4)
                periodo_semana = f"{data_inicio_semana.strftime('%d/%m')} a {data_fim_semana.strftime('%d/%m')}"

                aula_inicio_sem = (sem - 1) * aulas_semana
                aula_fim_sem = aula_inicio_sem + aulas_semana - 1
                
                idx_obj_inicio = math.floor(aula_inicio_sem * len(objetos) / total_aulas_componente) if total_aulas_componente > 0 else 0
                idx_obj_fim = math.floor(aula_fim_sem * len(objetos) / total_aulas_componente) if total_aulas_componente > 0 else 0
                idx_obj_inicio = min(idx_obj_inicio, len(objetos) - 1)
                idx_obj_fim = min(idx_obj_fim, len(objetos) - 1)

                conteudos_semana = list(dict.fromkeys(objetos[idx_obj_inicio : idx_obj_fim + 1]))
                obj_atual = " / ".join(conteudos_semana)

                habilidades_semana = []
                if habilidades_raw:
                    for idx in range(idx_obj_inicio, idx_obj_fim + 1):
                        hab_item = habilidades_raw[idx % len(habilidades_raw)]
                        hab_texto = str(hab_item.get('descricao', '')) if isinstance(hab_item, dict) else str(hab_item)
                        if hab_texto and hab_texto not in habilidades_semana:
                            habilidades_semana.append(hab_texto)
                
                hab_final = " | ".join(habilidades_semana) if habilidades_semana else habilidade_base
                
                linhas.append({
                    "Semana": periodo_semana,
                    "Habilidade": hab_final,
                    "Habilidades Integradas": "",
                    "Objetivos de Aprendizagem": f"Compreender e aplicar {obj_atual}",
                    "Objeto do Conhecimento": obj_atual,
                    "Metodologia": "Aula Prática / Hands-on",
                    "Material de Apoio": "Laboratório, Computador, Projetor",
                    "Estratégia de Avaliação": "Entrega de artefatos técnicos"
                })
                
        elif escala == "Mensal":
            mes_sel = st.selectbox("Mês", ["Fevereiro", "Março", "Abril", "Maio"])
            linhas.append({
                "Período": mes_sel,
                "Habilidade": habilidade_base,
                "Habilidades Integradas": "",
                "Objetivos de Aprendizagem": "Desenvolver as competências técnicas do mês",
                "Objeto do Conhecimento": " / ".join(objetos[:2]),
                "Metodologia": "PBL - Aprendizagem Baseada em Projetos",
                "Material de Apoio": "Livro Didático, Slides",
                "Estratégia de Avaliação": "Atividade Prática e Teórica"
            })
            
        else:  # Trimestral
            for i in range(duracao_view):
                sem = (view_start_week + i) - dados_agendamento.get("inicio", 0) + 1

                for aula_num in range(1, aulas_semana + 1):
                    data_inicio_semana = data_inicio_view + timedelta(weeks=i)
                    data_fim_semana = data_inicio_semana + timedelta(days=4)
                    
                    mes_nome = meses_pt.get(data_inicio_semana.month, "")
                    if data_inicio_semana.month != data_fim_semana.month:
                        mes_nome = f"{meses_pt.get(data_inicio_semana.month, '')}/{meses_pt.get(data_fim_semana.month, '')}"

                    aula_indice_geral = (sem - 1) * aulas_semana + (aula_num - 1)
                    idx_obj = math.floor(aula_indice_geral * len(objetos) / total_aulas_componente) if total_aulas_componente > 0 else 0
                    idx_obj = min(idx_obj, len(objetos) - 1)
                    obj_atual = objetos[idx_obj]

                    hab_texto = habilidade_base
                    if habilidades_raw:
                        hab_item = habilidades_raw[idx_obj % len(habilidades_raw)]
                        if isinstance(hab_item, dict):
                            hab_texto = f"{hab_item.get('codigo', '')} - {hab_item.get('descricao', '')}"
                        else:
                            hab_texto = str(hab_item)
                    
                    if not hab_texto: hab_texto = habilidade_base
                    
                    linhas.append({
                        "Mês": mes_nome,
                        "Semana": f"{data_inicio_semana.strftime('%d/%m')} a {data_fim_semana.strftime('%d/%m')}",
                        "Aula": f"Aula {aula_num}",
                        "Habilidade": hab_texto,
                        "Habilidades Integradas": "",
                        "Objetivos de Aprendizagem": f"Compreender e aplicar {obj_atual}",
                        "Objeto do Conhecimento": obj_atual,
                        "Metodologia": "Projetos Práticos" if "Modular" in tipo_curso else "Ensino Híbrido",
                        "Material de Apoio": "Recursos Digitais, Quadro",
                        "Estratégia de Avaliação": "Avaliação Contínua"
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
                "competencia_especifica": comp_especifica,
                "lista_aulas": lista_aulas,
                "planilha": df_editado.to_dict(orient="records")
            }
            utils.salvar_planejamento(plano_save)
            st.success("✅ Planejamento salvo com sucesso! Você pode fechar e voltar depois.")
    with c2:
        # Passando comp_especifica como principal para o documento, ou concatenando
        comp_texto_doc = f"Competência Geral: {comp_geral}\n\nCompetência Específica: {comp_especifica}"
        docx_bytes = utils.gerar_docx_planejamento(escola, professor, turma_sel, comp_sel, escala, comp_texto_doc, df_editado, trimestre_sel, municipio_atual, lista_aulas)
        
        st.download_button(
            label="📄 Baixar DOCX",
            data=docx_bytes,
            file_name=f"planejamento_{turma_sel}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    with c3:
        comp_texto_doc = f"Competência Geral: {comp_geral}\n\nCompetência Específica: {comp_especifica}"
        pdf_bytes = utils.gerar_pdf_planejamento(escola, professor, turma_sel, comp_sel, escala, comp_texto_doc, df_editado, trimestre_sel, municipio_atual, lista_aulas)
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
                "comp_especifica": comp_especifica,
                "municipio": municipio_atual,
                "lista_aulas": lista_aulas,
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

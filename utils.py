import streamlit as st
import json
import os
from fpdf import FPDF
import io
from pypdf import PdfWriter, PdfReader
import pandas as pd
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import date

# --- Integração com Google Drive ---
try:
    import google_storage
    HAS_GOOGLE_STORAGE = True
except ImportError:
    HAS_GOOGLE_STORAGE = False

try:
    # Se a variável de ambiente estiver definida (pelo run.bat), força local
    if os.environ.get("FORCE_LOCAL_MODE") == "1":
        USE_CLOUD_STORAGE = False
    else:
        USE_CLOUD_STORAGE = (
            HAS_GOOGLE_STORAGE and
            st.secrets.get("drive", {}).get("usar_nuvem", False)
        )
except Exception:
    USE_CLOUD_STORAGE = False

def aplicar_estilo():
    """Aplica o CSS global baseado nas configurações de sessão."""
    tema = st.session_state.get('tema', "Padrão")
    tamanho_fonte = st.session_state.get('tamanho_fonte', 16)
    
    padding_top = "0rem" if tema == "Compacto" else "2rem"
    font_style = "Arial Narrow" if tema == "Compacto" else "sans-serif"
    
    st.markdown(f"""
        <style>
        html, body, [class*="st-"] {{
            font-size: {tamanho_fonte}px;
            font-family: {font_style};
        }}
        .main .block-container {{
            padding-top: {padding_top};
        }}
        /* Ajuste para as tabelas não ficarem gigantes */
        .stDataFrame div[data-testid="stTable"] {{
            font-size: {tamanho_fonte - 2}px;
        }}
        
        /* Ocultar elementos de UI do Streamlit que são em inglês */
        /* #MainMenu {{visibility: hidden;}} */
        footer {{visibility: hidden;}}
        /* [data-testid="stToolbar"] {{visibility: hidden;}} */

        /* Correção para Mobile: Forçar exibição do botão de menu */
        @media (max-width: 768px) {{
            [data-testid="stSidebarCollapsedControl"] {{
                visibility: visible !important;
                display: block !important;
            }}
        }}
        </style>
        """, unsafe_allow_html=True)

def carregar_dados():
    """[DEPRECATED] Carrega o arquivo ementas.json da pasta data."""
    caminho = os.path.join("data", "ementas.json")
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    return {}

def carregar_ementas_oficiais():
    """[DEPRECATED] Carrega o arquivo ementas_oficiais.json da pasta data."""
    caminho = os.path.join("data", "ementas_oficiais.json")
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    return {}

def carregar_ementas_trimestre():
    """[DEPRECATED] Carrega o arquivo ementas_geral_1trimestre.json da pasta data."""
    caminho = os.path.join("data", "ementas_geral_1trimestre.json")
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    return {}

def carregar_escola_db():
    """Carrega o banco de dados da escola (escola_db.json) do local ou da nuvem."""
    filename = "escola_db.json"
    default_data = {"turmas": {}, "professores": []}
    
    data = default_data
    if USE_CLOUD_STORAGE:
        data = google_storage.load_json(filename, default_value=default_data)
    else:
        caminho = os.path.join("data", filename)
        if os.path.exists(caminho):
            try:
                with open(caminho, "r", encoding="utf-8-sig") as f:
                    content = f.read()
                    if content:
                        data = json.loads(content)
            except json.JSONDecodeError:
                st.warning(f"⚠️ Arquivo `{filename}` está mal formatado. Usando dados padrão.")
                data = default_data
    
    # --- AUTO-CORREÇÃO: Sincronizar com alunos.json se não houver turmas ---
    # Se o escola_db não tiver turmas, tenta pegar do alunos.json
    if not data.get("turmas"):
        alunos = carregar_alunos()
        if alunos:
            turmas_novas = {}
            for turma in alunos.keys():
                turmas_novas[turma] = {"componentes": []}
            data["turmas"] = turmas_novas
            # Opcional: Salvar essa inferência de volta para persistir
            # salvar_escola_db(data) 
            
    return data

def salvar_escola_db(dados):
    """Salva o arquivo escola_db.json no local ou na nuvem."""
    filename = "escola_db.json"
    
    if USE_CLOUD_STORAGE:
        google_storage.save_json(filename, dados)
    else:
        caminho = os.path.join("data", filename)
        os.makedirs("data", exist_ok=True)
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)

def carregar_calendario_letivo():
    """Carrega o arquivo calendario_letivo_2026.json da pasta data."""
    caminho = os.path.join("data", "calendario_letivo_2026.json")
    # Padrão de fallback (Bússola do Tempo padrão)
    padrao = {
        "trimestres": {
            "1º": {"inicio": "2026-02-19", "fim": "2026-05-22", "semana_inicio": 0, "semana_fim": 13},
            "2º": {"inicio": "2026-05-25", "fim": "2026-08-28", "semana_inicio": 13, "semana_fim": 26},
            "3º": {"inicio": "2026-08-31", "fim": "2026-12-18", "semana_inicio": 26, "semana_fim": 40}
        }
    }
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8-sig") as f:
            try:
                return json.load(f)
            except:
                return padrao
    return padrao

def carregar_curriculo_db():
    """Carrega o banco de dados do currículo (curriculo_db.json) do local ou da nuvem."""
    filename = "curriculo_db.json"
    default_data = {"BASICO": {}, "APROFUNDAMENTO": {}, "EPT": {}}
    
    if USE_CLOUD_STORAGE:
        return google_storage.load_json(filename, default_value=default_data)
        
    caminho = os.path.join("data", filename)
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    return default_data

def carregar_habilidades_csv():
    """Carrega habilidades de arquivos CSV na pasta data."""
    dados_csv = {}
    caminho_dir = "data"
    if not os.path.exists(caminho_dir):
        return dados_csv
        
    arquivos = [f for f in os.listdir(caminho_dir) if f.startswith("habilidades") and f.endswith(".csv")]
    
    for arquivo in arquivos:
        try:
            df = pd.read_csv(os.path.join(caminho_dir, arquivo))
            # Normaliza colunas para minúsculas e sem espaços
            df.columns = [c.lower().strip() for c in df.columns]
            
            if 'componente' in df.columns:
                for _, row in df.iterrows():
                    comp = str(row['componente']).strip()
                    
                    if comp not in dados_csv:
                        dados_csv[comp] = {"competencia": "", "habilidades": [], "objetos": []}
                    
                    # Preenche competência (pega a primeira não nula encontrada)
                    if 'competencia' in df.columns and pd.notna(row['competencia']) and not dados_csv[comp]["competencia"]:
                        dados_csv[comp]["competencia"] = row['competencia']
                        
                    if 'habilidade' in df.columns and pd.notna(row['habilidade']):
                        h = row['habilidade']
                        if h not in dados_csv[comp]["habilidades"]:
                            dados_csv[comp]["habilidades"].append(h)
                            
                    col_obj = 'objeto_conhecimento' if 'objeto_conhecimento' in df.columns else 'conteudo'
                    if col_obj in df.columns and pd.notna(row[col_obj]):
                        o = row[col_obj]
                        if o not in dados_csv[comp]["objetos"]:
                            dados_csv[comp]["objetos"].append(o)
        except Exception as e:
            print(f"Erro ao ler {arquivo}: {e}")
            
    return dados_csv

def salvar_ementas_trimestre(dados):
    """[DEPRECATED] Salva o arquivo ementas_geral_1trimestre.json na pasta data."""
    caminho = os.path.join("data", "ementas_geral_1trimestre.json")
    os.makedirs("data", exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

def carregar_config_componentes():
    """Carrega o arquivo config_componentes.json da pasta data (local ou nuvem)."""
    filename = "config_componentes.json"
    default_data = {
        "MAPEAMENTO_POR_CHAVE": {},
        "PADRAO_GERAL": {"tipo_curso": "Anual / Regular", "duracao_semanas": 13},
        "PADRAO_TECNICO_MODULAR": {"tipo_curso": "Modular Mensal (40h)", "duracao_semanas": 5}
    }
    
    if USE_CLOUD_STORAGE:
        return google_storage.load_json(filename, default_value=default_data)
        
    caminho = os.path.join("data", filename)
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    return default_data

def salvar_config_componentes(dados):
    """Salva o arquivo config_componentes.json na pasta data (local ou nuvem)."""
    filename = "config_componentes.json"
    if USE_CLOUD_STORAGE:
        google_storage.save_json(filename, dados)
    else:
        caminho = os.path.join("data", filename)
        os.makedirs("data", exist_ok=True)
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)

def salvar_planejamento(dados):
    """Salva um planejamento específico em data/planejamentos.json (local ou nuvem)."""
    filename = "planejamentos.json"
    
    # Carrega os planejamentos existentes ou cria um novo dicionário
    if USE_CLOUD_STORAGE:
        todos = google_storage.load_json(filename, default_value={})
    else:
        caminho = os.path.join("data", filename)
        if os.path.exists(caminho):
            try:
                with open(caminho, "r", encoding="utf-8-sig") as f:
                    todos = json.load(f)
            except json.JSONDecodeError:
                todos = {}
        else:
            todos = {}
        
    # Chave única para identificar o plano
    trimestre = dados.get("trimestre", "1º")
    chave = f"{dados['turma']}_{dados['componente']}_{dados['escala']}_{trimestre}"
    todos[chave] = dados

    # Salva o arquivo atualizado
    if USE_CLOUD_STORAGE:
        google_storage.save_json(filename, todos)
    else:
        caminho = os.path.join("data", filename)
        os.makedirs("data", exist_ok=True)
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(todos, f, indent=2, ensure_ascii=False)

def carregar_planejamento(turma, componente, escala, trimestre="1º"):
    """Carrega um planejamento específico se existir (local ou nuvem)."""
    filename = "planejamentos.json"
    
    if USE_CLOUD_STORAGE:
        todos = google_storage.load_json(filename, default_value={})
    else:
        caminho = os.path.join("data", filename)
        if os.path.exists(caminho):
            try:
                with open(caminho, "r", encoding="utf-8-sig") as f:
                    todos = json.load(f)
            except json.JSONDecodeError:
                todos = {}
        else:
            return None

    chave = f"{turma}_{componente}_{escala}_{trimestre}"
    return todos.get(chave)

def carregar_alunos():
    """Carrega o arquivo alunos.json da pasta data (local ou nuvem)."""
    filename = "alunos.json"
    if USE_CLOUD_STORAGE:
        return google_storage.load_json(filename, default_value={})
        
    caminho = os.path.join("data", filename)
    if os.path.exists(caminho):
        try:
            with open(caminho, "r", encoding="utf-8-sig") as f:
                content = f.read()
                if content:
                    return json.loads(content)
        except json.JSONDecodeError:
            st.warning(f"⚠️ Arquivo `{filename}` está mal formatado. Nenhum aluno carregado.")
            return {}
    return {}

def salvar_alunos(dados):
    """Salva o arquivo alunos.json na pasta data (local ou nuvem)."""
    filename = "alunos.json"
    if USE_CLOUD_STORAGE:
        return google_storage.save_json(filename, dados)
    else:
        caminho = os.path.join("data", filename)
        os.makedirs("data", exist_ok=True)
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
        return True

def salvar_dados_json(caminho_arquivo, dados_df):
    """Salva um DataFrame em um arquivo JSON (local ou nuvem)."""
    filename = os.path.basename(caminho_arquivo)
    
    if USE_CLOUD_STORAGE:
        # Converte DataFrame para lista de dicionários para ser compatível com JSON
        dados_dict = dados_df.to_dict(orient='records')
        google_storage.save_json(filename, dados_dict)
    else:
        # Salva localmente
        os.makedirs(os.path.dirname(caminho_arquivo), exist_ok=True)
        dados_df.to_json(caminho_arquivo, orient='records', indent=4, force_ascii=False)

def carregar_dados_json(caminho_arquivo):
    """Carrega um DataFrame de um arquivo JSON (local ou nuvem)."""
    filename = os.path.basename(caminho_arquivo)

    if USE_CLOUD_STORAGE:
        # Usa um sentinela para distinguir "arquivo não encontrado" de "arquivo vazio"
        sentinela = {"__arquivo_nao_encontrado__": True}
        dados_dict = google_storage.load_json(filename, default_value=sentinela)
        
        if dados_dict == sentinela:
            return None
            
        if dados_dict is not None:
            # Se o arquivo existe na nuvem mas está vazio, retorna um DF vazio
            if not dados_dict:
                return pd.DataFrame()
            return pd.DataFrame(dados_dict)
        return None # Retorna None se o arquivo não existe na nuvem

    # Lógica local
    if os.path.exists(caminho_arquivo):
        if os.path.getsize(caminho_arquivo) > 0:
            try:
                with open(caminho_arquivo, "r", encoding="utf-8-sig") as f:
                    return pd.DataFrame(json.load(f))
            except (ValueError, json.JSONDecodeError):
                print(f"Aviso: Arquivo JSON local inválido em {caminho_arquivo}.")
                return None
    return None

def listar_arquivos_dados(prefixo):
    """Lista arquivos de dados (frequencia, qualitativo) locais ou na nuvem."""
    arquivos = []
    if USE_CLOUD_STORAGE:
        # Agora busca na subpasta 'data'
        # Nota: list_files_in_subfolder retorna lista de dicts {'id', 'name'}, precisamos filtrar aqui
        todos_arquivos = google_storage.list_files_in_subfolder('data')
        arquivos = [f['name'] for f in todos_arquivos if prefixo in f['name']]
    else:
        if os.path.exists("data"):
            arquivos = [f for f in os.listdir("data") if f.startswith(prefixo) and f.endswith(".json")]
    return arquivos

def listar_pdfs_referencia():
    """Lista PDFs disponíveis na pasta 'pdf' (Nuvem) ou 'data/pdf' (Local)."""
    if USE_CLOUD_STORAGE:
        arquivos = google_storage.list_files_in_subfolder('pdf', 'application/pdf')
        return arquivos # Retorna lista de dicts [{'id':..., 'name':...}]
    else:
        # Modo Local
        caminho_pdf = os.path.join("data", "pdf")
        if not os.path.exists(caminho_pdf):
            os.makedirs(caminho_pdf, exist_ok=True)
        
        arquivos = []
        for f in os.listdir(caminho_pdf):
            if f.lower().endswith(".pdf"):
                arquivos.append({'name': f, 'id': os.path.join(caminho_pdf, f)})
        return arquivos

def extrair_texto_pdf_referencia(file_id_or_path):
    """Extrai texto de um PDF (seja do Drive ou Local)."""
    texto_completo = ""
    try:
        if USE_CLOUD_STORAGE:
            # Baixa bytes do Drive
            pdf_bytes = google_storage.download_file_bytes(file_id_or_path)
            if pdf_bytes:
                reader = PdfReader(pdf_bytes)
                for page in reader.pages:
                    texto_completo += page.extract_text() + "\n"
        else:
            # Lê local
            with open(file_id_or_path, 'rb') as f:
                reader = PdfReader(f)
                for page in reader.pages:
                    texto_completo += page.extract_text() + "\n"
    except Exception as e:
        print(f"Erro ao ler PDF: {e}")
        return ""
        
    return texto_completo

def gerar_docx_planejamento(escola, professor, turma, componente, escala, comp_geral, df, trimestre="1º", municipio=""):
    """Gera o DOCX do planejamento escolar."""
    doc = Document()
    
    # Título
    heading = doc.add_heading('Planejamento Escolar', 0)
    heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Informações
    p = doc.add_paragraph()
    p.add_run(f"Escola: {escola}\n").bold = True
    p.add_run(f"Professor: {professor} | Turma: {turma}\n")
    p.add_run(f"Componente: {componente} | Escala: {escala} | Trimestre: {trimestre} | Município: {municipio}\n")
    
    # Competência
    doc.add_heading('Competência Geral:', level=2)
    doc.add_paragraph(comp_geral)
    
    # Tabela
    if not df.empty:
        t = doc.add_table(rows=1, cols=len(df.columns))
        t.style = 'Table Grid'
        
        # Cabeçalho
        hdr_cells = t.rows[0].cells
        for i, col_name in enumerate(df.columns):
            hdr_cells[i].text = str(col_name)
            hdr_cells[i].paragraphs[0].runs[0].font.bold = True
            
        # Dados
        for _, row in df.iterrows():
            row_cells = t.add_row().cells
            for i, val in enumerate(row):
                row_cells[i].text = str(val)
                
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def gerar_docx_frequencia(turma, data_aula, df):
    """Gera o DOCX da lista de frequência."""
    doc = Document()
    
    heading = doc.add_heading('Lista de Frequência', 0)
    heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    p = doc.add_paragraph()
    p.add_run(f"Turma: {turma}\n").bold = True
    p.add_run(f"Data: {data_aula.strftime('%d/%m/%Y')}")
    
    if not df.empty:
        # Tabela com 3 colunas: Nº, Nome, Assinatura
        t = doc.add_table(rows=1, cols=3)
        t.style = 'Table Grid'
        
        hdr_cells = t.rows[0].cells
        hdr_cells[0].text = "Nº"
        hdr_cells[1].text = "Nome do Aluno"
        hdr_cells[2].text = "Assinatura / Presença"
        
        for cell in hdr_cells:
            cell.paragraphs[0].runs[0].font.bold = True
            
        for _, row in df.iterrows():
            row_cells = t.add_row().cells
            row_cells[0].text = str(row['Nº'])
            row_cells[1].text = str(row['Nome do Aluno'])
            row_cells[2].text = "" # Espaço para assinatura
            
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def gerar_pdf_planejamento(escola, professor, turma, componente, escala, comp_geral, df, trimestre, municipio):
    """Gera o PDF do planejamento escolar."""
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Planejamento Escolar", ln=True, align='C')
    
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Escola: {escola}", ln=True)
    pdf.cell(0, 10, f"Professor: {professor} | Turma: {turma}", ln=True)
    pdf.multi_cell(0, 8, f"Componente: {componente}\nEscala: {escala} | Trimestre: {trimestre} | Município: {municipio}", align='L')
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Competência Geral:", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 5, comp_geral)
    pdf.ln(5)
    
    # Tabela
    if not df.empty:
        pdf.set_font("Arial", 'B', 8)
        
        # Pesos para distribuição inteligente de largura
        pesos = {
            "Nº": 0.5,
            "Mês": 0.8,
            "Semana": 0.8,
            "Aula": 0.8,
            "Período": 1.5,
            "Habilidade": 3.0,
            "Objetivos": 3.0,
            "Conteúdo": 3.0,
            "Metodologia": 2.0,
            "Avaliação": 2.0
        }
        
        page_width = 277
        total_peso = sum(pesos.get(col, 1.5) for col in df.columns)
        col_widths = {col: (pesos.get(col, 1.5) / total_peso) * page_width for col in df.columns}
    
        for col in df.columns:
            pdf.cell(col_widths[col], 10, str(col), border=1, align='C')
        pdf.ln()

        pdf.set_font("Arial", size=9)
        line_height = 5
        
        for _, row in df.iterrows():
            # Calcula altura máxima da linha
            max_lines = 1
            for col in df.columns:
                text = str(row[col])
                lines = split_into_lines(pdf, text, col_widths[col] - 2, 9)
                max_lines = max(max_lines, len(lines))
            
            row_height = max_lines * line_height
            
            # Checa se a linha cabe na página, se não, adiciona uma nova e redesenha o cabeçalho
            if pdf.get_y() + row_height > pdf.page_break_trigger:
                pdf.add_page(orientation=pdf.cur_orientation)
                pdf.set_font("Arial", 'B', 8)
                for col_header in df.columns:
                    pdf.cell(col_widths[col_header], 10, str(col_header), border=1, align='C')
                pdf.ln()
                pdf.set_font("Arial", size=9)

            
            for col in df.columns:
                text = str(row[col]).replace('\u2013', '-').replace('\u201c', '"').replace('\u201d', '"')
                w = col_widths[col]
                x, y = pdf.get_x(), pdf.get_y()
                pdf.rect(x, y, w, row_height) # Borda
                pdf.multi_cell(w, line_height, text, border=0, align='L') # Texto
                pdf.set_xy(x + w, y) # Próxima célula
            
            pdf.ln(row_height)
    return bytes(pdf.output())

def gerar_capa_resumo(lista_planos):
    """Gera uma página de capa com o resumo dos planos na cesta."""
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    if not lista_planos:
        return pdf.output(dest='S').encode('latin-1', 'replace')

    # Dados gerais (pega do primeiro plano)
    primeiro = lista_planos[0]
    escola = primeiro.get('escola', '')
    professor = primeiro.get('professor', '')
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 15, "Resumo do Planejamento Integrado", ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, f"Escola: {escola}", ln=True)
    pdf.cell(0, 8, f"Professor: {professor}", ln=True)
    pdf.cell(0, 8, "Início do Ano Letivo: 19/02/2026", ln=True)
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Componentes Curriculares na Cesta:", ln=True)
    
    # Configuração de datas (Via Bússola do Tempo)
    calendario = carregar_calendario_letivo()
    trimestres_data = calendario.get("trimestres", {})
    
    pdf.set_font("Arial", 'B', 10)
    # Cabeçalho da tabela
    pdf.cell(80, 8, "Componente", border=1)
    pdf.cell(50, 8, "Turma", border=1)
    pdf.cell(20, 8, "Trim.", border=1, align='C')
    pdf.cell(40, 8, "Previsão Início", border=1, align='C')
    pdf.ln()
    
    pdf.set_font("Arial", size=9)
    
    for plano in lista_planos:
        comp = str(plano.get('componente', ''))
        turma = str(plano.get('turma', ''))
        trim = str(plano.get('trimestre', '1º'))
        
        data_inicio_str = trimestres_data.get(trim, {}).get("inicio", "2026-02-19")
        try:
            data_str = date.fromisoformat(data_inicio_str).strftime('%d/%m/%Y')
        except ValueError:
            data_str = "19/02/2026"
        
        # Calcula altura da linha baseado no texto (wrap)
        lines_comp = split_into_lines(pdf, comp, 78, 9)
        lines_turma = split_into_lines(pdf, turma, 48, 9)
        max_lines = max(len(lines_comp), len(lines_turma), 1)
        h_line = 6
        h_row = max_lines * h_line
        
        # Verifica quebra de página
        if pdf.get_y() + h_row > 275:
            pdf.add_page()
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(80, 8, "Componente", border=1)
            pdf.cell(50, 8, "Turma", border=1)
            pdf.cell(20, 8, "Trim.", border=1, align='C')
            pdf.cell(40, 8, "Previsão Início", border=1, align='C')
            pdf.ln()
            pdf.set_font("Arial", size=9)
        
        x, y = pdf.get_x(), pdf.get_y()
        
        # Desenha bordas (retângulos) com a altura total da linha
        pdf.rect(x, y, 80, h_row)
        pdf.rect(x+80, y, 50, h_row)
        pdf.rect(x+130, y, 20, h_row)
        pdf.rect(x+150, y, 40, h_row)
        
        # Preenche conteúdo
        pdf.multi_cell(80, h_line, comp, border=0, align='L')
        pdf.set_xy(x + 80, y)
        pdf.multi_cell(50, h_line, turma, border=0, align='L')
        pdf.set_xy(x + 130, y)
        pdf.cell(20, h_row, trim, border=0, align='C')
        pdf.set_xy(x + 150, y)
        pdf.cell(40, h_row, data_str, border=0, align='C')
        
        pdf.set_xy(x, y + h_row) # Move para próxima linha
        
    return bytes(pdf.output())
    
def consolidar_planos(lista_planos):
    """
    Recebe uma lista de dicionários com dados dos planos e gera um único PDF.
    Cada item da lista deve conter: escola, professor, turma, componente, escala, comp_geral, df (DataFrame).
    """
    merger = PdfWriter()
    
    # Adiciona capa com resumo
    if lista_planos:
        capa_bytes = gerar_capa_resumo(lista_planos)
        merger.append(io.BytesIO(capa_bytes))
    
    for plano in lista_planos: #itera sobre os planos da cesta
        escola = plano['escola']
        professor = plano['professor']
        turma = plano['turma']
        componente = plano['componente']
        escala = plano['escala']
        comp_geral = plano['comp_geral']
        df = plano['df']
        municipio = plano.get('municipio', "")  # Retorna string vazia se não existir
        trimestre = plano.get('trimestre', '')
        
        # Cria um dicionário com os argumentos esperados
        args = {
            'escola': escola, 'professor': professor, 'turma': turma,
            'componente': componente, 'escala': escala, 'comp_geral': comp_geral,
            'df': df, 'trimestre': trimestre, 'municipio': municipio
        }

        pdf_bytes = gerar_pdf_planejamento(**args)
        merger.append(io.BytesIO(pdf_bytes))
    
    output_buffer = io.BytesIO()
    merger.write(output_buffer)
    merger.close()
    output_buffer.seek(0)
    return output_buffer

def gerar_pdf_frequencia(escola, professor, turma, data_aula, df):
    """Gera o PDF da lista de frequência com status digital e cabeçalho completo."""
    pdf = FPDF()
    pdf.set_margins(8, 8, 8) # Margens reduzidas para aproveitar a página
    pdf.set_auto_page_break(auto=True, margin=8)
    pdf.add_page()
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, f"Lista de Frequência - {escola}", ln=True, align='C')
    pdf.ln(2)
    
    pdf.set_font("Arial", size=10)
    # pdf.cell(0, 5, f"Escola: {escola}", ln=True) # Removido pois já está no título
    pdf.cell(0, 5, f"Professor: {professor} | Turma: {turma}", ln=True)
    pdf.cell(0, 5, f"Data: {data_aula.strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(3)
    
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(10, 6, "Nº", border=1, align='C')
    pdf.cell(80, 6, "Nome do Aluno", border=1, align='C')
    pdf.cell(20, 6, "Status", border=1, align='C')
    pdf.cell(50, 6, "Assinatura", border=1, align='C')
    pdf.ln()
    
    pdf.set_font("Arial", size=8)
    num_alunos = len(df)
    for _, row in df.iterrows():
        status = "P" if row.get('Presença', False) else "F"
        pdf.cell(10, 6, str(row['Nº']), border=1, align='C')
        pdf.cell(80, 6, str(row['Nome do Aluno']).strip()[:50], border=1)
        pdf.cell(20, 6, status, border=1, align='C')
        pdf.cell(50, 6, "", border=1)  # Adiciona a célula para a assinatura
        pdf.ln()
        
    return bytes(pdf.output())


def gerar_pdf_qualitativo(escola, professor, turma, df, componente="", contexto=""):
    """Gera o PDF da ficha qualitativa."""
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.set_margins(7, 7, 7)
    pdf.set_auto_page_break(auto=True, margin=8)
    pdf.add_page()
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Ficha de Acompanhamento Qualitativo", ln=True, align='C')
    pdf.ln(1)
    
    pdf.set_font("Arial", size=9)
    pdf.cell(0, 5, f"Escola: {escola}", ln=True)
    pdf.cell(0, 5, f"Professor: {professor} | Turma: {turma}", ln=True)
    if componente or contexto:
        pdf.cell(0, 5, f"Componente: {componente} | Contexto: {contexto}", ln=True)
    pdf.ln(1)
    
    pdf.set_font("Arial", 'B', 7)
    pdf.cell(10, 5, "Nº", border=1, align='C')
    pdf.cell(90, 5, "Nome do Estudante", border=1, align='C')
    pdf.cell(18, 5, "Particip.", border=1, align='C')
    pdf.cell(18, 5, "Entrega", border=1, align='C')
    pdf.cell(18, 5, "Autonomia", border=1, align='C')
    pdf.cell(12, 5, "NM1", border=1, align='C')
    pdf.cell(12, 5, "NM2", border=1, align='C')
    pdf.cell(12, 5, "NM3", border=1, align='C')
    pdf.cell(12, 5, "MT", border=1, align='C')
    pdf.cell(12, 5, "Rec.", border=1, align='C')
    pdf.cell(15, 5, "Final", border=1, align='C')
    pdf.ln()
    
    pdf.set_font("Arial", size=5)
    for _, row in df.iterrows():
        pdf.cell(10, 5, str(row['Nº']), border=1, align='C')
        pdf.cell(90, 5, str(row['Nome do Estudante'])[:50], border=1)
        pdf.cell(18, 5, str(row.get('Participação', ''))[:15], border=1, align='C')
        pdf.cell(18, 5, str(row.get('Entrega', ''))[:15], border=1, align='C')
        pdf.cell(18, 5, str(row.get('Autonomia', ''))[:15], border=1, align='C')
        pdf.cell(12, 5, str(row.get('NM1', '')) if pd.notna(row.get('NM1')) else "", border=1, align='C')
        pdf.cell(12, 5, str(row.get('NM2', '')) if pd.notna(row.get('NM2')) else "", border=1, align='C')
        pdf.cell(12, 5, str(row.get('NM3', '')) if pd.notna(row.get('NM3')) else "", border=1, align='C')
        pdf.cell(12, 5, str(row.get('MT', '')) if pd.notna(row.get('MT')) else "", border=1, align='C')
        pdf.cell(12, 5, str(row.get('Recuperação', '')) if pd.notna(row.get('Recuperação')) else "", border=1, align='C')
        pdf.cell(15, 5, str(row.get('Nota Final', '')) if pd.notna(row.get('Nota Final')) else "", border=1, align='C')
        pdf.ln()
        
    return bytes(pdf.output())


def init_db():
    """[DEPRECATED] Função mantida apenas para compatibilidade, não faz nada."""
    pass

def sincronizar_bd():
    """[DEPRECATED] Função desativada na versão Cloud."""
    return 0

def importar_alunos_db():
    """[DEPRECATED]"""
    return 0

def listar_turmas_db():
    """Lista turmas disponíveis diretamente do JSON de alunos."""
    alunos = carregar_alunos()
    if alunos and isinstance(alunos, dict):
        return sorted(list(alunos.keys()))
    return []

def listar_alunos_turma_db(turma):
    """Retorna lista de alunos de uma turma diretamente do JSON."""
    alunos = carregar_alunos()
    return alunos.get(turma, [])

def carregar_perfil_professor():
    """Carrega o perfil do professor de data/professor_config.json (local ou nuvem)."""
    filename = "professor_config.json"
    if USE_CLOUD_STORAGE:
        return google_storage.load_json(filename, default_value={})
        
    caminho = os.path.join("data", filename)
    if os.path.exists(caminho):
        try:
            with open(caminho, "r", encoding="utf-8-sig") as f:
                content = f.read()
                if content:
                    return json.loads(content)
        except json.JSONDecodeError:
            return {}
    return {}

def salvar_perfil_professor(perfil):
    """Salva o perfil do professor em data/professor_config.json (local ou nuvem)."""
    filename = "professor_config.json"
    
    if USE_CLOUD_STORAGE:
        return google_storage.save_json(filename, perfil)
    else:
        caminho = os.path.join("data", filename)
        os.makedirs("data", exist_ok=True)
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(perfil, f, indent=2, ensure_ascii=False)
        return True

def listar_professores_db():
    """Lista os nomes dos professores cadastrados no escola_db.json."""
    escola_db = carregar_escola_db()
    return escola_db.get("professores", [])

def atualizar_lista_professores_db(novo_professor):
    """Adiciona um novo professor à lista geral em escola_db.json se não existir."""
    escola_db = carregar_escola_db()
    professores = escola_db.get("professores", [])
    
    # Verifica se já existe (case insensitive)
    if novo_professor.upper() not in [p.upper() for p in professores]:
        professores.append(novo_professor)
        professores.sort()
        escola_db["professores"] = professores
        salvar_escola_db(escola_db)

def salvar_professor_config_db(professor, email, municipio, config):
    """
    Salva a configuração do professor em um arquivo JSON específico no Drive.
    Nome do arquivo: perfil_{professor_sanitized}.json
    """
    safe_name = professor.replace(" ", "_").lower()
    filename = f"perfil_{safe_name}.json"
    
    # Adiciona metadados extras
    config["email"] = email
    config["municipio"] = municipio
    
    if USE_CLOUD_STORAGE:
        google_storage.save_json(filename, config)
    else:
        caminho = os.path.join("data", filename)
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

def carregar_perfil_professor_db(nome_professor):
    """Carrega o perfil de um professor específico do arquivo JSON."""
    safe_name = nome_professor.replace(" ", "_").lower()
    filename = f"perfil_{safe_name}.json"
    
    if USE_CLOUD_STORAGE:
        return google_storage.load_json(filename, default_value={})
    
    caminho = os.path.join("data", filename)
    if os.path.exists(caminho):
        try:
            with open(caminho, "r", encoding="utf-8-sig") as f:
                content = f.read()
                if content:
                    return json.loads(content)
        except json.JSONDecodeError:
            st.warning(f"⚠️ Arquivo de perfil `{filename}` está mal formatado.")
            return {}
    return {}

def split_into_lines(pdf, text, width, font_size):
    """Splits text into multiple lines based on the available width."""
    pdf.set_font("Arial", size=font_size)
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = f"{current_line} {word}".strip()
        if pdf.get_string_width(test_line) < width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line.strip())
    return lines

def cell_with_textwrap(pdf, w, h, text, border=0, align='L'):
    """Wrap text within a cell."""
    x = pdf.get_x()
    y = pdf.get_y()
    pdf.multi_cell(w, h, str(text), border=border, align=align)
    pdf.set_xy(x + w, y)

def gerar_pdf_aula_ia(texto_markdown):
    """Gera um PDF a partir do texto Markdown gerado pela IA."""
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    
    # --- SUPORTE A FONTE EXTERNA (TTF) ---
    font_dir = os.path.join("data", "fonts")
    font_regular = os.path.join(font_dir, "DejaVuSans.ttf")
    font_bold = os.path.join(font_dir, "DejaVuSans-Bold.ttf")
    font_italic = os.path.join(font_dir, "DejaVuSans-Oblique.ttf")
    
    # Download automático da fonte se não existir
    try:
        if not os.path.exists(font_regular) or not os.path.exists(font_bold) or not os.path.exists(font_italic):
            import urllib.request
            os.makedirs(font_dir, exist_ok=True)
            base_url = "https://raw.githubusercontent.com/dejavu-fonts/dejavu-fonts/master/ttf/"
            
            if not os.path.exists(font_regular):
                print(f"Baixando {font_regular}...")
                urllib.request.urlretrieve(base_url + "DejaVuSans.ttf", font_regular)
            if not os.path.exists(font_bold):
                print(f"Baixando {font_bold}...")
                urllib.request.urlretrieve(base_url + "DejaVuSans-Bold.ttf", font_bold)
            if not os.path.exists(font_italic):
                print(f"Baixando {font_italic}...")
                urllib.request.urlretrieve(base_url + "DejaVuSans-Oblique.ttf", font_italic)
    except Exception as e:
        print(f"Aviso: Não foi possível baixar as fontes automaticamente: {e}")

    font_family = "Arial"
    
    if os.path.exists(font_regular):
        try:
            pdf.add_font('DejaVu', '', font_regular)
            if os.path.exists(font_bold):
                pdf.add_font('DejaVu', 'B', font_bold)
            else:
                pdf.add_font('DejaVu', 'B', font_regular)
            
            if os.path.exists(font_italic):
                pdf.add_font('DejaVu', 'I', font_italic)
            else:
                pdf.add_font('DejaVu', 'I', font_regular)
                
            font_family = "DejaVu"
        except Exception as e:
            print(f"Erro ao carregar fonte externa, usando Arial: {e}")

    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    lines = texto_markdown.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            pdf.ln(2)
            continue
            
        if line.startswith('# '):
            pdf.set_font(font_family, 'B', 16)
            pdf.multi_cell(0, 10, line.replace('# ', '').replace('**', ''), align='C')
            pdf.ln(5)
        elif line.startswith('## '):
            pdf.set_font(font_family, 'B', 14)
            pdf.ln(3)
            pdf.multi_cell(0, 8, line.replace('## ', '').replace('**', ''), align='L')
            pdf.ln(2)
        elif line.startswith('### '):
            pdf.set_font(font_family, 'B', 12)
            pdf.ln(2)
            pdf.multi_cell(0, 7, line.replace('### ', '').replace('**', ''), align='L')
            pdf.ln(1)
        elif line.startswith('> '):
            pdf.set_font(font_family, 'I', 10)
            pdf.set_text_color(80, 80, 80)
            pdf.set_x(20)
            pdf.multi_cell(0, 6, line.replace('> ', '').replace('**', ''))
            pdf.set_text_color(0, 0, 0)
            pdf.ln(2)
        elif line.startswith('---'):
            y = pdf.get_y()
            pdf.line(10, y, 200, y)
            pdf.ln(5)
        elif line.startswith('**') and ':**' in line:
            parts = line.split(':**', 1)
            if len(parts) == 2:
                key = parts[0].replace('**', '') + ':'
                val = parts[1].strip().replace('**', '')
                pdf.set_font(font_family, 'B', 11)
                pdf.write(6, key + ' ')
                pdf.set_font(font_family, '', 11)
                pdf.write(6, val)
                pdf.ln(6)
            else:
                pdf.set_font(font_family, '', 11)
                pdf.multi_cell(0, 6, line.replace('**', ''))
        elif line.startswith('- ') or line.startswith('* '):
            pdf.set_font(font_family, '', 11)
                # Indentação para lista usando cell em vez de write para evitar erros de cursor
            pdf.set_x(pdf.l_margin + 5)
            pdf.cell(5, 6, '-', align='C')
            pdf.multi_cell(0, 6, line[2:].replace('**', ''))
        else:
            pdf.set_font(font_family, '', 11)
            pdf.set_x(pdf.l_margin) # Garante que começa na margem esquerda
            pdf.multi_cell(0, 6, line.replace('**', ''))
            
    return bytes(pdf.output())

def carregar_horario_global():
    """Carrega o quadro de horários completo da escola."""
    filename = "horario_global.json"
    if USE_CLOUD_STORAGE:
        return google_storage.load_json(filename, default_value={})
    
    caminho = os.path.join("data", filename)
    if os.path.exists(caminho):
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def obter_horario_professor_do_global(nome_professor):
    """
    Filtra o horário global para encontrar as aulas de um professor específico.
    Retorna uma lista de dicionários formatada para DataFrame.
    """
    global_db = carregar_horario_global()
    aulas_prof = []
    
    # Mapeamento de ordem para ordenação
    ordem_dias = {"SEGUNDA- FEIRA": 1, "SEGUNDA-FEIRA": 1, "TERÇA-FEIRA": 2, "QUARTA-FEIRA": 3, "QUINTA-FEIRA": 4, "SEXTA-FEIRA": 5}
    
    for dia, periodos in global_db.items():
        for periodo, salas in periodos.items():
            for sala, dados in salas.items():
                # Verifica se o nome do professor está contido no registro (busca flexível)
                prof_db = dados.get("professor", "").lower()
                if nome_professor.lower() in prof_db or prof_db in nome_professor.lower():
                    aulas_prof.append({
                        "Dia": dia,
                        "OrdemDia": ordem_dias.get(dia, 9),
                        "Período": periodo,
                        "Horário": dados.get("horario", ""),
                        "Sala": sala,
                        "Disciplina": dados.get("disciplina", "")
                    })
    
    # Ordena por Dia e depois por Período
    aulas_prof.sort(key=lambda x: (x["OrdemDia"], x["Período"]))
    return aulas_prof

def criar_botao_voltar():
    """Cria um botão padronizado para voltar ao menu principal."""
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🏠 Voltar para o Menu Principal", use_container_width=True):
            st.switch_page("app.py")
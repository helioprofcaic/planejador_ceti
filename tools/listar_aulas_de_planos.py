import os
import pandas as pd
import re

def rotular_componente_por_caminho(path_str):
    """Tenta identificar o componente curricular com base em palavras-chave no caminho do arquivo."""
    # 1. Prioridade: Padrão de nome de arquivo "Nome_Componente_(Turma).md"
    filename = os.path.basename(path_str)
    match = re.match(r"^(.*)[_\s]\((.*)\)\.md$", filename, re.IGNORECASE)
    if match:
        comp_nome = match.group(1).replace('_', ' ').strip().title()
        turma_nome = match.group(2).replace('_', ' ').strip().upper()
        return f"{comp_nome} ({turma_nome})"

    path_lower = path_str.lower().replace('\\', '/') # Normaliza para lower e com /
    parts = path_lower.split('/')
    
    comp_identificado = None
    
    # Mapeamento de palavras-chave para nomes de componentes
    mapa_componentes = {
        'robotica': 'Robótica',
        'programacao estruturada': 'Programação Estruturada',
        'poo': 'Programação Orientada a Objetos',
        'orientada a objetos': 'Programação Orientada a Objetos',
        'web': 'Programação Web',
        'front-end': 'Programação Web',
        'mentoria': 'Mentorias Tec',
        "MENTORIA": 'Mentorias Tec II', 
        "MENTORIA TEC": 'Mentorias Tec II',
        "MENTORIA TEC II": 'Mentorias Tec II',
        "MENTORIA TEC II (2Ano DS)": 'Mentorias Tec II',
        'Mentorias Tec II (2Ano DS)': 'Mentorias Tec II',
        'pensamento computacional': 'Pensamento Computacional',
        'inteligencia artificial': 'Inteligência Artificial',
        'ia': 'Inteligência Artificial',
        'computacao': 'Computação',
        'iot': 'Internet das Coisas',
        'devops': 'DevOps',
        'seguranca': 'Segurança de Dados',
        'teste': 'Teste de Sistemas',
        'microsservicos': 'Microsserviços',
        'ux': 'UI/UX',
        'ui': 'UI/UX',
        'empreendedorismo': 'Empreendedorismo',
        'projeto integrador': 'Projeto Integrador',
    }

    for chave, valor in mapa_componentes.items():
        if chave in path_lower:
            comp_identificado = valor
            break
            
    # Fallback: Pega o nome da pasta pai se nenhum rótulo for encontrado
    if not comp_identificado:
        if len(parts) >= 2:
            comp_identificado = parts[-2].replace('_', ' ').replace('-', ' ').title()
        else:
            comp_identificado = "Não Identificado"

    # Tenta identificar a turma pela estrutura de pastas
    turma_identificada = ""
    for part in reversed(parts[:-1]):
        if part in ['data', 'planejamento', 'aulas']: continue
        if comp_identificado.lower() in part.replace('_', ' '): continue
        
        # Heurística simples para identificar turma
        if any(x in part for x in ['ano', 'serie', 'turma', '1', '2', '3', '9']):
            turma_identificada = part.replace('_', ' ').replace('-', ' ').title()
            # Normalização básica
            turma_identificada = turma_identificada.replace("9ano", "9º Ano").replace("1serie", "1ª Série").replace("2serie", "2ª Série").replace("3serie", "3ª Série")
            break
            
    if turma_identificada:
        return f"{comp_identificado} ({turma_identificada})"
        
    return comp_identificado

def parse_aulas_from_md(filepath, base_dir):
    """
    Analisa um arquivo Markdown de aula/roteiro e extrai uma lista de nomes de aulas,
    incluindo o prefixo "Aula XX" quando presente. Retorna também o caminho e um rótulo de componente.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"    - Erro ao ler o arquivo {filepath}: {e}")
        return []

    aulas_encontradas = []
    
    # Caminho relativo para facilitar a leitura no CSV
    caminho_relativo = os.path.relpath(filepath, base_dir)
    componente_rotulado = rotular_componente_por_caminho(caminho_relativo)

    # --- NOVO: Extrair Objetivos ---
    objetivos = ""
    # Estratégia em duas partes para mais robustez
    # 1. Encontrar o início da seção de Objetivos
    match_inicio = re.search(r'^(##\s*.*Objetivos.*|\*\*Objetivos:?\*\*)$', content, re.MULTILINE | re.IGNORECASE)

    if match_inicio:
        # Pega todo o conteúdo a partir do início da seção de objetivos
        conteudo_a_partir_dos_objetivos = content[match_inicio.end():]

        # 2. Encontrar o início da PRÓXIMA seção (## ou ---)
        match_fim = re.search(r'^\s*(##|---)', conteudo_a_partir_dos_objetivos, re.MULTILINE)

        objetivos_bruto = ""
        if match_fim:
            # Se encontrou o fim, pega o texto entre os dois
            objetivos_bruto = conteudo_a_partir_dos_objetivos[:match_fim.start()].strip()
        else:
            # Se não, pega tudo até o final do arquivo
            objetivos_bruto = conteudo_a_partir_dos_objetivos.strip()

        if objetivos_bruto:
            # Remove frases introdutórias comuns (ex: "Ao final desta aula...")
            objetivos_bruto = re.sub(r'^.*?Ao final desta aula.*?(?::|\n)', '', objetivos_bruto, flags=re.IGNORECASE | re.DOTALL).strip()

            # Substitui marcadores de lista (*, -) por pipes
            objetivos = re.sub(r'(?:\n|^)\s*[\*\-]\s+', ' | ', objetivos_bruto)

            # Limpeza geral de quebras de linha e espaços
            objetivos = objetivos.replace('\n', ' ')
            objetivos = re.sub(r'\s+', ' ', objetivos)
            objetivos = re.sub(r'\s*\|\s*', ' | ', objetivos)
            objetivos = objetivos.strip(' |').strip()

    # Regex para capturar o nome completo da aula em linhas que contenham a palavra "Aula"
    # Suporta listas (*, -) e títulos (#)
    padrao_aula = re.compile(r'^(?:[\*\-]\s+|#+\s+)(.*?(?:Aula(?:s)?\s*.*))', re.MULTILINE | re.IGNORECASE)

    matches = padrao_aula.findall(content)
    if matches:
        for nome in matches:
            nome_limpo = nome.strip().replace('**', '')
            # Remove leading emojis/symbols that might be part of the heading/list item
            nome_limpo = re.sub(r'^(?:[\U0001F000-\U0001F9FF]|\s|#|\*|\-|\.)+', '', nome_limpo).strip()
            if nome_limpo:
                aulas_encontradas.append({
                    'Componente': componente_rotulado,
                    'Nome da Aula': nome_limpo,
                    'Objetivos': objetivos,
                    'Arquivo': caminho_relativo,
                })
    else:
        # Fallback: Tenta pegar o título principal se não achar "Aula" explícito
        tema_principal = (re.search(r'^#+ 🎨 (.*)', content, re.MULTILINE) or 
                          re.search(r'^#+ (.*)', content, re.MULTILINE) or 
                          ['',''])[1].strip()
        
        if tema_principal:
            # Se o título principal for o nome da aula, adiciona-o.
            tema_principal_limpo = re.sub(r'^(?:[\U0001F000-\U0001F9FF]|\s|#|\*|\-|\.)+', '', tema_principal).strip()
            if tema_principal_limpo:
                aulas_encontradas.append({
                'Componente': componente_rotulado,
                'Nome da Aula': tema_principal_limpo,
                'Objetivos': objetivos,
                'Arquivo': caminho_relativo,
            })
        else:
            # Último recurso: usa o nome do arquivo se não achar título
            nome_arquivo = os.path.splitext(os.path.basename(filepath))[0].replace('_', ' ')
            aulas_encontradas.append({
                'Componente': componente_rotulado,
                'Nome da Aula': nome_arquivo,
                'Objetivos': objetivos,
                'Arquivo': caminho_relativo,
            })

    return aulas_encontradas

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Procura APENAS na pasta de planejamento
    input_dir = os.path.join(base_dir, "data", "planejamento")
    
    output_dir = os.path.join(base_dir, "data", "aulas")
    output_csv_path = os.path.join(output_dir, "lista_geral_de_aulas.csv")

    os.makedirs(output_dir, exist_ok=True)
    all_aulas_data = []
    
    print(f"🔎 Iniciando varredura de arquivos .md...")

    if not os.path.exists(input_dir):
        print(f"❌ Erro: O diretório de entrada '{input_dir}' não foi encontrado.")
        return
        
    print(f"  -> Varrendo pasta: '{os.path.relpath(input_dir, base_dir)}'")
    for root, _, files in os.walk(input_dir):
        for filename in sorted(files):
            if filename.lower().endswith(".md"):
                filepath = os.path.join(root, filename)
                dados_aulas = parse_aulas_from_md(filepath, base_dir)
                if dados_aulas:
                    all_aulas_data.extend(dados_aulas)

    if not all_aulas_data:
        print("⚠️ Nenhuma aula encontrada nos arquivos .md.")
        return

    df = pd.DataFrame(all_aulas_data)
    # Organiza as colunas
    df = df[['Componente', 'Nome da Aula', 'Objetivos']]
    df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')

    print(f"\n✅ Processo concluído! {len(all_aulas_data)} aulas foram compiladas.")
    print(f"CSV salvo em: '{output_csv_path}'")

if __name__ == "__main__":
    main()
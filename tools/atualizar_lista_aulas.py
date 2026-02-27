import pandas as pd
import json
import os
import unicodedata

# --- CONFIGURAÇÃO ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "aulas", "lista_geral_de_aulas.csv")
CURRICULO_PATH = os.path.join(BASE_DIR, "data", "curriculo_db.json")

def normalizar_texto(texto):
    """Remove acentos e padroniza para maiúsculas."""
    if not texto or pd.isna(texto): return ""
    return ''.join(c for c in unicodedata.normalize('NFD', str(texto))
                  if unicodedata.category(c) != 'Mn').upper()

def buscar_dados_curriculo(nome_comp, curriculo_db):
    """Busca dados do componente no currículo."""
    if not curriculo_db or not nome_comp:
        return {}

    nome_norm = normalizar_texto(nome_comp)

    for secao in ["EPT", "APROFUNDAMENTO", "BASICO"]:
        secao_data = curriculo_db.get(secao, {})
        for db_key, db_val in secao_data.items():
            db_key_norm = normalizar_texto(db_key)
            if nome_norm in db_key_norm or db_key_norm in nome_norm:
                return db_val
    return {}

def rotular_componente_por_caminho(path_str):
    """Tenta identificar o componente curricular com base em palavras-chave no caminho do arquivo."""
    if pd.isna(path_str): return "Não Identificado"
    path_lower = str(path_str).lower().replace('\\', '/')
    parts = path_lower.split('/')
    comp_identificado = None
    
    mapa_componentes = {
        'robotica': 'Robótica',
        'programacao estruturada': 'Programação Estruturada',
        'poo': 'Programação Orientada a Objetos',
        'orientada a objetos': 'Programação Orientada a Objetos',
        'web': 'Programação Web',
        'front-end': 'Programação Web',
        'mentoria': 'Mentoria Tec',
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
            
    # Fallback: Pega o nome da pasta pai
    if not comp_identificado:
        if len(parts) >= 2:
            # Assume estrutura data/aulas/TURMA/COMPONENTE/arquivo.md
            comp_identificado = parts[-2].replace('_', ' ').title()
        else:
            comp_identificado = "Não Identificado"
            
    # Tenta identificar a turma
    turma_identificada = ""
    for part in reversed(parts[:-1]):
        if part in ['data', 'planejamento', 'aulas']: continue
        if comp_identificado and comp_identificado.lower() in part.replace('_', ' '): continue
        
        if any(x in part for x in ['ano', 'serie', 'turma', '1', '2', '3', '9']):
            turma_identificada = part.replace('_', ' ').replace('-', ' ').title()
            turma_identificada = turma_identificada.replace("9ano", "9º Ano").replace("1serie", "1ª Série").replace("2serie", "2ª Série").replace("3serie", "3ª Série")
            break
            
    if turma_identificada:
        return f"{comp_identificado} ({turma_identificada})"
        
    return comp_identificado

def atualizar_csv():
    if not os.path.exists(CSV_PATH):
        print(f"❌ Erro: Arquivo CSV não encontrado em {CSV_PATH}")
        print("Execute primeiro o script 'listar_aulas_de_planos.py'.")
        return

    print(f"📖 Lendo CSV: {CSV_PATH}")
    try:
        df = pd.read_csv(CSV_PATH)
    except Exception as e:
        print(f"❌ Erro ao ler CSV: {e}")
        return

    # Carrega currículo
    curriculo_db = {}
    if os.path.exists(CURRICULO_PATH):
        with open(CURRICULO_PATH, 'r', encoding='utf-8') as f:
            curriculo_db = json.load(f)
    else:
        print("⚠️ Aviso: curriculo_db.json não encontrado.")

    # Garante colunas
    if 'Componente' not in df.columns: df['Componente'] = ""
    if 'Competencia' not in df.columns: df['Competencia'] = ""

    count_comp = 0
    count_competencia = 0

    print("🔄 Processando linhas...")
    for index, row in df.iterrows():
        arquivo = str(row.get('Arquivo', ''))
        comp_atual = str(row.get('Componente', ''))
        
        # 1. Tenta identificar componente se estiver vazio ou genérico
        if not comp_atual or comp_atual == "nan" or comp_atual == "Não Identificado":
            novo_comp = rotular_componente_por_caminho(arquivo)
            if novo_comp != "Não Identificado":
                df.at[index, 'Componente'] = novo_comp
                comp_atual = novo_comp
                count_comp += 1
        
        # 2. Busca competência baseada no componente
        competencia_atual = str(row.get('Competencia', ''))
        if not competencia_atual or competencia_atual == "nan":
            dados = buscar_dados_curriculo(comp_atual, curriculo_db)
            nova_competencia = dados.get("competencia", "")
            if nova_competencia:
                df.at[index, 'Competencia'] = nova_competencia
                count_competencia += 1

    # Salva
    df.to_csv(CSV_PATH, index=False, encoding='utf-8-sig')
    print(f"\n✅ Atualização concluída!")
    print(f"   - Componentes identificados/corrigidos: {count_comp}")
    print(f"   - Competências preenchidas: {count_competencia}")
    print(f"   - Arquivo salvo em: {CSV_PATH}")

if __name__ == "__main__":
    atualizar_csv()
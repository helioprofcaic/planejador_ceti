import json
import os
import pandas as pd
import unicodedata

# --- CONFIGURAÇÃO ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CURRICULO_JSON = os.path.join(BASE_DIR, "data", "curriculo_db.json")
ESCOLA_JSON = os.path.join(BASE_DIR, "data", "escola", "escola_db.json")
CSV_EXPORT = os.path.join(BASE_DIR, "data", "matriz_competencias.csv")

def normalizar_texto(texto):
    """Remove acentos e padroniza para maiúsculas."""
    if not texto: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', str(texto))
                  if unicodedata.category(c) != 'Mn').upper()

def carregar_json(caminho):
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_json(caminho, dados):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

def buscar_dados_curriculo(nome_comp, curriculo_db):
    """Busca dados do componente no currículo e retorna os dados e a seção."""
    if not curriculo_db or not nome_comp:
        return {}, "EPT"

    nome_norm = normalizar_texto(nome_comp)
    
    partial_match_with_content = None
    secao_partial_with_content = None
    exact_match_empty = None
    secao_exact_empty = None
    partial_match_empty = None
    secao_partial_empty = None

    for secao in ["EPT", "APROFUNDAMENTO", "BASICO"]:
        secao_data = curriculo_db.get(secao, {})
        for db_key, db_val in secao_data.items():
            db_key_norm = normalizar_texto(db_key)
            
            has_content = bool(db_val.get("competencia"))

            if nome_norm == db_key_norm:
                if has_content:
                    return db_val, secao # Prioridade máxima
                elif not exact_match_empty:
                    exact_match_empty = db_val
                    secao_exact_empty = secao
            elif (nome_norm in db_key_norm or db_key_norm in nome_norm):
                if has_content and not partial_match_with_content:
                    partial_match_with_content = db_val
                    secao_partial_with_content = secao
                elif not has_content and not partial_match_empty:
                    partial_match_empty = db_val
                    secao_partial_empty = secao
    
    if partial_match_with_content: return partial_match_with_content, secao_partial_with_content
    if exact_match_empty: return exact_match_empty, secao_exact_empty
    if partial_match_empty: return partial_match_empty, secao_partial_empty
    
    return {}, "EPT"

def main():
    print("--- Gerenciador de Currículo e Competências ---")
    
    # 1. Carregar Bancos de Dados
    curriculo_db = carregar_json(CURRICULO_JSON)
    escola_db = carregar_json(ESCOLA_JSON)
    
    # Garante estrutura do currículo
    for secao in ["BASICO", "APROFUNDAMENTO", "EPT"]:
        if secao not in curriculo_db: curriculo_db[secao] = {}

    # 2. Identificar todos os componentes existentes na escola
    todos_componentes = set()
    if "turmas" in escola_db:
        for turma in escola_db["turmas"].values():
            for comp in turma.get("componentes", []):
                todos_componentes.add(comp)
    
    # Adiciona também os que já estão no currículo (caso não estejam em turmas ainda)
    for secao in curriculo_db.values():
        for comp in secao.keys():
            todos_componentes.add(comp)
            
    lista_componentes = sorted(list(todos_componentes))
    print(f"🔎 Total de Componentes identificados: {len(lista_componentes)}")

    # 3. Verificar modo de operação (Importar ou Exportar)
    modo = "exportar"
    if os.path.exists(CSV_EXPORT):
        resposta = input(f"Arquivo '{os.path.basename(CSV_EXPORT)}' encontrado.\nDeseja IMPORTAR as alterações dele para o sistema? (s/n): ").lower()
        if resposta == 's':
            modo = "importar"

    if modo == "exportar":
        # --- EXPORTAÇÃO (JSON -> CSV) ---
        dados_csv = []
        for comp in lista_componentes:
            
            # Busca dados atuais
            dados_encontrados, secao_encontrada = buscar_dados_curriculo(comp, curriculo_db)
            
            competencia = dados_encontrados.get("competencia", "")
            habs = dados_encontrados.get("habilidades", [])
            habilidades = " | ".join(habs) if isinstance(habs, list) else str(habs)
            
            dados_csv.append({
                "Componente": comp,
                "Seção (BASICO/EPT/APROFUNDAMENTO)": secao_encontrada,
                "Competência": competencia,
                "Habilidades (separadas por |)": habilidades
            })
            
        df = pd.DataFrame(dados_csv)
        df.to_csv(CSV_EXPORT, index=False, encoding='utf-8-sig')
        print(f"\n✅ Arquivo gerado: {CSV_EXPORT}")
        print("👉 Abra este arquivo no Excel, preencha as competências EPT faltantes e execute este script novamente para importar.")

    else:
        # --- IMPORTAÇÃO (CSV -> JSON) ---
        try:
            df = pd.read_csv(CSV_EXPORT)
            df = df.fillna("")
            
            atualizados = 0
            for _, row in df.iterrows():
                comp = row["Componente"].strip()
                secao = row["Seção (BASICO/EPT/APROFUNDAMENTO)"].strip().upper()
                competencia = row["Competência"].strip()
                habs_str = row["Habilidades (separadas por |)"].strip()
                
                if not secao: secao = "EPT"
                if secao not in curriculo_db: curriculo_db[secao] = {}
                
                # Atualiza ou Cria
                habilidades = [h.strip() for h in habs_str.split("|") if h.strip()]
                
                curriculo_db[secao][comp] = {
                    "competencia": competencia,
                    "habilidades": habilidades
                }
                atualizados += 1
            
            salvar_json(CURRICULO_JSON, curriculo_db)
            print(f"\n✅ Sucesso! {atualizados} componentes atualizados no banco de dados (curriculo_db.json).")
            
        except Exception as e:
            print(f"❌ Erro ao ler CSV: {e}")

if __name__ == "__main__":
    main()
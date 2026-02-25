
import re
import json
import os

# --- CONFIGURAÇÃO ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARQUIVO_MD = os.path.join(BASE_DIR, "docs", "HORÁRIO - 2026ATUALIZADO.doc.md")
PASTA_DADOS = os.path.join(BASE_DIR, "data")
ARQUIVO_GLOBAL = os.path.join(PASTA_DADOS, "horario_global.json")
PASTA_PROFESSORES = os.path.join(PASTA_DADOS, "perfis")

# Mapeamento de nomes curtos (tabela) para nomes completos (sistema)
# Adicione aqui conforme necessário
MAPA_NOMES = {
    "Hélio": "Helio Lima", "Hèlio": "Helio Lima", "Héli": "Helio Lima", "Helio": "Helio Lima",
    "Louri": "Lourival", "Louriv": "Lourival", "Lour": "Lourival", "Louriva": "Lourival",
    "Júlia": "Júlia", "Júli": "Júlia",
    "Lucile": "Lucilene", "Lucil": "Lucilene", "Lucilen": "Lucilene",
    "Dulci": "Dulcinete", "Dulcin": "Dulcinete", "Dulcine": "Dulcinete",
    "Elisa": "Elisangela", "Elisan": "Elisangela", "Elisang": "Elisangela", ".Elisan": "Elisangela",
    "Rosang": "Rosangela", "Rosan": "Rosangela", "Rosa": "Rosangela",
    "Ariste": "Aristeu", "Arist": "Aristeu",
    "Adoni": "Adonias", "Adon": "Adonias", "Adonia": "Adonias",
    "Gilm": "Gilmar", "Gilma": "Gilmar",
    "Brun": "Bruno",
    "Dougl": "Douglas", "Doug": "Douglas",
    "Muar": "Muara", "Muara": "Muara",
    "A.Rosa": "Ana Rosa", "A.Ros": "Ana Rosa", "A.Ro": "Ana Rosa", "A,Rosa": "Ana Rosa",
    "Suza": "Suzana", "Suzan": "Suzana",
    "Fca": "Francisca", "Fco": "Francisca", "Francisca": "Francisca",
    "JFco": "Jose Francisco", "Jose Francisco": "Jose Francisco", "Fco": "Jose Francisco",
    "Rays": "Rayssa", "Rayss": "Rayssa",
    "Silvan": "Silvana", "Silvana": "Silvana",
    "Arian": "Ariana", "Ariana": "Ariana",
    "Victor": "Victor",
    "Edio": "Edio"
}

# Lista de termos para ignorar (disciplinas ou lixo que aparecem na coluna de professor)
IGNORAR = [
    "\\-", "-", "I", "N", "T", "E", "R", "V", "A", "L", "O",
    "Mat", "Fisica", "Físi", "Físic", "Game Desig", "Arq. De Sist.", "Pens.Comp.", 
    "Seg.Saú.Tra", "Fun.Ges.Pe", "Tecnol.Infor", "Ed.Amb.Sust", "Éti", 
    "Perc.Apro", "Fund.Admin", "Anális", "Gestão", "P.Vida", "C.Afr",
    "Lóg. de Pro", "Arte Digital", "P.Vi", "P.Vid", "P. Vida", "Estudo", "Estud", "Est",
    "Int.Art", "Int.Artif", "I.Art", "I.Arti", "Rob", "Robótic", "C.Leit", "M.Fi", "M.F",
    "E.Trâ", "E.Rel", "D.T", "D.T.", "D.Té", "D.Téc", "A.P", "Aprof", "Aprof.", "Aprofund",
    "Recom", "Rec", "Reco", "E.Fí", "E.Fís", "E.Físi", "Esp", "Espa", "Espa.", "Espan", "Espo", "Esport",
    "Bio", "Biol", "Biolo", "Biolog", "Quí", "Quím", "Quími", "Químic", "Química",
    "Filo", "Filos", "Soci", "Soc", "Hist", "Histó", "Histór", "História",
    "Geo", "Geog", "Geogra", "Port", "Portu", "Por", "Po", "Ing", "Ingl", "Inglê", "Inglês",
    "Lei", "Leit", "Leitu", "Leitur", "Art", "Arte", "M.Fin", "M.Finc", "I.Ar", "Técn", "Com", "Trab"
]

def limpar_texto(texto):
    return texto.strip().replace("**", "")

def processar_horario():
    if not os.path.exists(ARQUIVO_MD):
        print(f"Erro: Arquivo não encontrado: {ARQUIVO_MD}")
        return

    with open(ARQUIVO_MD, "r", encoding="utf-8") as f:
        linhas = f.readlines()

    horario_global = {}
    professores_detectados = {}
    
    dia_atual = ""
    salas = []

    print("--- Iniciando Processamento do Horário ---")

    for linha in linhas:
        linha = linha.strip()
        
        # Ignora linhas de separação ou vazias
        if not linha.startswith("|") or "---" in linha:
            continue

        colunas = [c.strip() for c in linha.split("|")]
        # Remove o primeiro e último elemento vazios gerados pelo split do markdown
        if len(colunas) > 2:
            colunas = colunas[1:-1]
        
        # Cabeçalho (Identifica Salas)
        if "SALA/ DIAS" in colunas[0] or "Horário" in colunas[2]:
            # Mapeia as salas a partir da coluna 3 (índice 3 no array 0-based)
            # Colunas: [Dia, H, Horario, Sala1, Sala2...]
            salas = [s.replace("**", "").strip() for s in colunas[3:]]
            print(f"Salas detectadas: {salas}")
            continue

        # Detecta Dia da Semana
        primeira_coluna = limpar_texto(colunas[0])
        if "FEIRA" in primeira_coluna.upper() or "SEXT" in primeira_coluna.upper():
            dia_atual = primeira_coluna.upper().replace(",", "").strip()
            if dia_atual not in horario_global:
                horario_global[dia_atual] = {}
        
        # Detecta Aula/Período
        periodo = limpar_texto(colunas[1])
        horario_tempo = limpar_texto(colunas[2])
        
        # Pula linhas de intervalo ou rodapé
        if not periodo or periodo == "-" or "S/01" in linha or "INTERVALO" in linha.upper():
            continue

        # Processa as células de aula
        conteudos = colunas[3:]
        
        for i, conteudo in enumerate(conteudos):
            if i >= len(salas): break
            
            sala = salas[i]
            conteudo_limpo = limpar_texto(conteudo)
            
            if conteudo_limpo and conteudo_limpo != "-":
                # Tenta separar Professor / Disciplina
                partes = conteudo_limpo.split("/")
                prof_curto = partes[0].strip()
                disciplina = partes[1].strip() if len(partes) > 1 else "Geral"
                
                # Normaliza nome do professor
                prof_nome_real = MAPA_NOMES.get(prof_curto, prof_curto)

                # Filtra nomes inválidos ou disciplinas na coluna errada
                if prof_nome_real in IGNORAR or len(prof_nome_real) < 3:
                    continue
                
                # Adiciona ao Global
                if periodo not in horario_global[dia_atual]:
                    horario_global[dia_atual][periodo] = {}
                
                horario_global[dia_atual][periodo][sala] = {
                    "professor": prof_nome_real,
                    "disciplina": disciplina,
                    "horario": horario_tempo
                }

                # Adiciona ao Individual
                if prof_nome_real not in professores_detectados:
                    professores_detectados[prof_nome_real] = []
                
                professores_detectados[prof_nome_real].append({
                    "Dia": dia_atual,
                    "Período": periodo,
                    "Horário": horario_tempo,
                    "Sala": sala,
                    "Disciplina": disciplina
                })

    # Salvar Global
    if not os.path.exists(PASTA_DADOS):
        os.makedirs(PASTA_DADOS)
        
    with open(ARQUIVO_GLOBAL, "w", encoding="utf-8") as f:
        json.dump(horario_global, f, indent=4, ensure_ascii=False)
    print(f"✅ Horário Global salvo em: {ARQUIVO_GLOBAL}")

    # Salvar Individuais
    if not os.path.exists(PASTA_PROFESSORES):
        os.makedirs(PASTA_PROFESSORES)

    for prof, aulas in professores_detectados.items():
        # Gera nome de arquivo seguro (padrao utils.py: perfil_nome_sobrenome.json)
        safe_name = prof.replace(" ", "_").lower()
        caminho_prof = os.path.join(PASTA_PROFESSORES, f"perfil_{safe_name}.json")
        
        # Consolida vinculos (Turma -> Componentes) para o perfil
        vinculos_map = {}
        for aula in aulas:
            turma = aula['Sala']
            disciplina = aula['Disciplina']
            if turma not in vinculos_map:
                vinculos_map[turma] = set()
            vinculos_map[turma].add(disciplina)
        
        vinculos = []
        for turma, comps in vinculos_map.items():
            vinculos.append({
                "turma": turma,
                "componentes": sorted(list(comps))
            })
            
        perfil_data = {
            "professor": prof,
            "email": "",
            "municipio": "",
            "vinculos": vinculos
        }
        
        with open(caminho_prof, "w", encoding="utf-8") as f:
            json.dump(perfil_data, f, indent=2, ensure_ascii=False)
            
    print(f"✅ {len(professores_detectados)} perfis de professores gerados em: {PASTA_PROFESSORES}")
    print("Lista de Professores Identificados:", sorted(list(professores_detectados.keys())))

    # --- ATUALIZAR ESCOLA_DB.JSON ---
    # Isso garante que os nomes apareçam na página de Configuração
    arquivo_escola_db = os.path.join(PASTA_DADOS, "escola", "escola_db.json")
    if os.path.exists(arquivo_escola_db):
        try:
            with open(arquivo_escola_db, "r", encoding="utf-8") as f:
                escola_db = json.load(f)
            
            # Atualiza a lista de professores mantendo os existentes e adicionando novos
            professores_existentes = set(escola_db.get("professores", []))
            professores_novos = set(professores_detectados.keys())
            escola_db["professores"] = sorted(list(professores_existentes.union(professores_novos)))

            with open(arquivo_escola_db, "w", encoding="utf-8") as f:
                json.dump(escola_db, f, indent=2, ensure_ascii=False)
            print(f"✅ Banco de dados da escola atualizado com {len(escola_db['professores'])} professores.")
        except Exception as e:
            print(f"Erro ao atualizar escola_db.json: {e}")

if __name__ == "__main__":
    processar_horario()

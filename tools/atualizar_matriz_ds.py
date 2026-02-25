
import json
import os

# Configuração de Caminhos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARQUIVO_DB = os.path.join(BASE_DIR, "data", "escola", "escola_db.json")

# Matrizes Curriculares (Baseadas no MD fornecido)
MATRIZ_DS = {
    "1": [
        # FGB
        "LÍNGUA PORTUGUESA", "ARTE", "EDUCAÇÃO FÍSICA", "LINGUA ESTRANGEIRA INGLÊS", "LÍNGUA ESTRANGEIRA ESPANHOL",
        "MATEMÁTICA", "FÍSICA", "QUÍMICA", "BIOLOGIA", "GEOGRAFIA", "HISTÓRIA", "FILOSOFIA", "SOCIOLOGIA",
        # Itinerários
        "PROJETO DE VIDA", "MONITORIA / HORÁRIO DE ESTUDO", "ESPORTE INTEGRADA A EDUCAÇÃO FÍSICA",
        "CULTURA INTEGRADA A ARTE", "INTELIGÊNCIA ARTIFICIAL", "CIÊNCIAS DA NATUREZA (APROFUNDAMENTO)",
        "LINGUA PORTUGUESA (APROFUNDAMENTO)", "MATEMÁTICA (APROFUNDAMENTO)",
        # EPT
        "TECNOLOGIAS E AMBIENTES VIRTUAIS DE APRENDIZAGEM", "FUNDAMENTOS DA TECNOLOGIA DA INFORMAÇÃO",
        "EDUCAÇÃO AMBIENTAL E SUSTENTABILIDADE", "ARQUITETURA DE COMPUTADORES", "FUNDAMENTOS DE BANCO DE DADOS",
        "LÓGICA DE PROGRAMAÇÃO", "FUNDAMENTOS DE REDES DE COMPUTADORES", "INGLÊS TÉCNICO",
        "MÉTODOS ÁGEIS DE DESENVOLVIMENTO"
    ],
    "2": [
        # FGB
        "LÍNGUA PORTUGUESA", "ARTE", "EDUCAÇÃO FÍSICA", "LINGUA ESTRANGEIRA INGLÊS", "LÍNGUA ESTRANGEIRA ESPANHOL",
        "MATEMÁTICA", "FÍSICA", "QUÍMICA", "BIOLOGIA", "GEOGRAFIA", "HISTÓRIA", "FILOSOFIA", "SOCIOLOGIA",
        # Itinerários
        "MONITORIA / HORÁRIO DE ESTUDO", "ESPORTE INTEGRADA A EDUCAÇÃO FÍSICA", "CULTURA INTEGRADA A ARTE",
        "EDUCAÇÃO DO TRÂNSITO", "INTELIGÊNCIA ARTIFICIAL", "CIÊNCIAS DA NATUREZA (APROFUNDAMENTO)",
        "LINGUA PORTUGUESA (APROFUNDAMENTO)", "MATEMÁTICA (APROFUNDAMENTO)",
        # EPT
        "ADMINISTRAÇÃO DE BANCO DE DADOS", "PROGRAMAÇÃO ESTRUTURADA", "PROGRAMAÇÃO ORIENTADA A OBJETOS - POO",
        "PROGRAMAÇÃO WEB FRONT-END", "PROGRAMAÇÃO WEB BACK-END", "FUNDAMENTOS DE UI / UX OU IHC",
        "ÉTICA, TRABALHO E CIDADANIA", "PROGRAMAÇÃO PARA DISPOSITIVOS MÓVEIS", "MANUTENÇÃO DE SISTEMAS"
    ],
    "3": [
        # FGB
        "LÍNGUA PORTUGUESA", "ARTE", "EDUCAÇÃO FÍSICA", "LINGUA ESTRANGEIRA INGLÊS", "LÍNGUA ESTRANGEIRA ESPANHOL",
        "MATEMÁTICA", "FÍSICA", "QUÍMICA", "BIOLOGIA", "GEOGRAFIA", "HISTÓRIA", "FILOSOFIA", "SOCIOLOGIA",
        # Itinerários
        "MONITORIA / HORÁRIO DE ESTUDO", "ESPORTE INTEGRADA A EDUCAÇÃO FÍSICA", "CULTURA INTEGRADA A ARTE",
        "EDUCAÇÃO DO TRÂNSITO", "INTELIGÊNCIA ARTIFICIAL", "CIÊNCIAS DA NATUREZA (APROFUNDAMENTO)",
        "LINGUA PORTUGUESA (APROFUNDAMENTO)", "MATEMÁTICA (APROFUNDAMENTO)",
        # EPT
        "TESTE DE SISTEMAS E SEGURANÇA DE DADOS", "INTELIGÊNCIA ARTIFICIAL APLICADA A AUTOMAÇÃO",
        "INTERNET DAS COISAS - IOT", "ORIENTAÇÃO PROFISSIONAL E EMPREENDEDORISMO", "PROJETO INTEGRADOR"
    ]
}

def atualizar_matriz():
    if not os.path.exists(ARQUIVO_DB):
        print(f"Erro: Banco de dados não encontrado em {ARQUIVO_DB}")
        return

    with open(ARQUIVO_DB, "r", encoding="utf-8") as f:
        db = json.load(f)

    turmas = db.get("turmas", {})
    count = 0

    print("--- Iniciando Atualização da Matriz Curricular (DS) ---")

    for nome_turma, dados in turmas.items():
        # Identifica se é uma turma de DS (Desenvolvimento de Sistemas)
        # Verifica padrões como "DS", "T.I.", "Desenvolvimento"
        nome_upper = nome_turma.upper()
        if "DS" in nome_upper or "T.I." in nome_upper or "DESENVOLVIMENTO" in nome_upper:
            serie = None
            if "1ª" in nome_turma or "1º" in nome_turma:
                serie = "1"
            elif "2ª" in nome_turma or "2º" in nome_turma:
                serie = "2"
            elif "3ª" in nome_turma or "3º" in nome_turma:
                serie = "3"
            
            if serie:
                # Mescla os componentes existentes com a nova matriz
                comps_atuais = set(dados.get("componentes", []))
                novos_comps = MATRIZ_DS[serie]
                
                # Adiciona apenas o que falta
                for comp in novos_comps:
                    comps_atuais.add(comp)
                
                # Atualiza a lista ordenada
                dados["componentes"] = sorted(list(comps_atuais))
                print(f"✅ Turma '{nome_turma}' atualizada com matriz da {serie}ª Série.")
                count += 1

    if count > 0:
        with open(ARQUIVO_DB, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
        print(f"\nConcluído! {count} turmas foram atualizadas no escola_db.json.")
    else:
        print("\nNenhuma turma de DS encontrada para atualizar.")
        print("Dica: Verifique se os nomes das turmas contêm 'DS', 'T.I.' ou 'Desenvolvimento'.")

if __name__ == "__main__":
    atualizar_matriz()

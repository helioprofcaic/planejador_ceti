import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_PERFIS = os.path.join(BASE_DIR, "data", "perfis")
PASTA_FREQUENCIA = os.path.join(BASE_DIR, "data", "frequencia")

def gerar_frequencias():
    if not os.path.exists(PASTA_PERFIS):
        print("Pasta de perfis não encontrada.")
        return

    os.makedirs(PASTA_FREQUENCIA, exist_ok=True)
    
    # Lista todos os perfis existentes
    perfis = [f for f in os.listdir(PASTA_PERFIS) if f.startswith("perfil_") and f.endswith(".json")]
    
    print(f"Encontrados {len(perfis)} perfis. Verificando frequências...")
    
    for perfil_file in perfis:
        # Extrai o nome seguro do arquivo de perfil (perfil_nome_sobrenome.json -> nome_sobrenome)
        safe_name = perfil_file.replace("perfil_", "").replace(".json", "")
        
        caminho_freq = os.path.join(PASTA_FREQUENCIA, f"frequencia_{safe_name}.json")
        
        if not os.path.exists(caminho_freq):
            with open(caminho_freq, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2, ensure_ascii=False)
            print(f"✅ Criado: {os.path.basename(caminho_freq)}")
        else:
            print(f"ℹ️ Já existe: {os.path.basename(caminho_freq)}")

if __name__ == "__main__":
    gerar_frequencias()
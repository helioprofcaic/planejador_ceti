
import os
import json

def setup_admin():
    # Caminhos
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    perfis_dir = os.path.join(base_dir, "data", "perfis")
    os.makedirs(perfis_dir, exist_ok=True)
    
    arquivo_admin = os.path.join(perfis_dir, "perfil_helio_lima.json")
    
    # Dados iniciais com as senhas
    dados_admin = {
        "professor": "Helio Lima",
        "email": "helio@exemplo.com",
        "municipio": "Teresina",
        "vinculos": [],
        "senhas": {
            "admin": "helio@raldir",
            "usuario": "helio@raldir",
            "professor": "helio@raldir"
        }
    }
    
    # Se já existe, preserva dados e só adiciona senhas se faltarem
    if os.path.exists(arquivo_admin):
        with open(arquivo_admin, "r", encoding="utf-8") as f:
            try:
                existente = json.load(f)
                if "senhas" not in existente:
                    existente["senhas"] = dados_admin["senhas"]
                    print("⚠️ Perfil existente encontrado sem senhas. Adicionando senhas padrão...")
                    dados_admin = existente
                else:
                    print("✅ Perfil já possui senhas configuradas. Nenhuma alteração necessária.")
                    return
            except:
                print("⚠️ Arquivo existente corrompido. Sobrescrevendo...")
    
    with open(arquivo_admin, "w", encoding="utf-8") as f:
        json.dump(dados_admin, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Perfil de administrador configurado em: {arquivo_admin}")
    print("🔑 Senha inicial: helio@raldir")

if __name__ == "__main__":
    setup_admin()

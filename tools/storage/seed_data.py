# scripts/seed_data.py
import os
import sys
from dotenv import load_dotenv

# Adiciona o diretório raiz ao path para que possamos importar os módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

def run_seeder():
    """
    Função principal que carrega o ambiente e executa o seeder.
    """
    # O script espera que o arquivo .env esteja na pasta raiz (um nível acima de 'scripts')
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    env_path = os.path.join(project_root, '.env')
    load_dotenv(dotenv_path=env_path)

    # Este é um hack para fazer o `tools/storage/database.py` (que usa st.secrets)
    # funcionar fora de um app Streamlit, simulando o st.secrets.
    class MockSecrets(dict):
        def __getitem__(self, key):
            # Tenta obter do ambiente, se não existir, retorna None
            return os.environ.get(key)

    import streamlit as st
    st.secrets = MockSecrets()

    # Agora que o ambiente está configurado, podemos importar o módulo de banco de dados
    from tools import database as db

    if not db.is_db_connected():
        print("ERRO: Conexão com o banco de dados falhou.")
        print("Verifique se você criou um arquivo .env na raiz do projeto com SUPABASE_URL e SUPABASE_KEY.")
        return

    # Verificação básica da URL
    url = os.environ.get("SUPABASE_URL", "")
    if not url.startswith("http"):
        print(f"ERRO: A URL do Supabase no .env parece inválida: '{url}'")
        return

    print("Iniciando o processo de seeding do banco de dados...")

    # Caminho para o arquivo de dados. O nome foi padronizado.
    file_to_parse = os.path.join(project_root, 'data', 'escola', 'Escola.txt')

    try:
        with open(file_to_parse, 'r', encoding='utf-8') as f:
            text_content = f.read()
    except FileNotFoundError:
        print(f"ERRO: Arquivo de estrutura '{file_to_parse}' não encontrado. Crie este arquivo para definir a estrutura da escola.")
        return

    success, logs = db.import_school_structure(text_content)

    if success:
        print("\n--- LOGS DA IMPORTAÇÃO ---")
        print(logs)
        print("\n✅ Seeding da estrutura da escola concluído com sucesso!")
    else:
        print(f"\n❌ ERRO durante a importação da estrutura:")
        print(logs)

if __name__ == "__main__":
    run_seeder()
# scripts/sync_folders_from_db.py
import os
import sys
import re
from dotenv import load_dotenv

# Adiciona o diretório raiz ao path para que possamos importar os módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

def sanitize_foldername(name):
    """Remove caracteres inválidos para nomes de pastas."""
    if not name:
        return "_sem_nome_"
    # Remove caracteres inválidos no Windows/Linux/Mac
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

def run_sync():
    """
    Função principal que lê a estrutura do DB e cria as pastas locais.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    env_path = os.path.join(project_root, '.env')
    load_dotenv(dotenv_path=env_path)

    # Simula o st.secrets para rodar fora do Streamlit
    class MockSecrets(dict):
        def __getitem__(self, key):
            if key == "supabase":
                return {"url": os.environ.get("SUPABASE_URL"), "key": os.environ.get("SUPABASE_KEY")}
            return {}

    import streamlit as st
    st.secrets = MockSecrets()

    from tools import database as db

    if not db.is_db_connected():
        print("❌ ERRO: Conexão com o banco de dados falhou.")
        print("   Verifique se você criou um arquivo .env na raiz do projeto com SUPABASE_URL e SUPABASE_KEY.")
        return

    print("--- Iniciando Sincronização de Pastas (DB -> Local) ---")
    
    base_path = os.path.join(project_root, 'data', 'Turmas')
    print(f"Pasta base para sincronização: '{base_path}'")

    # 1. Buscar todas as turmas
    classes = db.get_classes()
    if not classes:
        print("⚠️ Nenhuma turma encontrada no banco de dados. Nada a fazer.")
        return

    created_count = 0
    for cls in classes:
        class_name = cls.get('name')
        class_id = cls.get('id')
        if not class_name or not class_id:
            continue

        sanitized_class_name = sanitize_foldername(class_name)
        
        # 2. Para cada turma, buscar as disciplinas
        subjects = db.get_subjects_for_class(class_id)
        if subjects:
            print(f"\n🏫 Processando Turma: {class_name}")
            for sub in subjects:
                subject_name = sub.get('name')
                if not subject_name:
                    continue
                
                sanitized_subject_name = sanitize_foldername(subject_name)
                
                # 3. Criar a estrutura de pastas
                full_path = os.path.join(base_path, sanitized_class_name, sanitized_subject_name)
                if not os.path.exists(full_path):
                    os.makedirs(full_path, exist_ok=True)
                    print(f"  ✅ Pasta criada: {os.path.join(sanitized_class_name, sanitized_subject_name)}")
                    created_count += 1

    print(f"\n--- Sincronização concluída. {created_count} novas pastas foram criadas. ---")

if __name__ == "__main__":
    run_sync()
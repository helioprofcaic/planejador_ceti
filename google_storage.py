import streamlit as st
import json
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# Escopos necessários para ler e escrever no Drive
SCOPES = ['https://www.googleapis.com/auth/drive']

def get_drive_service():
    """Autentica e retorna o serviço do Google Drive usando st.secrets."""
    if "gcp_service_account" not in st.secrets:
        st.warning("⚠️ Credenciais do Google Cloud não configuradas nos Secrets.")
        return None
    
    try:
        # Converte o objeto de configuração do Streamlit para dict
        creds_dict = dict(st.secrets["gcp_service_account"])
        
        # --- CORREÇÃO DE FORMATAÇÃO DA CHAVE PRIVADA ---
        if "private_key" in creds_dict:
            # 1. Verifica se o usuário esqueceu de substituir o placeholder "..." do exemplo
            if "..." in creds_dict["private_key"]:
                st.error("⚠️ Erro de Configuração: A chave privada contém '...'. Você esqueceu de substituir o valor de exemplo no arquivo secrets.toml pela sua chave real.")
                return None
            # 2. Substitui literais \n por quebras de linha reais (necessário para TOML/Streamlit)
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            
        creds = service_account.Credentials.from_service_account_info(
            creds_dict, scopes=SCOPES
        )
        return build('drive', 'v3', credentials=creds)
    except Exception as e:
        st.error(f"Erro na autenticação do Google Drive: {e}")
        return None

def get_folder_id():
    """Retorna o ID da pasta configurado."""
    if "drive" in st.secrets and "folder_id" in st.secrets["drive"]:
        return st.secrets["drive"]["folder_id"]
    return None

def find_file(service, filename, folder_id):
    """Procura o ID de um arquivo pelo nome dentro da pasta alvo."""
    query = f"name = '{filename}' and '{folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    return files[0]['id'] if files else None

def load_json(filename, default_value=None):
    """Carrega um JSON do Drive. Se não existir, retorna o valor padrão."""
    service = get_drive_service()
    folder_id = get_folder_id()
    
    if not service or not folder_id:
        return default_value or {}

    file_id = find_file(service, filename, folder_id)
    if not file_id:
        return default_value or {}

    try:
        content = service.files().get_media(fileId=file_id).execute()
        return json.loads(content.decode('utf-8'))
    except Exception as e:
        st.error(f"Erro ao ler {filename} do Drive: {e}")
        return default_value or {}

def save_json(filename, data):
    """Salva (sobrescreve) um arquivo JSON no Drive."""
    service = get_drive_service()
    folder_id = get_folder_id()
    
    if not service or not folder_id:
        return False

    file_id = find_file(service, filename, folder_id)
    
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    media = MediaIoBaseUpload(io.BytesIO(json_str.encode('utf-8')), mimetype='application/json')

    try:
        if file_id:
            # Atualiza arquivo existente
            service.files().update(fileId=file_id, media_body=media).execute()
        else:
            # Cria novo arquivo
            file_metadata = {'name': filename, 'parents': [folder_id]}
            service.files().create(body=file_metadata, media_body=media).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar {filename} no Drive: {e}")
        return False
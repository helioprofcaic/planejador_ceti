import streamlit as st
import json
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.http import MediaIoBaseDownload

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

def get_or_create_subfolder(service, parent_id, folder_name):
    """Verifica se uma subpasta existe. Se não, cria e retorna o ID."""
    query = f"mimeType = 'application/vnd.google-apps.folder' and name = '{folder_name}' and '{parent_id}' in parents and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    
    if files:
        return files[0]['id']
    else:
        # Cria a pasta se não existir
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }
        folder = service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')

def find_file(service, filename, folder_id):
    """Procura o ID de um arquivo pelo nome dentro da pasta alvo."""
    query = f"name = '{filename}' and '{folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    return files[0]['id'] if files else None

def load_json(filename, default_value=None):
    """Carrega um JSON da subpasta 'data' no Drive."""
    service = get_drive_service()
    root_id = get_folder_id()
    
    if not service or not root_id:
        return default_value or {}

    # 1. Tenta buscar na subpasta 'data'
    data_folder_id = get_or_create_subfolder(service, root_id, 'data')
    file_id = find_file(service, filename, data_folder_id)
    
    # 2. Fallback: Se não achar em 'data', tenta na raiz (caso o usuário não tenha movido)
    if not file_id:
        file_id = find_file(service, filename, root_id)

    if not file_id:
        if filename == "alunos.json":
            st.warning(f"⚠️ O arquivo `{filename}` não foi encontrado no Google Drive (nem na pasta 'data', nem na raiz). Verifique o nome e o upload.")
        return default_value or {}

    try:
        content = service.files().get_media(fileId=file_id).execute()
        # Usa utf-8-sig para lidar com BOM do Windows (comum em arquivos locais editados)
        return json.loads(content.decode('utf-8-sig'))
    except Exception as e:
        st.error(f"Erro ao ler {filename} do Drive: {e}")
        return default_value or {}

def save_json(filename, data):
    """Salva (sobrescreve) um arquivo JSON na subpasta 'data' no Drive."""
    service = get_drive_service()
    root_id = get_folder_id()
    
    if not service or not root_id:
        return False

    # Garante que salva na subpasta 'data'
    data_folder_id = get_or_create_subfolder(service, root_id, 'data')

    file_id = find_file(service, filename, data_folder_id)
    
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    media = MediaIoBaseUpload(io.BytesIO(json_str.encode('utf-8')), mimetype='application/json')

    try:
        if file_id:
            # Atualiza arquivo existente
            service.files().update(fileId=file_id, media_body=media).execute()
        else:
            # Cria novo arquivo
            file_metadata = {'name': filename, 'parents': [data_folder_id]}
            service.files().create(body=file_metadata, media_body=media).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar {filename} no Drive: {e}")
        return False

def list_files_in_subfolder(subfolder_name, mime_type=None):
    """Lista arquivos dentro de uma subpasta específica (ex: 'pdf')."""
    service = get_drive_service()
    root_id = get_folder_id()
    
    if not service or not root_id:
        return []
        
    target_folder_id = get_or_create_subfolder(service, root_id, subfolder_name)
    
    query = f"'{target_folder_id}' in parents and trashed = false"
    if mime_type:
        query += f" and mimeType = '{mime_type}'"
        
    results = service.files().list(q=query, fields="files(id, name)").execute()
    return results.get('files', [])

def download_file_bytes(file_id):
    """Baixa o conteúdo de um arquivo do Drive como bytes."""
    service = get_drive_service()
    if not service: return None
    
    request = service.files().get_media(fileId=file_id)
    file_io = io.BytesIO()
    downloader = MediaIoBaseDownload(file_io, request)
    
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        
    file_io.seek(0)
    return file_io
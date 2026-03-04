import streamlit as st
import utils
import google_storage
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError

st.set_page_config(page_title="Status da Nuvem", layout="wide")
utils.aplicar_estilo()

st.title("☁️ Status da Conexão com o Google Drive")
st.markdown("Verifique se a integração com o Google Drive está configurada e funcionando corretamente.")

st.divider()

# --- PASSO 1: VERIFICAR SECRETS ---
st.subheader("1. Verificação das Credenciais (`secrets.toml`)")

secrets_ok = True
try:
    if "gcp_service_account" not in st.secrets:
        st.error("❌ A seção `[gcp_service_account]` não foi encontrada no arquivo `.streamlit/secrets.toml`.")
        secrets_ok = False
    else:
        st.success("✅ Seção `[gcp_service_account]` encontrada.")

    if "drive" not in st.secrets or "folder_id" not in st.secrets.drive:
        st.error("❌ A chave `folder_id` não foi encontrada na seção `[drive]` do arquivo `.streamlit/secrets.toml`.")
        secrets_ok = False
    else:
        st.success("✅ Chave `folder_id` encontrada.")
except Exception:
    st.warning("⚠️ Arquivo `.streamlit/secrets.toml` não encontrado ou inacessível.")
    secrets_ok = False

if not secrets_ok:
    st.warning("A configuração básica no arquivo de segredos está incompleta. O sistema não conseguirá se conectar ao Google Drive.")
    st.stop()

st.divider()

# --- PASSO 2: TENTAR CONEXÃO ---
st.subheader("2. Teste de Autenticação com o Google Drive")

with st.spinner("Tentando autenticar com a API do Google..."):
    service = google_storage.get_drive_service()

if service:
    st.success("✅ Autenticação com o Google Drive bem-sucedida!")
else:
    st.error("❌ Falha na autenticação com o Google Drive.")
    st.info("Possíveis causas:")
    st.markdown("""
    - A chave JSON da Service Account em `secrets.toml` está incorreta ou mal formatada.
    - A API do Google Drive não está habilitada no seu projeto do Google Cloud.
    - Problemas de rede ou firewall impedindo a conexão com os servidores do Google.
    """)
    st.stop()

st.divider()

# --- PASSO 3: VERIFICAR ACESSO À PASTA ---
st.subheader("3. Teste de Acesso à Pasta de Dados")

folder_id = google_storage.get_folder_id()
st.write(f"**ID da Pasta configurado:** `{folder_id}`")

with st.spinner(f"Verificando permissões na pasta..."):
    try:
        # Tenta buscar os metadados da pasta. Se falhar, é porque não tem permissão.
        service.files().get(fileId=folder_id, fields='name').execute()
        st.success("✅ Acesso à pasta confirmado!")

    except RefreshError as e:
        st.error("❌ Erro de Credencial (Invalid Grant): Conta não encontrada.")
        st.warning("Isso significa que a Service Account foi deletada ou a chave foi revogada no Google Cloud.")
        st.info("👉 **Solução:** Crie uma nova Service Account (ou uma nova chave) no console do Google Cloud e atualize o `secrets.toml`.")
    except HttpError as error:
        st.error("❌ Erro ao acessar a pasta no Google Drive!")
        if error.resp.status == 404:
            st.warning("Erro 404: Pasta não encontrada. Verifique se o `folder_id` está correto.")
        elif error.resp.status in [401, 403]:
            st.warning("Erro 401/403: Permissão negada.")
            email_sa = st.secrets.get("gcp_service_account", {}).get("client_email", "NÃO ENCONTRADO")
            st.info(f"**Ação necessária:** Compartilhe sua pasta do Drive com o seguinte e-mail (dando permissão de 'Editor'):")
            st.code(email_sa, language="")
        else:
            st.error(f"Detalhes do erro: {error}")
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado: {e}")
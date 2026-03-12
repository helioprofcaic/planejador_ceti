import streamlit as st
import utils

# --- Módulos de Conexão ---
if utils.HAS_GOOGLE_STORAGE:
    import google_storage
    from googleapiclient.errors import HttpError
    from google.auth.exceptions import RefreshError
if utils.HAS_SUPABASE:
    import database as db

st.set_page_config(page_title="Status da Nuvem", layout="wide")
utils.aplicar_estilo()

st.title("📡 Status de Conexão")
st.markdown("Verifique o status das integrações com serviços externos como Google Drive e Supabase.")

st.divider()

# --- GOOGLE DRIVE ---
st.header("☁️ Status da Conexão com o Google Drive")

if not utils.HAS_GOOGLE_STORAGE:
    st.warning("Módulo `google_storage` não encontrado. A verificação do Google Drive está desabilitada.")
else:
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
    else:
        st.divider()

        # --- PASSO 2: TENTAR CONEXÃO ---
        st.subheader("2. Teste de Autenticação com o Google Drive")

        with st.spinner("Tentando autenticar com a API do Google..."):
            service = google_storage.get_drive_service()

        if service:
            st.success("✅ Autenticação com o Google Drive bem-sucedida!")

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
        else:
            st.error("❌ Falha na autenticação com o Google Drive.")
            st.info("Possíveis causas:")
            st.markdown("""
            - A chave JSON da Service Account em `secrets.toml` está incorreta ou mal formatada.
            - A API do Google Drive não está habilitada no seu projeto do Google Cloud.
            - Problemas de rede ou firewall impedindo a conexão com os servidores do Google.
            """)

st.divider()

# --- SUPABASE ---
st.header("🛰️ Status da Conexão com o Supabase")

if not utils.HAS_SUPABASE:
    st.warning("Módulo `database.py` não encontrado. A verificação do Supabase está desabilitada.")
else:
    # 4.1 Verificação dos Secrets
    st.subheader("1. Verificação das Credenciais (`secrets.toml`)")
    supabase_secrets_ok = True
    try:
        if "supabase" not in st.secrets:
            st.error("❌ A seção `[supabase]` não foi encontrada no arquivo `.streamlit/secrets.toml`.")
            st.info("👉 **Solução:** Adicione a seção `[supabase]` com as chaves `url` e `key` no seu arquivo de segredos.")
            supabase_secrets_ok = False
        else:
            st.success("✅ Seção `[supabase]` encontrada.")
            supabase_config = st.secrets["supabase"]
            
            if "url" not in supabase_config or not supabase_config["url"]:
                st.error("❌ A chave `url` não foi encontrada ou está vazia dentro da seção `[supabase]`.")
                supabase_secrets_ok = False
            else:
                st.success("✅ Chave `url` encontrada.")

            if "key" not in supabase_config or not supabase_config["key"]:
                st.error("❌ A chave `key` não foi encontrada ou está vazia dentro da seção `[supabase]`.")
                supabase_secrets_ok = False
            else:
                st.success("✅ Chave `key` encontrada.")
    except Exception:
        st.warning("⚠️ Arquivo `.streamlit/secrets.toml` não encontrado ou inacessível.")
        supabase_secrets_ok = False

    if supabase_secrets_ok:
        st.subheader("2. Teste de Conexão e Estrutura")
        with st.spinner("Tentando conectar e verificar o banco de dados..."):
            is_connected = db.is_db_connected()
            structure_ok = db.check_db_structure() if is_connected else False

        if is_connected and structure_ok:
            st.success("✅ Conexão e estrutura do banco de dados validadas com sucesso!")
            st.subheader("3. Status de Ativação")
            use_supabase_flag = st.secrets.get("supabase", {}).get("usar_supabase", False)

            if use_supabase_flag:
                st.success("✅ **Modo Banco de Dados está ATIVO.**")
                st.info("O aplicativo está configurado para usar o Supabase como fonte de dados principal.")
            else:
                st.warning("🟡 **Modo Banco de Dados está INATIVO.**")
                st.markdown("""
                A conexão com o Supabase foi bem-sucedida, mas o modo de banco de dados não está ativado.
                Para usar o Repositório de Aulas com o banco de dados, você precisa ativá-lo.

                **Para ativar, siga os passos:**
                1. Abra o arquivo `.streamlit/secrets.toml` no seu projeto.
                2. Adicione ou edite a seção `[supabase]` para que fique assim:
                ```toml
                [supabase]
                usar_supabase = true
                url = "SUA_URL_AQUI"
                key = "SUA_CHAVE_AQUI"
                ```
                3. Salve o arquivo e recarregue esta página. O sistema priorizará o Supabase quando ativado.
                """)
        elif not is_connected:
            st.error("❌ Falha na conexão com o Supabase. Verifique se a `url` e a `key` na seção `[supabase]` estão corretas.")
            connection_error = db.get_connection_error()
            if connection_error:
                st.error("Detalhes do erro:")
                st.code(connection_error, language="text")
        elif not structure_ok:
            st.error("❌ Tabela `app_users` não encontrada. O banco de dados pode não ter sido inicializado corretamente.")
            st.info("👉 **Solução:** Execute o script SQL fornecido (`tools/storage/database_schema.md`) para criar as tabelas necessárias.")
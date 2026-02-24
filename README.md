# 🏫 Planejador Escolar - CETI

Sistema de gestão docente desenvolvido em Python com Streamlit, focado na automação de planejamentos, frequência e avaliação qualitativa para o contexto de escolas de tempo integral e ensino técnico (EPT).

## 🚀 Funcionalidades

*   **📅 Planejamento Inteligente**: Geração de planos semanais, mensais e trimestrais alinhados à BNCC e Itinerários Formativos.
*   **🤖 Gerador de Aulas com IA**: Criação de roteiros de aula completos, criativos e alinhados à BNCC utilizando Inteligência Artificial (Google Gemini).
*   **📝 Frequência Digital**: Chamada diária com exportação para PDF/DOCX.
*   **📊 Ficha Qualitativa**: Acompanhamento socioemocional e técnico por projeto ou período.
*   **⚙️ Configuração Flexível**: Adaptação para diferentes cargas horárias (40h, 80h, 120h) e perfis docentes.
*   **📄 Geração de Documentos**: Exportação automática de relatórios formatados.

## 🛠️ Instalação

### 🪟 Windows (Automático - Recomendado)

Utilize o arquivo `run.bat` incluído no projeto. Ele realizará a configuração inicial (criação do ambiente virtual e instalação das dependências) e iniciará o sistema automaticamente.

1.  Clone o repositório.
2.  Execute o arquivo `run.bat`.

### 🐧 Linux/Mac ou Instalação Manual

1.  Clone o repositório:
    ```bash
    git clone https://github.com/helioprofcaic/planejador_ceti.git
    cd planejador-ceti
    ```

2.  Crie um ambiente virtual (opcional, mas recomendado):
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

## ☁️ Persistência na Nuvem (Google Drive)

Para salvar dados sensíveis (como `alunos.json`) de forma segura e remota:

1.  **Habilitar a API e Criar a Chave JSON (Credencial)**

    <details>
    <summary><b>Clique para ver o passo a passo detalhado</b></summary>

    1.  **Acesse o Google Cloud Console**: Faça login em console.cloud.google.com.
    2.  **Crie ou selecione um projeto**: No topo da página, selecione um projeto existente ou clique em "Novo projeto".
    3.  **Habilite a Google Drive API**:
        *   Use a barra de busca para procurar por "Google Drive API".
        *   Clique em "Ativar". Ou acesse diretamente por este link e clique em "Ativar".
    4.  **Crie uma Conta de Serviço (Service Account)**:
        *   No menu de navegação (☰), vá para `APIs e serviços > Credenciais`.
        *   Clique em `+ CRIAR CREDENCIAIS` e selecione `Conta de serviço`.
        *   Dê um nome para a conta (ex: `planejador-escolar-bot`), uma descrição e clique em `CRIAR E CONTINUAR`.
        *   Pule a etapa de "Conceder acesso" (opcional) clicando em `CONTINUAR`.
        *   Pule a última etapa clicando em `CONCLUÍDO`.
    5.  **Gere a Chave JSON**:
        *   Na lista de contas de serviço, encontre a que você acabou de criar e clique no e-mail dela.
        *   Vá para a aba `CHAVES`.
        *   Clique em `ADICIONAR CHAVE > Criar nova chave`.
        *   Selecione `JSON` como o tipo e clique em `CRIAR`.
        *   **O download de um arquivo JSON começará automaticamente. Este é o arquivo que você precisa!**
    6.  **Copie o conteúdo do JSON**: Abra o arquivo baixado com um editor de texto (como Bloco de Notas ou VS Code) e copie todo o seu conteúdo.

    </details>

2.  **Configurar a Pasta no Google Drive**
    *   Crie uma nova pasta no seu Google Drive pessoal (ex: `DadosPlanejador`).
    *   Clique com o botão direito na pasta, vá em `Compartilhar > Compartilhar`.
    *   No campo "Adicionar pessoas e grupos", cole o `client_email` que está dentro do arquivo JSON que você baixou.
    *   Garanta que a permissão seja de **Editor** e clique em `Enviar`.
    *   Abra a pasta e copie o ID dela da URL do navegador. (Ex: `https://.../folders/AQUI_ESTA_O_ID`).

2.  **Dependências**:
    Garanta que seu `requirements.txt` contenha:
    ```text
    google-api-python-client
    google-auth
    ```

3.  **Configuração de Segredos**:
    Renomeie o arquivo `.streamlit/secrets.toml.example` para `.streamlit/secrets.toml` e preencha com suas credenciais. O conteúdo deve ficar assim:

    ```toml
    [drive]
    folder_id = "ID_DA_SUA_PASTA_AQUI"

    [gcp_service_account]
    # Cole aqui o conteúdo do JSON da sua Service Account
    type = "service_account"
    project_id = "..."
    # ... demais campos ...
    ```

## 📂 Configuração de Dados (Importante!)

Por questões de segurança e LGPD, os dados reais dos alunos não estão incluídos neste repositório.

1.  Vá até a pasta `data/`.
2.  Renomeie o arquivo `alunos_sample.json` para `alunos.json`.
3.  Edite o arquivo `alunos.json` com os dados reais da sua turma ou importe via sistema.
4.  O arquivo `escola_db.json` contém a estrutura das turmas e componentes. Ajuste conforme a matriz da sua escola.

## ▶️ Como Rodar

**Windows:** Execute o arquivo `run.bat`.

**Manual / Terminal:** Execute o comando abaixo:

```bash
streamlit run app.py
```

##  Documentação e Tutoriais

*   👨‍🏫 Guia do Professor - Configuração de perfil e primeiros passos.
*   🤖 Guia do Gerador de Aulas (IA) - Como criar roteiros automáticos com Inteligência Artificial.
*   📊 Guia de Avaliação Qualitativa - Registro de desempenho socioemocional.
*   💾 Guia da Estrutura de Dados - Entenda os arquivos JSON e o banco de dados.

---
Desenvolvido para otimizar a rotina pedagógica.
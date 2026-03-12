# 🛠️ Documentação Técnica - Planejador CETI

Este documento descreve a arquitetura, estrutura de dados e procedimentos de manutenção do sistema.

---

## 1. Arquitetura do Sistema

O projeto é construído em **Python** utilizando o framework **Streamlit**.

*   **Frontend:** Streamlit (Interface Web Reativa).
*   **Backend:** Python (Lógica de processamento).
*   **Persistência:** Arquivos JSON (Local ou Google Drive).
*   **IA:** Google Gemini API (`google-generativeai`).

### Estrutura de Pastas

*   `app.py`: Ponto de entrada (Home e Menu).
*   `utils.py`: Biblioteca de funções utilitárias (Carregamento de dados, Geração de PDF, Estilos).
*   `google_storage.py`: Módulo de integração com a API do Google Drive.
*   `pages/`: Módulos do sistema (cada arquivo `.py` é uma página no menu).
*   `data/`: Armazenamento de dados (JSONs, CSVs).
    *   `escola/`: Dados institucionais (`escola_db.json`, `alunos.json`).
    *   `perfis/`: Configurações dos professores (`perfil_nome.json`).
    *   `aulas/`: Roteiros gerados pela IA (para modo local/arquivo).
*   `Turmas/`: Estrutura de pastas contendo as aulas em `.md` para importação no banco de dados.
*   `tools/`: Scripts de automação e manutenção.
    *   `storage/`: Scripts para popular o banco de dados (`seed_data.py`, `seed_lessons.py`).

---

## 2. Persistência de Dados

O sistema não utiliza um SGBD tradicional (SQL), mas sim uma estrutura de arquivos JSON relacionais.

### Principais Arquivos

| Arquivo | Localização | Descrição |
| :--- | :--- | :--- |
| `escola_db.json` | `data/escola/` | Lista de turmas, componentes curriculares e lista global de professores. |
| `alunos.json` | `data/escola/` | Mapeamento de `Nome da Turma` -> `Lista de Alunos`. Dados sensíveis. |
| `horario_global.json` | `data/` | Grade horária completa da escola (importada do DOC/MD). |
| `perfil_{nome}.json` | `data/perfis/` | Configurações individuais (turmas, senhas, API Key) de cada professor. |
| `curriculo_db.json` | `data/` | Base de competências e habilidades da BNCC/Itinerários. |
| `config_componentes.json` | `data/` | Regras de carga horária (Anual, Modular, Semestral). |

---

## 3. Modos de Operação (Banco de Dados vs. Arquivos)

O sistema suporta três modos de persistência, com a seguinte prioridade:

1.  **Supabase (`usar_supabase = true`):** Modo principal. Todas as operações de leitura e escrita são feitas no banco de dados PostgreSQL via Supabase. É o modo mais robusto e recomendado para produção.
2.  **Google Drive (`usar_nuvem = true`):** Modo legado. Utiliza a API do Google Drive para ler e gravar arquivos JSON. Requer configuração de uma Service Account.
3.  **Local (`usar_nuvem = false` e `usar_supabase = false`):** Lê e grava diretamente na pasta `data/` do disco. Ideal para desenvolvimento e testes rápidos sem conexão.

A configuração é feita no arquivo `.streamlit/secrets.toml`.

### Configuração do Supabase

1.  Crie um projeto no Supabase.
2.  Vá em `Project Settings > API`.
3.  Copie a `URL` e a chave `anon` (public).
4.  Adicione ao seu arquivo `.streamlit/secrets.toml`:
    ```toml
    [supabase]
    usar_supabase = true
    url = "SUA_URL_AQUI"
    key = "SUA_CHAVE_ANON_AQUI"
    ```
5.  Execute o SQL de criação de tabelas, que pode ser encontrado em `tools/storage/database_schema.md`, no Editor de SQL do Supabase.

### Configuração do Google Drive

O sistema suporta um modo de operação legado com o Google Drive.

*   **Modo Nuvem (`usar_nuvem = true`):** Utiliza a API do Google Drive para ler e gravar arquivos JSON.
    *   Requer uma **Service Account** (Conta de Serviço) do Google Cloud.
    *   A pasta alvo no Drive deve ser compartilhada com o e-mail da Service Account.

---

## 4. Scripts de Manutenção (`tools/`)

### Populando o Banco de Dados (Seeding)

Quando o modo Supabase está ativo, o banco de dados precisa ser populado com a estrutura da escola e as aulas.

1.  **`tools/storage/seed_data.py`**
    *   **O que faz:** Lê o arquivo `data/escola/Escola.txt` e cria a estrutura de Escola, Turmas e Disciplinas no banco de dados.
    *   **Como usar:**
        ```bash
        python tools/storage/seed_data.py
        ```

2.  **`tools/storage/seed_lessons.py`**
    *   **O que faz:** Varre a pasta `data/Turmas/` em busca de arquivos `.md` organizados por `Turma/Disciplina/Semana/` e os importa como aulas no banco de dados, incluindo o conteúdo do quiz.
    *   **Como usar:**
        ```bash
        python tools/storage/seed_lessons.py
        ```

3.  **`tools/storage/sync_folders_from_db.py`**
    *   **O que faz:** Sincroniza a estrutura de pastas local (`data/Turmas/`) com base nas turmas e disciplinas existentes no banco de dados. Útil para garantir que o ambiente local reflita a estrutura da nuvem antes de adicionar novos arquivos de aula. Este script **não altera** o banco de dados.
    *   **Como usar:**
        ```bash
        python tools/storage/sync_folders_from_db.py
        ```

> **Importante:** Para rodar os scripts de seeding, você precisa ter um arquivo `.env` na raiz do projeto com as mesmas chaves `SUPABASE_URL` e `SUPABASE_KEY` do seu `secrets.toml`.

### Scripts Legados

### `processar_horario.py`
Lê o arquivo Markdown do horário escolar (`docs/HORÁRIO...md`), extrai as informações e gera:
1.  `data/horario_global.json`: O quadro geral.
2.  `data/perfis/perfil_*.json`: Perfis iniciais para cada professor identificado.
3.  Atualiza a lista de professores em `escola_db.json`.

### `atualizar_matriz_ds.py`
Injeta automaticamente as disciplinas do curso de Desenvolvimento de Sistemas (FGB, Itinerários, EPT) nas turmas correspondentes no `escola_db.json`.

### `setup_admin.py`
Cria ou restaura o perfil do administrador (`Helio Lima`) com as senhas iniciais, caso o arquivo seja perdido.

---

## 5. Segurança

*   **Senhas:** As senhas de acesso (Admin, Usuário, Professor) são armazenadas no JSON do perfil do administrador (`perfil_helio_lima.json`) e **não** no código-fonte.
*   **Dados Sensíveis:** O arquivo `alunos.json` e os perfis contendo chaves de API devem ser protegidos. O `.gitignore` já está configurado para ignorar a pasta `data/` (exceto arquivos de exemplo).
*   **Visitantes:** O perfil "Visitante" tem acesso restrito (somente leitura em áreas não sensíveis) e não pode visualizar a lista de alunos.

---

## 6. Procedimento de Deploy

Para atualizar o sistema em produção:

1.  Garanta que o `requirements.txt` esteja atualizado.
2.  No Streamlit Cloud, configure os **Secrets** com as credenciais do Google Drive.
3.  Certifique-se de que a variável `usar_nuvem` esteja como `true`.
4.  Faça o push para o branch `main` do GitHub.

### Adicionando Novos Professores
A forma mais fácil é rodar o script `processar_horario.py` localmente (com o arquivo de horário atualizado) e subir os JSONs gerados para a pasta `data/perfis/` no Google Drive.

Alternativamente, o professor pode criar seu próprio perfil na página de **Configuração** do app.
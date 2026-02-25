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
    *   `aulas/`: Roteiros gerados pela IA.
*   `tools/`: Scripts de automação e manutenção.

---

## 2. Banco de Dados (JSON)

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

## 3. Integração com Google Drive

O sistema suporta dois modos de operação, definidos em `.streamlit/secrets.toml`:

1.  **Modo Local (`usar_nuvem = false`):** Lê e grava diretamente na pasta `data/` do disco. Ideal para desenvolvimento.
2.  **Modo Nuvem (`usar_nuvem = true`):** Utiliza a API do Google Drive para ler e gravar arquivos JSON.
    *   Requer uma **Service Account** (Conta de Serviço) do Google Cloud.
    *   A pasta alvo no Drive deve ser compartilhada com o e-mail da Service Account.

---

## 4. Scripts de Manutenção (`tools/`)

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
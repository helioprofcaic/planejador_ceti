# 📖 Guia Rápido dos Arquivos de Dados (JSON)

Este tutorial explica a função de cada arquivo `.json` na pasta `data/`. Entender essa estrutura é fundamental para manter e expandir o sistema.

---

## 🚀 Arquivos Ativos (O Coração do Sistema)

Estes são os arquivos essenciais que o sistema utiliza no dia a dia.

### 1. `escola_db.json`
*   **O que é?** É o **Banco de Dados Institucional**. Contém a lista de professores, as turmas da escola e quais componentes são ofertados em cada turma.
*   **Onde é usado?**
    *   `Página 5 (Configuração)`: Para listar as turmas oficiais que um professor pode escolher.
    *   `Página 6 (Config. Componentes)`: Para listar os componentes disponíveis para configuração de carga horária.

### 2. `curriculo_db.json`
*   **O que é?** É o **Banco de Dados Pedagógico**. Organizado em hierarquia (Básico, Aprofundamento, EPT), contém as competências, habilidades e objetos de conhecimento de cada disciplina.
*   **Onde é usado?**
    *   `Página 1 (Planejamento)`: Para buscar o conteúdo (habilidades, objetos) de um componente e gerar o plano de aula automaticamente.

### 3. `alunos.json`
*   **O que é?** É a **Base de Dados Oficial dos Alunos**. Contém a lista de chamada de todas as turmas.
*   **Onde é usado?**
    *   `Página 3 (Frequência)`: Para gerar a lista de presença do dia.
    *   `Página 2 (Ficha Qualitativa)`: Para listar os alunos no acompanhamento pedagógico.

### 4. `config_componentes.json`
*   **O que é?** É o **Motor do Planejamento Trimestral**. Ele contém as regras de negócio que definem a carga horária de cada tipo de disciplina (ex: Robótica tem 2 aulas/semana, POO tem 4 aulas/semana, etc.).
*   **Onde é usado?**
    *   `Página 1 (Planejamento)`: Para calcular quantas linhas (aulas) devem ser geradas na tabela do plano trimestral.
    *   `Página 6 (Config. Componentes)`: É a interface que permite editar este arquivo de forma visual.

### 5. `professor_config.json`
*   **O que é?** É o **Perfil Personalizado do Professor**. Ele guarda as turmas e componentes que cada professor selecionou para si.
*   **Onde é usado?** Em quase todas as páginas, para filtrar a interface e mostrar apenas o que é relevante para o professor logado.
*   **Como editar?** Pela `Página 5 (Configuração)` no sistema. Cada professor terá o seu.

### 6. `planejamentos.json`
*   **O que é?** É o seu **Arquivo de Rascunhos Salvos**. Toda vez que você clica em "💾 Salvar Planejamento" na Página 1, o conteúdo da tabela é guardado aqui.
*   **Onde é usado?**
    *   `Página 1 (Planejamento)`: O sistema verifica este arquivo primeiro. Se encontrar um plano salvo para a turma/componente, ele o carrega, evitando que você perca seu trabalho.
*   **Como editar?** Indiretamente, ao salvar um planejamento na `Página 1`.

---

## 🗑️ Arquivos Antigos (Podem ser Arquivados)

Durante o desenvolvimento, criamos vários arquivos para testes. Os arquivos listados abaixo **não são mais utilizados** pelo sistema e podem ser **removidos ou movidos** para uma pasta `_arquivados` para limpar o projeto e evitar confusão.

*   `ementas.json`
*   `ementas_completo.json`
*   `ementas_geral_1trimestre.json`
*   `ementas_oficiais.json`
*   `ementas_oficiais_tecnico.json`
*   `competencias_oficiais.json`
*   `escola.json`
*   `data_alunos.json`

Manter apenas os 5 arquivos ativos na pasta `data/` tornará o projeto muito mais claro.

---

## 🔗 Fluxo de Dados Simplificado

1.  **Primeiro Acesso**: O professor vai à **Página 5 (Configuração)**.
2.  **Seleção**: A página lê `escola_db.json` para mostrar as turmas oficiais. O professor escolhe as suas e salva, gerando seu `professor_config.json`.
3.  **Planejamento**: O professor vai à **Página 1 (Planejamento)**.
    *   O sistema lê `professor_config.json` para saber quais turmas e componentes mostrar.
    *   Para gerar o plano, ele busca as regras em `config_componentes.json` e o conteúdo em `curriculo_db.json`.
    *   Ao salvar, o trabalho vai para `planejamentos.json`.
4.  **Gestão de Turma**: O professor vai à **Página 3 (Frequência)**.
    *   O sistema lê `professor_config.json` para mostrar a turma correta e busca os nomes em `alunos.json`.

---

## 💾 Como Fazer Backup dos Dados

Para garantir a segurança das informações (planejamentos salvos, configurações e listas de alunos), recomenda-se fazer cópias de segurança regularmente.

### Procedimento Simples:
1.  **Localize a pasta `data/`**: Ela está na raiz do projeto e contém todos os arquivos JSON importantes.
2.  **Copie a pasta**: Copie a pasta `data/` inteira.
3.  **Salve em local seguro**: Cole em um Pen Drive, Google Drive ou outra pasta (ex: `backup_data_2026-02-22`).

**Para restaurar:** Basta substituir a pasta `data/` atual pela versão do backup.

Espero que este guia ajude a clarear a estrutura!
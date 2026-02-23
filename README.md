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

1.  Clone o repositório:
    ```bash
    git clone https://github.com/seu-usuario/planejador-ceti.git
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

## 📂 Configuração de Dados (Importante!)

Por questões de segurança e LGPD, os dados reais dos alunos não estão incluídos neste repositório.

1.  Vá até a pasta `data/`.
2.  Renomeie o arquivo `alunos_sample.json` para `alunos.json`.
3.  Edite o arquivo `alunos.json` com os dados reais da sua turma ou importe via sistema.
4.  O arquivo `escola_db.json` contém a estrutura das turmas e componentes. Ajuste conforme a matriz da sua escola.

## ▶️ Como Rodar

Execute o comando abaixo no terminal:

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
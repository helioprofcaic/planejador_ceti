import os

def criar_arquivo_aula(filepath, escola, professor, componente, turma, semana, aula_num, tema, objetivos, conteudo, atividade, quiz):
    content = f"""# 🏫 Escola: {escola}
# 👨‍🏫 Professor: {professor}
# 📚 Componente: {componente}
# 🎓 Turma: {turma}
# 📅 Semana: {semana:02d} | Aula: {aula_num:02d}

---

## 🎯 Objetivos da Aula
{objetivos}

## 📑 Sumário
1. Introdução e Contextualização
2. Desenvolvimento do Tema
3. Atividade Prática
4. Avaliação e Fechamento

---

## 💡 Tópicos Abordados

{conteudo}

---

## 🛠️ Atividade Prática
**Título:** {tema} na Prática

**Instruções:**
{atividade}

---

## 📝 Quiz de Fixação
{quiz}
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Criado: {filepath}")

# --- CONFIGURAÇÃO GERAL ---
output_dir = os.path.join("data", "aulas")
os.makedirs(output_dir, exist_ok=True)

escola = "CETI PROFESSOR RALDIR CAVALCANTE BASTOS"
professor = "Helio Lima"

# ==============================================================================
# DISCIPLINA 1: PENSAMENTO COMPUTACIONAL II (2º ANO DS) - 8 AULAS
# ==============================================================================
comp_pc = "PENSAMENTO COMPUTACIONAL II"
turma_pc = "2ª SÉRIE - Turma: I-B (Técnico DS)"

conteudos_pc = [
    {
        "tema": "Boas-vindas e Revisão de Lógica",
        "obj": "- Apresentar o plano de curso.\n- Revisar os 4 pilares do Pensamento Computacional.",
        "cont": "### 1. Os 4 Pilares\n- **Decomposição:** Quebrar problemas grandes em menores.\n- **Reconhecimento de Padrões:** Identificar similaridades.\n- **Abstração:** Focar no essencial.\n- **Algoritmos:** Passo a passo da solução.\n\n### 2. Dinâmica de Grupo\nDiscussão sobre como usamos algoritmos no dia a dia (ex: receita de bolo, trajeto para escola).",
        "ativ": "Em grupos, descrever o algoritmo para 'Trocar uma lâmpada' utilizando os 4 pilares.",
        "quiz": "1. Qual pilar envolve ignorar detalhes irrelevantes?\n   - [ ] a) Decomposição\n   - [x] b) Abstração\n   - [ ] c) Algoritmo"
    },
    {
        "tema": "Ambiente de Desenvolvimento (IDE)",
        "obj": "- Configurar o ambiente de programação.\n- Executar o primeiro código 'Hello World'.",
        "cont": "### 1. Ferramentas\n- Instalação do Python.\n- Configuração do VS Code.\n- Uso do Google Colab como alternativa.\n\n### 2. O Terminal\nComandos básicos e execução de scripts `.py`.",
        "ativ": "Instalar o VS Code e criar um arquivo `ola.py` que imprime seu nome e uma frase motivacional.",
        "quiz": "1. Qual a extensão de um arquivo Python?\n   - [ ] a) .java\n   - [x] b) .py\n   - [ ] c) .txt"
    },
    {
        "tema": "Variáveis e Tipos de Dados (Revisão)",
        "obj": "- Relembrar tipagem dinâmica no Python.\n- Manipular strings e números.",
        "cont": "### 1. Tipos Primitivos\n- `int` (Inteiros)\n- `float` (Decimais)\n- `str` (Textos)\n- `bool` (Booleanos)\n\n### 2. Conversão (Casting)\nUso de `int()`, `str()` e `float()`.",
        "ativ": "Criar um programa que pede o nome e a idade do usuário, e calcula em que ano ele fará 100 anos.",
        "quiz": "1. Qual função converte texto para número inteiro?\n   - [x] a) int()\n   - [ ] b) str()\n   - [ ] c) float()"
    },
    {
        "tema": "Operadores Aritméticos e Lógicos",
        "obj": "- Realizar cálculos matemáticos.\n- Utilizar lógica booleana.",
        "cont": "### 1. Aritmética\nSoma `+`, Subtração `-`, Multiplicação `*`, Divisão `/`, Resto `%`.\n\n### 2. Lógica\nOperadores `and`, `or`, `not`. Tabelas verdade.",
        "ativ": "Desenvolver uma calculadora de IMC (Índice de Massa Corporal) simples.",
        "quiz": "1. O que resulta `10 % 3`?\n   - [ ] a) 3\n   - [x] b) 1\n   - [ ] c) 0"
    },
    {
        "tema": "Estruturas Condicionais Simples",
        "obj": "- Implementar tomadas de decisão no código.",
        "cont": "### 1. O comando IF\nSintaxe básica e indentação.\n\n### 2. O comando ELSE\nDefinindo o caminho alternativo.",
        "ativ": "Criar um verificador de maioridade: Se idade >= 18, imprime 'Maior', senão 'Menor'.",
        "quiz": "1. O que é obrigatório após a condição do `if`?\n   - [ ] a) Ponto e vírgula\n   - [x] b) Dois pontos (:)\n   - [ ] c) Chaves {}"
    },
    {
        "tema": "Estruturas Condicionais Aninhadas (Elif)",
        "obj": "- Tratar múltiplas condições.",
        "cont": "### 1. O comando ELIF\nEncadeando múltiplas verificações.\n\n### 2. Boas Práticas\nEvitando o 'hadouken' (excesso de indentação).",
        "ativ": "Sistema de Notas: Recebe nota 0-10 e classifica em: Reprovado, Recuperação, Aprovado, Excelente.",
        "quiz": "1. Quantos `elif` posso ter em um bloco?\n   - [ ] a) Apenas 1\n   - [x] b) Quantos forem necessários\n   - [ ] c) No máximo 3"
    },
    {
        "tema": "Introdução a Listas",
        "obj": "- Armazenar múltiplos dados em uma variável.",
        "cont": "### 1. Criação de Listas\nSintaxe `[]` e índices (começando em 0).\n\n### 2. Métodos Básicos\n`append()`, `remove()`, `len()`.",
        "ativ": "Criar uma lista de compras onde o usuário pode adicionar 5 itens via input.",
        "quiz": "1. Como acesso o primeiro item da lista `L`?\n   - [x] a) L[0]\n   - [ ] b) L[1]\n   - [ ] c) L.first()"
    },
    {
        "tema": "Avaliação Diagnóstica Prática",
        "obj": "- Verificar o nível de assimilação da turma.",
        "cont": "### 1. Desafio de Código\nResolução de 3 problemas práticos envolvendo todo o conteúdo da semana.\n\n### 2. Correção Comentada\nFeedback imediato.",
        "ativ": "Resolver a lista de exercícios 'Semana 01' no laboratório.",
        "quiz": "1. (Questão bônus) Python é uma linguagem:\n   - [ ] a) Compilada\n   - [x] b) Interpretada\n   - [ ] c) De baixo nível"
    }
]

for i, aula in enumerate(conteudos_pc):
    filename = f"2ano_PCII_Sem01_Aula{i+1:02d}.md"
    criar_arquivo_aula(os.path.join(output_dir, filename), escola, professor, comp_pc, turma_pc, 1, i+1, aula["tema"], aula["obj"], aula["cont"], aula["ativ"], aula["quiz"])


# ==============================================================================
# DISCIPLINA 2: TESTES DE SISTEMAS (3º ANO DS) - 4 AULAS (Semana 1)
# ==============================================================================
comp_testes = "TESTE DE SISTEMAS E SEGURANÇA DE DADOS"
turma_testes = "3ª SÉRIE - Turma: I-A (Técnico DS)"

conteudos_testes = [
    {
        "tema": "Introdução à Qualidade de Software",
        "obj": "- Compreender o conceito de qualidade.\n- Diferenciar Erro, Defeito e Falha.",
        "cont": "### 1. Por que testar?\nO custo do erro em produção. Casos famosos de falhas de software.\n\n### 2. Terminologia\n- **Erro:** Ação humana.\n- **Defeito (Bug):** O problema no código.\n- **Falha:** O comportamento inesperado visível.",
        "ativ": "Pesquisar um caso real de falha de software que causou prejuízo financeiro e apresentar para a turma.",
        "quiz": "1. Quem comete o 'Erro'?\n   - [ ] a) O computador\n   - [x] b) O desenvolvedor\n   - [ ] c) O usuário"
    },
    {
        "tema": "Verificação e Validação (V&V)",
        "obj": "- Distinguir os dois conceitos fundamentais da qualidade.",
        "cont": "### 1. Verificação\n'Estamos construindo o produto corretamente?' (Foco no processo/requisitos).\n\n### 2. Validação\n'Estamos construindo o produto certo?' (Foco na necessidade do cliente).",
        "ativ": "Debate: Um software pode ser verificado mas não validado? Dê exemplos.",
        "quiz": "1. Testar se o software atende ao desejo do cliente é:\n   - [ ] a) Verificação\n   - [x] b) Validação\n   - [ ] c) Depuração"
    },
    {
        "tema": "O Modelo V de Desenvolvimento",
        "obj": "- Entender como os testes se encaixam no ciclo de vida.",
        "cont": "### 1. O 'V'\nLado esquerdo (Desenvolvimento) vs Lado direito (Testes).\n\n### 2. Níveis de Teste\nUnitário, Integração, Sistema e Aceitação.",
        "ativ": "Desenhar o Modelo V no caderno e mapear quais testes validam quais fases do projeto.",
        "quiz": "1. Qual teste valida o Código/Unidade?\n   - [x] a) Teste Unitário\n   - [ ] b) Teste de Sistema\n   - [ ] c) Teste de Aceitação"
    },
    {
        "tema": "Tipos de Teste: Caixa Branca vs Caixa Preta",
        "obj": "- Classificar as técnicas de teste.",
        "cont": "### 1. Caixa Branca\nTeste estrutural. O testador conhece o código fonte.\n\n### 2. Caixa Preta\nTeste funcional. O testador foca nas entradas e saídas, sem ver o código.",
        "ativ": "Simulação: Testar uma 'Caixa Misteriosa' (função desconhecida) apenas inserindo valores e observando o resultado (Caixa Preta).",
        "quiz": "1. O teste funcional, focado na entrada/saída, é:\n   - [ ] a) Caixa Branca\n   - [x] b) Caixa Preta\n   - [ ] c) Caixa Cinza"
    }
]

for i, aula in enumerate(conteudos_testes):
    filename = f"3ano_Testes_Sem01_Aula{i+1:02d}.md"
    criar_arquivo_aula(os.path.join(output_dir, filename), escola, professor, comp_testes, turma_testes, 1, i+1, aula["tema"], aula["obj"], aula["cont"], aula["ativ"], aula["quiz"])

print("\n✨ Processo concluído! 12 planos de aula gerados na pasta 'data/aulas'.")
